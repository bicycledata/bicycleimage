#!/usr/bin/env python3
"""First-run bootstrap for bicycleinit service.

This script is intended to run once from systemd, clone the real application
repository, install its dependencies into the current venv, then replace
itself with the repository's own entrypoint.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_URL = "https://github.com/bicycledata/bicycleinit.git"


def run(cmd: list[str], cwd: Path | None = None) -> None:
	subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def copy_tree(src: Path, dst: Path) -> None:
	for item in src.iterdir():
		target = dst / item.name
		if item.is_dir():
			if target.exists():
				shutil.rmtree(target)
			shutil.copytree(item, target)
		else:
			target.parent.mkdir(parents=True, exist_ok=True)
			shutil.copy2(item, target)


def main() -> int:
	app_dir = Path(__file__).resolve().parent
	this_script = Path(__file__).resolve()

	with tempfile.TemporaryDirectory(prefix="bicycleinit-bootstrap-") as tmp:
		clone_dir = Path(tmp) / "repo"
		run(["git", "clone", "--depth", "1", REPO_URL, str(clone_dir)])

		req = clone_dir / "requirements.txt"
		if req.exists():
			run([sys.executable, "-m", "pip", "install", "--no-cache-dir", "-r", str(req)])

		repo_entry = clone_dir / "bicycleinit.py"
		if not repo_entry.exists():
			raise RuntimeError("Repository does not contain bicycleinit.py")

		copy_tree(clone_dir, app_dir)

	os.chmod(app_dir / "bicycleinit.py", 0o755)

	if this_script.exists() and this_script.samefile(app_dir / "bicycleinit.py"):
		# Replaced in-place by repository entrypoint; nothing left to do.
		pass

	# Exit cleanly; systemd Restart=always will start the real script next.
	return 0


if __name__ == "__main__":
	try:
		raise SystemExit(main())
	except Exception as exc:  # pragma: no cover
		print(f"bootstrap failed: {exc}", file=sys.stderr)
		raise
