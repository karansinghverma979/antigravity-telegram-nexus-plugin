# 🌐 Telegram Nexus Operational Rules & Channel Invariants

Whenever interacting with Karan's Telegram channel or dispatching alerts from Motobook workstation, all agents must strictly obey these directives:

---

### 1. 📱 The Spacious Card Standard (Mobile UX)
Outbound messages to Telegram must prevent visual fatigue on mobile screens:
* **Double Spacing**: Generous blank lines before and after every bullet, title, and section.
* **Visual Dividers**: Use `───────────────` between sections.
* **Micro-Paragraphs**: Cap text blocks at 2–3 lines maximum.
* **Safe HTML & Strict Entity Escaping**:
  - Allowed tags: `<b>`, `<i>`, `<code>`, `<pre>`.
  - **MANDATORY**: Never output raw `&` or `<`. Always escape as `&amp;` and `&lt;` (a single raw `&` causes Telegram to fail HTML parsing and render all tags as literal plain text).

---

### 2. 💬 Native Message Bubble Quoting (`reply_to_message_id`)
* **Always Quote**: Whenever answering a question, responding to a command, acknowledging a task, or reporting job status, pass `reply_to_message_id=msg["message_id"]` (or `job["original_message_id"]`).
* Never send disconnected floating messages when responding to an inbound query.

---

### 3. ⚡ Non-Blocking Execution & Fast-Path Routing
* **Fast-Path (`is_fast_path: True`)**: Direct conversational answers, status telemetry, `/strike`, `/task`, `/ping` $\rightarrow$ Respond immediately (<2s).
* **Slow-Path (`is_fast_path: False`)**: Coding, refactoring, research, `/genimage`, `/gendoc` $\rightarrow$
  1. Create job ticket via `nexus_job_create` (e.g. `JOB-01`).
  2. Send instant ACK card quoting `reply_to_message_id`: `⚡ Job [JOB-XX] Queued`.
  3. Delegate work to a worker subagent or background task.
  4. **CRITICAL**: Re-arm `poll_wait.py` in the **exact same turn** before ending execution. Never wait for the worker to finish before re-arming!

---

### 4. 🔒 The Sacred Re-Arming Invariant
* At the end of every active turn, re-arm the reactive polling trigger:
  `python "$HOME/.gemini/config/plugins/telegram-nexus-plugin/scripts/poll_wait.py"`
  via `run_command(WaitMsBeforeAsync=500)` before sleeping.
* The agent must never terminate or go dead after 1 or 2 messages.

---

### 5. 🛡️ Sovereign Security & Multimodal Intake
* **Zero Secret Leaks**: Never print Telegram bot tokens, API keys, or raw environment variables into Telegram chats or public audit files.
* **Autonomous Vision**: Inbound media in `~/.gemini/media/` must be inspected directly via `view_file` (screenshots, photos, PDFs). Never claim inability to view files.
