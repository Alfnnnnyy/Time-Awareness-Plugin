<div align="center">

# 🕐 Time Context

**A zero-dependency Python plugin for Hermes Agent that gives your AI accurate time, timezone, and message-delay awareness.**

<br>

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![Hermes](https://img.shields.io/badge/Hermes-plugin-8A2BE2)](https://hermes-agent.nousresearch.com)

</div>

---

## Overview

Large language models have no inherent sense of time. **Time Context** solves this by injecting a structured temporal block on every turn so the model always knows the current time, the user's timezone, and message delay.

```
────────────────────────────────────────────────────
  Temporal Context
────────────────────────────────────────────────────
  Server time:  2026-07-07 12:03:45 UTC
  Server tz:    CST (UTC+08:00)
  User time:    2026-07-07 13:03:45
  User tz:      Asia/Jayapura (UTC+09:00)
  Delay:        28s ago
────────────────────────────────────────────────────
```

---

## Installation

```bash
# Download plugin files
mkdir -p ~/.hermes/plugins/time-awareness
curl -fsSL https://raw.githubusercontent.com/Alfnnnnyy/Time-Awareness-Plugin/main/plugin.yaml \
  -o ~/.hermes/plugins/time-awareness/plugin.yaml
curl -fsSL https://raw.githubusercontent.com/Alfnnnnyy/Time-Awareness-Plugin/main/__init__.py \
  -o ~/.hermes/plugins/time-awareness/__init__.py

# Enable
hermes plugins enable time-awareness
hermes config set plugins.entries.time-awareness.user_timezone "Asia/Jayapura"

# Restart gateway
/restart
```

Once enabled, temporal context is injected automatically on every turn — no manual command needed.

---

## Configuration

| Key | Default | Description |
|---|---|---|
| `user_timezone` | `"UTC"` | Any IANA timezone (e.g. `"Asia/Jayapura"`, `"America/New_York"`) |
| `show_delay` | `true` | Track message delay between turns |

---

## Timezone Reference

Supports **~600 IANA timezones**. Common examples:

| Location | IANA Timezone | Offset |
|---|---|---|
| Jayapura, Indonesia (WIT) | `Asia/Jayapura` | +09:00 |
| Jakarta, Indonesia (WIB) | `Asia/Jakarta` | +07:00 |
| Makassar, Indonesia (WITA) | `Asia/Makassar` | +08:00 |
| Tokyo, Japan | `Asia/Tokyo` | +09:00 |
| Shanghai / Beijing | `Asia/Shanghai` | +08:00 |
| London, UK | `Europe/London` | +00:00/+01:00 |
| New York, USA | `America/New_York` | -05:00/-04:00 |

---

## How It Works

The plugin registers a `pre_llm_call` hook that fires automatically before every API call. It:

1. Reads the current UTC time
2. Resolves the user's timezone from config
3. Converts UTC to user local time
4. Calculates message delay since the last user message
5. Injects the formatted block into the **user message** — not the system prompt — preserving prompt cache warmth.

---

## Project Structure

```
time-awareness/
├── README.md               # This file
├── LICENSE                 # MIT
├── plugin.yaml             # Hermes plugin manifest
├── __init__.py             # Hermes plugin code
└── install.sh              # Installer script
```

---

## Requirements

- **Hermes Agent** (recent version with plugin support)
- **Python 3.9+** (stdlib only — `zoneinfo` built in)
- Nothing else

---

## License

MIT © [Alfnnnnyy](https://github.com/Alfnnnnyy)
