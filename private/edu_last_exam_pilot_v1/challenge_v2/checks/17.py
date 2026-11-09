"""Offline exact-arithmetic audit of synthetic anchor calibration; no API calls."""
from fractions import Fraction as F
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "stimuli/17/calibration.json").read_text(), parse_float=F)
extra = json.loads((ROOT / "stimuli/17/joint_anchor.json").read_text(), parse_float=F)


def joint_table(pa, pb, both):
    table = (both, pa - both, pb - both, 1 - pa - pb + both)
    assert min(table) >= 0 and sum(table) == 1
    assert table[0] + table[1] == pa and table[0] + table[2] == pb
    return table


def main():
    anchor = data["single_skill_anchor_model"]
    low = anchor["correct_if_not_mastered"]
    span = anchor["correct_if_mastered"] - low
    marginal = {g: tuple((obs[k] - low) / span for k in ("A_anchor", "B_anchor"))
                for g, obs in data["historical_anchor_correct_probabilities"].items()}
    assert marginal == {"G1": (F(4, 5), F(3, 5)), "G2": (F(2, 5), F(7, 10))}
    weights = data["target_group_weights"]
    pa, pb = (sum(weights[g] * marginal[g][i] for g in weights) for i in (0, 1))
    assert (pa, pb) == (F(1, 2), F(27, 40))
    bounds = {g: (max(F(0), sum(p) - 1), min(p)) for g, p in marginal.items()}
    joint_bounds = tuple(sum(weights[g] * bounds[g][i] for g in weights) for i in (0, 1))
    assert joint_bounds == (F(7, 40), F(9, 20))
    models = data["candidate_response_models"]
    jmodel = models["J"]
    jscore = lambda j: jmodel["correct_otherwise"] + (jmodel["correct_if_both_mastered"] - jmodel["correct_otherwise"]) * j
    jrange = tuple(map(jscore, joint_bounds))
    amodel, bmodel = models["A_only"], models["B_only"]
    ascore = amodel["correct_otherwise"] + (amodel["correct_if_A_mastered"] - amodel["correct_otherwise"]) * pa
    bscore = bmodel["correct_otherwise"] + (bmodel["correct_if_B_mastered"] - bmodel["correct_otherwise"]) * pb
    assert jrange == (F("0.36375"), F("0.5425"))
    assert ascore == F("0.5") and bscore == F("0.70625")
    assert jrange[0] < ascore < jrange[1] < bscore
    for i in (0, 1):
        for g, (a, b) in marginal.items():
            joint_table(a, b, bounds[g][i])
    band_low, band_high = data["selection_band"]
    assert band_low <= ascore <= band_high
    assert jrange[0] < band_low and bscore > band_high
    updated = {g: (q - extra["correct_otherwise"]) / (extra["correct_if_both_mastered"] - extra["correct_otherwise"])
               for g, q in extra["group_correct_probabilities"].items()}
    assert updated == {"G1": F(1, 2), "G2": F(3, 10)}
    for g, both in updated.items():
        joint_table(*marginal[g], both)
    updated_jscore = jscore(sum(weights[g] * updated[g] for g in weights))
    assert updated_jscore == F("0.4775")
    assert band_low <= updated_jscore < ascore <= band_high
    # Exhaust all hundredth-grid joint probabilities, not just the two witnesses.
    feasible = []
    for j1 in (F(i, 100) for i in range(101)):
        for j2 in (F(i, 100) for i in range(101)):
            if bounds["G1"][0] <= j1 <= bounds["G1"][1] and bounds["G2"][0] <= j2 <= bounds["G2"][1]:
                feasible.append(jscore(weights["G1"] * j1 + weights["G2"] * j2))
    assert (min(feasible), max(feasible)) == jrange
    print(f"PASS 17: exact bounds, feasible endpoint tables, {len(feasible)} joint worlds, updated selection")


if __name__ == "__main__":
    main()
