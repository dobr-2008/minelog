from __future__ import annotations

from rules import Rules, Rule
import re 
from dataclasses import dataclass, asdict
from typing import Any 

_Framework_Prefixes_ = (
    "java.", "javax." , "jdk." , "sun." , "com.sun", "net.minecraft",
    "com.mojang", "net.fabricmc." , "net.minecraftforge." , "cpw.mods.",
    "org.spongepowered.", "org.objectweb." , "org.lwjgl." , "kotlin.",
)

_Cause_Re = re.compile(r"^\s*Caused by:\s*(.+)$", re.IGNORECASE)
_Exception_Re = re.compile(r"(?:[\w.$]+(?:Exception|Error)|FATAL|CRITICAL)")
_Stack_Frame_Re_ = re.compile(r"^\s*at\s+([\w.$]+)\([^)]*\)")

def line_has_error(line: str ) -> bool:
    return bool(re.search(r"\b(ERROR|FATAL|CRITICAL)\b|\b\w+(?:Exception|Error)\b", line, re.I))

def line_has_warning(line: str ) -> bool:
     return bool(re.search(r"\bWARN(?:ING)?\b", line, re.I))

def extract_cause(lines: list[str]) -> dict[str , Any] | None:
     matches = []
     for index, line in enumerate(lines):
          match = _Cause_Re.search(line)
          if match:
               matches.append({"line_number" : index + 1 , "text": line.strip() , "cause": match.group(1).strip()})
     return matches[-1] if matches else None

def package_hints(lines: list[str], cause: dict[str,Any] | None, limit: int = 5) -> list[dict[str, Any]]:
     start = max(0 , (cause ["line_number"] -1 ) if cause else 0)
     candidates: list[dict[str,Any]] = []
     seen: set[str] = set()
     for index in range(start, min(len(lines), start + 80)):
          match = _Stack_Frame_Re_.search(lines[index])
          if not match:
               continue
          class_name = match.group(1).rsplit("." , 1) [0] if "." in match.group(1) else match.group(1)
          if class_name.startswith(_Framework_Prefixes_):
               continue
          package = class_name.rsplit("." , 1)[0] if "." in class_name else class_name
          if package not in seen:
               seen.add(package)
               candidates.append({"line_number": index + 1, "class_name" : class_name, "package_hint": package})
          if len(candidates) >= limit:
               break 
     return candidates

def analyze_log(log_text: str , context_lines: int = 2 ) -> dict [str , Any]:
     if not isinstance(log_text, str):
          raise TypeError("log_text must be a string")
     if context_lines <0 or context_lines > 10:
          raise ValueError("context_lines must be between 0 and 10")

     lines = log_text.splitlines()
     findings: list[dict[str , Any]] = []

     for rule in Rules:
          regex = re.compile(rule.pattern , re.IGNORECASE)
          matched_index = [i for i, line in enumerate(lines) if regex.search(line)]
          if not matched_index:
               continue
          evidence = []
          seen_ranges: set[tuple[ int , int ]] = set()
          for index in matched_index[:8]:
               start = max(0, index - context_lines)
               end = min(len(lines), index + context_lines + 1)
               if (start, end) in seen_ranges:
                    continue
               seen_ranges.add((start , end ))
               evidence.append({
                    "line_number": index+1,
                    "text":lines[index].strip()[:700],
                    "context_start": start + 1,
                    "context": [line[:700] for line in lines[start:end]],
               })

          findings.append({
               **asdict(rule),
               "total_matches": len(matched_index),
               "score": min(99, rule.base_score + min(len(matched_index) -1 , 5 )),
               "evidence": evidence,
          })
     findings.sort(key=lambda item: (item["score"] , item["total_matches"]), reverse=True)
     root_cause = extract_cause(lines)
     pkg_hints = package_hints(lines, root_cause)

     return {
          "total_lines": len(lines),
          "error_like_lines": sum(line_has_error(line) for line in lines ),
          "warning_lines": sum(line_has_warning(line) for line in lines ),
          "findings": findings,
          "deepest_cause": root_cause,
          "package_hints": pkg_hints,
          "notes": [            
            "A matching pattern is evidence of a symptom, not proof of the root cause.",
            "Package hints are not verified mod IDs.",
          ],
     }

def format_report(filename: str , analysis: dict[str , Any], ai_explanation: str  | None = None) -> str:
     out = [ 
          "minelog diagnostic report",
          "=" * 32,
          f"File: {filename}",
          f"Total Lines: {analysis['total_lines']}" ,
          f"Error-like lines: {analysis['error_like_lines']}",
          f"Warning lines: {analysis['warning_lines']}",
          "",
          "Rule-Based findings",
          "=" * 32 
     ]
     if not analysis["findings"]:
          out.append("No configured error patterns were detected, This does not prove the log is healthy")
     for finding in analysis["findings"]:
          out.extend([
               "",
               f"[{finding['severity']}] {finding['title']} — heuristic priority {finding['score']}/99",
               f"Meaning: {finding['meaning']}",
               f"Suggested next step: {finding['next_step']}",
               f"Matches: {finding['total_matches']}",
          ])
          for evidence in finding["evidence"]:
               out.append(f" Line {evidence['line_number']}: {evidence['text']}")

     if analysis.get("package_hints"):
          out.extend(["", "PACKAGE / CLASS HINTS (NOT VERIFIED MOD IDS)"])
          for hint in analysis["package_hints"]:
               out.append(f"Line {hint['line_number']}: {hint['class_name']} ({hint['package_hint']})")

     if ai_explanation:
          out.extend(["", "ai explanation", "=" * 32, ai_explanation.strip()])

     out.extend([
                  "",
        "CAUTION",
        "This report contains hypotheses to investigate, not a guaranteed root-cause diagnosis.",
        "Review the original log and back up worlds/configuration before making changes."

     ])
     return "\n".join(out)

