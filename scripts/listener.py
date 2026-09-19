#!/usr/bin/env python3
"""
Telegram Nexus Sovereign Autonomous Dispatcher & C2 Sentinel
Provides live terminal monitoring, daemon lifecycle management, and reactive polling orchestration.
"""

import sys
import os
import time
import json
import psutil
import argparse
from pathlib import Path

# Force UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PLUGIN_MCP = Path(__file__).resolve().parent.parent / "mcp"
sys.path.insert(0, str(PLUGIN_MCP))

import server

LOG_DIR = Path(os.path.expanduser("~/.gemini/logs"))
PID_FILE = LOG_DIR / "telegram_nexus_trigger.pid"
STOP_FILE = LOG_DIR / "telegram_nexus_stop.flag"
JOB_REGISTRY_PATH = LOG_DIR / "telegram_jobs.json"

def get_status():
    is_running = False
    pid = None
    if PID_FILE.exists():
        try:
            with open(PID_FILE, "r", encoding="utf-8") as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                if "python" in proc.name().lower():
                    is_running = True
        except Exception:
            pass

    jobs_data = server.load_jobs()
    active = [j for j in jobs_data.values() if j.get("status") == "in_progress"]
    completed = [j for j in jobs_data.values() if j.get("status") == "completed"]

    print("┌─────────────────────────────────────────────────────────────┐")
    print("│ 📡 TELEGRAM NEXUS: C2 GATEWAY & SENTINEL TELEMETRY          │")
    print("├─────────────────────────────────────────────────────────────┤")
    print(f"│ 🤖 Poller State    : {'ACTIVE & LISTENING' if is_running else 'IDLE / STOPPED':<39}│")
    print(f"│ ⚙️  Active PID      : {str(pid) if is_running else 'None':<39}│")
    print(f"│ 👤 Authenticated ID: {str(server.load_config().get('owner_chat_id', 'Unbound')):<39}│")
    print("├─────────────────────────────────────────────────────────────┤")
    print(f"│ 🎟️ Active Jobs In Progress : {len(active):<30}│")
    print(f"│ ✅ Total Completed Jobs    : {len(completed):<30}│")
    print("└─────────────────────────────────────────────────────────────┘")
    return is_running

def stop_listener():
    print("🛑 Stopping Telegram Nexus Listener...", flush=True)
    STOP_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STOP_FILE, "w", encoding="utf-8") as f:
        f.write("stop")

    if PID_FILE.exists():
        try:
            with open(PID_FILE, "r", encoding="utf-8") as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                proc.terminate()
                time.sleep(0.5)
            PID_FILE.unlink(missing_ok=True)
        except Exception:
            pass
    print("✅ Telegram Nexus Listener stopped and PID released.", flush=True)

def test_connection():
    """Verify bot token validity, owner binding, and Telegram API responsiveness."""
    print("🔍 Testing Telegram API connectivity...", flush=True)
    res = server.tool_get_status({})
    status = res.get("status")
    if status == "online":
        print("✅ Telegram API Connection: ONLINE")
        print(f"🤖 Bot Username          : @{res.get('bot_username')}")
        print(f"👤 Authenticated Owner   : {res.get('owner_chat_id')}")
        print(f"👑 Owner Bound           : {res.get('owner_bound')}")
    else:
        print(f"❌ Status: {status}")
        print(f"⚠️ Message: {res.get('message')}")

def run_dashboard():
    print("┌─────────────────────────────────────────────────────────────┐")
    print("│ 📡 TELEGRAM NEXUS: IN-SESSION REACTIVE GATEWAY              │")
    print("├─────────────────────────────────────────────────────────────┤")
    print("│ 💡 The reactive event loop is designed to run directly      │")
    print("│    inside your active Antigravity session (agy terminal).   │")
    print("│                                                             │")
    print("│ 🚀 Usage in agy:                                            │")
    print("│    /telegram-nexus start  -> Start live in-session listener │")
    print("│    /telegram-nexus stop   -> Stop in-session listener       │")
    print("│    /telegram-nexus status -> View live gateway telemetry    │")
    print("│                                                             │")
    print("│ ⚙️ CLI Flags:                                               │")
    print("│    --status               -> Check running state & jobs     │")
    print("│    --stop                 -> Halt background trigger cleanly│")
    print("│    --test                 -> Test bot token & API link      │")
    print("│    --trigger              -> Run single trigger cycle       │")
    print("└─────────────────────────────────────────────────────────────┘")
    get_status()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram Nexus Sovereign Controller & Sentinel")
    parser.add_argument("--status", action="store_true", help="Check listener status & job telemetry")
    parser.add_argument("--stop", action="store_true", help="Stop running listener cleanly")
    parser.add_argument("--test", action="store_true", help="Test bot token and Telegram API connectivity")
    parser.add_argument("--trigger", action="store_true", help="Run single reactive trigger cycle")
    args = parser.parse_args()

    if args.status:
        get_status()
    elif args.stop:
        stop_listener()
    elif args.test:
        test_connection()
    elif args.trigger:
        from poll_wait import run_trigger
        run_trigger()
    else:
        run_dashboard()
