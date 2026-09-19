---
name: telegram-nexus
description: Sovereign Telegram Automation Nexus & Private Mobile C2 Gateway for Google Antigravity. Use when managing Telegram bot alerts, remote mobile thought intake into Spark.md, asynchronous multi-job delegation, or daily strike mobile synchronizations.
---

# 🌐 Telegram Nexus: Sovereign Mobile C2 Gateway

Use this skill whenever Karan invokes `/nexus`, `/telegram`, or needs to manage communications, mobile thought buffering, asynchronous background delegation, or system telemetry between Motobook, Blaze 5G, and Telegram.

> **Single Source of Truth**: This skill is the authoritative operating governor for `antigravity-telegram-nexus-plugin`. It enforces strict sovereign isolation, ensuring the gateway operates exclusively for Karan's personal Command & Control (C2) with zero public or visitor exposure.

---

## 🏛️ Operating Philosophy & Core Directives

### 1. 🛡️ Strict Sovereign Owner Invariant (Personal Use Only)
* **100% Owner Gated**:
  - Strictly restricted to the authenticated Telegram `owner_chat_id`.
  - Powers **Voice/Text-to-Spark Intake**: Messages, voice notes, photos, and documents sent by Karan are auto-appended to `~/.gemini/Spark.md` and `~/.gemini/media/`.
  - Powers **System Alert Sink**: Long builds, failed CI pipelines, and daily strike checklists are delivered directly to Karan's phone.
* **Unauthorized Access Drop & Denial**:
  - Any message from a non-owner `chat_id` is immediately rejected with an access-denied security notice and discarded.
  - Zero visitor queue, zero visitor interaction, and zero public exposure.

### 2. ⚡ Master-Worker Asynchronous Pipeline & Multi-Turn Concurrency
* **Master Dispatcher Role (Zero Blocking)**:
  - When messages arrive, the Master Dispatcher categorizes each item into Fast-Path vs. Slow-Path:
    - **Fast Path (Pure Conversation / Status)**: Master answers immediately (<2 seconds).
    - **Slow Path (Heavy Jobs / Tools / Code / Research)**: Master creates a `JOB-XX` ticket via `nexus_job_create`, fires an immediate ACK card to Telegram, and delegates to a Worker Subagent.
* **Non-Blocking Multi-Turn Queue**:
  - If multiple messages arrive in a single 30s window (e.g. 5 messages):
    - Each message is routed independently without head-of-line blocking.
    - In the subsequent window, the Master continues to receive and process new messages while background workers are actively executing.
  - When a worker finishes a job, the Master formats the result and dispatches the completion card to Telegram.

### 3. 🎯 Channel Persona Isolation (Mobile vs. Terminal)
* **Local Terminal Chat (Here)**: Remains in full-depth Master Systems Architect & Engineering mode (code diffs, raw logs, deep architecture, terminal commands). Never constrained by mobile formatting rules.
* **Telegram Mobile Channel**: Outbound messages are strictly formatted using the **Spacious Card Standard**:
  - Generous breathing room (blank lines before and after every point).
  - Modular visual dividers (`───────────────`).
  - Micro-chunked paragraphs (maximum 2–3 lines per block) to eliminate mobile visual fatigue.

### 4. ⚡ Zero-Daemon Invariant (0 MB Idle RAM)
* Telegram Nexus runs via native HTTPS REST API (`getUpdates`, `sendMessage`) inside the `telegram-nexus-mcp` server.
* No long-running background Python daemons, no memory leaks, and zero background CPU usage on Motobook.

### 5. 🔒 Credential Quarantine
* Bot tokens and owner bindings are stored strictly in `~/.gemini/config/telegram_config.json`.
* **Zero secrets inside git trees**: Never commit `.env`, tokens, or chat IDs into the repository.

### 6. 👁️ Autonomous Vision & Multimodal Media Intake
* **Automatic Download**: When Karan sends photos, screenshots, PDFs, code files, or voice notes, the gateway immediately downloads the payload into `~/.gemini/media/`.
* **Multi-Modal Inspection**: The agent uses `view_file(AbsolutePath=...)` to visually inspect screenshots, schematics, multi-page PDFs, syllabi, or datasets directly with multi-modal vision.
* **Zero-Denial Invariant**: Never state an inability to see photos or read PDFs. Files reside on Motobook's local storage and are inspected immediately.

---

## 🎮 Command Workflows & Shorthand Suite

### 1. Terminal Governance Commands (Motobook Workstation)

| Command / Shorthand | Target Action | Underlying Mechanism |
| :--- | :--- | :--- |
| **`/telegram-nexus start`** / `/nexus start` | Start live background checking loop | Spawns managed background subagent task |
| **`/telegram-nexus stop`** / `/nexus stop` | Stop live loop and halt all background tokens | Kills managed background task |
| **`/telegram-nexus summary`** / `/nexus summary` | Render executive activity briefing card | `nexus_get_summary` |
| **`/telegram-nexus status`** / `/nexus status` | Check bot connection, loop state, and active jobs | `nexus_get_status` + `nexus_job_list` |
| **`/telegram-nexus jobs`** / `/nexus jobs` | List all active and recent `JOB-XX` tickets | `nexus_job_list` |
| **`/telegram-nexus alert <msg>`** | Send instant alert or report to Karan's phone | `nexus_send_alert` |
| **`/telegram-nexus spark`** | Pull unhandled phone thoughts into `Spark.md` | `nexus_ingest_spark` |
| **`/telegram-nexus log`** | Inspect persistent audit trail of all bot events | `nexus_get_audit_log` |

### 2. Mobile Slash Commands & Specialized Hooks (Karan on Telegram)

| Mobile Slash Command | Speed / Path | Specialized Agent Hook & Execution |
| :--- | :--- | :--- |
| **`/genimage <prompt>`** | Slow Path (`JOB-XX`) | Generates AI visual on Motobook $\rightarrow$ delivers via `nexus_send_photo` |
| **`/gendoc <ext> <topic>`** | Slow Path (`JOB-XX`) | Generates `.md`/`.txt`/`.csv` document $\rightarrow$ delivers via `nexus_send_document` |
| **`/gsuite <query>`** | Fast/Slow Path | Queries Google Workspace MCP (Gmail, Calendar, Drive, Docs) |
| **`/strike`** | Fast Path (<2s) | Queries `campaigns.sqlite` strikes table $\rightarrow$ returns today's strike checklist |
| **`/task`** | Fast Path (<2s) | Queries active campaigns & operations tree from `campaigns.sqlite` |
| **`/job`** | Fast Path (<1s) | Lists active and completed asynchronous background worker tickets |
| **`/spark <note>`** | Fast Path (<1s) | Appends note to `~/.gemini/Spark.md` and attaches `⚡` reaction |
| **`/status`** | Fast Path (<2s) | Dispatches Motobook battery, RAM, and gateway health telemetry |
| **`/help`** | Fast Path (<1s) | Displays interactive command palette and documentation |

---

## 🔄 Cross-Channel Activity Briefing & Zero-Token Context Sync

### The Problem: Context Bleed & Interruption Avoidance
When Karan runs `/telegram-nexus start` on Motobook, the background subagent handles mobile communications independently. Streaming every minor mobile greeting or status check into the main laptop terminal would pollute conversation context and burn tokens unnecessarily.

### The Solution: Instant On-Demand Context Hydration
Both the main laptop agent and the background Telegram subagent share authoritative single-source-of-truth disk ledgers:
1. `~/.gemini/logs/telegram_jobs.json`: State machine of all worker tickets (`JOB-XX`).
2. `~/.gemini/logs/telegram_nexus.jsonl`: Append-only structured JSON Lines audit log.
3. `~/.gemini/Spark.md`: Ephemeral thoughts and task captures.

When Karan asks:
- *"What happened on Telegram?"*
- *"What did we do through Telegram?"*
- or executes `/telegram-nexus summary`

The main agent calls `nexus_get_summary`. In <10ms, it parses these ledgers and generates an instant **Executive Briefing Card**:

```text
┌─────────────────────────────────────────────────────────────┐
│ 📡 TELEGRAM NEXUS: ACTIVITY & TELEMETRY BRIEFING            │
├─────────────────────────────────────────────────────────────┤
│ 👤 Owner Chat ID   : 1416939230                             │
│ 🤖 Bot State       : Online & Ready                         │
│ ⏱️  Last Activity   : 2026-09-20 00:59:43 IST               │
├─────────────────────────────────────────────────────────────┤
│ 📊 Past 24 Hours Traffic                                    │
│  • Inbound Messages: 4   (Cmds: 1)                         │
│  • Ingested Sparks : 1   -> ~/.gemini/Spark.md               │
│  • Outbound Alerts : 4   dispatches to phone               │
│  • Quarantined     : 8   visitor pings                     │
├─────────────────────────────────────────────────────────────┤
│ 🎟️ Asynchronous Job Tickets                                │
│  • In Progress     : 0                                      │
│  • Completed       : 1                                      │
│  • Failed          : 0                                      │
├─────────────────────────────────────────────────────────────┤
│ ✅ Recently Completed Jobs:                                 │
│  • [JOB-01] Vacuum completed, 40 strikes and 56..          │
└─────────────────────────────────────────────────────────────┘
```

### Proactive Session Integration (Rule 2 - 360° Session Boot Radar)
At the boot of any new session or when switching contexts, the primary agent can silently inspect `telegram_jobs.json` and `Spark.md` (<50 tokens). If new sparks or completed jobs were registered from mobile while away, it proactively surfaces them without requiring manual prompting.

---

## 🎫 Asynchronous Job Ticket Lifecycle

Jobs are tracked in `~/.gemini/logs/telegram_jobs.json`:
```text
[Incoming Heavy Task] ──► nexus_job_create ──► Issue [JOB-01]
                                                    │
         ┌──────────────────────────────────────────┴────────────────┐
         │ (Instant Ack to Telegram)                                 │
         ▼                                                           ▼
  "⚡ Job [JOB-01] Queued"                                    [Worker Subagent executes]
                                                                     │ (Done)
                                                                     ▼
                                                              nexus_job_update
                                                                     │
                                                                     ▼
                                                             [Delivered to Phone]
```

---

## 📜 Immutable Audit Logging Architecture
All bot activity is recorded in dual formats at `~/.gemini/logs/`:
* **Human-Readable Log**: `~/.gemini/logs/telegram_nexus.log` (Formatted timestamped entries with event types and actors).
* **Machine-Readable Ledger**: `~/.gemini/logs/telegram_nexus.jsonl` (Append-only structured JSON Lines for deterministic querying and forensics).

Logged event types: `OWNER_INBOUND`, `UNAUTHORIZED_ACCESS_BLOCKED`, `OUTBOUND_ALERT`, `SPARK_INGEST`, `MEDIA_DOWNLOAD`, `JOB_CREATED`, `JOB_UPDATED`, `CONFIG_UPDATE`.

