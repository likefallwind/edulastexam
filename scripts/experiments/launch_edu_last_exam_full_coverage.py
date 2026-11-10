#!/usr/bin/env python3
"""Snapshot the full-coverage pilot and start it in durable detached tmux."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

SUPERVISOR = '''#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import json, os, subprocess, sys
control=Path(__file__).resolve().parent
config=json.loads((control/'config.json').read_text())
def now(): return datetime.now(timezone.utc).isoformat()
def write(name,data):
    target=control/name
    temporary=target.with_name(target.name+'.tmp')
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\\n')
    temporary.replace(target)
code=1
write('started.json',{'at':now(),'pid':os.getpid(),'state':'running'})
try:
    with (Path(config['output'])/'run.log').open('a') as log:
        child=subprocess.Popen(config['command'],cwd=config['source_snapshot'],stdout=log,stderr=subprocess.STDOUT)
        write('child.json',{'pid':child.pid,'at':now()})
        code=child.wait()
except Exception as exc:
    key=os.environ.get(config['api_key_env'],'')
    message=str(exc)
    if key: message=message.replace(key,'[REDACTED]')
    write('supervisor_error.json',{'error':message,'at':now()})
finally:
    write('finished.json',{'at':now(),'exit_code':code})
    (control/'exit_code.txt').write_text(str(code)+'\\n')
    (Path(config['output'])/'process_exit_code.txt').write_text(str(code)+'\\n')
sys.exit(code)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true", help="Write snapshots/config without starting any API request")
    parser.add_argument("--with-judge", action="store_true")
    parser.add_argument("--name", help="Unique lowercase/digit/underscore run label")
    args = parser.parse_args()
    import re
    name = args.name or datetime.now().strftime("%Y%m%d_%H%M%S") + "_glm53flash"
    if not re.fullmatch(r"[a-z0-9_]+", name):
        parser.error("Invalid run label")
    output = ROOT / "reports/eval/edu_last_exam_full_coverage_v1/_exploratory" / name / "GLM-5.3-Flash"
    control = ROOT / "eval" / ("full_coverage_" + name)
    source = output.parent / "source_snapshot"
    if output.exists() or control.exists():
        raise SystemExit("Run label already exists; use its preserved command to resume or choose a new label")
    # Validate authoring and deterministic environments before preparing a paid run.
    subprocess.run([sys.executable, str(ROOT / "scripts/build/build_edu_last_exam_full_coverage.py"), "--check"], cwd=ROOT, check=True)
    output.mkdir(parents=True)
    control.mkdir(parents=True)
    for relative in ("private/edu_last_exam_full_coverage_v1", "scripts/full_coverage"):
        shutil.copytree(ROOT / relative, source / relative, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for relative in ("scripts/experiments/run_edu_last_exam_full_coverage.py", "scripts/experiments/run_edu_last_exam_challenge_v2.py", "scripts/eval/minimax_client.py"):
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    command = [sys.executable, str(source / "scripts/experiments/run_edu_last_exam_full_coverage.py"), "--batch", str(source / "private/edu_last_exam_full_coverage_v1"), "--output", str(output), "--model", "GLM-5.3-Flash", "--concurrency", "4", "--timeout", "600", "--retries", "2"]
    if args.with_judge:
        command.append("--with-judge")
    subprocess.run([*command, "--dry-run"], cwd=source, check=True, stdout=(control / "dry_run.json").open("w"))
    hashes = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    (output.parent / "source_snapshot_manifest.json").write_text(json.dumps(hashes, indent=2) + "\n")
    config = {"root": str(ROOT), "source_snapshot": str(source), "output": str(output), "command": command,
              "api_key_env": "GLM_API", "concurrency": 4, "tmux_socket": "edu_full_" + name, "tmux_session": "edu_full_" + name,
              "judging": "same_model_exploratory" if args.with_judge else "not_run"}
    (control / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    (control / "supervisor.py").write_text(SUPERVISOR)
    if not args.prepare_only:
        if not os.environ.get("GLM_API"):
            raise SystemExit("GLM_API is not set; snapshots prepared but job not started")
        shell_command = "exec " + shlex.quote(sys.executable) + " " + shlex.quote(str(control / "supervisor.py")) + " >> " + shlex.quote(str(control / "supervisor.log")) + " 2>&1"
        environment = {k: v for k, v in os.environ.items() if k in {"PATH", "HOME", "LANG", "LC_ALL", "TERM", "GLM_API", "TMPDIR"}}
        subprocess.run(["tmux", "-L", config["tmux_socket"], "new-session", "-d", "-s", config["tmux_session"], "-c", str(source), shell_command], env=environment, check=True)
    print(json.dumps({"state": "prepared" if args.prepare_only else "launched", "control": str(control), "output": str(output), "tmux_socket": config["tmux_socket"], "tmux_session": config["tmux_session"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
