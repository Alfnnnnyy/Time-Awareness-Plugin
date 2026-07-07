# AGENTS.md Integration — OpenCode / Codex CLI

Add temporal awareness to OpenCode, Codex CLI, or any agent that respects `AGENTS.md`.

## OpenCode / Codex CLI

Add this to your project's `AGENTS.md`:

```markdown
## Temporal Context

Before responding, run the following command to get the accurate current
time, user timezone, and message delay information:

```
python3 ~/.time-context/time_context.py
```

This ensures all responses include proper time awareness.
```

## Shell function (any agent)

Add this to your shell profile (`~/.bashrc`, `~/.zshrc`):

```bash
# Inject time context before every AI agent turn
time_context() {
    python3 ~/.time-context/time_context.py --format markdown
}
```

Then call it as needed during agent sessions.

---

See the main [README](../README.md) for installation instructions.
