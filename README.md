# Time Awareness Plugin for Hermes Agent 🕐

Injects **accurate temporal context** into every LLM turn — so the agent always knows the current time, the user's timezone, and how much time has passed since the last message.

## Why?

LLMs have no inherent sense of time. Without this plugin, the model has to guess:

- "What time is it now?" → 🔮 wild guess
- "Did the user message come 5 seconds or 5 hours ago?" → 🤷 no way to know
- "What's the local time for the user?" → 🤔 depends on server TZ

With the plugin, every API call includes a block like:

```
## Temporal Context
Server time:  2026-07-07 12:03:45 UTC
Server tz:    Asia/Shanghai (UTC+08:00)
User time:    2026-07-07 11:03:45
User tz:      Asia/Jakarta (UTC+07:00)
Delay:        28s ago
Note:         User is actively chatting (delay <5min)
```

## Installation

```bash
# Create the plugins directory if it doesn't exist
mkdir -p ~/.hermes/plugins/time-awareness

# Copy plugin files
cp -r * ~/.hermes/plugins/time-awareness/
```

Then enable it in `config.yaml`:

```yaml
plugins:
  enabled:
    - time-awareness
```

Optionally configure timezone and behaviour:

```yaml
plugins:
  enabled:
    - time-awareness
  entries:
    time-awareness:
      user_timezone: "Asia/Jakarta"    # IANA timezone name
      auto_detect_timezone: true       # (future) detect from platform
      show_delay: true                 # Track message delay between turns
```

Restart Hermes (or `/restart` in gateway).

## Configuration

| Key | Default | Description |
|---|---|---|
| `user_timezone` | `"UTC"` | **Any IANA timezone** (e.g. `"Asia/Jayapura"`, `"America/New_York"`, `"Europe/London"`) |
| `auto_detect_timezone` | `false` | Auto-detect from platform metadata (future) |
| `show_delay` | `true` | Show time elapsed since previous message |

## Timezones

The plugin supports **all IANA timezones** — ~600 in total, covering every region in the world. Set yours to whatever matches your location.

Common examples:

| Location | IANA Timezone |
|---|---|
| Jayapura, Indonesia (WIT) | `Asia/Jayapura` |
| Jakarta, Indonesia (WIB) | `Asia/Jakarta` |
| Makassar, Indonesia (WITA) | `Asia/Makassar` |
| Hong Kong / Beijing | `Asia/Shanghai` |
| Tokyo, Japan | `Asia/Tokyo` |
| Singapore | `Asia/Singapore` |
| New York, USA | `America/New_York` |
| London, UK | `Europe/London` |
| Sydney, Australia | `Australia/Sydney` |
| Dubai, UAE | `Asia/Dubai` |
| Moscow, Russia | `Europe/Moscow` |
| São Paulo, Brazil | `America/Sao_Paulo` |

Run `python3 -c "import zoneinfo; print(*sorted(zoneinfo.available_timezones()), sep='\\n')"` to see every supported timezone.

## How It Works

The plugin registers a `pre_llm_call` hook. Hermes fires this hook once per turn, right before the API call. The plugin:

1. Reads the current UTC time (`datetime.now(timezone.utc)`)
2. Resolves the user's timezone from config (or falls back to UTC)
3. Formats both timestamps with timezone info
4. Calculates the delay since the last user message (per-session tracking)
5. Returns the formatted context block

The context block is injected into the **user message** (not the system prompt), so the system prompt cache stays warm.

## Project Structure

```
time-awareness/
├── plugin.yaml        # Plugin manifest
├── __init__.py        # Plugin code (hooks + registration)
└── README.md          # This file
```

## Requirements

- Hermes Agent (any recent version with plugin support)
- Python 3.9+ (for `zoneinfo` — stdlib since 3.9)
- No external dependencies

## License

MIT
