# Project Instructions

## Temporal Context

Before every response, you MUST run the following command to get the
accurate current time, user timezone, and message delay:

    python3 ~/.time-context/time_context.py

Use this information to:
- Reference the correct current time in your responses
- Adjust timezone-aware suggestions (e.g., "good morning" vs "good evening")
- Consider whether the user is actively chatting or returning later
- Format timestamps in the user's local timezone

Do NOT guess the current time or timezone — always use the command output.
