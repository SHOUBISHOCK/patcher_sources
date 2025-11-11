# services/firewall.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Callable

# Windows flag to hide PowerShell console window
CREATE_NO_WINDOW = 0x08000000


def _run_powershell(cmd: str) -> subprocess.CompletedProcess:
    """Run a PowerShell command completely silently, without flashing a console window."""
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    return subprocess.run(
        [
            "powershell.exe",
            "-WindowStyle", "Hidden",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            cmd
        ],
        capture_output=True,
        text=True,
        startupinfo=startupinfo,
        creationflags=CREATE_NO_WINDOW
    )



def remove_rules(rule_prefix: str) -> bool:
    """Remove all Windows Firewall rules matching the given prefix."""
    ps = f"""
    $rules = Get-NetFirewallRule | Where-Object {{ $_.DisplayName -like '{rule_prefix}*' }}
    if ($rules) {{
        $rules | Remove-NetFirewallRule
    }}
    """
    _run_powershell(ps)
    return True


def add_block_rules_from_ip_file(
    ip_file: str | Path,
    rule_prefix: str = "GameSpamFilter",
    progress_callback: Callable[[int, str], None] | None = None
) -> bool:
    """
    Creates inbound and outbound firewall rules blocking all IPs in chunks.
    Emits progress via progress_callback(percent, message).
    """
    ip_file = Path(ip_file)
    if not ip_file.exists():
        raise FileNotFoundError(f"IP file not found: {ip_file}")

    with open(ip_file, "r", encoding="utf-8") as f:
        ips = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]

    if not ips:
        raise ValueError("No valid IPs found in file")

    chunk_size = 200  # Safe limit per rule
    total = len(ips)
    chunks = [ips[i:i + chunk_size] for i in range(0, total, chunk_size)]

    for i, chunk in enumerate(chunks, start=1):
        rule_name_out = f"{rule_prefix}_OUT_{i}"
        rule_name_in = f"{rule_prefix}_IN_{i}"
        addresses = ",".join(chunk)

        for direction, rule_name in [("Outbound", rule_name_out), ("Inbound", rule_name_in)]:
            ps = f"""
            New-NetFirewallRule -DisplayName '{rule_name}' -Direction {direction} -Action Block -RemoteAddress {addresses} -Protocol Any -Profile Any
            """
            result = _run_powershell(ps)

            if result.returncode != 0:
                msg = result.stderr.strip() or "Unknown PowerShell error"
                if progress_callback:
                    progress_callback(int(i / len(chunks) * 100), f"⚠️ Error: {msg}")
                raise RuntimeError(msg)

        percent = int(i / len(chunks) * 100)
        if progress_callback:
            progress_callback(percent, f"✅ Added IP chunk {i}/{len(chunks)}")

    if progress_callback:
        progress_callback(100, f"🎉 Added {len(chunks)} inbound/outbound rule pairs successfully.")
    return True


def verify_rules_exist(rule_prefix: str) -> bool:
    """Check whether any rules with the given prefix exist."""
    ps = f"Get-NetFirewallRule | Where-Object {{ $_.DisplayName -like '{rule_prefix}*' }}"
    result = _run_powershell(ps)
    return bool(result.stdout.strip())
