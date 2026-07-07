#!/usr/bin/env python3
"""
🕐 Time Context — universal temporal awareness for AI agents.

Zero-dependency Python script. Works with ANY agent:
  Hermes, Claude Code, Codex CLI, OpenCode, Cline, Continue, etc.

Usage:
  python3 time_context.py
  USER_TIMEZONE="Asia/Jayapura" python3 time_context.py
  python3 time_context.py --format markdown
  python3 time_context.py --format json
  python3 time_context.py --timezone Asia/Jayapura

Output:
  A structured temporal context block with server time, user timezone,
  and optional message delay tracking.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time as _time
from datetime import datetime, timezone, timedelta

try:
    import zoneinfo
except ImportError:
    # Python < 3.9 fallback
    try:
        from backports import zoneinfo  # type: ignore
    except ImportError:
        print(
            "zoneinfo not available. Python 3.9+ is recommended.\n"
            "Install backports.zoneinfo: pip install backports.zoneinfo",
            file=sys.stderr,
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_offset(offset_secs: float) -> str:
    """Format a UTC offset in seconds to ±HH:MM."""
    sign = "+" if offset_secs >= 0 else "-"
    total_min = int(abs(offset_secs) // 60)
    hh, mm = divmod(total_min, 60)
    return f"{sign}{hh:02d}:{mm:02d}"


def _format_delay(seconds: float) -> str:
    """Format a duration in seconds into human-friendly string."""
    if seconds < 0:
        return ""
    if seconds < 5:
        return "just now"
    if seconds < 60:
        return f"{seconds:.0f}s ago"
    if seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s ago"
    if seconds < 86400:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m ago"
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    return f"{days}d {hours}h ago"


# ---------------------------------------------------------------------------
# Per-session delay tracking (lightweight, in-memory)
# ---------------------------------------------------------------------------
_session_last_seen: dict[str, float] = {}
_session_file: str | None = None


def _load_session_state():
    """Load session state from disk if a session file is configured."""
    global _session_last_seen
    path = os.environ.get("TIME_CONTEXT_STATE")
    if not path:
        return
    _session_file = path
    try:
        import json as _json
        with open(path) as _f:
            data = _json.load(_f)
        if isinstance(data, dict):
            _session_last_seen = {k: float(v) for k, v in data.items()}
    except (FileNotFoundError, ValueError):
        pass


def _save_session_state():
    """Persist session state to disk."""
    if not _session_file:
        return
    try:
        import json as _json
        with open(_session_file, "w") as _f:
            _json.dump(_session_last_seen, _f)
    except OSError:
        pass


def _get_delay(session_id: str) -> str | None:
    """Calculate delay since last message in a session. Returns None on first message."""
    now = _time.time()
    last = _session_last_seen.get(session_id)
    _session_last_seen[session_id] = now
    if last is None:
        return None
    return _format_delay(now - last)


# ---------------------------------------------------------------------------
# Core context builder
# ---------------------------------------------------------------------------

def build_context(
    *,
    user_timezone: str = "UTC",
    session_id: str | None = None,
    format: str = "plain",  # noqa: A002
) -> str:
    """Build the temporal context block.

    Args:
        user_timezone: IANA timezone name (e.g. "Asia/Jayapura").
        session_id: Optional session identifier for delay tracking.
        format: Output format — "plain", "markdown", or "json".

    Returns:
        Formatted temporal context string.
    """
    now_utc = datetime.now(timezone.utc)

    # Server timezone
    _is_dst = _time.daylight and _time.localtime().tm_isdst
    server_tz_name = _time.tzname[1] if _is_dst else _time.tzname[0]
    server_offset_secs = -(_time.altzone if _is_dst else _time.timezone)
    server_offset_str = _format_offset(server_offset_secs)

    # User timezone
    try:
        user_tz = zoneinfo.ZoneInfo(user_timezone)
        user_now = now_utc.astimezone(user_tz)
        user_offset = user_now.utcoffset()
        user_offset_str = _format_offset(
            user_offset.total_seconds() if user_offset else 0
        )
    except (ValueError, zoneinfo.ZoneInfoNotFoundError):
        user_tz_name = "UTC"
        user_now = now_utc
        user_offset_str = "+00:00"
        user_timezone = user_tz_name
    else:
        user_tz_name = user_timezone

    # Delay
    delay_str = None
    if session_id:
        delay_str = _get_delay(session_id)

    if format == "json":
        data = {
            "utc_time": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "server_timezone": server_tz_name,
            "server_offset": server_offset_str,
            "user_timezone": user_tz_name,
            "user_offset": user_offset_str,
            "user_local_time": user_now.strftime("%Y-%m-%d %H:%M:%S"),
            "message_delay": delay_str,
        }
        return json.dumps(data, indent=2)

    # Build block
    lines = []
    sep = "─" * 52

    if format == "markdown":
        lines.append("## Temporal Context\n")
        lines.append(f"| Field | Value |")
        lines.append(f"|---|---|")
        lines.append(f"| **Server time** | `{now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC` |")
        lines.append(f"| **Server tz** | `{server_tz_name} (UTC{server_offset_str})` |")
        lines.append(f"| **User time** | `{user_now.strftime('%Y-%m-%d %H:%M:%S')}` |")
        lines.append(f"| **User tz** | `{user_tz_name} (UTC{user_offset_str})` |")
        if delay_str:
            lines.append(f"| **Delay** | `{delay_str}` |")
            if delay_str and delay_str.endswith("ago") and not delay_str.endswith("d "):
                lines.append(f"| **Note** | `User is actively chatting (delay <5min)` |")
        return "\n".join(lines)

    # Plain / default
    lines.append(f"{sep}")
    lines.append(f"  Temporal Context")
    lines.append(f"{sep}")
    lines.append(f"  Server time:  {now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append(f"  Server tz:    {server_tz_name} (UTC{server_offset_str})")
    lines.append(f"  User time:    {user_now.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  User tz:      {user_tz_name} (UTC{user_offset_str})")
    if delay_str:
        lines.append(f"  Delay:        {delay_str}")
    lines.append(f"{sep}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="🕐 Time Context — temporal awareness for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  time_context.py\n"
            "  time_context.py --format markdown\n"
            "  time_context.py --format json\n"
            "  time_context.py --timezone Asia/Jayapura\n"
            "  USER_TIMEZONE=Asia/Jakarta time_context.py\n"
            "  time_context.py --session chat-123\n"
        ),
    )
    parser.add_argument(
        "--timezone", "-tz",
        default=os.environ.get("USER_TIMEZONE", "UTC"),
        metavar="TZ",
        help="IANA timezone (default: $USER_TIMEZONE or UTC)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["plain", "markdown", "json"],
        default="plain",
        help="Output format (default: plain)",
    )
    parser.add_argument(
        "--session",
        default=None,
        help="Session identifier for message delay tracking",
    )
    args = parser.parse_args()

    context = build_context(
        user_timezone=args.timezone,
        session_id=args.session,
        format=args.format,
    )
    print(context)


if __name__ == "__main__":
    main()
