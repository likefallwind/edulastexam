#!/usr/bin/env python3
"""Freeze verified sources and start a durable GLM-5.3-Flash background run."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.source_fidelity.core import AUDIT_REL, BATCH_REL, digest, write_json
from scripts.experiments.launch_edu_last_exam_full_coverage import SUPERVISOR


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    label = args.name or datetime.now().strftime("%Y%m%d_%H%M%S") + "_glm53flash"
    if not re.fullmatch(r"[a-z0-9_]+", label):
        parser.error("Invalid run name")
    output = ROOT / "reports/eval/edu_last_exam_source_fidelity_v1/_exploratory" / label / "GLM-5.3-Flash"
    source = output.parent / "source_snapshot"
    control = ROOT / "eval" / ("source_fidelity_" + label)
    if output.exists() or control.exists():
        raise ValueError("Run already exists; preserve it and use a new name or its recorded resume command")
    if not args.prepare_only and not os.environ.get("GLM_API"):
        raise ValueError("GLM_API must be inherited from the user's configured environment")
    subprocess.run([sys.executable, str(ROOT / "scripts/build/build_edu_last_exam_source_fidelity.py"), "--check"], cwd=ROOT, check=True)
    output.mkdir(parents=True)
    control.mkdir(parents=True)
    ignored = shutil.ignore_patterns(".git", ".env", ".env.*", "__pycache__", "*.pyc", "node_modules", ".venv", ".pytest_cache", "download_chunks", "*.part", "download.pid", "download.log")
    directories = [AUDIT_REL, BATCH_REL, Path("scripts/source_fidelity"), Path("sources/datasets/edu_last_exam_source_fidelity_v1")]
    for relative in directories:
        if (ROOT / relative).exists():
            shutil.copytree(ROOT / relative, source / relative, ignore=ignored)
    for relative in ["scripts/experiments/run_edu_last_exam_source_fidelity.py", "scripts/experiments/run_edu_last_exam_challenge_v2.py", "scripts/eval/minimax_client.py"]:
        destination = source / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    hashes = {str(p.relative_to(source)): digest(p.read_bytes()) for p in sorted(source.rglob("*")) if p.is_file()}
    write_json(output.parent / "source_snapshot_manifest.json", hashes)
    command = [sys.executable, str(source / "scripts/experiments/run_edu_last_exam_source_fidelity.py"), "--output", str(output),
               "--model", "GLM-5.3-Flash", "--concurrency", "4", "--timeout", "600", "--retries", "2"]
    with (control / "dry_run.json").open("w") as file:
        subprocess.run([*command, "--dry-run"], cwd=source, check=True, stdout=file)
    config = {"root": str(ROOT), "source_snapshot": str(source), "output": str(output), "command": command,
              "api_key_env": "GLM_API", "concurrency": 4, "tmux_socket": "edu_source_" + label, "tmux_session": "edu_source_" + label,
              "scoring": "original_metrics_and_explicit_pending_original_judges"}
    write_json(control / "config.json", config)
    (control / "supervisor.py").write_text(SUPERVISOR)
    if not args.prepare_only:
        command_text = "exec " + shlex.quote(sys.executable) + " " + shlex.quote(str(control / "supervisor.py")) + " >> " + shlex.quote(str(control / "supervisor.log")) + " 2>&1"
        environment = {k:v for k,v in os.environ.items() if k in {"PATH", "HOME", "LANG", "LC_ALL", "TERM", "GLM_API", "MINIMAX_API_KEY", "TMPDIR"}}
        subprocess.run(["tmux", "-L", config["tmux_socket"], "new-session", "-d", "-s", config["tmux_session"], "-c", str(source), command_text], env=environment, check=True)
    print(json.dumps({"status": "prepared" if args.prepare_only else "launched", "output": str(output), "control": str(control), "source_snapshot_files": len(hashes)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
