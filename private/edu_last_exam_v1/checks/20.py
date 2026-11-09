"""Check actual reference JavaScript against independent RC equations (Node required)."""
import json
import math
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1]
javascript = re.search(r"<script>(.*?)</script>", (root / "reference/20/corrected.html").read_text(), re.S).group(1)
stub = """
const document={getElementById:()=>({value:'',textContent:'',addEventListener(){},setAttribute(){}})};
const window={};
"""
exercise = """
const output=[];
function save(){output.push(window.sim.snapshot());}
reset();save();advance(.3);save();setMode('discharge');setResistance(1000);save();
advance(.1);save();setResistance(4000);save();advance(.2);save();
setMode('charge');advance(.1);save();reset();save();
console.log(JSON.stringify(output));
"""
result = subprocess.run(["node", "-e", stub + javascript + exercise], text=True, capture_output=True, check=True)
states = json.loads(result.stdout)

midpoint_exercise = """
reset(); advance(2); console.log(JSON.stringify(window.sim.snapshot()));
"""
midpoint_result = subprocess.run(["node", "-e", stub + javascript + midpoint_exercise], text=True, capture_output=True, check=True)
midpoint_state = json.loads(midpoint_result.stdout)
v1 = 10 * (1 - math.exp(-.3 / .2))
v2 = v1 * math.exp(-.1 / .1)
v3 = v2 * math.exp(-.2 / .4)
v4 = 10 + (v3 - 10) * math.exp(-.1 / .4)
expected = [(0, 0, .005), (.3, v1, (10-v1)/2000), (.3, v1, -v1/1000),
            (.4, v2, -v2/1000), (.4, v2, -v2/4000), (.6, v3, -v3/4000),
            (.7, v4, (10-v4)/4000), (0, 0, .005)]
for state, values in zip(states, expected, strict=True):
    for key, value in zip(("time", "voltage", "current"), values):
        assert math.isclose(state[key], value, abs_tol=1e-10), (key, state, value)
    for sample in state["samples"]:
        assert 0 <= sample["voltage"] <= 10
    assert state["samples"][-1]["time"] == state["time"]
    assert state["samples"][-1]["voltage"] == state["voltage"]
for before, after in zip(states[1:6], states[2:7]):
    assert after["samples"][:len(before["samples"])] == before["samples"]
assert states[-1]["samples"] == [{"time": 0, "voltage": 0}]
midpoint = [sample for sample in midpoint_state["samples"] if abs(sample["time"] - 1.0) <= 0.01]
assert midpoint and math.isclose(midpoint[0]["voltage"], 10 * (1 - math.exp(-1 / 0.2)), abs_tol=0.05)
print("20: actual reference JavaScript matches piecewise RC law, signed current, continuity, history and reset")
