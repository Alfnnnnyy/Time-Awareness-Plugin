<div align="center">

# 🕐 Time Context

**A zero-dependency CLI tool that gives any AI agent accurate time, timezone, and message-delay awareness.**

<br>

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)

</div>

---

## Overview

Large language models have **no inherent sense of time**. Without external context, they cannot know:

- What time it is right now
- Which timezone the user is in
- Whether the last message arrived 5 seconds or 5 hours ago
- Whether the user is actively chatting or returning to a cold conversation

**Time Context** solves this by providing a structured temporal block that any agent can consume:

```
────────────────────────────────────────────────────
  Temporal Context
────────────────────────────────────────────────────
  Server time:  2026-07-07 12:03:45 UTC
  Server tz:    CST (UTC+08:00)
  User time:    2026-07-07 13:03:45
  User tz:      Asia/Jayapura (UTC+09:00)
  Delay:        28s ago
  Note:         User is actively chatting (delay <5min)
────────────────────────────────────────────────────
```

---

## Quick Start

```bash
# 1. Install (zero dependencies — pure Python stdlib)
curl -fsSL https://raw.githubusercontent.com/Alfnnnnyy/Time-Awareness-Plugin/main/time_context.py \
  -o /usr/local/bin/time_context.py && chmod +x /usr/local/bin/time_context.py

# 2. Set your timezone
export USER_TIMEZONE="Asia/Jayapura"

# 3. Run it
python3 /usr/local/bin/time_context.py
```

Output formats:

```bash
time_context.py                          # Plain (default)
time_context.py --format markdown        # Markdown table
time_context.py --format json            # JSON
time_context.py --session chat-123       # With delay tracking
```

---

## Integration

### Any agent — standalone CLI

```bash
# One-shot
python3 /usr/local/bin/time_context.py --format markdown

# Pipe into your prompt
echo "Current time context: $(python3 /usr/local/bin/time_context.py --format json)"
```

### Claude Code

Create `~/.claude/commands/time.md`:

````markdown
---
description: "Show current time, timezone, and message delay"
---

Run this to get accurate temporal context:

```bash
python3 /usr/local/bin/time_context.py --format markdown
```
````

Then use `/time` during any Claude Code session.

### OpenCode / Codex CLI

OpenCode reads `AGENTS.md` from your project root. Codex CLI reads `CLAUDE.md`. Both are plain markdown files that get injected into the agent's system prompt — the agent sees the instructions on every turn.

Create `AGENTS.md` (or `CLAUDE.md`) in your project root:

```markdown
## Temporal Context

Before every response, you MUST run the following command to get the
accurate current time, user timezone, and message delay:

```
python3 ~/.time-context/time_context.py
```

Use this to reference the correct time, adjust for timezone,
and consider whether the user is actively chatting.
```

Or copy the ready-made file:

```bash
curl -fsSL https://raw.githubusercontent.com/Alfnnnnyy/Time-Awareness-Plugin/main/examples/AGENTS.md \
  -o AGENTS.md
```

### Hermes Agent

Install as a native plugin for automatic injection on every turn:

```bash
# Copy plugin files
mkdir -p ~/.hermes/plugins/time-awareness
cp plugin.yaml __init__.py ~/.hermes/plugins/time-awareness/

# Enable
hermes plugins enable time-awareness
hermes config set plugins.entries.time-awareness.user_timezone "Asia/Jayapura"

# Restart Hermes gateway
/restart
```

Once enabled, temporal context is injected automatically — no manual command needed.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `USER_TIMEZONE` | `"UTC"` | Any IANA timezone (e.g. `"Asia/Jayapura"`, `"America/New_York"`) |
| `TIME_CONTEXT_STATE` | `~/.time-context/session_state.json` | Path to session state file for delay tracking |

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

> Run `python3 -c "import zoneinfo; print(*sorted(zoneinfo.available_timezones()), sep='\\n')"` to see them all.

---

## How It Works

`time_context.py` is a single-file, zero-dependency Python script that:

1. Reads the current UTC time (`datetime.now(timezone.utc)`)
2. Resolves the user's timezone from `USER_TIMEZONE` (or falls back to UTC)
3. Calculates the server timezone offset from `time.timezone`
4. Converts UTC to user local time
5. Tracks message delay per session via a JSON file in `~/.time-context/`
6. Outputs the formatted block in your chosen format

### Hermes plugin mode

When loaded as a Hermes plugin, the `pre_llm_call` hook fires automatically before every API call. The temporal context is injected into the **user message** — not the system prompt — so the prompt cache stays warm. Delay tracking uses in-memory state (the plugin runs in a long-lived process).

---

## Project Structure

```
time-context/
├── README.md               # This file
├── LICENSE                 # MIT
├── time_context.py         # ⭐ Universal CLI script (use this)
├── plugin.yaml             # Hermes plugin manifest
├── __init__.py             # Hermes plugin code
├── install.sh              # Interactive installer
└── examples/
    ├── CLAUDE.md           # Claude Code / Codex CLI integration
    └── AGENTS.md           # OpenCode integration
```

> Use `time_context.py` for any agent. The `plugin.yaml` + `__init__.py` are only needed for Hermes native-plugin mode.

---

## Requirements

- **Python 3.9+** (stdlib only — `zoneinfo` built in)
- Nothing else

---

## License

MIT © [Alfnnnnyy](https://github.com/Alfnnnnyy)
