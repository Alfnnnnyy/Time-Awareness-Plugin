<div align="center">

# 🕐 Time Context

**Accurate temporal awareness for every AI agent turn — server time, user timezone, and message delay, injected automatically.**

<br>

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![Hermes](https://img.shields.io/badge/Hermes-plugin-8A2BE2)](https://hermes-agent.nousresearch.com)
[![Claude Code](https://img.shields.io/badge/Claude_Code-ready-000)](https://docs.anthropic.com/en/docs/claude-code)
[![Codex](https://img.shields.io/badge/Codex-ready-000)](https://codex.openai.com)
[![OpenCode](https://img.shields.io/badge/OpenCode-ready-000)](https://github.com/sst/opencode)

</div>

---

## Overview

Large language models have **no inherent sense of time**. Without external context, they cannot know:

- What time it is right now
- Which timezone the user is in
- Whether the last message arrived 5 seconds or 5 hours ago
- Whether the user is actively chatting or returning to a cold conversation

**Time Context** solves this by injecting a structured temporal block into every turn — so the agent always operates with accurate time awareness.

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

## Supported Agents

| Agent | Integration Method | Status |
|---|---|---|
| **Hermes Agent** | Native plugin (`plugin.yaml` + hook) | ✅ Full |
| **Claude Code** | Shell command via `~/.claude/commands/` | ✅ Supported |
| **OpenCode / Codex CLI** | `AGENTS.md` template + shell script | ✅ Supported |
| **Any AI agent** | Standalone `time_context` CLI script | ✅ Supported |

---

## Quick Start

### 1. Install the script

```bash
# Download and install
curl -fsSL https://raw.githubusercontent.com/Alfnnnnyy/hermes-time-awareness/main/install.sh | bash

# Or manually
mkdir -p ~/.time-context
curl -fsSL https://raw.githubusercontent.com/Alfnnnnyy/hermes-time-awareness/main/time_context.py -o ~/.time-context/time_context.py
chmod +x ~/.time-context/time_context.py
```

### 2. Configure your timezone

```bash
# Set your IANA timezone (default: UTC)
export USER_TIMEZONE="Asia/Jayapura"
```

### 3. Wire it into your agent

<details>
<summary><b>Hermes Agent</b> (click to expand)</summary>

```bash
# Install plugin
mkdir -p ~/.hermes/plugins/time-awareness
cp -r * ~/.hermes/plugins/time-awareness/

# Enable
hermes plugins enable time-awareness
hermes config set plugins.entries.time-awareness.user_timezone "Asia/Jayapura"

# Restart gateway
/restart
```
</details>

<details>
<summary><b>Claude Code</b> (click to expand)</summary>

Add a custom slash command in `~/.claude/commands/`:

**`~/.claude/commands/time-context.json`:**
```json
{
  "name": "time",
  "description": "Inject current time and timezone context",
  "script": {
    "command": "python3",
    "args": ["~/.time-context/time_context.py", "--format", "markdown"]
  }
}
```

Or add to your `CLAUDE.md`:
```markdown
## Time Context
Before responding to time-sensitive queries, run:
```bash
python3 ~/.time-context/time_context.py
```
This outputs the current time, timezone, and message delay context.
```
</details>

<details>
<summary><b>OpenCode / Codex CLI</b> (click to expand)</summary>

Add this to your project's `AGENTS.md`:

```markdown
## Temporal Context
Before each response, the agent SHOULD check the current time by running:
```
python3 ~/.time-context/time_context.py
```

This ensures responses include accurate time, timezone, and delay information.
```

For persistent injection, use a pre-prompt hook or script that runs automatically.
</details>

<details>
<summary><b>Any agent (standalone CLI)</b> (click to expand)</summary>

```bash
# Basic usage
python3 ~/.time-context/time_context.py

# Custom timezone
USER_TIMEZONE="America/New_York" python3 ~/.time-context/time_context.py

# Markdown output (for embedding in responses)
python3 ~/.time-context/time_context.py --format markdown

# JSON output (for programmatic use)
python3 ~/.time-context/time_context.py --format json
```
</details>

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `USER_TIMEZONE` | `"UTC"` | Any IANA timezone (e.g. `"Asia/Jayapura"`, `"America/New_York"`) |

### Hermes Plugin Config

When used as a Hermes plugin, configure via `config.yaml`:

```yaml
plugins:
  enabled:
    - time-awareness
  entries:
    time-awareness:
      user_timezone: "Asia/Jayapura"    # Your IANA timezone
      auto_detect_timezone: false       # (future) auto-detect from platform
      show_delay: true                  # Track message delay between turns
```

---

## Timezone Reference

The plugin supports **all ~600 IANA timezones**. Common examples:

| Location | IANA Timezone | UTC Offset |
|---|---|---|
| Jayapura, Indonesia (WIT) | `Asia/Jayapura` | +09:00 |
| Jakarta, Indonesia (WIB) | `Asia/Jakarta` | +07:00 |
| Makassar, Indonesia (WITA) | `Asia/Makassar` | +08:00 |
| Tokyo, Japan | `Asia/Tokyo` | +09:00 |
| Shanghai / Beijing | `Asia/Shanghai` | +08:00 |
| Singapore | `Asia/Singapore` | +08:00 |
| London, UK | `Europe/London` | +00:00/+01:00 |
| New York, USA | `America/New_York` | -05:00/-04:00 |
| Dubai, UAE | `Asia/Dubai` | +04:00 |
| São Paulo, Brazil | `America/Sao_Paulo` | -03:00/-02:00 |

> **Tip:** Run `python3 -c "import zoneinfo; print(*sorted(zoneinfo.available_timezones()), sep='\\n')"` to see every supported timezone.

---

## Project Structure

```
time-context/
├── README.md               # This file
├── LICENSE                 # MIT License
├── plugin.yaml             # Hermes Agent plugin manifest
├── __init__.py             # Hermes Agent plugin code
├── time_context.py         # Universal standalone CLI script
├── install.sh              # Universal installer
├── examples/
│   ├── CLAUDE.md           # Claude Code integration example
│   └── AGENTS.md           # OpenCode/Codex integration example
```

---

## How It Works

The core logic lives in `time_context.py` — a zero-dependency Python script that:

1. Reads the current UTC time (`datetime.now(timezone.utc)`)
2. Resolves the user's timezone from `USER_TIMEZONE` env var (or falls back to UTC)
3. Calculates the time difference between server and user
4. Tracks per-session message delay via a lightweight in-memory store
5. Outputs a formatted temporal context block

### Hermes Plugin Mode

When loaded as a Hermes plugin, the `pre_llm_call` hook fires automatically before every API call. The temporal context is injected into the **user message** (not the system prompt), preserving prompt cache warmth.

### Standalone CLI Mode

Other agents call `time_context.py` as a subprocess. The script outputs the context block and exits — no server, no daemon, no dependencies.

---

## Requirements

- **Python 3.9+** (uses stdlib `zoneinfo` — no pip packages needed)
- Hermes Agent: any recent version with plugin support (for Hermes mode)
- Everything else: just Python

---

## License

MIT © [Alfnnnnyy](https://github.com/Alfnnnnyy)
