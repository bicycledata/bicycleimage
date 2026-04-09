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
import time
from pathlib import Path


REPO_URL = "https://github.com/bicycledata/bicycleinit.git"
WIFI_BOOTSTRAP_MARKER = Path("/var/lib/bicycledata/wifi-bootstrap.done")


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


def bootstrap_wifi_from_env() -> None:
	ssid = os.environ.get("BICYCLEDATA_WIFI_SSID", "").strip()
	psk = os.environ.get("BICYCLEDATA_WIFI_PSK", "").strip()
	if not ssid or not psk:
		return
	if WIFI_BOOTSTRAP_MARKER.exists():
		return

	for _ in range(30):
		status = subprocess.run(
			["sudo", "nmcli", "-t", "-f", "RUNNING", "general", "status"],
			check=False,
			capture_output=True,
			text=True,
		)
		if status.returncode == 0 and status.stdout.strip() == "running":
			break
		time.sleep(2)
	else:
		# NetworkManager not ready yet; service restart will retry.
		return

	con_name = ssid
	connections = subprocess.run(
		["sudo", "nmcli", "-t", "-f", "NAME", "connection", "show"],
		check=False,
		capture_output=True,
		text=True,
	)
	existing = set(line.strip() for line in connections.stdout.splitlines() if line.strip())

	if con_name in existing:
		run(["sudo", "nmcli", "connection", "modify", con_name, "connection.autoconnect", "yes"])
		run(["sudo", "nmcli", "connection", "modify", con_name, "wifi-sec.key-mgmt", "wpa-psk"])
		run(["sudo", "nmcli", "connection", "modify", con_name, "wifi-sec.psk", psk])
	else:
		# Do not bind to wlan0 here; interface may not exist yet on early boot.
		run(["sudo", "nmcli", "connection", "add", "type", "wifi", "con-name", con_name, "ssid", ssid])
		run(["sudo", "nmcli", "connection", "modify", con_name, "connection.autoconnect", "yes"])
		run(["sudo", "nmcli", "connection", "modify", con_name, "wifi-sec.key-mgmt", "wpa-psk"])
		run(["sudo", "nmcli", "connection", "modify", con_name, "wifi-sec.psk", psk])

	subprocess.run(["sudo", "nmcli", "connection", "up", con_name], check=False)
	WIFI_BOOTSTRAP_MARKER.parent.mkdir(parents=True, exist_ok=True)
	WIFI_BOOTSTRAP_MARKER.touch()


def main() -> int:
	app_dir = Path(__file__).resolve().parent
	this_script = Path(__file__).resolve()
	bootstrap_wifi_from_env()

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
