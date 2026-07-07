# Claude Code Integration — Time Context

This project adds temporal awareness to Claude Code.

## Option 1: Custom slash command

Create `~/.claude/commands/time.md`:

```markdown
---
description: "Show current time, timezone, and message delay"
---

Get accurate temporal context:

    python3 ~/.time-context/time_context.py --format markdown
```

Then use `/time` during any Claude Code session.

## Option 2: Project-level CLAUDE.md

Add this to your project's `CLAUDE.md`:

```markdown
## Temporal Awareness

Before responding to any time-sensitive query, run the following to get
accurate current time and timezone context:

```bash
python3 ~/.time-context/time_context.py --format markdown
```

This outputs:

| Field | Value |
|---|---|
| **Server time** | `2026-07-07 12:03:45 UTC` |
| **Server tz** | `CST (UTC+08:00)` |
| **User time** | `2026-07-07 13:03:45` |
| **User tz** | `Asia/Jayapura (UTC+09:00)` |
| **Delay** | `28s ago` |
```

---

See the main [README](../README.md) for installation instructions.
