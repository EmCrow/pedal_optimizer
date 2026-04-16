"""Theory and scale data loader for Pedal Architect."""

import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent


def _load_object(filename, fallback):
    path = DATA_DIR / filename
    if not path.exists():
        return fallback
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return payload if isinstance(payload, dict) else fallback


DEFAULT_CAGED_SHAPES = {
    "c": {"label": "C Shape", "minor_start_offset": 5, "major_start_offset": 2, "window_size": 5},
    "a": {"label": "A Shape", "minor_start_offset": 7, "major_start_offset": 4, "window_size": 5},
    "g": {"label": "G Shape", "minor_start_offset": 10, "major_start_offset": 7, "window_size": 5},
    "e": {"label": "E Shape", "minor_start_offset": 0, "major_start_offset": -3, "window_size": 5},
    "d": {"label": "D Shape", "minor_start_offset": 3, "major_start_offset": 0, "window_size": 5},
}

DEFAULT_SCALE_LIBRARY = {
    "minor_pentatonic": {
        "label": "Minor Pentatonic",
        "intervals": [0, 3, 5, 7, 10],
        "formula": "1 b3 4 5 b7",
        "family": "minor",
    },
    "major_pentatonic": {
        "label": "Major Pentatonic",
        "intervals": [0, 2, 4, 7, 9],
        "formula": "1 2 3 5 6",
        "family": "major",
    },
    "minor_blues": {
        "label": "Minor Blues",
        "intervals": [0, 3, 5, 6, 7, 10],
        "formula": "1 b3 4 b5 5 b7",
        "family": "minor",
    },
    "major_scale": {
        "label": "Major Scale (Ionian)",
        "intervals": [0, 2, 4, 5, 7, 9, 11],
        "formula": "1 2 3 4 5 6 7",
        "family": "major",
    },
    "natural_minor": {
        "label": "Natural Minor (Aeolian)",
        "intervals": [0, 2, 3, 5, 7, 8, 10],
        "formula": "1 2 b3 4 5 b6 b7",
        "family": "minor",
    },
    "mixolydian": {
        "label": "Mixolydian",
        "intervals": [0, 2, 4, 5, 7, 9, 10],
        "formula": "1 2 3 4 5 6 b7",
        "family": "major",
    },
}

DEFAULT_RESEARCH_NOTES = {
    "tone_research": [
        "Stacked SD-1 -> DS-1 boosts clarity and tightens low-end saturation in modern high-gain contexts.",
        "Placing GE-7 and EQ10 post-gain often improves final tonal contour control.",
    ],
    "order_research": [
        "Compression before gain usually improves note-to-note consistency.",
        "Delay and looper near chain end preserve modulation/trail clarity.",
    ],
    "theory_research": [
        "Minor pentatonic intervals: 1 b3 4 5 b7.",
        "Major pentatonic intervals: 1 2 3 5 6.",
    ],
}


CAGED_SHAPES = _load_object("caged_shapes.json", DEFAULT_CAGED_SHAPES)
SCALE_LIBRARY = _load_object("scales.json", DEFAULT_SCALE_LIBRARY)
RESEARCH_NOTES = _load_object("research_notes.json", DEFAULT_RESEARCH_NOTES)
