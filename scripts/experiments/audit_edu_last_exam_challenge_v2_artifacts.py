#!/usr/bin/env python3
"""Inspect this GLM trial's artifacts, without changing answers or grading them.

This is an exploratory audit, not a canonical benchmark scoring pipeline.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "reports/eval/edu_last_exam_challenge_v2/_exploratory/GLM-5.3/20261107_01"
OUT = ROOT / "reports/challenge_v2/reviews/2026-11-08"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", required=True)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    derived = OUT / "derived"
    derived.mkdir(exist_ok=True)
    cases = RUN / "cases"
    svg_raw = cases / "ELE-C2-19__base/attempt_01/artifacts/01_block_01.xml"
    svg_text = svg_raw.read_text()
    # Remove only the filename wrapper emitted on its own line; preserve SVG.
    svg_text = svg_text[svg_text.index("<svg"):]
    svg_copy = derived / "glm_corrected.svg"
    svg_copy.write_text(svg_text)
    xml = ET.fromstring(svg_text)
    assert not any(e.tag.rsplit("}", 1)[-1] == "script" for e in xml.iter())
    state_raw = cases / "ELE-C2-19__base/attempt_01/artifacts/02_block_02.json"
    state_text = state_raw.read_text()
    states = json.loads(state_text[state_text.index("{"):])["states"]
    state_checks = []
    for state in states:
        T = state["T_K"]
        h = min(10, 8 * T / 300)
        volume = 20 * h
        pressure = 100 * 160 * T / (300 * volume)
        force = max(0, (pressure - 100) * 1000 * .002)
        expected = {"h_cm": h, "V_cm3": volume, "P_kPa": pressure, "stop_force_N": force}
        ok = all(math.isclose(state[k], v, abs_tol=1e-8) for k, v in expected.items())
        state_checks.append({"id": state["id"], "expected": expected, "passed": ok})
    gas = [e for e in xml.iter() if e.tag.endswith("rect") and e.get("width") == "114" and e.get("height") not in {"14", None}]
    heights = [float(e.attrib["height"]) / 20 for e in gas]
    assert heights == [8, 10, 10, 8.8], heights
    assert all(float(e.attrib["y"]) + float(e.attrib["height"]) == 431 for e in gas)
    ascii_rows = {}
    for student, filename in (("A", "01_student_A.md"), ("B", "02_student_B.md")):
        text = (cases / "ELE-C2-14__base/attempt_01/artifacts" / filename).read_text()
        ascii_rows[student] = [{"line": number, "strip": m.group(), "characters": len(m.group())}
                               for number, line in enumerate(text.splitlines(), 1)
                               if (m := re.search(r"(?:\[[# :]*\])+", line))]
    page_errors, blocked_requests = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.browser, headless=True, args=["--no-sandbox"])
        context = browser.new_context(viewport={"width": 1320, "height": 1000}, service_workers="block")

        def guard(route):
            url = route.request.url
            if url.startswith(("file:", "data:", "about:")):
                route.continue_()
            else:
                blocked_requests.append(url)
                route.abort()

        context.route("**/*", guard)
        page = context.new_page()
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.goto(svg_copy.as_uri())
        page.wait_for_load_state("networkidle")
        page.locator("svg").screenshot(path=str(OUT / "glm_piston.png"))
        html_path = cases / "ELE-C2-20__base/attempt_01/artifacts/01_corrected.html"
        page.goto(html_path.as_uri())
        page.wait_for_load_state("networkidle")
        snapshots = []

        def snap():
            state = page.evaluate("sim.snapshot()")
            assert abs(float(page.locator("#voltage").inner_text()) - state["voltage"]) <= .002
            assert abs(float(page.locator("#current").inner_text()) - 1000 * state["current"]) <= .002
            snapshots.append(state)

        def advance(dt):
            page.locator("#dt").fill(str(dt))
            page.locator("#advance").click()
            snap()

        def resistance(r):
            page.locator("#resistance").fill(str(r))
            page.locator("#resistance").dispatch_event("change")

        snap()
        advance(.3)
        page.locator("#mode").select_option("discharge")
        resistance(1000)
        snap()
        advance(.1)
        resistance(4000)
        snap()
        advance(.2)
        page.locator("#mode").select_option("charge")
        advance(.1)
        v1 = 10 * (1 - math.exp(-1.5))
        v2, v3 = v1 * math.exp(-1), v1 * math.exp(-1.5)
        v4 = 10 + (v3 - 10) * math.exp(-.25)
        expected = [(0, 0, .005), (.3, v1, (10-v1)/2000), (.3, v1, -v1/1000),
                    (.4, v2, -v2/1000), (.4, v2, -v2/4000), (.6, v3, -v3/4000),
                    (.7, v4, (10-v4)/4000)]
        protocol = []
        for actual, gold in zip(snapshots, expected, strict=True):
            passed = all(math.isclose(actual[k], v, abs_tol=1e-9) for k, v in zip(("time", "voltage", "current"), gold))
            protocol.append({"actual": {k: actual[k] for k in ("time", "voltage", "current")}, "expected": gold, "passed": passed})
        prefix_ok = all(after["samples"][:len(before["samples"])] == before["samples"] for before, after in zip(snapshots, snapshots[1:]))
        page.screenshot(path=str(OUT / "glm_rc_protocol.png"), full_page=True)
        page.locator("#reset").click()
        reset_state = page.evaluate("sim.snapshot()")
        reset_ok = reset_state["samples"] == [{"time": 0, "voltage": 0}] and reset_state["mode"] == "charge" and reset_state["resistance"] == 2000
        # A visible-condition probe: 2 seconds is allowed by the original task.
        advance(2)
        points = [tuple(map(float, point.split(','))) for point in page.locator("#trace").get_attribute("points").split()]
        assert len(points) == 2, points
        rendered_mid_y = (points[0][1] + points[1][1]) / 2
        rendered_mid_v = (260-rendered_mid_y)/23.5
        physics_mid_v = 10 * (1-math.exp(-1/.2))
        page.screenshot(path=str(OUT / "glm_rc_two_seconds.png"), full_page=True)
        # The same physical endpoint reached in 20 small UI steps should also
        # demonstrate how the display depends on the user's step size.
        page.locator("#reset").click()
        for _ in range(20):
            page.evaluate("sim.advance(.1)")
        small_state = page.evaluate("sim.snapshot()")
        page.screenshot(path=str(OUT / "glm_rc_twenty_steps.png"), full_page=True)
        report = {"scope": "Codex artifact inspection, not formal scoring", "model": "GLM-5.3",
                  "piston": {"states": state_checks, "svg_gas_heights_cm": heights, "uniform_scale_passed": True,
                              "format_normalization": "Removed only leading filename=corrected.svg / filename=states.json wrapper for parsing; not counted as content failure"},
                  "fraction_ascii_rows": ascii_rows,
                  "rc": {"protocol": protocol, "history_preserved": prefix_ok, "reset_passed": reset_ok,
                         "large_step_display": {"dt_s": 2, "polyline_points": points, "midpoint_t_s": 1,
                                                "display_interpolated_voltage_V": rendered_mid_v,
                                                "physical_voltage_V": physics_mid_v,
                                                "difference_V": physics_mid_v-rendered_mid_v},
                         "same_endpoint_small_steps": {"steps": 20, "dt_s": .1, "state": small_state},
                         "interpretation_limit": "Endpoint values pass. Coarse straight interpolation is a visual-content issue; the task did not specify a curve error tolerance, so no automatic whole-item fail is assigned."},
                  "page_errors": page_errors, "blocked_external_requests": blocked_requests,
                  "source_sha256": {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in (svg_raw, state_raw, html_path)}}
        (OUT / "artifact_checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        browser.close()
    print(json.dumps({"piston_states_passed": all(x["passed"] for x in state_checks),
                      "rc_protocol_passed": all(x["passed"] for x in protocol), "history_preserved": prefix_ok,
                      "reset_passed": reset_ok, "rc_curve_midpoint_deviation_V": physics_mid_v-rendered_mid_v,
                      "page_errors": page_errors, "blocked_external_requests": blocked_requests}, ensure_ascii=False))


if __name__ == "__main__":
    main()
