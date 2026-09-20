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
| `nexus_send_alert` | Send high-priority alert or report with native message threading | `message`, `parse_mode`, `reply_to_message_id`, `job_id`, `reply_markup` |
| `nexus_ask_choice` | Send interactive choice card with tappable buttons (Yes/No, menus) | `prompt`, `options`, `reply_to_message_id` |
| `nexus_send_poll` | Dispatch native Telegram poll widget (single/multi-choice or quiz) | `question`, `options`, `is_anonymous`, `allows_multiple_answers`, `poll_type` |
| `nexus_send_checklist` | Deploy live-updating interactive checkbox widget (⬜ ⇄ ✅ in-place) | `title`, `items`, `reply_to_message_id` |
| `nexus_poll_updates` | Poll unread owner messages, auto-react with `⚡` & extract `message_id` | `limit` (default: 20) |
| `nexus_ingest_spark` | Ingest unhandled owner thoughts into `Spark.md` | None |
| `nexus_job_create` | Create asynchronous job ticket (`JOB-XX`) with `original_message_id` | `task`, `assigned_to`, `original_message_id` |
| `nexus_job_update` | Update progress, format duration, or mark job ticket completed | `job_id`, `status`, `result_summary`, `error` |
| `nexus_job_list` | Query active or recent job tickets | `status` |
| `nexus_job_get` | Retrieve deep dossier & execution metadata of a specific job ticket | `job_id` |
| `nexus_job_cancel` | Terminate and mark an in-progress job ticket as aborted | `job_id`, `reason` |
| `nexus_get_summary` | Generate executive activity briefing card of traffic, sparks & jobs | None |
| `nexus_send_photo` | Dispatch visual artifact (.jpg, .png) with native message threading | `photo_path`, `caption`, `reply_to_message_id`, `job_id` |
| `nexus_send_document` | Dispatch document (.md, .txt, .pdf, .csv) with native message threading | `doc_path`, `caption`, `reply_to_message_id`, `job_id` |
| `nexus_send_boot_greeting` | Dispatch executive handshake greeting & quick-action palette | `chat_id` |
| `nexus_get_audit_log` | Query immutable audit log of all bot actions and events | `limit`, `event_type` |

---

## 🎮 Sovereign Governance & Executive Commands

### 1. Terminal Governance Commands (Motobook Workstation)

| Executive Command | Target Action | Underlying Mechanism |
| :--- | :--- | :--- |
| **`/telegram-nexus start`** / `/nexus start` | Start in-session reactive trigger loop | Launches `poll_wait.py` with Sacred Re-Arming |
| **`/telegram-nexus stop`** / `/nexus stop` | Stop loop & release polling socket cleanly | Flags `STOP_FILE` & releases PID |
| **`/telegram-nexus summary`** / `/nexus summary` | Render executive activity briefing card | `nexus_get_summary` |
| **`/telegram-nexus status`** / `/nexus status` | Check gateway health, loop state & active jobs | `python listener.py --status` |
| **`/telegram-nexus jobs`** / `/nexus jobs` | List active and recent asynchronous job tickets | `nexus_job_list` |
| **`/telegram-nexus alert <msg>`** | Send instant alert or report to Karan's phone | `nexus_send_alert` |
| **`/telegram-nexus spark`** | Pull unhandled phone thoughts into `Spark.md` | `nexus_ingest_spark` |

### 2. Mobile Slash Commands & Agent Hooks (Karan on Telegram)

| Mobile Slash Command | Speed / Path | Specialized Agent Hook & Execution |
| :--- | :--- | :--- |
| **`/ping`** | Fast Path (<0.1s) | Latency benchmark test $\rightarrow$ returns instant pong & connection health |
| **`/joblist`** (or `/jobs`) | Fast Path (<0.1s) | Displays active background worker queue & recent job ticket dossiers |
| **`/jobstatus <id>`** | Fast Path (<0.1s) | Deep inspection of specific ticket (e.g. `/jobstatus JOB-01` or `/jobstatus 1`) |
| **`/jobcancel <id>`** | Fast Path (<0.1s) | Cancels & aborts active background worker execution |
| **`/strike`** | Fast Path (<2s) | Queries `campaigns.sqlite` strikes table $\rightarrow$ returns today's strike checklist |
| **`/task`** | Fast Path (<2s) | Queries active execution campaigns from `campaigns.sqlite` |
| **`/status`** | Fast Path (<0.1s) | Dispatches Motobook battery, RAM, and gateway health telemetry |
| **`/spark <note>`** | Fast Path (<0.1s) | Ingests thought into `~/.gemini/Spark.md` and appends to Spark queue |
| **`/genimage <prompt>`** | Slow Path (`JOB-XX`) | Generates AI visual on Motobook $\rightarrow$ delivers via `nexus_send_photo` |
| **`/gendoc <ext> <topic>`** | Slow Path (`JOB-XX`) | Generates `.md`/`.txt`/`.csv` document $\rightarrow$ delivers via `nexus_send_document` |
| **`/gsuite <query>`** | Fast/Slow Path | Queries Google Workspace MCP (Gmail, Calendar, Drive, Docs) |
| **`/help`** | Fast Path (<0.1s) | Displays interactive command palette and documentation |

### 3. Swipe-Reply Quick Actions (Natural Language Shortcuts)

Swipe right on any `[JOB-XX]` ticket card on Telegram and reply:
- **`status`** / **`info`** / **`check`** $\rightarrow$ Instant full job dossier
- **`cancel`** / **`stop`** / **`kill`** $\rightarrow$ Terminate the active ticket immediately

### 4. 🔘 Interactive Mobile Widgets, Choices & Real-Time Voting Engine

```text
┌─────────────────────────────────┐      ┌────────────────────────────────┐
│        nexus_ask_choice         │      │        nexus_send_poll         │
│  (Buttons: Yes/No, Menus, etc.) │      │  (Native Telegram Poll Widget) │
└────────────────┬────────────────┘      └───────────────┬────────────────┘
                 │                                       │
                 ▼                                       ▼
    sendMessage + inline_keyboard                   sendPoll API
                 │                                       │
                 ▼                                       ▼
       callback_query update                    poll_answer update
                 │                                       │
                 └──────────────► Agent Awake ◄──────────┘
```

* **Interactive Choices (`nexus_ask_choice`)**:
  - Sends a clean card with single-row or multi-row tap buttons (`[["Yes", "No"]]` or `[["Deploy Prod", "Deploy Staging"], ["Abort"]]`).
  - Tapping an option immediately responds via `callback_data` and delivers your choice directly to the agent without manual typing.
* **Native Telegram Polls (`nexus_send_poll`)**:
  - Uses Telegram's native `sendPoll` API (supports single-choice, multiple-choice, and quiz mode).
  - Captures `poll_answer` events and delivers voter selections back to the workstation.
* **Live Interactive Checklists (`nexus_send_checklist`)**:
  - Dispatches interactive checkbox buttons (`[⬜ Strike #1]`, `[⬜ Strike #2]`).
  - Tapping toggles between `⬜` and `✅` in-place in real-time via `editMessageReplyMarkup` with haptic mobile toasts.
  - `[🏁 Finish Checklist]` finalizes the widget and delivers a completion notice to the agent.

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

## ⚡ In-Session Reactive Event Loop & The 4-Minute Watchdog

### 1. Zero-Token Reactive Wakeup (`poll_wait.py`)
Rather than burning tokens on empty polling loops or polling in a dead-end loop:
- `poll_wait.py` holds Telegram's HTTPS socket silently in the background (0% CPU, 0 MB idle RAM, 0 tokens).
- The exact millisecond Karan messages from Telegram, `poll_wait.py` outputs the payload and exits with code 0.
- Antigravity CLI catches the task completion and **automatically wakes up the live agent in the active terminal window**, preserving 100% of the conversation context!

### 2. The Sacred Re-Arming Invariant
- At the end of every turn (after formulating the reply or queuing a job), the agent **must re-arm `poll_wait.py`** before ending its turn.
- This guarantees the agent runs continuously across turns without ever stopping automatically.

### 3. The 4-Minute Watchdog Sentinel
- If an asynchronous job (`JOB-XX`) executes for **$\ge 4$ minutes (240s)**:
  - `poll_wait.py` detects the elapsed time and wakes up the agent.
  - The agent immediately dispatches an interim progress update card to Telegram:
    `⏳ Job [JOB-XX] Progress Update: Elapsed 4+ minutes... Still crunching on Motobook.`

### 4. Mandatory `job-id completed` Format & Failure Alerts
- **Upon Success**:
  ```text
  ✅ Job [JOB-XX] Completed
  ───────────────
  Task: <description>
  Duration: <time>
  Summary: <deliverables>
  ```
- **Upon Failure**:
  ```text
  ❌ Job [JOB-XX] Failed
  ───────────────
  Task: <description>
  Error: <details>
  ```

---

## 🏛️ Standardized Antigravity Plugin Architecture

This plugin strictly complies with Google Antigravity's official plugin filesystem specification:

```text
plugins/telegram-nexus-plugin/
├── plugin.json         # Required manifest declaring plugin, version & discovery metadata
├── mcp_config.json     # Portable MCP server definition for telegram-nexus
├── rules/              # Ambient operational rules injected when plugin is active
│   └── AGENTS.md       # Consolidated lightweight rules (Spacious Card Standard & Threading)
├── agents/             # Dedicated autonomous subagent definitions
│   └── telegram_nexus.md # Sovereign Master Dispatcher & Non-Blocking Async Agent
├── skills/             # On-demand progressive disclosure skills
│   └── telegram-nexus/
│       └── SKILL.md    # Multi-step command runbook & operational workflows
├── mcp/                # Pure Python stdio MCP server implementation
│   └── server.py       # JSON-RPC server with fast-path heuristics & slash handlers
├── scripts/            # Autonomous event triggers & sentinel daemons
│   ├── listener.py     # Continuous loop controller & telemetry monitor
│   └── poll_wait.py    # Zero-token reactive trigger (holds long-poll socket)
├── assets/             # Media assets, hero card logos & badges
│   └── nexus_logo.jpg
├── README.md           # Sovereign dual-audience documentation
└── SECURITY.md         # OpenSSF-aligned security policy & threat model
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
