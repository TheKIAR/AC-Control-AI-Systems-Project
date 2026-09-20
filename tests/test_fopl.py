from src.fopl.advisor import build_advisor, build_rules, temp_band
from src.fopl.knowledge_base import Atom, KnowledgeBase, Rule, Variable


def test_temp_bands_match_fuzzy_thresholds():
    assert temp_band(16) == "Cold"
    assert temp_band(20) == "Comfort"
    assert temp_band(24) == "Warm"
    assert temp_band(28) == "Hot"
    assert temp_band(33) == "ExtremeHeat"


def test_hot_occupied_full_cooling():
    result = build_advisor(30, occupied=True, night=False, energy_saver=False)
    assert "AC_HIGH(R1)" in result["conclusions"]
    assert "AC_ECO(R1)" not in result["conclusions"]


def test_saver_mode_caps_cooling_at_eco():
    result = build_advisor(30, occupied=True, night=False, energy_saver=True)
    assert "AC_ECO(R1)" in result["conclusions"]
    assert "AC_HIGH(R1)" not in result["conclusions"]


def test_empty_room_saves_energy():
    result = build_advisor(30, occupied=False)
    assert "AC_OFF(R1)" in result["conclusions"]
    assert "BLINDS_DOWN(R1)" in result["conclusions"]
    assert "LIGHTS_OFF(R1)" in result["conclusions"]
    assert "AC_HIGH(R1)" not in result["conclusions"]


def test_cold_room_heating_policy():
    assert "HEATER_ON(R1)" in build_advisor(16, occupied=True)["conclusions"]
    assert "HEATER_OFF(R1)" in build_advisor(16, occupied=False)["conclusions"]


def test_comfort_standby_and_ventilation():
    assert "AC_STANDBY(R1)" in build_advisor(22, occupied=True)["conclusions"]
    assert "WINDOWS_OPEN(R1)" in build_advisor(26, occupied=False, night=False)["conclusions"]
    assert "WINDOWS_OPEN(R1)" not in build_advisor(26, occupied=False, night=True)["conclusions"]


def test_night_lighting_and_overheat_alert():
    assert "DIM_LIGHTS(R1)" in build_advisor(22, occupied=True, night=True)["conclusions"]
    assert "ALERT_OVERHEAT(R1)" in build_advisor(35)["conclusions"]
    assert "AC_HIGH(R1)" in build_advisor(35, occupied=True)["conclusions"]


def test_trace_explains_every_conclusion():
    result = build_advisor(32, occupied=True, night=True, energy_saver=False)
    assert len(result["fired"]) >= 2  # cooling + lighting rules fire
    assert any("R1-HighCooling" in line for line in result["fired"])
    assert any("R8-NightDim" in line for line in result["fired"])


def test_negation_as_failure_and_fixpoint():
    kb = KnowledgeBase(constants=["R1"])
    r = Variable("r")
    kb.rules.append(Rule(
        "NoOccupant", ["r"],
        [Atom("Occupied", [r], negated=True)],
        Atom("LightsOff", [r]),
    ))
    trace = kb.forward_chain()
    assert ("LightsOff", ("R1",)) in kb.facts
    assert kb.ask("LightsOff") == [("R1",)]
    # Second run reaches fixpoint immediately with no new firings.
    assert kb.forward_chain() == []
    assert len(trace) == 1


def test_chained_rules_fire_in_order():
    kb = KnowledgeBase(constants=["R1"])
    r = Variable("r")
    kb.tell("Motion", "R1")
    kb.rules.append(Rule("R1", ["r"], [Atom("Motion", [r])], Atom("Occupied", [r])))
    kb.rules.append(Rule("R2", ["r"], [Atom("Occupied", [r])], Atom("LightsOn", [r])))
    trace = kb.forward_chain()
    assert [name for name, _, _ in trace] == ["R1", "R2"]
    assert ("LightsOn", ("R1",)) in kb.facts


def test_thirteen_policy_rules():
    assert len(build_rules()) == 13
