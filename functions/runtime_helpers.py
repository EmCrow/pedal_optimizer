"""Runtime formatting and range helpers."""


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def to_clock(percent):
    clamped = clamp(int(round(percent)), 0, 100)
    start_minutes = 7 * 60
    sweep_minutes = 10 * 60
    absolute = int(round(start_minutes + (clamped / 100.0) * sweep_minutes))
    hours = absolute // 60
    minutes = absolute % 60
    if hours > 12:
        hours -= 12
    return f"{hours}:{minutes:02d}"


def quick_knob(value):
    if not isinstance(value, (int, float)):
        value = 50
    safe = clamp(int(round(value)), 0, 100)
    return f"{to_clock(safe)} ({safe}%)"


def db_value(value):
    safe = int(round(value)) if isinstance(value, (int, float)) else 0
    return f"+{safe} dB" if safe > 0 else f"{safe} dB"


def percent_from_db(value, low=-12, high=12):
    safe = clamp(int(round(value if isinstance(value, (int, float)) else 0)), low, high)
    span = max(1, high - low)
    return int(round(((safe - low) / span) * 100))
