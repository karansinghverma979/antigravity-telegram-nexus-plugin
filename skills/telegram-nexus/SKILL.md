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
  - Strictly restricted to the authenticated Telegram `owner_chat_id` (`1416939230`).
  - Powers **Voice/Text-to-Spark Intake**: Messages, voice notes, photos, and documents sent by Karan are auto-appended to `~/.gemini/Spark.md` and `~/.gemini/media/`.
  - Powers **System Alert Sink**: Long builds, failed CI pipelines, and daily strike checklists are delivered directly to Karan's phone.
* **Unauthorized Access Drop & Denial**:
  - Any message from a non-owner `chat_id` is immediately rejected with an access-denied security notice and discarded.
  - Zero visitor queue, zero visitor interaction, and zero public exposure.

### 2. ⚡ Simultaneous Multi-Command & Non-Blocking Reactive Loop
* **Zero Socket Blocking**:
  - The reactive trigger script runs silently in the background:
    ```pwsh
    python "$HOME/.gemini/config/plugins/telegram-nexus-plugin/scripts/poll_wait.py"
    ```
  - **0 tokens burned** during waiting.
  - The moment Karan sends a message (or multiple messages), `poll_wait.py` outputs the batch and exits with code 0.
  - Antigravity catches the completion event and **instantly wakes up the live agent in the terminal window**!
* **Non-Blocking Job Triage**:
  - For fast queries: Reply immediately.
  - For heavy jobs:
    1. Create job ticket via `nexus_job_create` with `original_message_id`.
    2. Immediately dispatch queued ACK card quoting `reply_to_message_id`.
    3. Delegate the heavy task to a background worker (`invoke_subagent` or background task).
* **The Sacred Re-Arming Invariant (MANDATORY IN THE SAME TURN)**:
  - At the end of every turn, after dispatching replies or queuing jobs:
    **Always re-arm `poll_wait.py` via `run_command(WaitMsBeforeAsync=500)` in that very same turn!**
  - Never wait for background workers to finish before re-arming the listener!
  - If another message comes in while a worker is crunching, the agent immediately wakes up, handles the new message, re-arms, and sleeps!

### 3. 💬 Native Message Threading ("Reply to this message")
* Every outbound communication must thread directly to Karan's originating message:
  - Fast replies pass `reply_to_message_id = msg["message_id"]`.
  - Queued ACKs pass `reply_to_message_id = msg["message_id"]`.
  - 4-minute progress updates pass `reply_to_message_id = job["original_message_id"]`.
  - Completion cards pass `reply_to_message_id = job["original_message_id"]`.
  - Failure alerts pass `reply_to_message_id = job["original_message_id"]`.
* In Telegram, this displays a native reply quote directly above the bot's response bubble, eliminating any confusion when multiple commands are running concurrently.

### 4. ⏱️ The 4-Minute Watchdog & Progress Sentinel
* If any background job (`JOB-XX`) takes **more than 4 minutes (240s)**:
  - `poll_wait.py` detects the elapsed time and automatically wakes up the agent.
  - The agent dispatches an interim progress update card quoting the originating message:
    ```text
    ⏳ <b>Job [JOB-XX] Progress Update</b>

    ───────────────

    🎯 <b>Task:</b> <task description>

    ⏱️ <b>Elapsed:</b> 4+ minutes (Crunching)

    🚀 <b>Status:</b> Heavy execution active on Motobook workstation. Will notify you immediately upon completion!

    ───────────────

    ⚡ <i>Motobook Sentinel Active</i>
    ```
  - Re-arm `poll_wait.py` immediately.

### 5. 🎟️ Mandatory `job-id completed` Format & Failure Alert
* **Upon Success**:
  - Delivered strictly in the requested **`job-id completed`** format:
    ```text
    ✅ <b>Job [JOB-XX] Completed</b>

    ───────────────

    🎯 <b>Task:</b> <task description>

    ⏱️ <b>Duration:</b> <job.duration_str>

    📋 <b>Summary:</b>
    <concise summary of deliverables>

    ───────────────

    ⚡ <i>Delivered from Motobook Workstation</i>
    ```
* **Upon Failure**:
  - Dispatches immediate failure card:
    ```text
    ❌ <b>Job [JOB-XX] Failed</b>

    ───────────────

    🎯 <b>Task:</b> <task description>

    ⚠️ <b>Error Details:</b>
    <error reason>

    ───────────────

    ⚡ <i>Motobook Sentinel Alert</i>
    ```

### 6. 🎯 Channel Persona Isolation (Mobile vs. Terminal)
* **Local Terminal Chat**: Full-depth systems engineering mode (architecture plans, diffs, telemetry, raw terminal commands).
* **Telegram Mobile Channel**: Outbound messages are strictly formatted using the **Spacious Card Standard**:
  - Generous blank lines before and after every point.
  - Modular visual dividers (`───────────────`).
  - Micro-chunked paragraphs (maximum 2–3 lines per block) to eliminate mobile visual fatigue.
  - Safe HTML formatting (`<b>`, `<i>`, `<code>`, `<pre>`).

### 7. 👁️ Autonomous Vision & Multimodal Media Intake
* **Automatic Download**: Inbound photos, screenshots, PDFs, code files, or audio notes are saved directly into `~/.gemini/media/`.
* **Multi-Modal Inspection**: The agent uses `view_file(AbsolutePath=...)` to visually inspect screenshots, schematics, multi-page PDFs, or syllabi directly with vision capabilities.
* **Zero-Denial Invariant**: Never state an inability to see photos or read PDFs. Files reside locally on Motobook.

---

## 🎮 Command Workflows & Shorthand Suite

### 1. Terminal Governance Commands (Motobook Workstation)

| Command / Shorthand | Target Action | Underlying Mechanism |
| :--- | :--- | :--- |
| **`/telegram-nexus start`** | Start live reactive trigger loop in active session | Launches `poll_wait.py` with Sacred Re-Arming |
| **`/telegram-nexus stop`** | Stop live loop and release polling socket | Flags `STOP_FILE` & releases PID |
| **`/telegram-nexus status`** | Check bot connection, trigger state, and active jobs | `python listener.py --status` |
| **`/telegram-nexus summary`** | Render executive activity briefing card | `nexus_get_summary` |
| **`/telegram-nexus jobs`** | List all active and recent `JOB-XX` tickets | `nexus_job_list` |
| **`/telegram-nexus alert <msg>`** | Send instant alert or report to Karan's phone | `nexus_send_alert` |
| **`/telegram-nexus spark`** | Pull unhandled phone thoughts into `Spark.md` | `nexus_ingest_spark` |
| **`/telegram-nexus log`** | Inspect persistent audit trail of all bot events | `nexus_get_audit_log` |

### 2. Mobile Slash Commands & Specialized Handlers (Karan on Telegram)

| Mobile Slash Command | Speed / Path | Specialized Execution |
| :--- | :--- | :--- |
| **`/start`** / **`/help`** | Fast Path (<0.1s) | Returns interactive Command Palette & executive guide |
| **`/ping`** | Fast Path (<0.1s) | Latency benchmark test $\rightarrow$ returns instant pong & connection health |
| **`/joblist`** (or `/jobs`) | Fast Path (<0.1s) | Lists active background worker queue & recent job ticket dossiers |
| **`/jobstatus <id>`** | Fast Path (<0.1s) | Detailed dossier of specific job ticket (e.g. `/jobstatus JOB-01`) |
| **`/jobcancel <id>`** | Fast Path (<0.1s) | Terminate and mark an in-progress job ticket as aborted |
| **`/status`** | Fast Path (<0.1s) | Dispatches Motobook battery, RAM & gateway telemetry |
| **`/strike`** | Fast Path (<0.1s) | Queries `campaigns.sqlite` strikes table $\rightarrow$ returns today's strike checklist |
| **`/task`** | Fast Path (<0.1s) | Queries active campaigns & operations tree from `campaigns.sqlite` |
| **`/spark <note>`** | Fast Path (<0.1s) | Appends note to `~/.gemini/Spark.md` and attaches `⚡` reaction |
| **`/genimage <prompt>`** | Slow Path (`JOB-XX`) | Generates AI visual on Motobook $\rightarrow$ delivers via `nexus_send_photo` |
| **`/gendoc <ext> <topic>`** | Slow Path (`JOB-XX`) | Generates `.md`/`.txt`/`.csv` document $\rightarrow$ delivers via `nexus_send_document` |
| **`/stop`** | Control Path | Halts the active polling trigger cleanly |

### 3. Swipe-Reply Quick Actions (Natural Language Shortcuts)
- Reply to any `[JOB-XX]` card with **`status`** / **`info`** / **`check`** $\rightarrow$ Instant job dossier
- Reply to any `[JOB-XX]` card with **`cancel`** / **`stop`** / **`kill`** $\rightarrow$ Terminate the ticket immediately

