"""time-awareness plugin for Hermes Agent.

Injects a ``## Temporal Context`` block into the user message on every API
call so the model always knows the current time, the user's timezone,
and the message delay.

Part of the universal Time Context project — the same temporal awareness
can be wired into Claude Code, Codex CLI, OpenCode, or any AI agent.

Configure your timezone in config.yaml:

    plugins:
      enabled:
        - time-awareness
      entries:
        time-awareness:
          user_timezone: "Asia/Jayapura"
          show_delay: true
"""

from __future__ import annotations

import logging
import time as _time
import threading
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Per-session message timestamp tracking
_session_last_seen: Dict[str, float] = {}
_session_lock = threading.Lock()


def _get_plugin_config(key: str, default: Any = None) -> Any:
    """Read a config value from ``plugins.entries.time-awareness.*``."""
    try:
        from hermes_cli.config import load_config
        cfg = load_config() or {}
        entries = (cfg.get("plugins") or {}).get("entries") or {}
        entry = entries.get("time-awareness") or {}
        return entry.get(key, default)
    except Exception:
        return default


def _detect_user_timezone(
    platform: str,
    sender_id: str,
    fallback: str = "UTC",
) -> str:
    """Detect or resolve the user's IANA timezone.

    Resolution order:
      1. Explicit ``user_timezone`` in config.yaml
      2. Auto-detect from gateway platform metadata (future)
      3. Fallback to ``UTC``
    """
    explicit = _get_plugin_config("user_timezone")
    if explicit and isinstance(explicit, str) and explicit.strip():
        return explicit.strip()

    auto = _get_plugin_config("auto_detect_timezone")
    if auto:
        logger.info(
            "Auto-detect requested for %s/%s, but no platform timezone "
            "source is wired yet. Falling back to UTC.",
            platform, sender_id,
        )

    return fallback


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


def _on_pre_llm_call(
    session_id: str = "",
    task_id: str = "",
    turn_id: str = "",
    user_message: str = "",
    conversation_history: list | None = None,
    is_first_turn: bool = False,
    model: str = "",
    platform: str = "",
    sender_id: str = "",
    **_: Any,
) -> str:
    """Build and inject temporal context into the user message."""
    now_utc = datetime.now(timezone.utc)

    # Server timezone
    import zoneinfo
    _is_dst = _time.daylight and _time.localtime().tm_isdst
    server_tz_name = _time.tzname[1] if _is_dst else _time.tzname[0]
    server_offset_secs = -(_time.altzone if _is_dst else _time.timezone)
    server_offset_str = _format_offset(server_offset_secs)

    # User timezone
    user_tz_name = _detect_user_timezone(platform, sender_id)
    try:
        user_tz = zoneinfo.ZoneInfo(user_tz_name)
        user_now = now_utc.astimezone(user_tz)
        user_offset = user_now.utcoffset()
        user_offset_str = _format_offset(
            user_offset.total_seconds() if user_offset else 0
        )
    except Exception:
        user_tz_name = "UTC"
        user_now = now_utc
        user_offset_str = "+00:00"

    # Build the context block
    lines: list[str] = []
    lines.append(f"Server time:  {now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append(f"Server tz:    {server_tz_name} (UTC{server_offset_str})")
    lines.append(f"User time:    {user_now.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"User tz:      {user_tz_name} (UTC{user_offset_str})")

    # Message delay tracking
    show_delay = _get_plugin_config("show_delay", True)
    if show_delay and session_id:
        now_ts = _time.time()
        with _session_lock:
            last_ts = _session_last_seen.get(session_id, None)
            _session_last_seen[session_id] = now_ts
        if last_ts is not None:
            delay = now_ts - last_ts
            delay_str = _format_delay(delay)
            lines.append(f"Delay:        {delay_str}")
            if delay < 300:
                lines.append("Note:         User is actively chatting (delay <5min)")

    return "## Temporal Context\n" + "\n".join(lines)


def register(ctx) -> None:
    """Register the time-awareness hooks."""
    ctx.register_hook("pre_llm_call", _on_pre_llm_call)
    logger.info("time-awareness plugin loaded")
