---
name: telegram-nexus
description: Sovereign Telegram Automation Nexus, Mobile C2 Gateway & Dispatch Firewall for Google Antigravity. Use when managing Telegram bot alerts, remote mobile thought intake into Spark.md, daily strike mobile synchronizations, or portfolio visitor dispatch relays.
---

# 🌐 Telegram Nexus: Sovereign Mobile C2 & Dispatch Gateway

Use this skill whenever Karan invokes `/nexus`, `/telegram`, or needs to manage communications, mobile thought buffering, or system telemetry between Motobook, Blaze 5G, and Telegram.

> **Single Source of Truth**: This skill is the authoritative operating governor for `antigravity-telegram-nexus-plugin`. It manages the dual-chamber security boundary separating Karan's private Command & Control (C2) channel from the public portfolio dispatch relay.

---

## 🏛️ Operating Philosophy & Core Directives

### 1. 🛡️ Dual-Chamber Security Invariant
* **Chamber 1 (Private C2 Channel)**:
  - Strictly restricted to Karan's authenticated Telegram `owner_chat_id`.
  - Powers **Voice/Text-to-Spark Intake**: Messages sent by Karan are auto-appended to `~/.gemini/Spark.md`.
  - Powers **System Alert Sink**: Long builds, failed CI pipelines, and daily strike checklists are delivered directly to Karan's phone.
* **Chamber 2 (Public Portfolio Dispatch Firewall)**:
  - Public visitors on `karansinghverma979.github.io` interact through `@BotUsername`.
  - Visitors **never** see Karan's phone number or personal Telegram handle.
  - Inquiries are queued for Karan's review with 1-click reply relay via `nexus_reply_visitor`.

### 2. ⚡ Zero-Daemon Invariant (0 MB Idle RAM)
* Telegram Nexus runs via native HTTPS REST API (`getUpdates`, `sendMessage`) inside the `telegram-nexus-mcp` server.
* No long-running background Python daemons, no memory leaks, and zero background CPU usage on Motobook.

### 3. 🔒 Credential Quarantine
* Bot tokens and owner bindings are stored strictly in `~/.gemini/config/telegram_config.json`.
* **Zero secrets inside git trees**: Never commit `.env`, tokens, or chat IDs into the repository.

---

## 🎮 Command Workflows & Shorthand Suite

| Command / Shorthand | Target Action | MCP Tool Executed |
| :--- | :--- | :--- |
| **`/nexus status`** | Check bot connection health & owner binding | `nexus_get_status` |
| **`/nexus alert <message>`** | Send instant alert or report to Karan's phone | `nexus_send_alert` |
| **`/nexus spark`** | Pull unhandled phone thoughts into `Spark.md` | `nexus_ingest_spark` |
| **`/nexus poll`** | Check incoming messages & public inquiries | `nexus_poll_updates` |
| **`/nexus log`** | Inspect persistent audit trail of all bot events | `nexus_get_audit_log` |
| **`/nexus reply <chat_id> <msg>`** | Reply to a portfolio visitor through the bot | `nexus_reply_visitor` |

---

## 📜 Immutable Audit Logging Architecture
All bot activity is recorded in dual formats at `~/.gemini/logs/`:
* **Human-Readable Log**: `~/.gemini/logs/telegram_nexus.log` (Formatted timestamped entries with event types and actors).
* **Machine-Readable Ledger**: `~/.gemini/logs/telegram_nexus.jsonl` (Append-only structured JSON Lines for deterministic querying and forensics).

Logged event types: `OWNER_INBOUND`, `VISITOR_INBOUND`, `OUTBOUND_ALERT`, `SPARK_INGEST`, `MEDIA_DOWNLOAD`, `CONFIG_UPDATE`, `VISITOR_REPLY`.

---

## 🛠️ Onboarding & Initial Configuration (1-Minute Setup)

1. Open Telegram $\rightarrow$ Search for **`@BotFather`** $\rightarrow$ Type `/newbot`.
2. Choose a Name (e.g. `Karan Executive Nexus`) and Username (e.g. `KSVNexusBot`).
3. Copy the HTTP API token provided by BotFather.
4. Run:
   ```powershell
   # Call nexus_configure with the bot token
   ```
5. Send `/start` to your newly created bot on Telegram. The bot will automatically detect your Chat ID and bind you as the Sovereign Owner.
