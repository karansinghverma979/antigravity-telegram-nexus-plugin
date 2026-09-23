# 🌐 Telegram Nexus: Core Invariants

1. **Spacious Mobile Card Standard**: Outbound messages require double spacing, micro-paragraphs (2–3 lines max), dividers (`───────────────`), and strict HTML escaping (`&amp;`, `&lt;`).
2. **Native Reply Quoting**: Always pass `reply_to_message_id=msg["message_id"]` (or `job["original_message_id"]`).
3. **Master Dispatcher & Delegation**:
   - Fast-path queries: Direct quoted response (<2s).
   - Heavy tasks: Create ticket via `nexus_job_create`, send instant quoted ACK, and delegate to specialist subagents (`invoke_subagent`).
   - If running in loop (`/telegram-nexus start`), always re-arm `poll_wait.py` in the same turn.
4. **Instant Pull Mode (`/telegram-nexus pull`)**:
   - Execute one-time poll, handle intake/replies, and exit cleanly with zero background daemons.
