#!/usr/bin/env python3
"""
Telegram Nexus MCP Server
Sovereign Telegram Automation Nexus, Mobile C2 Gateway & Dispatch Firewall for Google Antigravity.
Zero-daemon, pure Python standard library stdio JSON-RPC implementation.
"""

import sys
import json
import os
import urllib.request
import urllib.parse
import urllib.error
import datetime
import time
import traceback
from pathlib import Path

# Quarantined configuration file outside git-tracked repositories
CONFIG_PATH = Path(os.path.expanduser("~/.gemini/config/telegram_config.json"))
SPARK_PATH = Path(os.path.expanduser("~/.gemini/Spark.md"))
MEDIA_DIR = Path(os.path.expanduser("~/.gemini/media"))
LOG_DIR = Path(os.path.expanduser("~/.gemini/logs"))
AUDIT_LOG_PATH = LOG_DIR / "telegram_nexus.log"
AUDIT_JSONL_PATH = LOG_DIR / "telegram_nexus.jsonl"

def record_audit_event(event_type: str, actor: str, chat_id: str, action: str, details: dict = None):
    """
    Append an immutable audit event to both human-readable log and machine-readable JSONL.
    """
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        now_dt = datetime.datetime.now()
        ts_iso = now_dt.isoformat()
        ts_human = now_dt.strftime("%Y-%m-%d %H:%M:%S IST")
        
        event_record = {
            "timestamp": ts_iso,
            "human_time": ts_human,
            "event_type": event_type,
            "actor": actor,
            "chat_id": chat_id,
            "action": action,
            "details": details or {}
        }
        
        # 1. Machine-readable JSON Lines log
        with open(AUDIT_JSONL_PATH, "a", encoding="utf-8") as f_json:
            f_json.write(json.dumps(event_record, ensure_ascii=False) + "\n")
            
        # 2. High-contrast Human-readable audit log
        log_line = f"[{ts_human}] [{event_type:<18}] [Actor: {actor} | ID: {chat_id}] Action: {action}"
        if details:
            details_str = json.dumps(details, ensure_ascii=False)
            if len(details_str) > 120:
                details_str = details_str[:117] + "..."
            log_line += f" | {details_str}"
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f_log:
            f_log.write(log_line + "\n")
    except Exception:
        pass

def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "bot_token": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        "owner_chat_id": os.environ.get("TELEGRAM_OWNER_CHAT_ID", ""),
        "last_update_id": 0
    }

def save_config(cfg: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def telegram_api_call(method: str, params: dict = None) -> dict:
    cfg = load_config()
    token = cfg.get("bot_token")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured in ~/.gemini/config/telegram_config.json")
    
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = None
    headers = {"User-Agent": "Antigravity-Telegram-Nexus/1.0"}
    
    if params:
        data = json.dumps(params).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body)
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        try:
            err_json = json.loads(err_msg)
            return err_json
        except Exception:
            return {"ok": False, "description": f"HTTP {e.code}: {e.reason} - {err_msg}"}
    except Exception as e:
        return {"ok": False, "description": str(e)}

def ensure_bot_commands():
    """Register official slash commands in Telegram bot UI."""
    commands = [
        {"command": "start", "description": "Authenticate / view connection status"},
        {"command": "spark", "description": "Log thought directly to Spark.md"},
        {"command": "status", "description": "Check Motobook & Blaze telemetry"},
        {"command": "strike", "description": "Check active tactical strikes"},
        {"command": "help", "description": "View command guide & help"}
    ]
    try:
        telegram_api_call("setMyCommands", {"commands": commands})
    except Exception:
        pass

def download_telegram_file(file_id: str, dest_path: Path) -> bool:
    """Download a file from Telegram Cloud API by file_id."""
    cfg = load_config()
    token = cfg.get("bot_token")
    if not token or not file_id:
        return False
    res = telegram_api_call("getFile", {"file_id": file_id})
    if not res.get("ok"):
        return False
    file_path = res.get("result", {}).get("file_path")
    if not file_path:
        return False
    file_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(file_url, headers={"User-Agent": "Antigravity-Telegram-Nexus/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response, open(dest_path, "wb") as f:
            f.write(response.read())
        record_audit_event("MEDIA_DOWNLOAD", "system", "local", f"Saved {dest_path.name}", {"file_id": file_id, "size_bytes": dest_path.stat().st_size})
        return True
    except Exception as e:
        record_audit_event("MEDIA_ERROR", "system", "local", f"Download failed for {file_id}", {"error": str(e)})
        return False

# -----------------------------------------------------------------------------
# Tool Implementations
# -----------------------------------------------------------------------------

def tool_get_status(args: dict) -> dict:
    """Check bot health, token validity, and owner binding."""
    cfg = load_config()
    token = cfg.get("bot_token")
    owner_id = cfg.get("owner_chat_id")
    
    if not token:
        return {
            "status": "unconfigured",
            "message": "Bot token not set. Configure bot_token in ~/.gemini/config/telegram_config.json",
            "owner_bound": bool(owner_id)
        }
    
    res = telegram_api_call("getMe")
    if not res.get("ok"):
        record_audit_event("STATUS_ERROR", "system", "telegram", f"getMe failed: {res.get('description')}")
        return {
            "status": "error",
            "message": f"Telegram API error: {res.get('description')}",
            "owner_bound": bool(owner_id)
        }
    
    ensure_bot_commands()
    bot_info = res.get("result", {})
    return {
        "status": "online",
        "bot_username": bot_info.get("username"),
        "bot_name": bot_info.get("first_name"),
        "owner_chat_id": owner_id or "Not yet bound (Send /start to the bot to bind)",
        "owner_bound": bool(owner_id)
    }

def tool_configure(args: dict) -> dict:
    """Set bot token or owner chat ID."""
    cfg = load_config()
    updated = []
    if "bot_token" in args and args["bot_token"]:
        cfg["bot_token"] = args["bot_token"].strip()
        updated.append("bot_token")
    if "owner_chat_id" in args and args["owner_chat_id"]:
        cfg["owner_chat_id"] = str(args["owner_chat_id"]).strip()
        updated.append("owner_chat_id")
    
    save_config(cfg)
    record_audit_event("CONFIG_UPDATE", "admin", cfg.get("owner_chat_id", "system"), f"Updated config fields: {', '.join(updated)}")
    return {
        "status": "success",
        "updated_fields": updated,
        "owner_chat_id": cfg.get("owner_chat_id")
    }

def tool_send_alert(args: dict) -> dict:
    """Send high-priority alert or notification to Karan's Telegram."""
    cfg = load_config()
    chat_id = args.get("chat_id") or cfg.get("owner_chat_id")
    if not chat_id:
        return {"ok": False, "error": "No owner_chat_id configured. Set it or provide chat_id."}
    
    message = args.get("message", "")
    parse_mode = args.get("parse_mode", "HTML")
    
    params = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": args.get("disable_preview", True)
    }
    res = telegram_api_call("sendMessage", params)
    if res.get("ok"):
        msg_id = res.get("result", {}).get("message_id")
        record_audit_event("OUTBOUND_ALERT", "antigravity", str(chat_id), f"Sent alert #{msg_id}", {"preview": message[:100], "message_id": msg_id})
    else:
        record_audit_event("ALERT_FAILED", "antigravity", str(chat_id), f"Alert failed: {res.get('description')}")
    return res

def tool_poll_updates(args: dict) -> dict:
    """Fetch new messages from Telegram and auto-bind owner if /start detected."""
    cfg = load_config()
    offset = cfg.get("last_update_id", 0) + 1
    limit = args.get("limit", 20)
    
    res = telegram_api_call("getUpdates", {"offset": offset, "limit": limit, "timeout": 0})
    if not res.get("ok"):
        return {"ok": False, "error": res.get("description")}
    
    updates = res.get("result", [])
    processed_messages = []
    new_last_id = cfg.get("last_update_id", 0)
    
    for u in updates:
        up_id = u.get("update_id", 0)
        if up_id > new_last_id:
            new_last_id = up_id
        
        msg = u.get("message") or u.get("channel_post")
        if not msg:
            continue
        
        from_user = msg.get("from", {})
        chat = msg.get("chat", {})
        chat_id = str(chat.get("id"))
        text = msg.get("text", "")
        sender_username = from_user.get("username", "")
        sender_name = f"{from_user.get('first_name', '')} {from_user.get('last_name', '')}".strip()
        
        media_type = "text"
        file_id = ""
        duration = 0
        if "voice" in msg:
            media_type = "voice"
            file_id = msg["voice"].get("file_id", "")
            duration = msg["voice"].get("duration", 0)
            if not text:
                text = f"[🎙️ Voice Note: {duration}s]"
        elif "audio" in msg:
            media_type = "audio"
            file_id = msg["audio"].get("file_id", "")
            duration = msg["audio"].get("duration", 0)
            if not text:
                text = f"[🎵 Audio: {duration}s]"
        elif "photo" in msg:
            media_type = "photo"
            file_id = msg["photo"][-1].get("file_id", "")
            caption = msg.get("caption", "")
            text = f"[📷 Photo: {caption}]" if caption else "[📷 Photo]"
        elif "document" in msg:
            media_type = "document"
            file_id = msg["document"].get("file_id", "")
            file_name = msg["document"].get("file_name", "file")
            caption = msg.get("caption", "")
            text = f"[📎 File: {file_name}] {caption}".strip()
        elif "location" in msg:
            media_type = "location"
            lat = msg["location"].get("latitude")
            lon = msg["location"].get("longitude")
            text = f"[📍 Location: {lat}, {lon}] https://maps.google.com/?q={lat},{lon}"
        elif "contact" in msg:
            media_type = "contact"
            c_name = f"{msg['contact'].get('first_name', '')} {msg['contact'].get('last_name', '')}".strip()
            c_phone = msg['contact'].get('phone_number', '')
            text = f"[👤 Contact: {c_name} - {c_phone}]"

        # Auto-bind owner if empty and command is /start or /auth
        if not cfg.get("owner_chat_id") and text.startswith(("/start", "/auth")):
            cfg["owner_chat_id"] = chat_id
            save_config(cfg)
            telegram_api_call("sendMessage", {
                "chat_id": chat_id,
                "text": f"👑 <b>Sovereign Owner Bound</b>\nChat ID <code>{chat_id}</code> is now authenticated as the primary controller for Antigravity.",
                "parse_mode": "HTML"
            })
        
        is_owner = (chat_id == str(cfg.get("owner_chat_id", "")))
        event_tag = "OWNER_INBOUND" if is_owner else "VISITOR_INBOUND"
        record_audit_event(
            event_tag,
            sender_username or sender_name or ("owner" if is_owner else "visitor"),
            chat_id,
            f"Received {media_type}",
            {"text": text[:150], "media_type": media_type, "update_id": up_id, "file_id": file_id}
        )
        processed_messages.append({
            "update_id": up_id,
            "chat_id": chat_id,
            "sender_name": sender_name,
            "sender_username": sender_username,
            "text": text,
            "media_type": media_type,
            "file_id": file_id,
            "duration": duration,
            "date": msg.get("date"),
            "is_owner": is_owner
        })
    
    if new_last_id > cfg.get("last_update_id", 0):
        cfg["last_update_id"] = new_last_id
        save_config(cfg)
    
    return {
        "ok": True,
        "count": len(processed_messages),
        "messages": processed_messages,
        "owner_chat_id": cfg.get("owner_chat_id")
    }

def tool_ingest_spark(args: dict) -> dict:
    """Pull unhandled thoughts sent by Karan on Telegram and append directly to Spark.md."""
    poll_res = tool_poll_updates({"limit": 50})
    if not poll_res.get("ok"):
        return poll_res
    
    messages = poll_res.get("messages", [])
    owner_notes = [m for m in messages if m.get("is_owner") and m.get("text") and not m.get("text").startswith("/")]
    
    if not owner_notes:
        return {"status": "noop", "message": "No new personal notes found from Telegram owner.", "count": 0}
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    new_spark_lines = [f"\n---", f"### {now_str} (via Telegram Nexus)"]
    for note in owner_notes:
        mtype = note.get("media_type", "text")
        fid = note.get("file_id", "")
        if fid and mtype in ("voice", "photo", "document", "audio"):
            ext = "oga" if mtype == "voice" else ("mp3" if mtype == "audio" else ("jpg" if mtype == "photo" else "bin"))
            fname = f"{mtype}_{note.get('date', int(time.time()))}_{note.get('update_id')}.{ext}"
            fdest = MEDIA_DIR / fname
            downloaded = download_telegram_file(fid, fdest)
            if downloaded:
                new_spark_lines.append(f"* {note['text']} (saved: `~/.gemini/media/{fname}`)")
            else:
                new_spark_lines.append(f"* {note['text']}")
        else:
            new_spark_lines.append(f"* {note['text']}")
    new_spark_lines.append("")
    
    SPARK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SPARK_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(new_spark_lines))
    
    record_audit_event(
        "SPARK_INGEST",
        "owner",
        str(cfg.get("owner_chat_id", "")),
        f"Ingested {len(owner_notes)} notes into Spark.md",
        {"count": len(owner_notes), "notes": [n['text'][:100] for n in owner_notes]}
    )
    
    return {
        "status": "success",
        "ingested_count": len(owner_notes),
        "spark_file": str(SPARK_PATH),
        "notes": [n["text"] for n in owner_notes]
    }

def tool_reply_visitor(args: dict) -> dict:
    """Reply back to an outside visitor / collaborator via the bot."""
    visitor_chat_id = args.get("visitor_chat_id")
    message = args.get("message")
    if not visitor_chat_id or not message:
        return {"ok": False, "error": "visitor_chat_id and message are required."}
    
    params = {
        "chat_id": visitor_chat_id,
        "text": message,
        "parse_mode": args.get("parse_mode", "HTML")
    }
    res = telegram_api_call("sendMessage", params)
    if res.get("ok"):
        record_audit_event("VISITOR_REPLY", "antigravity", str(visitor_chat_id), "Reply dispatched to visitor", {"preview": message[:100]})
    else:
        record_audit_event("REPLY_FAILED", "antigravity", str(visitor_chat_id), f"Failed to reply to visitor: {res.get('description')}")
    return res

def tool_get_audit_log(args: dict) -> dict:
    """Inspect the immutable audit log of all events, messages, and actions that passed through the bot."""
    limit = args.get("limit", 50)
    event_filter = args.get("event_type")
    
    if not AUDIT_JSONL_PATH.exists():
        return {
            "status": "empty",
            "total_events": 0,
            "events": [],
            "log_file": str(AUDIT_LOG_PATH)
        }
    
    records = []
    try:
        with open(AUDIT_JSONL_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    if event_filter and r.get("event_type") != event_filter:
                        continue
                    records.append(r)
                except Exception:
                    continue
    except Exception as e:
        return {"status": "error", "error": str(e)}
        
    recent = records[-limit:]
    return {
        "status": "success",
        "total_logged": len(records),
        "returned_count": len(recent),
        "log_file": str(AUDIT_LOG_PATH),
        "jsonl_file": str(AUDIT_JSONL_PATH),
        "events": recent
    }

# -----------------------------------------------------------------------------
# MCP Server Tool Definitions & JSON-RPC Loop
# -----------------------------------------------------------------------------

TOOLS = [
    {
        "name": "nexus_get_status",
        "description": "Check Telegram Nexus bot status, connectivity health, and owner binding.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "nexus_configure",
        "description": "Configure bot token and/or owner chat ID in ~/.gemini/config/telegram_config.json.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bot_token": {"type": "string", "description": "Bot token obtained from @BotFather"},
                "owner_chat_id": {"type": "string", "description": "Karan's Telegram chat/user ID"}
            }
        }
    },
    {
        "name": "nexus_send_alert",
        "description": "Send high-priority alert, build report, or telemetry to Karan's Telegram phone.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "HTML or plain text message to send"},
                "parse_mode": {"type": "string", "enum": ["HTML", "MarkdownV2"], "default": "HTML"},
                "chat_id": {"type": "string", "description": "Optional target chat ID (defaults to owner)"}
            },
            "required": ["message"]
        }
    },
    {
        "name": "nexus_poll_updates",
        "description": "Fetch and triage incoming messages/updates sent to the bot.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 20, "description": "Number of updates to fetch"}
            }
        }
    },
    {
        "name": "nexus_ingest_spark",
        "description": "Polls owner notes from Telegram and auto-appends them into ~/.gemini/Spark.md.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "nexus_reply_visitor",
        "description": "Send a reply to a visitor or collaborator who reached out through the bot.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "visitor_chat_id": {"type": "string", "description": "Visitor's Telegram chat ID"},
                "message": {"type": "string", "description": "Reply text to deliver"}
            },
            "required": ["visitor_chat_id", "message"]
        }
    },
    {
        "name": "nexus_get_audit_log",
        "description": "Inspect the persistent audit log of all events, messages, alerts, and actions passing through the bot.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50, "description": "Maximum number of audit events to return"},
                "event_type": {"type": "string", "description": "Optional filter by event_type (e.g. OWNER_MESSAGE, VISITOR_MESSAGE, OUTBOUND_ALERT, SPARK_INGEST)"}
            }
        }
    }
]

TOOL_HANDLERS = {
    "nexus_get_status": tool_get_status,
    "nexus_configure": tool_configure,
    "nexus_send_alert": tool_send_alert,
    "nexus_poll_updates": tool_poll_updates,
    "nexus_ingest_spark": tool_ingest_spark,
    "nexus_reply_visitor": tool_reply_visitor,
    "nexus_get_audit_log": tool_get_audit_log
}

def send_json(data):
    body = json.dumps(data)
    sys.stdout.write(body + "\n")
    sys.stdout.flush()

def handle_jsonrpc(line: str):
    if not line.strip():
        return
    try:
        req = json.loads(line)
    except Exception:
        return
    
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})
    
    if method == "initialize":
        send_json({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "telegram-nexus-mcp",
                    "version": "1.0.0"
                }
            }
        })
    elif method == "notifications/initialized":
        pass
    elif method == "tools/list":
        send_json({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS
            }
        })
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        handler = TOOL_HANDLERS.get(tool_name)
        
        if not handler:
            send_json({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found."}
            })
            return
        
        try:
            res_data = handler(args)
            send_json({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(res_data, indent=2)
                        }
                    ],
                    "isError": False
                }
            })
        except Exception as err:
            send_json({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error in '{tool_name}': {str(err)}\n{traceback.format_exc()}"
                        }
                    ],
                    "isError": True
                }
            })
    elif method == "ping":
        send_json({"jsonrpc": "2.0", "id": req_id, "result": {}})
    else:
        if req_id is not None:
            send_json({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method '{method}' not implemented."}
            })

def main():
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    
    for line in sys.stdin:
        handle_jsonrpc(line)

if __name__ == "__main__":
    main()
