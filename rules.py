from dataclasses import dataclass , asdict
import re 

@dataclass(frozen=True)
class Rule:
    key: str
    title: str
    pattern: str
    severity: str 
    meaning : str 
    next_step : str 
    base_score: int 

Rules: tuple[Rule, ... ] = (
    Rule(
        key="out of memory", 
        title="possible lack of memory",
        pattern=r"OutOfMemoryError|Java heap space|GC overhead limit exceeded|Direct buffer memory|Metaspace",
        severity="critical",
        meaning="JVM has run out of memory",
        next_step="Increase memory limit or look for memory leak",
        base_score=95,
    ),
    Rule(
        key="missing class", 
        title="missing class or depenancy",
        pattern=r"NoClassDefFoundError|ClassNotFoundException",
        severity="High",
        meaning="a class could not be loaded , A missing dependancy , incompatible version or failed initialisation",
        next_step="inspect 'caused by' section and verify minecraft , loader, mods and dependancys",
        base_score=88,
    ),
    Rule(
        key="mod_loading",
        title="mod loading or inititilization failure",
        pattern=r"ModLoadingException|Failed to load mod|Failed to construct mod|Exception while loading.*mod|Error loading mod",
        severity="High",
        meaning="a mod has failed during startup or inititilization",
        next_step="read the exception chain and check dependancies and requirements",
        base_score=82,
    ),
        Rule(
        key="server_tick",
        title="exception in server tick loop",
        pattern=r"Exception in server tick loop|Ticking entity|Ticking block entity",
        severity="High",
        meaning="an excepssion occured while game or server was processing a tick, root cause often somewhere in stack trace",
        next_step="inspect cause and the first relevent entity / block entity / non-vanilla class",
        base_score=78,
    ),
        Rule(
        key="class_version",
        title="java bytecode version missmatch",
        pattern=r"UnsupportedClassVersionError",
        severity="high",
        meaning="a class may have never bene compiled for a newer java version",
        next_step="check the Minecraft version's required Java version and the java executable",
        base_score=84,
    ),
        Rule(
        key="incompatible mods",
        title="possible mod or version incompatability",
        pattern=r"Incompatible mod set|requires .* but .* is present|Mod resolution failed|depends on .* which is missing",
        severity="high",
        meaning="the mod looader detected an incompatible or missing mod requirement",
        next_step="check dependancy / version requirement",
        base_score=85,
    ),
        Rule(
        key="server_lag",
        title="server tick delay",
        pattern=r"Can't keep up!|Can't keep up,|overloaded\? Running .*ms or .* ticks behind",
        severity="warning",
        meaning="the server is falling behind its tick schedule , performance warning",
        next_step= "profile with spark and inspect entities , chunk generation , block entities, and mod tasks",
        base_score=45,
    ),
        Rule(
        key="timeout",
        title="timeout or stalled operation",
        pattern=r"Timed out|Read timed out|Connection timed out|Watchdog.*crash",
        severity="warning",
        meaning="connection or an operation took too long , server stalls or networking",
        next_step= "compare timestamp with server tps, thread dumps / profiler data and network symptoms",
        base_score=48,
    ),
        Rule(
        key="mixin failure",
        title="mixin transformation failure",
        pattern=r"MixinApplyError|Mixin apply failed|MixinTransformerError|InvalidMixinException",
        severity="high",
        meaning="a maxin transformation failed , a version mismatch or conflicting mods",
        next_step="identify the mixin name , target class and first revelvant exception",
        base_score=86,
    ),
)
