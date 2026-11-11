"""Run generated artifacts without network, credentials, or personal files."""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import time


def command_for(command, workspace, readonly_paths=(), env=None):
    workspace = Path(workspace).resolve(strict=True)
    if not workspace.is_dir():
        raise ValueError("Isolation workspace must be an existing dedicated directory")
    args = ["bwrap", "--unshare-all", "--die-with-parent", "--new-session", "--clearenv"]
    for path in ("/usr", "/bin", "/lib", "/lib64", "/etc/fonts", "/etc/alternatives", "/etc/ld.so.cache"):
        if Path(path).exists():
            args += ["--ro-bind", path, path]
    args += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--tmpfs", "/home", "--tmpfs", "/run"]
    for source in readonly_paths:
        source = Path(source).absolute()
        if not source.exists() or source.name.startswith(".env") or str(source) in {"/", "/home", "/home/likefallwind", "/etc", "/proc"}:
            raise ValueError(f"Refusing unsafe read-only mount: {source}")
        args += ["--ro-bind", str(source), str(source)]
    args += ["--bind", str(workspace), "/work", "--chdir", "/work"]
    safe_env = {"PATH": "/usr/bin:/bin", "HOME": "/tmp", "TMPDIR": "/tmp", "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"}
    for name, value in (env or {}).items():
        if any(word in name.upper() for word in ("API", "KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "AUTH")):
            raise ValueError("Credentials must not enter artifact execution")
        safe_env[name] = str(value)
    for name, value in safe_env.items():
        args += ["--setenv", name, value]
    if not command or not all(isinstance(part, str) for part in command):
        raise ValueError("Use an explicit command argument list")
    # Resource limits apply to the whole nested process tree; timeout is enforced below.
    # Linux RLIMIT_NPROC counts the host uid's threads too, even across namespaces.
    # 512 can reject an otherwise healthy Chromium on a busy development host.
    return ["prlimit", "--nproc=4096", "--nofile=4096", "--fsize=1073741824", "--", *args, "--", *command]


def isolated_run(command, workspace, readonly_paths=(), timeout=180, env=None, report_path=None):
    args = command_for(command, workspace, readonly_paths, env)
    started = time.monotonic()
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                               start_new_session=True, env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
    expired = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        expired = True
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
    result = {"command": command, "returncode": process.returncode, "stdout": stdout, "stderr": stderr,
              "timed_out": expired, "elapsed_seconds": round(time.monotonic() - started, 3),
              "isolation": {"engine": "bubblewrap", "network": False, "credentials": False,
                            "workspace": str(Path(workspace).resolve()), "readonly_paths": [str(p) for p in readonly_paths]}}
    if report_path:
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        Path(report_path).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result
