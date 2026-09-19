# 🌐 Telegram Nexus: Sovereign Mobile C2 Gateway & Dispatch Firewall

[![OpenSSF Scorecard](https://img.shields.io/badge/OpenSSF-Hardened-10B981?style=for-the-badge&logo=shield)](SECURITY.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-00F0FF?style=for-the-badge)](LICENSE)
[![Zero Daemon](https://img.shields.io/badge/Runtime-0_MB_Idle_RAM-F59E0B?style=for-the-badge)](mcp/server.py)
[![Antigravity Plugin](https://img.shields.io/badge/Google_Antigravity-Plugin-4285F4?style=for-the-badge&logo=google)](plugin.json)

> **Sovereign Telegram Automation Nexus, Mobile Command & Control (C2) Gateway, and Asynchronous Dispatch Firewall for Google Antigravity.**

---

## ⚡ 5-Second Architectural Hook

```text
┌─────────────────────────────────────────────────────────────┐
│ 🏛️ TELEGRAM NEXUS DUAL-CHAMBER ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   [ Karan on Blaze 5G ]          [ Portfolio Visitor ]      │
│            ▲                               ▲                │
│            │ (Private C2)                  │ (Inquiry Form) │
│            ▼                               ▼                │
│     ┌─────────────────────────────────────────────┐         │
│     │    @YourNexusBot (Telegram Cloud API)       │         │
│     └─────────────────────────────────────────────┘         │
│                            ▲                                │
│                            │ (Zero-Daemon HTTPS REST)       │
│                            ▼                                │
│     ┌─────────────────────────────────────────────┐         │
│     │  antigravity-telegram-nexus-plugin (MCP)    │         │
│     │  • Zero-Daemon (0 MB Idle RAM)              │         │
│     │  • Quarantined Config in ~/.gemini/config/  │         │
│     └─────────────────────────────────────────────┘         │
│                            ▲                                │
│                            │ (stdio JSON-RPC)               │
│                            ▼                                │
│     ┌─────────────────────────────────────────────┐         │
│     │  Motobook Developer Workstation             │         │
│     │  • Auto-append to Spark.md                  │         │
│     │  • Real-time Build / CI Incident Pager      │         │
│     │  • campaigns.sqlite Daily Strike HUD        │         │
│     └─────────────────────────────────────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
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
    "C:\\Users\\karan\\.gemini\\config\\plugins\\telegram-nexus-plugin\\mcp\\server.py"
  ],
  "disabled": false
}
```

### 3. Bind Sovereign Ownership
1. Send `/start` to your newly created bot on Telegram.
2. The bot automatically binds your private Telegram Chat ID as the **Sovereign Owner**.
3. All future voice/text notes will be routed to your local `~/.gemini/Spark.md`, and alerts will be delivered directly to your phone.

---

## 🛠️ MCP Tool Suite

| Tool Name | Scope & Function | Payload Parameters |
| :--- | :--- | :--- |
| `nexus_get_status` | Check bot connectivity, health, and owner binding | None |
| `nexus_configure` | Set bot token or owner chat ID in isolated config | `bot_token`, `owner_chat_id` |
| `nexus_send_alert` | Send high-priority alert or report to Karan's phone | `message`, `parse_mode` |
| `nexus_poll_updates` | Poll unread messages and public visitor inquiries | `limit` (default: 20) |
| `nexus_ingest_spark` | Ingest unhandled owner thoughts into `Spark.md` | None |
| `nexus_get_audit_log` | Query immutable audit log of all bot actions and events | `limit`, `event_type` |
| `nexus_reply_visitor` | Forward reply to a portfolio visitor through the bot | `visitor_chat_id`, `message` |

---

## 🔒 Security & OpenSSF Hardening

- **Zero Path Leaks**: All user directory references utilize dynamic environment expansion (`~`, `%USERPROFILE%`).
- **Zero Token Commits**: Tokens are quarantined in `~/.gemini/config/telegram_config.json`, which is excluded from git tracking via `.gitignore`.
- **Dual-Chamber Isolation**: Outside visitors can never trigger administrative system commands or view Karan's private phone number.
- **SHA Action Pinning**: GitHub Actions in `.github/workflows/` are pinned to immutable commit SHAs.

---

## 📜 License

MIT License © 2026 Karan Singh Verma.
