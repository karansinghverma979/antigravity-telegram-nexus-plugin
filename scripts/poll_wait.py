#!/usr/bin/env python3
"""
Telegram Nexus Reactive Event Trigger for Google Antigravity.

Holds the Telegram long-polling socket silently in the background.
Exits IMMEDIATELY with code 0 when:
1. One or more incoming messages arrive from the authenticated owner (Karan).
2. An active job reaches the 4-minute threshold without an interim heartbeat.
3. An explicit stop signal is detected.

When this script exits with code 0, Antigravity CLI's reactive engine automatically
wakes up the live agent in the terminal window with full context intact!
"""

import sys
import os
import time
import json
import datetime
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

def run_trigger():
    # Clear any stale stop flag
    if STOP_FILE.exists():
        STOP_FILE.unlink(missing_ok=True)

    # Acquire PID lock to avoid duplicate poll sockets
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if PID_FILE.exists():
        try:
            with open(PID_FILE, "r", encoding="utf-8") as f:
                existing_pid = int(f.read().strip())
            import psutil
            if existing_pid != os.getpid() and psutil.pid_exists(existing_pid):
                proc = psutil.Process(existing_pid)
                if "python" in proc.name().lower():
                    # Another instance is already actively holding the polling socket
                    print(json.dumps({"event": "ALREADY_LISTENING", "pid": existing_pid}, ensure_ascii=False), flush=True)
                    sys.exit(0)
        except Exception:
            pass

    with open(PID_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))

    try:
        while True:
            try:
                # 1. Check for explicit stop request
                if STOP_FILE.exists():
                    STOP_FILE.unlink(missing_ok=True)
                    print(json.dumps({"event": "STOP_REQUESTED"}, ensure_ascii=False), flush=True)
                    sys.exit(0)

                # 2. Check for active background jobs reaching the 4-minute threshold
                if JOB_REGISTRY_PATH.exists():
                    try:
                        with open(JOB_REGISTRY_PATH, "r", encoding="utf-8") as f:
                            jobs = json.load(f)
                        now_epoch = time.time()
                        for j_id, j_data in jobs.items():
                            if j_data.get("status") == "in_progress" and not j_data.get("heartbeat_4m_sent"):
                                created_epoch = j_data.get("created_at_epoch")
                                if created_epoch and (now_epoch - created_epoch) >= 240: # 4 minutes
                                    j_data["heartbeat_4m_sent"] = True
                                    with open(JOB_REGISTRY_PATH, "w", encoding="utf-8") as f_out:
                                        json.dump(jobs, f_out, indent=2, ensure_ascii=False)
                                    
                                    payload = {
                                        "event": "JOB_HEARTBEAT_4M",
                                        "job_id": j_id,
                                        "task": j_data.get("task", ""),
                                        "elapsed_seconds": int(now_epoch - created_epoch),
                                        "original_message_id": j_data.get("original_message_id")
                                    }
                                    print(json.dumps(payload, ensure_ascii=False), flush=True)
                                    sys.exit(0)
                    except Exception:
                        pass

                # 3. Long-poll Telegram (20-second hold at Telegram edge)
                # IMPORTANT: dry_run=True means we detect messages WITHOUT consuming
                # the offset. The agent will see the same messages on its real poll call.
                try:
                    res = server.tool_poll_updates({"timeout": 20, "dry_run": True})
                    if res.get("ok"):
                        messages = res.get("messages", [])
                        # All returned messages are from owner (non-owner blocked at gate)
                        # is_owner field removed from slim payload — presence = owner
                        owner_msgs = messages  # All passed gating = owner messages
                        if owner_msgs:
                            # Fire typing indicator + ⚡ reaction BEFORE waking agent
                            # This gives instant visual feedback while agent boots (~3-5s)
                            try:
                                cfg = server.load_config()
                                chat_id = cfg.get("owner_chat_id", "")
                                if chat_id:
                                    server.telegram_api_call("sendChatAction", {
                                        "chat_id": chat_id, "action": "typing"
                                    })
                                    # React to first message with ⚡
                                    first_msg_id = owner_msgs[0].get("message_id")
                                    if first_msg_id:
                                        server.telegram_api_call("setMessageReaction", {
                                            "chat_id": chat_id,
                                            "message_id": first_msg_id,
                                            "reaction": [{"type": "emoji", "emoji": "⚡"}]
                                        })
                            except Exception:
                                pass
                            # Exit to wake agent
                            payload = {
                                "event": "OWNER_MESSAGES",
                                "count": len(owner_msgs),
                                "messages": owner_msgs
                            }
                            print(json.dumps(payload, ensure_ascii=False), flush=True)
                            sys.exit(0)
                    else:
                        err = res.get("error", "")
                        if "409" in str(err):
                            time.sleep(2)
                except Exception as e:
                    time.sleep(2)

                # Brief socket rest between empty cycles
                time.sleep(0.3)

            except SystemExit:
                raise
            except Exception as loop_err:
                time.sleep(1)

    finally:
        if PID_FILE.exists():
            try:
                with open(PID_FILE, "r", encoding="utf-8") as f:
                    if f.read().strip() == str(os.getpid()):
                        PID_FILE.unlink(missing_ok=True)
            except Exception:
                pass

if __name__ == "__main__":
    try:
        run_trigger()
    except SystemExit as se:
        code = se.code if se.code is not None else 0
        sys.exit(code)
    except Exception as e:
        import traceback
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / "poll_wait_crash.log", "a", encoding="utf-8") as f:
            f.write(f"\n--- CRASH AT {datetime.datetime.now()} ---\n{traceback.format_exc()}\n")
        sys.exit(0)
