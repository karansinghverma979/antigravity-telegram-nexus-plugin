# 🌐 Telegram Nexus: Sovereign Mobile C2 Gateway

[![OpenSSF Scorecard](https://img.shields.io/badge/OpenSSF-Hardened-10B981?style=for-the-badge&logo=shield)](SECURITY.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-00F0FF?style=for-the-badge)](LICENSE)
[![Zero Daemon](https://img.shields.io/badge/Runtime-0_MB_Idle_RAM-F59E0B?style=for-the-badge)](mcp/server.py)
[![Antigravity Plugin](https://img.shields.io/badge/Google_Antigravity-Plugin-4285F4?style=for-the-badge&logo=google)](plugin.json)

> **Sovereign Telegram Automation Nexus, Private Mobile Command & Control (C2) Gateway, and Asynchronous Multi-Job Queue for Google Antigravity.**

---

## ⚡ Architectural Blueprint: Master-Worker Pipeline

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ 🏛️ SOVEREIGN MASTER-WORKER COMMAND & CONTROL (C2) ARCHITECTURE           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   [ Karan on Blaze 5G ]          [ Unauthorized Senders ]               │
│            ▲                               ▲                            │
│            │ (Private C2)                  │ (Untrusted)                │
│            ▼                               ▼                            │
│     ┌─────────────────────────────────────────────┐                     │
│     │    @YourNexusBot (Telegram Cloud API)       │                     │
│     └─────────────────────────────────────────────┘                     │
│                            ▲                                            │
│                            │ (Zero-Daemon HTTPS REST)                   │
│                            ▼                                            │
│     ┌─────────────────────────────────────────────┐                     │
│     │  👑 MASTER DISPATCHER AGENT (Ultra-Lean)    │                     │
│     │  • Strict Sovereign Owner Whitelist         │                     │
│     │  • Attaches instant ⚡ reaction to bubble   │                     │
│     │  • Triggers "typing..." status bar header   │                     │
│     └──────────────────────┬──────────────────────┘                     │
│                            │                                            │
│     ┌──────────────────────┴──────────────────────┐                     │
│     ▼                                             ▼                     │
│  [ FAST PATH: Pure Query ]                  [ SLOW PATH: Heavy Jobs ]   │
│  • General queries, ideas, status           • Code, file export, db     │
│  • Answered directly in <2 seconds          • Issues ticket [JOB-XX]    │
│                                             • Hands off to Subagents:   │
│                                               - research subagent       │
│                                               - win_janitor subagent    │
│                                               - git / code subagent     │
│                                                   │                     │
│                                                   ▼ (Upon Completion)   │
│                                             Dispatches completion card  │
│                                             & documents back to phone   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart & Installation (1-Minute Setup)

### 1. Create Your Bot
1. Open Telegram, search for **`@BotFather`**, and send `/newbot`.
2. Choose a Display Name (e.g. `Karan Executive Nexus`) and Username (e.g. `KSVNexusBot`).
3. Copy the HTTP API token provided by BotFather.

### 2. Register in Antigravity (`~/.gemini/config/mcp_config.json`)
Add the server entry to your MCP configuration:

```jsonc
"telegram-nexus": {
  "command": "python",
  "args": [
    "<HOME>/.gemini/config/plugins/telegram-nexus-plugin/mcp/server.py"
  ],
  "disabled": false
}
```

### 3. Bind Sovereign Ownership
1. Send `/start` to your newly created bot on Telegram.
2. The bot automatically detects and binds your private Telegram Chat ID as the **Sovereign Owner**.
3. All future voice/text notes will be routed to your local `~/.gemini/Spark.md`, and alerts will be delivered directly to your phone.
4. Any non-owner user attempting to message the bot receives an instant security rejection notice, and their message is dropped.

---

## 🛠️ MCP Tool Suite

| Tool Name | Scope & Function | Payload Parameters |
| :--- | :--- | :--- |
| `nexus_get_status` | Check bot connectivity, health, and owner binding | None |
| `nexus_configure` | Set bot token or owner chat ID in isolated config | `bot_token`, `owner_chat_id` |
| `nexus_send_alert` | Send high-priority alert or report to Karan's phone | `message`, `parse_mode` |
| `nexus_poll_updates` | Poll unread owner messages & auto-react with `⚡` | `limit` (default: 20) |
| `nexus_ingest_spark` | Ingest unhandled owner thoughts into `Spark.md` | None |
| `nexus_job_create` | Create asynchronous job ticket (`JOB-XX`) for background delegation | `task`, `assigned_to` |
| `nexus_job_update` | Update progress or mark a job ticket completed | `job_id`, `status`, `result_summary` |
| `nexus_job_list` | Query active or recent job tickets | `status` |
| `nexus_get_summary` | Generate executive activity briefing card of traffic, sparks & jobs | None |
| `nexus_send_photo` | Dispatch visual artifact or image (.jpg, .png) to Telegram | `photo_path`, `caption` |
| `nexus_send_document` | Dispatch document or report (.md, .txt, .pdf, .csv) to Telegram | `doc_path`, `caption` |
| `nexus_get_audit_log` | Query immutable audit log of all bot actions and events | `limit`, `event_type` |

---

## 🎮 Sovereign Governance & Executive Commands

### 1. Terminal Governance Commands (Motobook Workstation)

| Executive Command | Target Action | Underlying Mechanism |
| :--- | :--- | :--- |
| **`/telegram-nexus start`** / `/nexus start` | Start managed checking loop | Spawns background subagent task |
| **`/telegram-nexus stop`** / `/nexus stop` | Stop loop & halt background token consumption | Kills background listener task |
| **`/telegram-nexus summary`** / `/nexus summary` | Render executive activity briefing card | `nexus_get_summary` |
| **`/telegram-nexus status`** / `/nexus status` | Check gateway health, loop state & active jobs | `nexus_get_status` + `nexus_job_list` |
| **`/telegram-nexus jobs`** / `/nexus jobs` | List active and recent asynchronous job tickets | `nexus_job_list` |
| **`/telegram-nexus alert <msg>`** | Send instant alert or report to Karan's phone | `nexus_send_alert` |
| **`/telegram-nexus spark`** | Pull unhandled phone thoughts into `Spark.md` | `nexus_ingest_spark` |

### 2. Mobile Slash Commands & Agent Hooks (Karan on Telegram)

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

## 🔄 Cross-Channel Activity Briefing & Zero-Token Context Hydration

To prevent terminal distraction and context pollution while working on the laptop:
1. **Background Subagent**: Operates purely in the background, updating disk ledgers (`telegram_jobs.json`, `telegram_nexus.jsonl`, `Spark.md`) without sending chat messages into the primary conversation.
2. **Instant On-Demand Briefing**: When Karan asks *"What happened on Telegram?"* or runs `/telegram-nexus summary`, the main agent executes `nexus_get_summary` in <10ms to display an executive briefing card:

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

---

## 🔒 Security & Architectural Invariants

- **Non-Blocking Multi-Turn Queue**: When multiple messages arrive in a batch, Master triages each item independently, creates job tickets, and continues receiving subsequent turns without head-of-line blocking.
- **Channel Persona Isolation**: Spacious Card formatting (dividers, micro-chunks, breathing room) applies **strictly to outbound Telegram messages**. Main terminal session remains in unconstrained Master Systems Architect mode.
- **Autonomous Multimodal Media Intake**: Inbound photos, screenshots, PDFs, documents, and voice notes are automatically downloaded to `~/.gemini/media/` and passed directly to the agent's vision/document inspection tools (`view_file`), enabling immediate visual analysis of errors, diagrams, and multi-page PDFs.
- **Zero Path Leaks**: All user directory references utilize portable dynamic environment expansion (`~`, `%USERPROFILE%`).
- **Zero Token Commits**: Tokens are quarantined in `~/.gemini/config/telegram_config.json`, which is excluded from git tracking via `.gitignore`.
- **Strict Sovereign Owner Gating**: Only the authenticated owner chat ID can interact with the workstation; all unauthorized callers receive immediate 403 access denial with zero system footprint.
- **Immutable Audit Logging**: Every transaction, rejected access attempt, job creation, and outbound alert is recorded in local append-only log files (`~/.gemini/logs/telegram_nexus.log` and `.jsonl`).
- **SHA Action Pinning**: GitHub Actions in `.github/workflows/` are pinned to immutable commit SHAs.

---

## 📜 License

MIT License © 2026 Karan Singh Verma.
