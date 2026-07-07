def _init_session_state(session_id: str | None):
    """Ensure session persistence is wired up.

    Called once from ``main()``.  If ``--session`` was passed without
    ``TIME_CONTEXT_STATE``, picks a default path so delay tracking
    persists across CLI invocations.
    """
    global _session_last_seen, _session_file
    if not session_id:
        return

    # Check env var first — _load_session_state sets _session_file
    # when TIME_CONTEXT_STATE is defined.
    _load_session_state()
    if _session_file is not None:
        return  # env var was set and loaded successfully

    # Default state path when no explicit env var
    default_dir = os.path.join(os.path.expanduser("~"), ".time-context")
    os.makedirs(default_dir, exist_ok=True)
    default_path = os.path.join(default_dir, "session_state.json")
    _session_file = default_path

    # Load existing state from default path
    try:
        import json as _json
        with open(default_path) as _f:
            data = _json.load(_f)
        if isinstance(data, dict):
            _session_last_seen = {k: float(v) for k, v in data.items()}
    except (FileNotFoundError, ValueError):
        pass