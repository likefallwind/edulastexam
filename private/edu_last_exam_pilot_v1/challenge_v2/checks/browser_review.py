"""Render source SVGs and verify the reference HTML through real controls.

Requires Python Playwright and a locally installed Chromium. Use --browser PATH.
This checks authoring artifacts, not a tested model's answers.
"""
import argparse
import json
import math
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", required=True)
    args = parser.parse_args()
    batch = Path(__file__).resolve().parents[1]
    repo = batch.parents[2]
    output = repo / "reports/challenge_v2/authoring_checks"
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.browser, headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
        rendered = []
        for source in sorted(batch.glob("stimuli/*/*.svg")) + sorted(batch.glob("reference/*/*.svg")):
            page.goto(source.as_uri())
            page.wait_for_load_state("networkidle")
            page.locator("svg").screenshot(path=str(source.with_suffix(".png")))
            rendered.append(str(source.relative_to(batch)))
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto((batch / "reference/20/corrected.html").as_uri())
        page.wait_for_load_state("networkidle")
        snapshots = []

        def save():
            snapshots.append(page.evaluate("window.sim.snapshot()"))
            state = snapshots[-1]
            assert math.isclose(float(page.locator("#voltage").inner_text()), state["voltage"], abs_tol=.000002)
            assert math.isclose(float(page.locator("#current").inner_text()), state["current"] * 1000, abs_tol=.000002)

        def advance(dt):
            page.locator("#dt").fill(str(dt))
            page.locator("#advance").click()
            save()

        def resistance(value):
            page.locator("#resistance").fill(str(value))
            page.locator("#resistance").dispatch_event("change")

        save()
        advance(.3)
        page.locator("#mode").select_option("discharge")
        resistance(1000)
        save()
        advance(.1)
        resistance(4000)
        save()
        advance(.2)
        page.locator("#mode").select_option("charge")
        advance(.1)
        expected = json.loads((batch / "reference/20/protocol.json").read_text())
        for actual, gold in zip(snapshots, expected, strict=True):
            for key in ("time", "voltage", "current"):
                assert math.isclose(actual[key], gold[key], abs_tol=1e-10)
        for before, after in zip(snapshots, snapshots[1:]):
            assert after["samples"][:len(before["samples"])] == before["samples"]
        points = page.locator("#trace").get_attribute("points").split()
        assert len(points) == len(snapshots[-1]["samples"])
        for point, sample in zip(points, snapshots[-1]["samples"]):
            x, y = map(float, point.split(","))
            assert math.isclose(x, 55 + 715 * sample["time"] / .7, abs_tol=.0001)
            assert math.isclose(y, 260 - 23.5 * sample["voltage"], abs_tol=.0001)
        page.screenshot(path=str(output / "rc_reference.png"), full_page=True)
        page.locator("#reset").click()
        reset = page.evaluate("window.sim.snapshot()")
        assert reset["samples"] == [{"time": 0, "voltage": 0}]
        assert reset["mode"] == "charge" and reset["resistance"] == 2000
        assert len(page.locator("#trace").get_attribute("points").split()) == 1
        assert not errors, errors
        # Confirm the intentionally flawed stimulus exhibits the claimed defect.
        page.goto((batch / "stimuli/20/simulator.html").as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("sim.advance(.3)")
        before = page.evaluate("sim.snapshot()")
        page.locator("#mode").select_option("discharge")
        after = page.evaluate("sim.snapshot()")
        assert before["voltage"] > 7 and after["voltage"] == 0
        page.goto((batch / "reference/14/learner_material.html").as_uri())
        page.wait_for_load_state("networkidle")
        for student in ("A", "B"):
            page.locator(f"#learner-{student}").screenshot(path=str(output / f"fraction_reference_{student}.png"))
        review_page = batch / "review.html"
        review_verified = False
        if review_page.exists():
            page.goto(review_page.as_uri())
            page.wait_for_load_state("networkidle")
            assert page.locator("article").count() == 21
            assert page.locator("article details").count() == 21
            assert page.locator("article details[open]").count() == 0
            assert page.evaluate("Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)")
            page.locator("#ELE-C2-15 summary").click()
            assert page.locator("#ELE-C2-15 details[open]").count() == 1
            page.evaluate("window.scrollTo(0,0)")
            page.screenshot(path=str(output / "review_index.png"))
            review_verified = True
        assert not errors, errors
        report = {"status": "passed", "scope": "authored_reference_and_stimulus_only", "model_evaluation": "not_run", "rendered_svg": rendered,
                  "rc_protocol_points": len(expected), "rc_dom_history_and_reset": "passed", "intentional_stimulus_defect_reproduced": True,
                  "review_page_verified": review_verified, "fraction_reference_screenshots": 2,
                  "page_errors": errors, "browser_version": browser.version}
        (output / "browser_review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        browser.close()
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
