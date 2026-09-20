"""Smart-room advisor: FOPL knowledge base for climate + energy policy.

Real-world use case: a classroom / study room controller that decides
AC, heating, lighting, blinds, windows and safety alerts from sensor
facts (temperature, occupancy, night, energy-saver mode).

Temperature bands intentionally match the project's fuzzy controller:
Cold < 20°C, Comfort 20–24°C, Warm 24–28°C, Hot ≥ 28°C, plus an
ExtremeHeat ≥ 33°C safety band.
"""

from .knowledge_base import Atom, KnowledgeBase, Rule, Variable

ROOM = "R1"

COLD_MAX = 20.0
COMFORT_MAX = 24.0
WARM_MAX = 28.0
EXTREME_MIN = 33.0

ACTION_PREDICATES = (
    "AC_HIGH",
    "AC_ECO",
    "AC_OFF",
    "AC_STANDBY",
    "HEATER_ON",
    "HEATER_OFF",
    "LIGHTS_OFF",
    "DIM_LIGHTS",
    "BLINDS_DOWN",
    "WINDOWS_OPEN",
    "ALERT_OVERHEAT",
)


def temp_band(temperature):
    """Map a temperature reading to its qualitative band predicate."""
    temperature = float(temperature)
    if temperature >= EXTREME_MIN:
        return "ExtremeHeat"
    if temperature >= WARM_MAX:
        return "Hot"
    if temperature >= COMFORT_MAX:
        return "Warm"
    if temperature >= COLD_MAX:
        return "Comfort"
    return "Cold"


def _r(name, premises, conclusion, description=""):
    """premises: list of (predicate, positive_bool). False = negated ¬."""
    r = Variable("r")
    return Rule(
        name,
        ["r"],
        [Atom(pred, [r], negated=(not positive)) for pred, positive in premises],
        Atom(conclusion, [r]),
        description,
    )


def build_rules():
    """The room policy: 13 FOPL rules with variables, ∧ and ¬."""
    return [
        _r("R1-HighCooling",
           [("Hot", True), ("Occupied", True), ("EnergySaver", False)],
           "AC_HIGH", "Hot occupied room, full comfort → strong cooling."),
        _r("R2-EcoCooling",
           [("Warm", True), ("Occupied", True)],
           "AC_ECO", "Warm occupied room → eco cooling."),
        _r("R3-SaverCooling",
           [("Hot", True), ("Occupied", True), ("EnergySaver", True)],
           "AC_ECO", "Saver mode caps cooling at eco even when hot."),
        _r("R4a-EmptyHotAC",
           [("Hot", True), ("Occupied", False)],
           "AC_OFF", "Nobody in a hot room → AC off, save energy."),
        _r("R4b-EmptyHotBlinds",
           [("Hot", True), ("Occupied", False)],
           "BLINDS_DOWN", "Block sun in the empty hot room."),
        _r("R5-HeatOn",
           [("Cold", True), ("Occupied", True)],
           "HEATER_ON", "Cold occupied room → heating on."),
        _r("R6-HeatOff",
           [("Cold", True), ("Occupied", False)],
           "HEATER_OFF", "Nobody in a cold room → heating off."),
        _r("R7a-ComfortStandby",
           [("Comfort", True), ("Occupied", True)],
           "AC_STANDBY", "Comfortable and occupied → climate standby."),
        _r("R7b-ComfortEmpty",
           [("Comfort", True), ("Occupied", False)],
           "AC_OFF", "Comfortable and empty → everything off."),
        _r("R8-NightDim",
           [("Night", True), ("Occupied", True)],
           "DIM_LIGHTS", "Occupied at night → dimmed lighting."),
        _r("R9-LightsOff",
           [("Occupied", False)],
           "LIGHTS_OFF", "Empty room → lights off, day or night."),
        _r("R10-Ventilate",
           [("Warm", True), ("Occupied", False), ("Night", False)],
           "WINDOWS_OPEN", "Warm empty room by day → natural ventilation."),
        _r("R11-OverheatAlert",
           [("ExtremeHeat", True)],
           "ALERT_OVERHEAT", "Safety override at extreme heat."),
    ]


def build_advisor(temperature, occupied=True, night=False, energy_saver=False):
    """Ground sensor facts, run forward chaining, return results dict."""
    kb = KnowledgeBase(constants=[ROOM])
    band = temp_band(temperature)
    kb.tell(band, ROOM)
    if band == "ExtremeHeat":
        kb.tell("Hot", ROOM)  # extreme heat implies hot for cooling rules
    if occupied:
        kb.tell("Occupied", ROOM)
    if night:
        kb.tell("Night", ROOM)
    if energy_saver:
        kb.tell("EnergySaver", ROOM)
    kb.rules.extend(build_rules())

    trace = kb.forward_chain()
    facts = sorted(f"{pred}({', '.join(args)})" for pred, args in kb.facts)
    return {
        "temperature": float(temperature),
        "band": band,
        "occupied": bool(occupied),
        "night": bool(night),
        "energy_saver": bool(energy_saver),
        "facts": facts,
        "conclusions": kb.conclusions(ACTION_PREDICATES),
        "fired": kb.describe_trace(trace),
    }
