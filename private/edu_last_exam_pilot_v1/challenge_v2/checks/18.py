"""Offline rational distractor and one-slip diagnosis audit; no API calls."""
import csv
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ("C", "E1", "E2", "E3")


def outputs(row):
    a, b, c, d = (int(row[k]) for k in ("a", "b", "c", "d"))
    return (F(a*d+b*c, b*d), F(a+c, b+d), F(a+c, max(b, d)), F(a+b*c, b*d))


def distance(left, right):
    return sum(a != b for a, b in zip(left, right))


def main():
    with (ROOT / "stimuli/18/item_bank.csv").open() as handle:
        bank = {row["item_id"]: outputs(row) for row in csv.DictReader(handle)}
    assert bank["P1"] == (F(5, 6), F(2, 5), F(2, 3), F(1, 2))
    assert bank["P2"] == (F(7, 12), F(2, 7), F(1, 2), F(1, 3))
    assert bank["P3"] == (F(13, 20), F(1, 3), F(3, 5), F(7, 20))
    assert bank["P4"] == (F(13, 20), F(1, 3), F(3, 5), F(9, 20))
    assert bank["P5"] == (F(5, 6), F(1, 3), F(1, 2), F(5, 18))
    assert bank["P6"][0] == bank["P6"][2] == F(2, 3)
    assert F(1, 3) == F(3, 9)
    valid = [k for k, values in bank.items() if len(set(values)) == 4]
    assert valid == ["P1", "P2", "P3", "P4", "P5"]
    assert all(0 < value < 1 for k in valid for value in bank[k])
    triples = list(combinations(valid, 3))
    assert len(triples) == 10
    tested_records = 0
    for selected in triples:
        expected = [tuple(bank[k][rule] for k in selected) for rule in range(4)]
        assert all(distance(a, b) == 3 for a, b in combinations(expected, 2))
        for observed in product(*(bank[k] for k in selected)):
            compatible = [i for i, profile in enumerate(expected) if distance(observed, profile) <= 1]
            assert len(compatible) <= 1
            tested_records += 1
        for profile in expected:
            assert sum(distance(obs, profile) <= 1 for obs in product(*(bank[k] for k in selected))) == 10
    for pair in combinations(valid, 2):
        # A mixed C/E1 record is one slip from each, proving non-identifiability.
        c = tuple(bank[k][0] for k in pair)
        e1 = tuple(bank[k][1] for k in pair)
        mixed = (c[0], e1[1])
        assert distance(mixed, c) == distance(mixed, e1) == 1
    profiles = [tuple(bank[k][i] for k in ("P1", "P2", "P3")) for i in range(4)]
    observed_l = (F(2, 5), F(1, 2), F(1, 3))
    observed_m = (F(5, 6), F(1, 2), F(7, 20))
    assert tuple(distance(observed_l, p) for p in profiles) == (3, 1, 2, 3)
    assert tuple(distance(observed_m, p) for p in profiles) == (2, 3, 2, 2)
    print(f"PASS 18: {len(triples)} valid triples, {tested_records} answer records, minimum-length counterexamples, L/M diagnosis")


if __name__ == "__main__":
    main()
