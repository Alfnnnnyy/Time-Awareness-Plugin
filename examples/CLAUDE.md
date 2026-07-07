# Claude Code Custom Command — Time Context

This file goes in `~/.claude/commands/time.md` to add a `/time` slash command
that outputs accurate temporal context.

```markdown
---
description: "Show current time, timezone, and message delay"
---

Get accurate temporal context:

    python3 ~/.time-context/time_context.py --format markdown
```

## Usage

1. Save as `~/.claude/commands/time.md`
2. In any Claude Code session, type `/time`
3. Claude will run the command and display the temporal context

## Project CLAUDE.md

Alternatively, add temporal awareness to a specific project by putting
this in your project's `CLAUDE.md`:

```markdown
## Time Context

Before every response, you MUST run:

    python3 ~/.time-context/time_context.py --format markdown

This outputs the current time in the user's timezone and the delay
since the last message. Do not guess the time — use this command.
```
