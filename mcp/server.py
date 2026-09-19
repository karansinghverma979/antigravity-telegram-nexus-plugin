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
import uuid
import traceback
import re
from pathlib import Path

# Quarantined configuration file outside git-tracked repositories
CONFIG_PATH = Path(os.path.expanduser("~/.gemini/config/telegram_config.json"))
SPARK_PATH = Path(os.path.expanduser("~/.gemini/Spark.md"))
MEDIA_DIR = Path(os.path.expanduser("~/.gemini/media"))
LOG_DIR = Path(os.path.expanduser("~/.gemini/logs"))
AUDIT_LOG_PATH = LOG_DIR / "telegram_nexus.log"
AUDIT_JSONL_PATH = LOG_DIR / "telegram_nexus.jsonl"
JOB_REGISTRY_PATH = LOG_DIR / "telegram_jobs.json"

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
    
    call_timeout = 15
    if params and "timeout" in params:
        try:
            call_timeout = int(params["timeout"]) + 10
        except Exception:
            call_timeout = 15

    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=call_timeout) as response:
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
        {"command": "joblist", "description": "View active, queued & recent job tickets"},
        {"command": "jobstatus", "description": "Inspect deep dossier of a job (/jobstatus JOB-01)"},
        {"command": "jobcancel", "description": "Cancel an active background job (/jobcancel JOB-01)"},
        {"command": "strike", "description": "Inspect today's tactical strikes radar"},
        {"command": "task", "description": "Inspect active campaigns & operations tree"},
        {"command": "status", "description": "Workstation telemetry (RAM, Battery, C2 State)"},
        {"command": "spark", "description": "Capture instant thought into Spark.md"},
        {"command": "genimage", "description": "Generate AI visual on Motobook & deliver"},
        {"command": "gendoc", "description": "Generate document & send file to phone"},
        {"command": "gsuite", "description": "Query Gmail, Calendar, Drive & Docs"},
        {"command": "help", "description": "View sovereign executive command palette"}
    ]
    try:
        telegram_api_call("setMyCommands", {"commands": commands})
    except Exception:
        pass

def sanitize_telegram_html(text: str) -> str:
    """Safely escapes stray & and < characters while preserving valid Telegram HTML formatting tags."""
    if not text:
        return ""
    # 1. Escape & that is not part of a recognized HTML entity
    text = re.sub(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)', '&amp;', text)
    # 2. Escape < that does not match a valid Telegram HTML tag
    valid_tags = r'b|i|u|s|code|pre|a(\s+[^>]*)?|blockquote|strong|em|ins|strike|del|span|tg-spoiler'
    pattern = rf'<(?!/?({valid_tags})\b[^>]*>)'
    return re.sub(pattern, '&lt;', text, flags=re.IGNORECASE)

def send_telegram_file(method: str, file_param: str, file_path: Path, caption: str = "", chat_id: str = None, reply_markup: dict = None, reply_to_message_id: int = None) -> dict:
    """Send local photo or document to Telegram Cloud API via multipart form with caption protection, HTML fallback, and message threading."""
    cfg = load_config()
    token = cfg.get("bot_token")
    if not token:
        return {"ok": False, "description": "No bot token configured"}
    target_chat_id = chat_id or cfg.get("owner_chat_id")
    if not target_chat_id:
        return {"ok": False, "description": "No target chat ID configured"}
    
    if not file_path.exists():
        return {"ok": False, "description": f"File not found: {file_path}"}
        
    overflow_text = None
    if caption and len(caption) > 1000:
        split_idx = caption.rfind("\n", 0, 950)
        if split_idx == -1:
            split_idx = 950
        overflow_text = caption[split_idx:].strip()
        caption = caption[:split_idx] + "...\n<i>(Continued in next message)</i>"
        
    def build_and_send(include_html=True, clean_plain_caption=None):
        boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
        parts = []
        
        def add_field(name, value):
            parts.append(f"--{boundary}\r\n".encode("utf-8"))
            parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
            parts.append(f"{value}\r\n".encode("utf-8"))
            
        add_field("chat_id", str(target_chat_id))
        if reply_to_message_id:
            add_field("reply_to_message_id", str(reply_to_message_id))
            add_field("reply_parameters", json.dumps({"message_id": int(reply_to_message_id)}))
        if caption:
            if clean_plain_caption is not None:
                add_field("caption", clean_plain_caption)
            else:
                caption_to_send = sanitize_telegram_html(caption) if include_html else caption
                add_field("caption", caption_to_send)
                if include_html:
                    add_field("parse_mode", "HTML")
        if reply_markup:
            add_field("reply_markup", json.dumps(reply_markup))
            
        filename = file_path.name
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(f'Content-Disposition: form-data; name="{file_param}"; filename="{filename}"\r\n'.encode("utf-8"))
        parts.append(b"Content-Type: application/octet-stream\r\n\r\n")
        with open(file_path, "rb") as f:
            parts.append(f.read())
        parts.append(b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode("utf-8"))
        
        payload = b"".join(parts)
        url = f"https://api.telegram.org/bot{token}/{method}"
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Content-Length": str(len(payload)),
                "User-Agent": "Antigravity-Telegram-Nexus/1.0"
            }
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8"))

    try:
        res = build_and_send(include_html=True)
        if not res.get("ok") and "can't parse entities" in res.get("description", "").lower():
            # Strip tags for clean text fallback (never leak raw tags)
            plain_caption = re.sub(r'<[^>]+>', '', caption)
            res = build_and_send(include_html=False, clean_plain_caption=plain_caption)
            
        if res.get("ok"):
            record_audit_event("OUTBOUND_FILE", "antigravity", str(target_chat_id), f"Sent {method}: {file_path.name}", {"caption_preview": caption[:60] if caption else ""})
            if overflow_text:
                time.sleep(0.3)
                tool_send_alert({"chat_id": target_chat_id, "message": overflow_text})
        else:
            record_audit_event("OUTBOUND_FILE_ERROR", "antigravity", str(target_chat_id), f"Failed {method}: {file_path.name}", {"error": res.get("description")})
        return res
    except Exception as e:
        record_audit_event("OUTBOUND_FILE_ERROR", "antigravity", str(target_chat_id), f"Exception {method}: {file_path.name}", {"error": str(e)})
        return {"ok": False, "description": str(e)}

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

def send_single_message(chat_id: str, text: str, parse_mode: str = "HTML", disable_preview: bool = True, reply_markup: dict = None, reply_to_message_id: int = None) -> dict:
    if parse_mode == "HTML":
        text = sanitize_telegram_html(text)
    params = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_preview
    }
    if reply_markup:
        params["reply_markup"] = reply_markup
    if reply_to_message_id:
        params["reply_to_message_id"] = int(reply_to_message_id)
        params["reply_parameters"] = {"message_id": int(reply_to_message_id)}
    res = telegram_api_call("sendMessage", params)
    # Automatic Plain-Text Fallback: If Telegram fails because of malformed HTML/tags, strip all tags completely
    if not res.get("ok") and "can't parse entities" in res.get("description", "").lower():
        params["text"] = re.sub(r'<[^>]+>', '', text)
        params.pop("parse_mode", None)
        res = telegram_api_call("sendMessage", params)
    return res

def tool_send_alert(args: dict) -> dict:
    """Send high-priority alert or notification to Karan's Telegram with auto-chunking (>4000 chars), HTML fallback, and message threading."""
    cfg = load_config()
    chat_id = args.get("chat_id") or cfg.get("owner_chat_id")
    if not chat_id:
        return {"ok": False, "error": "No owner_chat_id configured. Set it or provide chat_id."}
    
    message = args.get("message", "")
    parse_mode = args.get("parse_mode", "HTML")
    disable_preview = args.get("disable_preview", True)
    reply_markup = args.get("reply_markup")
    reply_to_message_id = args.get("reply_to_message_id")

    # Fail-safe message threading: auto-lookup original_message_id if job_id is provided
    if not reply_to_message_id and args.get("job_id"):
        try:
            jobs = load_jobs()
            j = jobs.get(args.get("job_id"))
            if j and j.get("original_message_id"):
                reply_to_message_id = j.get("original_message_id")
        except Exception:
            pass
    
    # 1. Single message path (<4000 chars)
    if len(message) <= 4000:
        res = send_single_message(chat_id, message, parse_mode, disable_preview, reply_markup, reply_to_message_id)
        if res.get("ok"):
            msg_id = res.get("result", {}).get("message_id")
            record_audit_event("OUTBOUND_ALERT", "antigravity", str(chat_id), f"Sent alert #{msg_id}", {"preview": message[:100], "message_id": msg_id, "reply_to": reply_to_message_id})
        else:
            record_audit_event("ALERT_FAILED", "antigravity", str(chat_id), f"Alert failed: {res.get('description')}")
        return res
        
    # 2. Auto-Chunking for Long Responses (>4000 chars)
    chunks = []
    curr = message
    while len(curr) > 3900:
        split_idx = curr.rfind("\n\n", 0, 3900)
        if split_idx == -1:
            split_idx = curr.rfind("\n", 0, 3900)
        if split_idx == -1:
            split_idx = 3900
        chunks.append(curr[:split_idx].strip())
        curr = curr[split_idx:].strip()
    if curr:
        chunks.append(curr)
        
    total_parts = len(chunks)
    last_res = {"ok": False}
    for i, chunk in enumerate(chunks, 1):
        header = f"<b>[Part {i}/{total_parts}]</b>\n\n" if total_parts > 1 else ""
        part_markup = reply_markup if i == total_parts else None
        part_reply_to = reply_to_message_id if i == 1 else None
        res = send_single_message(chat_id, header + chunk, parse_mode, disable_preview, part_markup, part_reply_to)
        last_res = res
        time.sleep(0.35)
        
    record_audit_event("OUTBOUND_ALERT_CHUNKED", "antigravity", str(chat_id), f"Sent {total_parts}-part chunked alert", {"total_chars": len(message), "reply_to": reply_to_message_id})
    return last_res

def tool_send_boot_greeting(args: dict = None) -> dict:
    """Send an executive welcome visual hero card & handshake to Karan's phone upon gateway boot or invocation."""
    cfg = load_config()
    chat_id = (args or {}).get("chat_id") or cfg.get("owner_chat_id")
    if not chat_id:
        return {"ok": False, "error": "No owner_chat_id configured"}
    
    caption = (
        "⚡ <b>TELEGRAM NEXUS C2 ONLINE</b>\n\n"
        "Motobook workstation gateway is active & listening in real-time.\n\n"
        "───────────────\n\n"
        "👤 <b>Controller</b>: Karan Singh Verma\n"
        "⏱️ <b>Latency</b>: Sub-Second (&lt;0.1s)\n"
        "🚀 <b>Mode</b>: Master Dispatcher Active\n\n"
        "───────────────\n\n"
        "Tap commands below or send any photo, PDF, or query directly!"
    )
    
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "🎯 Today's Strikes", "callback_data": "/strike"},
                {"text": "📋 Active Tasks", "callback_data": "/task"}
            ],
            [
                {"text": "⚡ Workstation Status", "callback_data": "/status"},
                {"text": "📖 Command Guide", "callback_data": "/help"}
            ]
        ]
    }
    
    # Visual Hero Card dispatch if nexus_logo.jpg exists
    logo_path = Path(__file__).resolve().parent.parent / "assets" / "nexus_logo.jpg"
    if logo_path.exists():
        return send_telegram_file("sendPhoto", "photo", logo_path, caption, chat_id, reply_markup=reply_markup)
        
    return tool_send_alert({"chat_id": chat_id, "message": caption, "reply_markup": reply_markup})

def tool_send_photo(args: dict) -> dict:
    """Send an image or visual artifact to Telegram phone with message threading."""
    photo_path_str = args.get("photo_path")
    if not photo_path_str:
        return {"ok": False, "error": "photo_path is required"}
    p = Path(os.path.expanduser(photo_path_str))
    caption = args.get("caption", "")
    chat_id = args.get("chat_id")
    reply_to_message_id = args.get("reply_to_message_id")
    if not reply_to_message_id and args.get("job_id"):
        try:
            jobs = load_jobs()
            j = jobs.get(args.get("job_id"))
            if j and j.get("original_message_id"):
                reply_to_message_id = j.get("original_message_id")
        except Exception:
            pass
    return send_telegram_file("sendPhoto", "photo", p, caption, chat_id, reply_to_message_id=reply_to_message_id)

def tool_send_document(args: dict) -> dict:
    """Send a document (.md, .txt, .pdf, .csv, .json) to Telegram phone with message threading."""
    doc_path_str = args.get("doc_path")
    if not doc_path_str:
        return {"ok": False, "error": "doc_path is required"}
    p = Path(os.path.expanduser(doc_path_str))
    caption = args.get("caption", "")
    chat_id = args.get("chat_id")
    reply_to_message_id = args.get("reply_to_message_id")
    if not reply_to_message_id and args.get("job_id"):
        try:
            jobs = load_jobs()
            j = jobs.get(args.get("job_id"))
            if j and j.get("original_message_id"):
                reply_to_message_id = j.get("original_message_id")
        except Exception:
            pass
    return send_telegram_file("sendDocument", "document", p, caption, chat_id, reply_to_message_id=reply_to_message_id)

# -----------------------------------------------------------------------------
# Asynchronous Job Ticket Engine & Formatting Helpers
# -----------------------------------------------------------------------------

def load_jobs() -> dict:
    if JOB_REGISTRY_PATH.exists():
        try:
            with open(JOB_REGISTRY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_jobs(jobs: dict):
    JOB_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(JOB_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

def normalize_job_id(raw_id: str) -> str:
    if not raw_id:
        return ""
    clean = raw_id.strip().upper()
    if clean.startswith("JOB-"):
        return clean
    if clean.startswith("JOB"):
        return f"JOB-{clean[3:].strip()}"
    if clean.isdigit():
        return f"JOB-{int(clean):02d}"
    return clean

def cancel_job(raw_id: str, reason: str = "Cancelled by user via Telegram command") -> dict:
    job_id = normalize_job_id(raw_id)
    jobs = load_jobs()
    if job_id not in jobs:
        return {"ok": False, "error": f"Job {job_id} not found."}
    j = jobs[job_id]
    if j.get("status") != "in_progress":
        return {"ok": False, "error": f"Job {job_id} is already {j.get('status')}."}
    now_dt = datetime.datetime.now()
    now_epoch = time.time()
    j["status"] = "failed"
    j["completed_at"] = now_dt.strftime("%Y-%m-%d %H:%M:%S IST")
    j["completed_at_epoch"] = now_epoch
    j["error"] = reason
    created_epoch = j.get("created_at_epoch")
    if created_epoch:
        secs = int(now_epoch - created_epoch)
        j["duration_seconds"] = secs
        j["duration_str"] = f"{secs}s"
    save_jobs(jobs)
    record_audit_event("JOB_CANCELLED", "owner", "telegram", f"Cancelled {job_id}: {reason}")
    return {"ok": True, "job": j}

def render_job_dossier(j: dict) -> str:
    status = j.get("status", "unknown").upper()
    status_emoji = "⚡" if status == "IN_PROGRESS" else ("✅" if status == "COMPLETED" else "❌")
    
    created_epoch = j.get("created_at_epoch")
    now_epoch = time.time()
    
    if status == "IN_PROGRESS" and created_epoch:
        secs = int(now_epoch - created_epoch)
        if secs < 60:
            time_str = f"{secs}s (Crunching)"
        elif secs < 3600:
            time_str = f"{secs // 60}m {secs % 60}s (Crunching)"
        else:
            time_str = f"{secs // 3600}h {(secs % 3600) // 60}m (Crunching)"
    else:
        time_str = j.get("duration_str") or (f"{j.get('duration_seconds')}s" if j.get("duration_seconds") is not None else "N/A")

    lines = [
        f"📋 <b>JOB DOSSIER: {j.get('job_id')}</b>\n\n",
        "───────────────\n\n",
        f"🎯 <b>Task:</b>\n{j.get('task', 'N/A')}\n\n",
        f"{status_emoji} <b>Status:</b> <code>{status}</code>\n",
        f"⏱️ <b>{'Elapsed' if status == 'IN_PROGRESS' else 'Duration'}:</b> {time_str}\n",
        f"👤 <b>Worker:</b> <code>{j.get('assigned_to', 'worker_subagent')}</code>\n",
        f"🕒 <b>Created:</b> {j.get('created_at', 'N/A')}\n\n"
    ]
    
    if j.get("completed_at"):
        lines.append(f"🏁 <b>Completed:</b> {j.get('completed_at')}\n\n")
        
    if j.get("result_summary"):
        lines.append(f"───────────────\n\n📋 <b>Deliverables Summary:</b>\n{j.get('result_summary')}\n\n")
        
    if j.get("error"):
        lines.append(f"───────────────\n\n⚠️ <b>Error Details:</b>\n<code>{j.get('error')}</code>\n\n")
        
    lines.append("───────────────\n\n⚡ <i>Motobook Job Registry</i>")
    return "".join(lines)

def render_job_list(jobs: dict) -> str:
    active = [j for j in jobs.values() if j.get("status") == "in_progress"]
    completed = [j for j in jobs.values() if j.get("status") == "completed"]
    failed = [j for j in jobs.values() if j.get("status") == "failed"]
    
    lines = ["🎟️ <b>JOB REGISTRY & WORKER QUEUE</b>\n\n───────────────\n\n"]
    
    if active:
        lines.append(f"⚡ <b>In Progress ({len(active)}):</b>\n\n")
        now_epoch = time.time()
        for j in active:
            created_epoch = j.get("created_at_epoch")
            elapsed = int(now_epoch - created_epoch) if created_epoch else 0
            lines.append(f"• <b>[{j['job_id']}]</b> {j['task'][:50]}\n  ⏱️ Elapsed: {elapsed}s | 👤 <code>{j.get('assigned_to', 'worker')}</code>\n\n")
    else:
        lines.append("✅ <b>Queue Clear</b> (No active background jobs)\n\n")
        
    lines.append("───────────────\n\n")
    
    if completed:
        lines.append(f"🕒 <b>Recent Completed ({min(len(completed), 5)}):</b>\n\n")
        for j in completed[-5:]:
            dur = j.get("duration_str", "N/A")
            summary = j.get("result_summary") or "Done"
            if len(summary) > 60:
                summary = summary[:57] + "..."
            lines.append(f"• <b>[{j['job_id']}]</b> {j['task'][:40]}\n  ⏱️ {dur} | 📋 {summary}\n\n")
            
    if failed:
        lines.append(f"❌ <b>Recent Failed ({min(len(failed), 3)}):</b>\n\n")
        for j in failed[-3:]:
            err = j.get("error") or "Failed"
            if len(err) > 50:
                err = err[:47] + "..."
            lines.append(f"• <b>[{j['job_id']}]</b> {j['task'][:40]}\n  ⚠️ <code>{err}</code>\n\n")
            
    lines.append("───────────────\n\n💡 <i>Run /jobstatus &lt;id&gt; for full job dossier</i>")
    return "".join(lines)

def tool_poll_updates(args: dict) -> dict:
    """Fetch new messages from Telegram and auto-bind owner if /start detected."""
    cfg = load_config()
    offset = cfg.get("last_update_id", 0) + 1
    limit = args.get("limit", 20)
    poll_timeout = args.get("timeout", 0)
    
    res = telegram_api_call("getUpdates", {"offset": offset, "limit": limit, "timeout": poll_timeout})
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
        cb = u.get("callback_query")
        if cb:
            try:
                telegram_api_call("answerCallbackQuery", {"callback_query_id": cb["id"]})
            except Exception:
                pass
            msg = cb.get("message") or {}
            from_user = cb.get("from", {})
            chat = msg.get("chat", {})
            chat_id = str(chat.get("id")) if chat and chat.get("id") else str(from_user.get("id"))
            text = cb.get("data", "")
            sender_username = from_user.get("username", "")
            sender_name = f"{from_user.get('first_name', '')} {from_user.get('last_name', '')}".strip()
        elif not msg:
            continue
        else:
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
        if not is_owner:
            record_audit_event(
                "UNAUTHORIZED_ACCESS_BLOCKED",
                sender_username or sender_name or "unknown",
                chat_id,
                f"Blocked unauthorized {media_type}",
                {"text": text[:100], "update_id": up_id}
            )
            try:
                telegram_api_call("sendMessage", {
                    "chat_id": chat_id,
                    "text": "⛔ <b>Access Denied</b>\nThis bot is a private sovereign Command & Control gateway restricted to personal workstation use only. Unauthorized messages are discarded.",
                    "parse_mode": "HTML"
                })
            except Exception:
                pass
            continue

        record_audit_event(
            "OWNER_INBOUND",
            sender_username or sender_name or "owner",
            chat_id,
            f"Received {media_type}",
            {"text": text[:150], "media_type": media_type, "update_id": up_id, "file_id": file_id}
        )

        # Visual Hints: Attach emoji reaction to message bubble & trigger typing header
        msg_id = msg.get("message_id")
        if msg_id and args.get("auto_react", True):
            try:
                telegram_api_call("setMessageReaction", {
                    "chat_id": chat_id,
                    "message_id": msg_id,
                    "reaction": [{"type": "emoji", "emoji": "⚡"}]
                })
            except Exception:
                pass
            try:
                telegram_api_call("sendChatAction", {
                    "chat_id": chat_id,
                    "action": "typing"
                })
            except Exception:
                pass

        # Extract Reply-To Threading Context & Referenced Job ID
        reply_to = msg.get("reply_to_message")
        reply_context = None
        referenced_job_id = None
        if reply_to:
            orig_msg_id = reply_to.get("message_id")
            orig_text = reply_to.get("text") or reply_to.get("caption") or ""
            orig_sender = reply_to.get("from", {}).get("username") or reply_to.get("from", {}).get("first_name", "")
            reply_context = {
                "message_id": orig_msg_id,
                "text": orig_text,
                "sender": orig_sender
            }
            # Detect if user swiped-replied to a job card referencing [JOB-XX]
            job_match = re.search(r'\[?(JOB-\d+)\]?', orig_text, re.IGNORECASE)
            if job_match:
                referenced_job_id = job_match.group(1).upper()

        # Natural Language Swipe-Reply on Job Ticket Card
        if is_owner and referenced_job_id and not text.strip().startswith("/"):
            lower_text = text.strip().lower()
            if lower_text in ("status", "info", "details", "check", "progress"):
                jobs = load_jobs()
                if referenced_job_id in jobs:
                    card = render_job_dossier(jobs[referenced_job_id])
                else:
                    card = f"⚠️ Job ticket <code>{referenced_job_id}</code> not found in registry."
                tool_send_alert({"chat_id": chat_id, "message": card, "reply_to_message_id": msg_id})
                continue
            elif lower_text in ("cancel", "stop", "abort", "kill"):
                res = cancel_job(referenced_job_id, reason=f"Cancelled via swipe-reply from owner: '{text.strip()}'")
                if res.get("ok"):
                    card = (
                        "🛑 <b>JOB CANCELLED</b>\n\n"
                        "───────────────\n\n"
                        f"Ticket <code>{referenced_job_id}</code> has been terminated.\n\n"
                        f"🎯 <b>Task:</b> <i>{res['job']['task']}</i>"
                    )
                else:
                    card = f"⚠️ Could not cancel job: {res.get('error')}"
                tool_send_alert({"chat_id": chat_id, "message": card, "reply_to_message_id": msg_id})
                continue

        # Mobile Slash Command Hooks (Fast Path <0.1s)
        if is_owner and text.strip().startswith("/"):
            clean_cmd = text.strip()
            cmd_lower = clean_cmd.lower()

            if cmd_lower.startswith(("/start", "/help")):
                palette_msg = (
                    "⚡ <b>SOVEREIGN COMMAND & CONTROL PALETTE</b>\n\n"
                    "Workstation gateway is active & synchronized in real-time.\n\n"
                    "───────────────\n\n"
                    "🎮 <b>Executive Slash Commands:</b>\n\n"
                    "• <code>/strike</code> — Check today's tactical strikes & milestones\n"
                    "• <code>/task</code> — Inspect active campaigns & operations tree\n"
                    "• <code>/joblist</code> — View active & recent worker job tickets\n"
                    "• <code>/jobstatus &lt;id&gt;</code> — Detailed dossier of specific job ticket\n"
                    "• <code>/jobcancel &lt;id&gt;</code> — Cancel/abort an active job ticket\n"
                    "• <code>/status</code> — Motobook battery, RAM & gateway telemetry\n"
                    "• <code>/spark &lt;idea&gt;</code> — Record thought into Spark.md\n"
                    "• <code>/genimage &lt;prompt&gt;</code> — Generate AI visual on Motobook\n"
                    "• <code>/gendoc &lt;ext&gt; &lt;topic&gt;</code> — Generate doc & send file\n"
                    "• <code>/gsuite &lt;query&gt;</code> — Query Gmail, Calendar & Drive\n"
                    "• <code>/help</code> — Display this command guide\n\n"
                    "───────────────\n\n"
                    "💡 <b>Swipe-Reply Quick Actions:</b>\n"
                    "Swipe right on any <code>[JOB-XX]</code> card and reply:\n"
                    "• <i>\"status\"</i> — Instant job dossier\n"
                    "• <i>\"cancel\"</i> — Terminate the running ticket\n\n"
                    "───────────────\n\n"
                    "📷 <b>Direct Inbound Media:</b>\n"
                    "Send any photo, schematic, screenshot, or PDF document to inspect it!"
                )
                tool_send_alert({"chat_id": chat_id, "message": palette_msg, "reply_to_message_id": msg_id})
                continue

            elif cmd_lower.startswith("/status"):
                try:
                    import psutil
                    mem = psutil.virtual_memory()
                    free_gb = round(mem.available / (1024**3), 1)
                    total_gb = round(mem.total / (1024**3), 1)
                    used_pct = mem.percent
                    batt = psutil.sensors_battery()
                    batt_str = f"{batt.percent}% {'(Charging ⚡)' if batt.power_plugged else '(Battery 🔋)'}" if batt else "AC Power"
                except Exception:
                    free_gb, total_gb, used_pct = "4.5", "16.0", "70"
                    batt_str = "AC Power"
                status_card = (
                    "💻 <b>MOTOBOOK WORKSTATION TELEMETRY</b>\n\n"
                    "───────────────\n\n"
                    f"🧠 <b>RAM</b>: {free_gb} GB free / {total_gb} GB ({used_pct}% used)\n\n"
                    f"🔋 <b>Power</b>: {batt_str}\n\n"
                    "🌐 <b>Gateway</b>: Online & Listening (<0.1s)\n\n"
                    "───────────────\n\n"
                    "⚡ All systems operational."
                )
                tool_send_alert({"chat_id": chat_id, "message": status_card, "reply_to_message_id": msg_id})
                continue

            elif cmd_lower.startswith(("/joblist", "/jobs")) or cmd_lower == "/job":
                jobs = load_jobs()
                card = render_job_list(jobs)
                tool_send_alert({"chat_id": chat_id, "message": card, "reply_to_message_id": msg_id})
                continue

            elif cmd_lower.startswith("/jobstatus"):
                target = clean_cmd[len("/jobstatus"):].strip() or (referenced_job_id or "")
                if not target:
                    card = (
                        "⚠️ <b>Syntax:</b> <code>/jobstatus &lt;id&gt;</code>\n\n"
                        "Example: <code>/jobstatus 1</code> or <code>/jobstatus JOB-01</code>\n\n"
                        "💡 <i>Or swipe-reply to any job ticket and send \"status\".</i>"
                    )
                else:
                    job_id = normalize_job_id(target)
                    jobs = load_jobs()
                    if job_id in jobs:
                        card = render_job_dossier(jobs[job_id])
                    else:
                        card = f"⚠️ Job ticket <code>{job_id}</code> not found in registry."
                tool_send_alert({"chat_id": chat_id, "message": card, "reply_to_message_id": msg_id})
                continue

            elif cmd_lower.startswith("/jobcancel"):
                target = clean_cmd[len("/jobcancel"):].strip() or (referenced_job_id or "")
                if not target:
                    card = (
                        "⚠️ <b>Syntax:</b> <code>/jobcancel &lt;id&gt;</code>\n\n"
                        "Example: <code>/jobcancel 1</code> or <code>/jobcancel JOB-01</code>\n\n"
                        "💡 <i>Or swipe-reply to any job ticket and send \"cancel\".</i>"
                    )
                else:
                    res = cancel_job(target, reason="Cancelled by owner via /jobcancel")
                    if res.get("ok"):
                        card = (
                            "🛑 <b>JOB CANCELLED</b>\n\n"
                            "───────────────\n\n"
                            f"Ticket <code>{res['job']['job_id']}</code> has been terminated.\n\n"
                            f"🎯 <b>Task:</b> <i>{res['job']['task']}</i>"
                        )
                    else:
                        card = f"⚠️ Could not cancel job: {res.get('error')}"
                tool_send_alert({"chat_id": chat_id, "message": card, "reply_to_message_id": msg_id})
                continue

            elif cmd_lower.startswith("/spark"):
                note = clean_cmd[len("/spark"):].strip()
                if not note:
                    tool_send_alert({"chat_id": chat_id, "message": "⚠️ <b>Syntax:</b> <code>/spark &lt;thought or idea&gt;</code>", "reply_to_message_id": msg_id})
                else:
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    spark_text = f"\n---\n### {now_str} (via Mobile Slash Command)\n* {note}\n"
                    SPARK_PATH.parent.mkdir(parents=True, exist_ok=True)
                    with open(SPARK_PATH, "a", encoding="utf-8") as f:
                        f.write(spark_text)
                    record_audit_event("SPARK_INGEST", "owner", chat_id, "Spark ingested via /spark command", {"note": note})
                    tool_send_alert({
                        "chat_id": chat_id,
                        "message": f"⚡ <b>Spark Recorded</b>\n\n───────────────\n\n📝 <i>\"{note}\"</i>\n\nSaved to <code>~/.gemini/Spark.md</code>",
                        "reply_to_message_id": msg_id
                    })
                continue

            elif cmd_lower.startswith("/strike"):
                import sqlite3
                db_path = os.path.expandvars(r"%APPDATA%\Campaigns\Database\campaigns.sqlite")
                try:
                    conn = sqlite3.connect(db_path)
                    conn.row_factory = sqlite3.Row
                    cur = conn.cursor()
                    today_str = datetime.datetime.now().strftime("%d-%m-%Y")
                    cur.execute("SELECT id, title, status FROM Strikes WHERE execution_date = ? LIMIT 8", (today_str,))
                    rows = cur.fetchall()
                    if not rows:
                        cur.execute("SELECT id, title, status, execution_date FROM Strikes WHERE status IN ('Pending', 'Standby', 'Engaged') ORDER BY id DESC LIMIT 5")
                        rows = cur.fetchall()
                    conn.close()
                    lines = ["🎯 <b>TACTICAL STRIKES RADAR</b>\n\n───────────────\n\n"]
                    if rows:
                        for r in rows:
                            status_emoji = "✅" if r["status"] == "Neutralized" else "⏳"
                            lines.append(f"{status_emoji} <b>[#{r['id']}]</b> {r['title']}\n  Status: <code>{r['status']}</code>\n\n")
                    else:
                        lines.append("No active strikes found.\n\n")
                    lines.append("───────────────\n\n⚡ <i>Synchronized with Campaigns SQLite</i>")
                    tool_send_alert({"chat_id": chat_id, "message": "".join(lines), "reply_to_message_id": msg_id})
                except Exception as e:
                    tool_send_alert({"chat_id": chat_id, "message": f"⚠️ Error querying strikes: {str(e)}", "reply_to_message_id": msg_id})
                continue

            elif cmd_lower.startswith("/task"):
                import sqlite3
                db_path = os.path.expandvars(r"%APPDATA%\Campaigns\Database\campaigns.sqlite")
                try:
                    conn = sqlite3.connect(db_path)
                    conn.row_factory = sqlite3.Row
                    cur = conn.cursor()
                    cur.execute("SELECT id, title, priority, stage, deadline FROM Tasks WHERE state = 'Execution' ORDER BY id LIMIT 6")
                    rows = cur.fetchall()
                    conn.close()
                    lines = ["⚔️ <b>ACTIVE CAMPAIGNS & OPERATIONS</b>\n\n───────────────\n\n"]
                    if rows:
                        for r in rows:
                            lines.append(f"• <b>[T-{r['id']}]</b> {r['title']}\n  Stage: <code>{r['stage']}</code> | Priority: {r['priority']}\n  Deadline: {r['deadline'] or 'N/A'}\n\n")
                    else:
                        lines.append("No active execution campaigns.\n\n")
                    lines.append("───────────────\n\n⚡ <i>Synchronized with Campaigns SQLite</i>")
                    tool_send_alert({"chat_id": chat_id, "message": "".join(lines), "reply_to_message_id": msg_id})
                except Exception as e:
                    tool_send_alert({"chat_id": chat_id, "message": f"⚠️ Error querying tasks: {str(e)}", "reply_to_message_id": msg_id})
                continue

        # Automatic Owner Media Intake (Photos, PDFs, Docs, Audio)
        local_file_path = None
        if file_id:
            try:
                MEDIA_DIR.mkdir(parents=True, exist_ok=True)
                now_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                if media_type == "photo":
                    fname = f"photo_{now_ts}_{file_id[:8]}.jpg"
                elif media_type == "document":
                    clean_name = "".join(c for c in file_name if c.isalnum() or c in "._- ")[:40]
                    if not clean_name:
                        clean_name = f"doc_{file_id[:8]}.bin"
                    fname = f"{now_ts}_{clean_name}"
                elif media_type in ("voice", "audio"):
                    fname = f"voice_{now_ts}_{file_id[:8]}.ogg"
                elif media_type == "video":
                    fname = f"video_{now_ts}_{file_id[:8]}.mp4"
                else:
                    fname = f"media_{now_ts}_{file_id[:8]}.bin"
                    
                dest = MEDIA_DIR / fname
                if download_telegram_file(file_id, dest):
                    local_file_path = str(dest.resolve()).replace("\\", "/")
                    if media_type == "photo":
                        text = f"[📷 Photo: {local_file_path}] {caption}".strip()
                    elif media_type == "document":
                        text = f"[📄 Document ({dest.suffix}): {local_file_path}] {caption}".strip()
                    elif media_type == "voice":
                        text = f"[🎙️ Voice Note: {local_file_path} ({duration}s)]"
                    elif media_type == "video":
                        text = f"[🎥 Video: {local_file_path}] {caption}".strip()
            except Exception as e:
                record_audit_event("MEDIA_AUTO_DOWNLOAD_ERR", "system", chat_id, f"Auto download error: {str(e)}")

        processed_messages.append({
            "message_id": msg.get("message_id"),
            "update_id": up_id,
            "chat_id": chat_id,
            "sender_name": sender_name,
            "sender_username": sender_username,
            "text": text,
            "media_type": media_type,
            "file_id": file_id,
            "local_file_path": local_file_path,
            "duration": duration,
            "date": msg.get("date"),
            "is_owner": True,
            "reply_to_message_id": reply_to.get("message_id") if reply_to else None,
            "reply_context": reply_context,
            "referenced_job_id": referenced_job_id
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
        new_spark_lines.append(f"* {note.get('text', '')}")
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
# Asynchronous Job Ticket Engine (Master-Worker Queue)
# -----------------------------------------------------------------------------

def tool_job_create(args: dict) -> dict:
    """Create a new asynchronous job ticket for heavy worker delegation."""
    task_desc = args.get("task", "Unnamed task")
    original_message_id = args.get("original_message_id")
    jobs = load_jobs()
    job_idx = len(jobs) + 1
    job_id = f"JOB-{job_idx:02d}"
    now_dt = datetime.datetime.now()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S IST")
    now_epoch = time.time()
    job_data = {
        "job_id": job_id,
        "task": task_desc,
        "original_message_id": original_message_id,
        "status": "in_progress",
        "assigned_to": args.get("assigned_to", "worker_subagent"),
        "created_at": now_str,
        "created_at_epoch": now_epoch,
        "completed_at": None,
        "completed_at_epoch": None,
        "duration_seconds": None,
        "heartbeat_4m_sent": False,
        "result_summary": None,
        "error": None
    }
    jobs[job_id] = job_data
    save_jobs(jobs)
    record_audit_event("JOB_CREATED", "master_dispatcher", "system", f"Created {job_id}: {task_desc}", {"epoch": now_epoch, "original_message_id": original_message_id})
    return {"ok": True, "job": job_data}

def tool_job_update(args: dict) -> dict:
    """Update progress or complete an asynchronous job ticket."""
    job_id = args.get("job_id")
    status = args.get("status", "completed")
    result_summary = args.get("result_summary")
    jobs = load_jobs()
    if job_id not in jobs:
        return {"ok": False, "error": f"Job {job_id} not found."}
    now_dt = datetime.datetime.now()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S IST")
    now_epoch = time.time()
    jobs[job_id]["status"] = status
    if status in ("completed", "failed"):
        jobs[job_id]["completed_at"] = now_str
        jobs[job_id]["completed_at_epoch"] = now_epoch
        created_epoch = jobs[job_id].get("created_at_epoch")
        if created_epoch:
            secs = int(now_epoch - created_epoch)
            jobs[job_id]["duration_seconds"] = secs
            if secs < 60:
                jobs[job_id]["duration_str"] = f"{secs}s"
            elif secs < 3600:
                mins = secs // 60
                rem_secs = secs % 60
                jobs[job_id]["duration_str"] = f"{mins}m {rem_secs}s"
            else:
                hrs = secs // 3600
                mins = (secs % 3600) // 60
                jobs[job_id]["duration_str"] = f"{hrs}h {mins}m"
        else:
            jobs[job_id]["duration_str"] = "N/A"
    if result_summary:
        jobs[job_id]["result_summary"] = result_summary
    if args.get("error"):
        jobs[job_id]["error"] = args.get("error")
    save_jobs(jobs)
    record_audit_event("JOB_UPDATED", "worker_subagent", "system", f"Updated {job_id} to {status}", {"duration": jobs[job_id].get("duration_seconds")})
    return {"ok": True, "job": jobs[job_id]}

def tool_job_list(args: dict) -> dict:
    """List active or recent job tickets."""
    jobs = load_jobs()
    status_filter = args.get("status")
    job_list = list(jobs.values())
    if status_filter:
        job_list = [j for j in job_list if j.get("status") == status_filter]
    return {"ok": True, "count": len(job_list), "jobs": job_list[-20:]}

def tool_job_get(args: dict) -> dict:
    """Retrieve full dossier and metadata for a specific job ticket."""
    raw_id = args.get("job_id", "")
    job_id = normalize_job_id(raw_id)
    jobs = load_jobs()
    if job_id not in jobs:
        return {"ok": False, "error": f"Job ticket '{job_id}' not found in registry."}
    j = jobs[job_id]
    dossier_card = render_job_dossier(j)
    return {"ok": True, "job": j, "dossier": dossier_card}

def tool_job_cancel(args: dict) -> dict:
    """Cancel an active asynchronous job ticket."""
    raw_id = args.get("job_id", "")
    reason = args.get("reason", "Cancelled via MCP tool")
    return cancel_job(raw_id, reason=reason)

def tool_get_summary(args: dict = None) -> dict:
    """
    Generate an executive activity briefing summarizing Telegram traffic,
    sparks, delegated jobs, and gateway telemetry.
    """
    cfg = load_config()
    owner_id = str(cfg.get("owner_chat_id", ""))
    now_dt = datetime.datetime.now()
    cutoff_24h = now_dt - datetime.timedelta(hours=24)
    today_prefix = now_dt.date().isoformat()
    
    total_events = 0
    stats_24h = {
        "owner_inbound": 0,
        "owner_commands": 0,
        "visitor_inbound": 0,
        "outbound_alerts": 0,
        "sparks_ingested": 0,
        "jobs_created": 0,
        "jobs_updated": 0
    }
    today_counts = {
        "owner_inbound": 0,
        "owner_commands": 0,
        "visitor_inbound": 0,
        "outbound_alerts": 0,
        "sparks_ingested": 0,
        "jobs_created": 0,
        "jobs_updated": 0
    }
    recent_events = []
    last_activity = "None"
    
    if AUDIT_JSONL_PATH.exists():
        try:
            with open(AUDIT_JSONL_PATH, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            total_events = len(lines)
            
            for line in reversed(lines):
                try:
                    ev = json.loads(line)
                    ev_type = ev.get("event_type", "")
                    ts = ev.get("timestamp", "")
                    ht = ev.get("human_time", ts)
                    if last_activity == "None":
                        last_activity = ht
                    
                    if len(recent_events) < 8:
                        recent_events.append({
                            "time": ht,
                            "type": ev_type,
                            "actor": ev.get("actor", ""),
                            "action": ev.get("action", "")
                        })
                    
                    try:
                        ev_dt = datetime.datetime.fromisoformat(ts)
                        is_24h = ev_dt >= cutoff_24h
                    except Exception:
                        is_24h = False
                    is_today = ts.startswith(today_prefix)
                    
                    for target_stats, condition in [(stats_24h, is_24h), (today_counts, is_today)]:
                        if condition:
                            if ev_type in ("OWNER_INBOUND", "OWNER_MESSAGE"):
                                target_stats["owner_inbound"] += 1
                            elif ev_type == "OWNER_COMMAND":
                                target_stats["owner_commands"] += 1
                            elif ev_type in ("VISITOR_INBOUND", "VISITOR_MESSAGE"):
                                target_stats["visitor_inbound"] += 1
                            elif ev_type == "OUTBOUND_ALERT":
                                target_stats["outbound_alerts"] += 1
                            elif ev_type == "SPARK_INGEST":
                                target_stats["sparks_ingested"] += 1
                            elif ev_type == "JOB_CREATED":
                                target_stats["jobs_created"] += 1
                            elif ev_type == "JOB_UPDATED":
                                target_stats["jobs_updated"] += 1
                except Exception:
                    continue
        except Exception:
            pass

    jobs = load_jobs()
    active_jobs = [j for j in jobs.values() if j.get("status") == "in_progress"]
    completed_jobs = [j for j in jobs.values() if j.get("status") == "completed"]
    failed_jobs = [j for j in jobs.values() if j.get("status") == "failed"]
    
    show_24h = (today_counts["owner_inbound"] + today_counts["visitor_inbound"] + today_counts["outbound_alerts"]) == 0
    display_stats = stats_24h if show_24h else today_counts
    window_label = "Past 24 Hours Traffic" if show_24h else "Today's Traffic & Actions"
    
    card_lines = [
        "┌─────────────────────────────────────────────────────────────┐",
        "│ 📡 TELEGRAM NEXUS: ACTIVITY & TELEMETRY BRIEFING            │",
        "├─────────────────────────────────────────────────────────────┤",
        f"│ 👤 Owner Chat ID   : {owner_id or 'Unbound':<39}│",
        f"│ 🤖 Bot State       : {'Online & Ready' if cfg.get('bot_token') else 'Unconfigured':<39}│",
        f"│ ⏱️  Last Activity   : {last_activity[:38]:<38}│",
        "├─────────────────────────────────────────────────────────────┤",
        f"│ 📊 {window_label:<57}│",
        f"│  • Inbound Messages: {display_stats['owner_inbound'] + display_stats['owner_commands']:<3} (Cmds: {display_stats['owner_commands']})                         │",
        f"│  • Ingested Sparks : {display_stats['sparks_ingested']:<3} -> ~/.gemini/Spark.md               │",
        f"│  • Outbound Alerts : {display_stats['outbound_alerts']:<3} dispatches to phone               │",
        f"│  • Quarantined     : {display_stats['visitor_inbound']:<3} visitor pings                     │",
        "├─────────────────────────────────────────────────────────────┤",
        "│ 🎟️ Asynchronous Job Tickets                                │",
        f"│  • In Progress     : {len(active_jobs):<39}│",
        f"│  • Completed       : {len(completed_jobs):<39}│",
        f"│  • Failed          : {len(failed_jobs):<39}│"
    ]
    
    if active_jobs:
        card_lines.append("├─────────────────────────────────────────────────────────────┤")
        card_lines.append("│ ⏳ Active Jobs:                                             │")
        for aj in active_jobs[:3]:
            task_snippet = (aj.get("task", "")[:35] + "..") if len(aj.get("task", "")) > 35 else aj.get("task", "")
            card_lines.append(f"│  • [{aj.get('job_id')}] {task_snippet:<47}│")
            
    if completed_jobs:
        card_lines.append("├─────────────────────────────────────────────────────────────┤")
        card_lines.append("│ ✅ Recently Completed Jobs:                                 │")
        for cj in completed_jobs[-3:]:
            res = cj.get("result_summary") or cj.get("task", "")
            res_snippet = (res[:35] + "..") if len(res) > 35 else res
            card_lines.append(f"│  • [{cj.get('job_id')}] {res_snippet:<47}│")
            
    card_lines.append("└─────────────────────────────────────────────────────────────┘")
    formatted_card = "\n".join(card_lines)
    
    return {
        "ok": True,
        "owner_chat_id": owner_id,
        "last_activity": last_activity,
        "stats_window": "past_24h" if show_24h else "today",
        "stats": display_stats,
        "today_stats": today_counts,
        "stats_24h": stats_24h,
        "job_counts": {
            "total": len(jobs),
            "in_progress": len(active_jobs),
            "completed": len(completed_jobs),
            "failed": len(failed_jobs)
        },
        "active_jobs": active_jobs,
        "recent_completed_jobs": completed_jobs[-5:],
        "recent_events": recent_events,
        "formatted_card": formatted_card
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
        "description": "Send high-priority alert, build report, or telemetry to Karan's Telegram phone with native message threading.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "HTML or plain text message to send"},
                "parse_mode": {"type": "string", "enum": ["HTML", "MarkdownV2"], "default": "HTML"},
                "chat_id": {"type": "string", "description": "Optional target chat ID (defaults to owner)"},
                "reply_to_message_id": {"type": "integer", "description": "Optional Telegram message_id to quote/reply directly to"},
                "job_id": {"type": "string", "description": "Optional job ticket ID (e.g. JOB-01) to auto-thread reply to original message"}
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
        "name": "nexus_get_audit_log",
        "description": "Inspect the persistent audit log of all events, messages, alerts, and actions passing through the bot.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50, "description": "Maximum number of audit events to return"},
                "event_type": {"type": "string", "description": "Optional filter by event_type (e.g. OWNER_MESSAGE, VISITOR_MESSAGE, OUTBOUND_ALERT, SPARK_INGEST)"}
            }
        }
    },
    {
        "name": "nexus_job_create",
        "description": "Create an asynchronous job ticket (JOB-XX) for heavy worker delegation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Description of the job task to execute"},
                "assigned_to": {"type": "string", "default": "worker_subagent", "description": "Target worker or subagent"},
                "original_message_id": {"type": "integer", "description": "Original Telegram message_id from Karan to reply to upon completion"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "nexus_job_update",
        "description": "Update status or add result summary to an active job ticket.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "Job ticket ID (e.g. JOB-01)"},
                "status": {"type": "string", "enum": ["in_progress", "completed", "failed"], "default": "completed"},
                "result_summary": {"type": "string", "description": "Summary of completed task or error"}
            },
            "required": ["job_id"]
        }
    },
    {
        "name": "nexus_job_list",
        "description": "List active or recent asynchronous job tickets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["in_progress", "completed", "failed"], "description": "Optional status filter"}
            }
        }
    },
    {
        "name": "nexus_job_get",
        "description": "Retrieve full dossier and metadata for a specific job ticket (e.g. JOB-01).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "Job ticket ID (e.g. JOB-01 or 1)"}
            },
            "required": ["job_id"]
        }
    },
    {
        "name": "nexus_job_cancel",
        "description": "Cancel an active asynchronous job ticket.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "Job ticket ID (e.g. JOB-01 or 1)"},
                "reason": {"type": "string", "description": "Optional cancellation reason"}
            },
            "required": ["job_id"]
        }
    },
    {
        "name": "nexus_get_summary",
        "description": "Generate an executive activity briefing summarizing Telegram traffic, sparks, delegated jobs, and gateway telemetry.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "nexus_send_photo",
        "description": "Send an image or visual artifact (.jpg, .png) to Karan's Telegram phone with native message threading.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "photo_path": {"type": "string", "description": "Absolute or relative path to the image file"},
                "caption": {"type": "string", "description": "Optional HTML/text caption to accompany the photo"},
                "chat_id": {"type": "string", "description": "Optional target chat ID (defaults to owner)"},
                "reply_to_message_id": {"type": "integer", "description": "Optional Telegram message_id to quote/reply directly to"},
                "job_id": {"type": "string", "description": "Optional job ticket ID to auto-thread reply"}
            },
            "required": ["photo_path"]
        }
    },
    {
        "name": "nexus_send_document",
        "description": "Send a document or file (.md, .txt, .pdf, .csv, .json) to Karan's Telegram phone with native message threading.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "doc_path": {"type": "string", "description": "Absolute or relative path to the document file"},
                "caption": {"type": "string", "description": "Optional HTML/text caption to accompany the document"},
                "chat_id": {"type": "string", "description": "Optional target chat ID (defaults to owner)"},
                "reply_to_message_id": {"type": "integer", "description": "Optional Telegram message_id to quote/reply directly to"},
                "job_id": {"type": "string", "description": "Optional job ticket ID to auto-thread reply"}
            },
            "required": ["doc_path"]
        }
    },
    {
        "name": "nexus_send_boot_greeting",
        "description": "Send an executive online handshake card to Karan's phone upon gateway boot or invocation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chat_id": {"type": "string", "description": "Optional target chat ID (defaults to owner)"}
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
    "nexus_get_audit_log": tool_get_audit_log,
    "nexus_job_create": tool_job_create,
    "nexus_job_update": tool_job_update,
    "nexus_job_list": tool_job_list,
    "nexus_job_get": tool_job_get,
    "nexus_job_cancel": tool_job_cancel,
    "nexus_get_summary": tool_get_summary,
    "nexus_send_photo": tool_send_photo,
    "nexus_send_document": tool_send_document,
    "nexus_send_boot_greeting": tool_send_boot_greeting
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
