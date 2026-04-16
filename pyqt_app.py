#!/usr/bin/env python3
"""Pedal Architect desktop app (PyQt5).

Branch: py_app
"""

import copy
import itertools
import json
import math
import re
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets


PEDAL_LIBRARY = {
    "cs3": "BOSS CS-3",
    "sd1": "BOSS SD-1",
    "bd2": "BOSS BD-2",
    "ds1": "BOSS DS-1",
    "ge7": "BOSS GE-7",
    "eq10": "10-Band EQ",
    "ch1": "BOSS CH-1",
    "dd3": "BOSS DD-3",
    "rc30": "BOSS RC-30",
}

BANK_ORDER = ["cs3", "sd1", "bd2", "ds1", "ge7", "eq10", "ch1", "dd3", "rc30"]
DEFAULT_CHAIN = ["sd1", "ds1", "ge7", "eq10", "rc30"]

GENRE_PRESETS = {
    "metal": {
        "label": "Metal",
        "optimized_chain": ["cs3", "sd1", "ds1", "ge7", "eq10", "dd3", "rc30"],
        "amp": {"gain": 70, "bass": 58, "mid": 40, "treble": 63, "presence": 62, "master": 56},
        "pedals": {
            "cs3": {"level": 62, "tone": 46, "attack": 64, "sustain": 58},
            "sd1": {"drive": 16, "tone": 61, "level": 82},
            "bd2": {"gain": 24, "tone": 52, "level": 54},
            "ds1": {"dist": 73, "tone": 57, "level": 58},
            "ge7": {"mode": "Post-drive shape", "level": 2, "bands": {"100": -4, "200": -2, "400": 0, "800": 2, "1.6k": 1, "3.2k": 3, "6.4k": 2}},
            "eq10": {"mode": "Post-drive sculpt", "volume": 4, "gain": 2, "bands": {"31.25": -4, "62.5": -2, "125": 3, "250": 1, "500": -3, "1k": -1, "2k": 3, "4k": 4, "8k": 1, "16k": -2}},
            "ch1": {"effectLevel": 24, "eq": 55, "rate": 24, "depth": 28},
            "dd3": {"eLevel": 34, "fBack": 22, "dTime": 36, "mode": "320 ms"},
            "rc30": {"rhythmType": "Rock 1", "rhythmLevel": 16, "track1": 70, "track2": 66, "quantize": "On"},
        },
        "notes": [
            "Use SD-1 as a front boost to tighten palm-muted riffs.",
            "Stack GE-7 or 10-band EQ after distortion for modern cut and control.",
        ],
    },
    "rock": {
        "label": "Rock",
        "optimized_chain": ["cs3", "sd1", "bd2", "ds1", "ge7", "eq10", "dd3", "rc30"],
        "amp": {"gain": 62, "bass": 55, "mid": 57, "treble": 58, "presence": 56, "master": 60},
        "pedals": {
            "cs3": {"level": 58, "tone": 49, "attack": 54, "sustain": 49},
            "sd1": {"drive": 30, "tone": 55, "level": 66},
            "bd2": {"gain": 42, "tone": 54, "level": 61},
            "ds1": {"dist": 50, "tone": 57, "level": 59},
            "ge7": {"mode": "Post-drive shape", "level": 1, "bands": {"100": -2, "200": 0, "400": 1, "800": 2, "1.6k": 2, "3.2k": 1, "6.4k": 0}},
            "eq10": {"mode": "Post-drive sculpt", "volume": 2, "gain": 1, "bands": {"31.25": -3, "62.5": -1, "125": 1, "250": 2, "500": 2, "1k": 2, "2k": 1, "4k": 1, "8k": 0, "16k": -1}},
            "ch1": {"effectLevel": 33, "eq": 54, "rate": 36, "depth": 44},
            "dd3": {"eLevel": 36, "fBack": 28, "dTime": 42, "mode": "400 ms"},
            "rc30": {"rhythmType": "Rock 2", "rhythmLevel": 18, "track1": 72, "track2": 68, "quantize": "On"},
        },
        "notes": [
            "Balanced mids help guitars sit in a full-band mix.",
            "Blend BD-2 and DS-1 for rhythm crunch plus lead sustain.",
        ],
    },
    "classic-rock": {
        "label": "Classic Rock",
        "optimized_chain": ["cs3", "bd2", "sd1", "ge7", "dd3", "rc30", "ch1"],
        "amp": {"gain": 55, "bass": 56, "mid": 60, "treble": 55, "presence": 54, "master": 62},
        "pedals": {
            "cs3": {"level": 56, "tone": 48, "attack": 50, "sustain": 47},
            "sd1": {"drive": 40, "tone": 53, "level": 62},
            "bd2": {"gain": 48, "tone": 51, "level": 63},
            "ds1": {"dist": 38, "tone": 50, "level": 56},
            "ge7": {"mode": "Pre-drive focus", "level": 1, "bands": {"100": -3, "200": -1, "400": 2, "800": 3, "1.6k": 2, "3.2k": 0, "6.4k": -1}},
            "eq10": {"mode": "Pre-drive push", "volume": 1, "gain": 0, "bands": {"31.25": -5, "62.5": -2, "125": 1, "250": 1, "500": 3, "1k": 2, "2k": 1, "4k": 0, "8k": -1, "16k": -3}},
            "ch1": {"effectLevel": 30, "eq": 52, "rate": 30, "depth": 38},
            "dd3": {"eLevel": 32, "fBack": 24, "dTime": 40, "mode": "300 ms"},
            "rc30": {"rhythmType": "Shuffle", "rhythmLevel": 14, "track1": 74, "track2": 68, "quantize": "On"},
        },
        "notes": [
            "Classic tones favor mids and moderate gain over heavy saturation.",
            "Use GE-7 in front for a focused solo push without harsh highs.",
        ],
    },
    "pop": {
        "label": "Pop",
        "optimized_chain": ["cs3", "sd1", "ch1", "ge7", "dd3", "rc30"],
        "amp": {"gain": 42, "bass": 50, "mid": 52, "treble": 63, "presence": 60, "master": 64},
        "pedals": {
            "cs3": {"level": 61, "tone": 54, "attack": 52, "sustain": 42},
            "sd1": {"drive": 16, "tone": 57, "level": 60},
            "bd2": {"gain": 28, "tone": 56, "level": 56},
            "ds1": {"dist": 30, "tone": 60, "level": 50},
            "ge7": {"mode": "Post-drive shape", "level": 1, "bands": {"100": -4, "200": -2, "400": 0, "800": 1, "1.6k": 2, "3.2k": 2, "6.4k": 1}},
            "eq10": {"mode": "Post-drive sculpt", "volume": 2, "gain": 0, "bands": {"31.25": -6, "62.5": -3, "125": -1, "250": 0, "500": 1, "1k": 1, "2k": 2, "4k": 3, "8k": 2, "16k": 0}},
            "ch1": {"effectLevel": 46, "eq": 57, "rate": 42, "depth": 52},
            "dd3": {"eLevel": 40, "fBack": 30, "dTime": 48, "mode": "450 ms"},
            "rc30": {"rhythmType": "Pop", "rhythmLevel": 21, "track1": 72, "track2": 70, "quantize": "On"},
        },
        "notes": [
            "Pop guitar is cleaner with controlled lows and polished upper mids.",
            "CH-1 plus DD-3 after gain gives width and movement without mud.",
        ],
    },
    "country": {
        "label": "Country",
        "optimized_chain": ["cs3", "sd1", "ch1", "ge7", "dd3", "rc30"],
        "amp": {"gain": 36, "bass": 48, "mid": 54, "treble": 66, "presence": 65, "master": 65},
        "pedals": {
            "cs3": {"level": 63, "tone": 57, "attack": 58, "sustain": 44},
            "sd1": {"drive": 14, "tone": 61, "level": 58},
            "bd2": {"gain": 22, "tone": 57, "level": 55},
            "ds1": {"dist": 20, "tone": 56, "level": 47},
            "ge7": {"mode": "Post-drive shape", "level": 2, "bands": {"100": -5, "200": -3, "400": -1, "800": 1, "1.6k": 2, "3.2k": 3, "6.4k": 1}},
            "eq10": {"mode": "Post-drive sculpt", "volume": 1, "gain": 0, "bands": {"31.25": -8, "62.5": -5, "125": -2, "250": -1, "500": 1, "1k": 2, "2k": 3, "4k": 2, "8k": 1, "16k": -1}},
            "ch1": {"effectLevel": 34, "eq": 56, "rate": 35, "depth": 40},
            "dd3": {"eLevel": 28, "fBack": 18, "dTime": 34, "mode": "220 ms"},
            "rc30": {"rhythmType": "Country", "rhythmLevel": 17, "track1": 74, "track2": 69, "quantize": "On"},
        },
        "notes": [
            "Lower gain and a bright top end preserve pick articulation.",
            "Compression first and moderate delay add classic country bounce.",
        ],
    },
    "hip-hop": {
        "label": "Hip Hop",
        "optimized_chain": ["cs3", "ge7", "eq10", "dd3", "rc30"],
        "amp": {"gain": 30, "bass": 72, "mid": 44, "treble": 48, "presence": 44, "master": 64},
        "pedals": {
            "cs3": {"level": 66, "tone": 45, "attack": 58, "sustain": 54},
            "sd1": {"drive": 8, "tone": 45, "level": 50},
            "bd2": {"gain": 14, "tone": 46, "level": 50},
            "ds1": {"dist": 16, "tone": 42, "level": 48},
            "ge7": {"mode": "Low-end pocket", "level": 3, "bands": {"100": 6, "200": 4, "400": 1, "800": -2, "1.6k": -1, "3.2k": 1, "6.4k": 0}},
            "eq10": {"mode": "Sub + body sculpt", "volume": 3, "gain": 0, "bands": {"31.25": 8, "62.5": 6, "125": 4, "250": 2, "500": 0, "1k": -2, "2k": -1, "4k": 1, "8k": 0, "16k": -2}},
            "ch1": {"effectLevel": 18, "eq": 48, "rate": 20, "depth": 22},
            "dd3": {"eLevel": 24, "fBack": 18, "dTime": 46, "mode": "480 ms"},
            "rc30": {"rhythmType": "Hip Hop", "rhythmLevel": 20, "track1": 74, "track2": 72, "quantize": "On"},
        },
        "notes": [
            "Hip Hop mode emphasizes low-end pocket while keeping rhythmic guitar lines clear.",
            "GE-7 and 10-band are tuned for body-first bass support with controlled top articulation.",
        ],
    },
    "blues": {
        "label": "Blues",
        "optimized_chain": ["cs3", "bd2", "sd1", "ge7", "dd3", "rc30"],
        "amp": {"gain": 49, "bass": 55, "mid": 62, "treble": 53, "presence": 50, "master": 61},
        "pedals": {
            "cs3": {"level": 57, "tone": 47, "attack": 49, "sustain": 52},
            "sd1": {"drive": 36, "tone": 50, "level": 64},
            "bd2": {"gain": 46, "tone": 49, "level": 64},
            "ds1": {"dist": 28, "tone": 45, "level": 53},
            "ge7": {"mode": "Pre-drive focus", "level": 2, "bands": {"100": -4, "200": -1, "400": 2, "800": 3, "1.6k": 2, "3.2k": 0, "6.4k": -2}},
            "eq10": {"mode": "Pre-drive push", "volume": 2, "gain": 1, "bands": {"31.25": -6, "62.5": -3, "125": 0, "250": 2, "500": 3, "1k": 2, "2k": 1, "4k": -1, "8k": -2, "16k": -4}},
            "ch1": {"effectLevel": 22, "eq": 50, "rate": 22, "depth": 28},
            "dd3": {"eLevel": 30, "fBack": 20, "dTime": 32, "mode": "260 ms"},
            "rc30": {"rhythmType": "Blues", "rhythmLevel": 13, "track1": 73, "track2": 67, "quantize": "On"},
        },
        "notes": [
            "Mids drive the vocal character of blues leads.",
            "BD-2 plus SD-1 gives touch-responsive breakup with extra sustain.",
        ],
    },
}

AMP_MODELS = {
    "orange_rockerverb_mk3": {
        "label": "Orange Rockerverb MKIII",
        "short_label": "Orange RV",
        "type": "electric",
        "base": {"gain": 74, "bass": 58, "mid": 56, "treble": 60, "presence": 58, "master": 56},
        "genre_offsets": {
            "metal": {"gain": 8, "bass": 3, "mid": -5, "treble": 2, "presence": 2, "master": -1},
            "rock": {"gain": 2, "bass": 1, "mid": 0, "treble": 1, "presence": 1, "master": 0},
            "classic-rock": {"gain": -6, "bass": 0, "mid": 2, "treble": -1, "presence": -1, "master": 1},
            "pop": {"gain": -12, "bass": -2, "mid": 1, "treble": 2, "presence": 1, "master": 2},
            "country": {"gain": -15, "bass": -3, "mid": 2, "treble": 3, "presence": 2, "master": 2},
            "hip-hop": {"gain": -18, "bass": 5, "mid": -3, "treble": -3, "presence": -4, "master": 2},
            "blues": {"gain": -8, "bass": 0, "mid": 3, "treble": -1, "presence": -1, "master": 1},
        },
        "note": "Orange profile adds thick mids with a chewy upper-mid attack.",
    },
    "marshall_jcm800_2203": {
        "label": "Marshall JCM800 2203",
        "short_label": "JCM800",
        "type": "electric",
        "base": {"gain": 68, "bass": 54, "mid": 62, "treble": 58, "presence": 57, "master": 58},
        "genre_offsets": {
            "metal": {"gain": 4, "bass": 2, "mid": -4, "treble": 2, "presence": 2, "master": -1},
            "rock": {"gain": 1, "bass": 1, "mid": 1, "treble": 1, "presence": 1, "master": 0},
            "classic-rock": {"gain": -5, "bass": 0, "mid": 3, "treble": -1, "presence": -2, "master": 2},
            "pop": {"gain": -12, "bass": -2, "mid": 0, "treble": 2, "presence": 1, "master": 2},
            "country": {"gain": -14, "bass": -3, "mid": 1, "treble": 3, "presence": 2, "master": 3},
            "hip-hop": {"gain": -18, "bass": 4, "mid": -2, "treble": -3, "presence": -4, "master": 2},
            "blues": {"gain": -8, "bass": 0, "mid": 3, "treble": -1, "presence": -1, "master": 2},
        },
        "note": "Marshall profile emphasizes mids and harmonic bite for classic to hard rock.",
    },
    "fender_acoustic_100": {
        "label": "Fender Acoustic 100",
        "short_label": "Acoustic 100",
        "type": "acoustic",
        "base": {"gain": 34, "bass": 45, "mid": 56, "treble": 64, "presence": 62, "master": 62},
        "genre_offsets": {
            "metal": {"gain": -8, "bass": -2, "mid": 2, "treble": 2, "presence": 2, "master": 0},
            "rock": {"gain": -4, "bass": -1, "mid": 1, "treble": 1, "presence": 1, "master": 0},
            "classic-rock": {"gain": -6, "bass": -1, "mid": 2, "treble": 0, "presence": 0, "master": 1},
            "pop": {"gain": -2, "bass": -1, "mid": 0, "treble": 2, "presence": 2, "master": 1},
            "country": {"gain": -3, "bass": -2, "mid": 1, "treble": 3, "presence": 3, "master": 1},
            "hip-hop": {"gain": -6, "bass": 5, "mid": -2, "treble": -1, "presence": -2, "master": 2},
            "blues": {"gain": -4, "bass": 0, "mid": 2, "treble": 0, "presence": 0, "master": 1},
        },
        "note": "Fender Acoustic profile keeps low end controlled and top end clear for piezo pickups.",
    },
    "fender_twin_reverb": {
        "label": "Fender Twin Reverb",
        "short_label": "Twin Reverb",
        "type": "electric",
        "base": {"gain": 40, "bass": 53, "mid": 49, "treble": 66, "presence": 62, "master": 65},
        "genre_offsets": {
            "metal": {"gain": 8, "bass": 1, "mid": -4, "treble": 0, "presence": 1, "master": -2},
            "rock": {"gain": 4, "bass": 0, "mid": 1, "treble": -1, "presence": 0, "master": 0},
            "classic-rock": {"gain": 2, "bass": 0, "mid": 2, "treble": -2, "presence": -1, "master": 1},
            "pop": {"gain": -2, "bass": -1, "mid": 0, "treble": 1, "presence": 1, "master": 1},
            "country": {"gain": -3, "bass": -2, "mid": 0, "treble": 2, "presence": 2, "master": 1},
            "hip-hop": {"gain": -8, "bass": 6, "mid": -3, "treble": -2, "presence": -3, "master": 2},
            "blues": {"gain": 0, "bass": 0, "mid": 2, "treble": -2, "presence": -2, "master": 1},
        },
        "note": "Twin Reverb profile provides clean headroom and bright articulation.",
    },
    "vox_ac30": {
        "label": "Vox AC30",
        "short_label": "Vox AC30",
        "type": "electric",
        "base": {"gain": 56, "bass": 49, "mid": 57, "treble": 64, "presence": 61, "master": 60},
        "genre_offsets": {
            "metal": {"gain": 2, "bass": 1, "mid": -3, "treble": 1, "presence": 1, "master": -1},
            "rock": {"gain": 1, "bass": 0, "mid": 1, "treble": 0, "presence": 1, "master": 0},
            "classic-rock": {"gain": -3, "bass": 0, "mid": 2, "treble": -1, "presence": -1, "master": 1},
            "pop": {"gain": -6, "bass": -1, "mid": 0, "treble": 1, "presence": 1, "master": 1},
            "country": {"gain": -8, "bass": -2, "mid": 1, "treble": 2, "presence": 2, "master": 1},
            "hip-hop": {"gain": -14, "bass": 4, "mid": -2, "treble": -3, "presence": -3, "master": 2},
            "blues": {"gain": -5, "bass": 0, "mid": 2, "treble": -1, "presence": -1, "master": 1},
        },
        "note": "AC30 profile adds upper-mid chime and lively attack.",
    },
    "mesa_dual_rectifier": {
        "label": "Mesa/Boogie Dual Rectifier",
        "short_label": "Dual Rectifier",
        "type": "electric",
        "base": {"gain": 78, "bass": 62, "mid": 44, "treble": 61, "presence": 60, "master": 54},
        "genre_offsets": {
            "metal": {"gain": 6, "bass": 3, "mid": -4, "treble": 2, "presence": 2, "master": -1},
            "rock": {"gain": -6, "bass": 0, "mid": 2, "treble": 0, "presence": 0, "master": 1},
            "classic-rock": {"gain": -14, "bass": -1, "mid": 4, "treble": -1, "presence": -2, "master": 2},
            "pop": {"gain": -18, "bass": -3, "mid": 2, "treble": 1, "presence": 1, "master": 2},
            "country": {"gain": -24, "bass": -4, "mid": 2, "treble": 2, "presence": 2, "master": 2},
            "hip-hop": {"gain": -20, "bass": 6, "mid": -4, "treble": -3, "presence": -4, "master": 2},
            "blues": {"gain": -15, "bass": -1, "mid": 4, "treble": -1, "presence": -2, "master": 2},
        },
        "note": "Rectifier profile brings modern low-end weight with aggressive high-gain response.",
    },
}

AUTO_AMP_BY_GENRE = {
    "electric": {
        "metal": "mesa_dual_rectifier",
        "rock": "marshall_jcm800_2203",
        "classic-rock": "marshall_jcm800_2203",
        "pop": "fender_twin_reverb",
        "country": "fender_twin_reverb",
        "hip-hop": "fender_twin_reverb",
        "blues": "vox_ac30",
    },
    "acoustic": {
        "metal": "fender_acoustic_100",
        "rock": "fender_acoustic_100",
        "classic-rock": "fender_acoustic_100",
        "pop": "fender_acoustic_100",
        "country": "fender_acoustic_100",
        "hip-hop": "fender_acoustic_100",
        "blues": "fender_acoustic_100",
    },
}

GUITAR_PROFILES = {
    "taylor_acoustic": {
        "label": "Taylor Acoustic (ES2 Bass/Treble)",
        "type": "acoustic",
        "controls": "bass_treble",
        "volume_advice": "Set guitar volume by ear just below feedback threshold.",
        "note": "Taylor profile trims low boom and adds top-end presence for live clarity.",
        "genres": {
            "metal": {"bass": 44, "treble": 56},
            "rock": {"bass": 47, "treble": 58},
            "classic-rock": {"bass": 49, "treble": 54},
            "pop": {"bass": 46, "treble": 61},
            "country": {"bass": 43, "treble": 64},
            "hip-hop": {"bass": 57, "treble": 48},
            "blues": {"bass": 51, "treble": 52},
        },
    },
    "electric_2_knob_toggle": {
        "label": "Electric 2 Knob + Toggle (Master Vol/Tone)",
        "type": "electric",
        "controls": "master_volume_tone_toggle",
        "note": "2-knob layout keeps pickup switching fast and predictable.",
        "genres": {
            "metal": {"volume": 93, "tone": 58, "toggle": "Bridge"},
            "rock": {"volume": 89, "tone": 56, "toggle": "Bridge"},
            "classic-rock": {"volume": 84, "tone": 51, "toggle": "Middle"},
            "pop": {"volume": 82, "tone": 58, "toggle": "Middle"},
            "country": {"volume": 87, "tone": 64, "toggle": "Bridge"},
            "hip-hop": {"volume": 85, "tone": 47, "toggle": "Middle"},
            "blues": {"volume": 80, "tone": 48, "toggle": "Neck"},
        },
    },
    "electric_4_knob_toggle": {
        "label": "Electric 4 Knob + Toggle (2V/2T)",
        "type": "electric",
        "controls": "dual_volume_tone_toggle",
        "note": "4-knob layout gives independent neck/bridge blend control.",
        "genres": {
            "metal": {"neckVolume": 62, "neckTone": 47, "bridgeVolume": 93, "bridgeTone": 61, "toggle": "Bridge"},
            "rock": {"neckVolume": 72, "neckTone": 52, "bridgeVolume": 88, "bridgeTone": 57, "toggle": "Bridge"},
            "classic-rock": {"neckVolume": 80, "neckTone": 56, "bridgeVolume": 84, "bridgeTone": 53, "toggle": "Middle"},
            "pop": {"neckVolume": 76, "neckTone": 56, "bridgeVolume": 80, "bridgeTone": 58, "toggle": "Middle"},
            "country": {"neckVolume": 66, "neckTone": 52, "bridgeVolume": 86, "bridgeTone": 64, "toggle": "Bridge"},
            "hip-hop": {"neckVolume": 82, "neckTone": 50, "bridgeVolume": 79, "bridgeTone": 52, "toggle": "Middle"},
            "blues": {"neckVolume": 87, "neckTone": 54, "bridgeVolume": 74, "bridgeTone": 49, "toggle": "Neck"},
        },
    },
}

AUTO_GUITAR_PROFILE_BY_TYPE = {
    "electric": "electric_2_knob_toggle",
    "acoustic": "taylor_acoustic",
}

STYLE_PLAYBOOK = {
    "metal": {
        "concertProgression": ["Am - F - C - G", "Am - G - F - G"],
        "capo5Shapes": ["Em - C - G - D", "Em - D - C - D"],
        "openShapes": ["Em", "C", "G", "D", "Am"],
        "capoGuide": "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
        "pentatonicFret": "G-shape minor pentatonic root area at the 8th fret (relative to nut).",
        "soloGuide": "Work the 8th-10th fret pocket with aggressive bends and short repeating motifs.",
    },
    "rock": {
        "concertProgression": ["C - G - Am - F", "D - G - A - G"],
        "capo5Shapes": ["G - D - Em - C", "A - D - E - D"],
        "openShapes": ["G", "D", "Em", "C", "A", "E"],
        "capoGuide": "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
        "pentatonicFret": "G-shape minor pentatonic root area at the 8th fret.",
        "soloGuide": "Target chord tones from the 8th-fret G-shape box and resolve on downbeats.",
    },
    "classic-rock": {
        "concertProgression": ["D - G - A - G", "C - F - G - F"],
        "capo5Shapes": ["A - D - E - D", "G - C - D - C"],
        "openShapes": ["A", "D", "E", "G", "C"],
        "capoGuide": "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
        "pentatonicFret": "G-shape minor pentatonic root area around the 8th fret.",
        "soloGuide": "Use 8th-fret box bends and vibrato for vintage lead phrasing.",
    },
    "pop": {
        "concertProgression": ["C - G - Am - F", "F - C - Dm - Bbmaj7"],
        "capo5Shapes": ["G - D - Em - C", "C - G - Am - Fmaj7"],
        "openShapes": ["C", "G", "Am", "Fmaj7", "D", "Em", "Cadd9"],
        "capoGuide": "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
        "pentatonicFret": "G-shape major/minor pentatonic pocket centered near fret 8.",
        "soloGuide": "Keep melodies in the 8th-fret box short, hooky, and rhythm-aware.",
    },
    "country": {
        "concertProgression": ["C - F - G - C", "G - C - D - G"],
        "capo5Shapes": ["G - C - D - G", "D - G - A - D"],
        "openShapes": ["G", "C", "D", "A", "Em"],
        "capoGuide": "Exact mapping: concert C-F-G becomes G-C-D shapes with capo on fret 5.",
        "pentatonicFret": "G-shape pentatonic home position at the 8th fret.",
        "soloGuide": "Use 8th-fret double-stops, quick slides, and bends into chord tones.",
    },
    "hip-hop": {
        "concertProgression": ["Am7 - Fmaj7 - C - Gsus2", "Dm7 - C - Bbmaj7 - Am7"],
        "capo5Shapes": ["Em7 - Cmaj7 - G - Dsus2", "Am7 - G - Fmaj7 - Em7"],
        "openShapes": ["Em7", "Cmaj7", "G", "Dsus2", "Am7", "Fmaj7"],
        "capoGuide": "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
        "pentatonicFret": "G-shape minor pentatonic around fret 8 (A-minor feel with capo 5).",
        "soloGuide": "Use sparse 8th-fret pocket phrases, rhythmic rests, and short slides.",
    },
    "blues": {
        "concertProgression": ["A7 - D7 - E7 - D7", "D7 - G7 - A7 - G7"],
        "capo5Shapes": ["E7 - A7 - B7 - A7", "A7 - D7 - E7 - D7"],
        "openShapes": ["E7", "A7", "B7", "D7", "G"],
        "capoGuide": "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
        "pentatonicFret": "G-shape minor pentatonic around the 8th fret with blue-note passing tones.",
        "soloGuide": "Target roots and b5 color tones in the 8th-fret box on turnarounds.",
    },
}

CIRCLE_FIFTHS_MAJOR = ["C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F"]
CIRCLE_FIFTHS_MINOR = ["Am", "Em", "Bm", "F#m", "C#m", "G#m", "Ebm", "Bbm", "Fm", "Cm", "Gm", "Dm"]
NASHVILLE_MAJOR_CHART = [
    ("C", ["C", "Dm", "Em", "F", "G", "Am", "Bdim"]),
    ("G", ["G", "Am", "Bm", "C", "D", "Em", "F#dim"]),
    ("D", ["D", "Em", "F#m", "G", "A", "Bm", "C#dim"]),
    ("A", ["A", "Bm", "C#m", "D", "E", "F#m", "G#dim"]),
    ("E", ["E", "F#m", "G#m", "A", "B", "C#m", "D#dim"]),
    ("B", ["B", "C#m", "D#m", "E", "F#", "G#m", "A#dim"]),
    ("F#", ["F#", "G#m", "A#m", "B", "C#", "D#m", "Fdim"]),
    ("Db", ["Db", "Ebm", "Fm", "Gb", "Ab", "Bbm", "Cdim"]),
    ("Ab", ["Ab", "Bbm", "Cm", "Db", "Eb", "Fm", "Gdim"]),
    ("Eb", ["Eb", "Fm", "Gm", "Ab", "Bb", "Cm", "Ddim"]),
    ("Bb", ["Bb", "Cm", "Dm", "Eb", "F", "Gm", "Adim"]),
    ("F", ["F", "Gm", "Am", "Bb", "C", "Dm", "Edim"]),
]
NOTE_ALIAS_MAP = {
    "CB": "B",
    "B#": "C",
    "DB": "Db",
    "C#": "Db",
    "D#": "Eb",
    "EB": "Eb",
    "E#": "F",
    "FB": "E",
    "F#": "F#",
    "GB": "F#",
    "G#": "Ab",
    "AB": "Ab",
    "A#": "Bb",
    "BB": "Bb",
}
CHORD_ROOT_RE = re.compile(r"^\s*([A-Ga-g])([#b]?)")

ORDER_NOTE_PATTERNS = {
    "cs3": ["cs-3", "cs3", "compress"],
    "sd1": ["sd-1", "sd1", "overdrive"],
    "bd2": ["bd-2", "bd2", "blues driver"],
    "ds1": ["ds-1", "ds1", "distortion"],
    "ge7": ["ge-7", "ge7"],
    "eq10": ["10-band", "10 band", "eq10", "10 channel"],
    "ch1": ["ch-1", "ch1", "chorus"],
    "dd3": ["dd-3", "dd3", "delay"],
    "rc30": ["rc-30", "rc30", "loop"],
}

STATE_FILE = Path(".pedal_architect_py_state.json")
PEDAL_MIME_TYPE = "application/x-pedal-architect-pedal-id"
PEDAL_SOURCE_MIME_TYPE = "application/x-pedal-architect-source"
AMP_NODE_ID = "__amp__"
GUITAR_NODE_ID = "__guitar__"
FONT_PRESET_SPECS = [
    ("small", "Small", 12),
    ("medium", "Medium", 14),
    ("large", "Large", 16),
    ("xl", "XL", 19),
]
FONT_PRESETS = {key: {"label": label, "px": px} for key, label, px in FONT_PRESET_SPECS}
THEME_PRESET_SPECS = [
    ("dark", "Dark"),
    ("light", "Light"),
    ("sunset", "Sunset"),
    ("ocean", "Ocean"),
]
THEMES = {
    "dark": {
        "bg": "#11161a",
        "text": "#e9efe4",
        "frame": "#3a464e",
        "panel": "#161f25",
        "tab": "#1d252b",
        "tab_selected_bg": "#d6fd73",
        "tab_selected_fg": "#1a230f",
        "group_title": "#d6e2cb",
        "canvas_bg": "#0f1418",
        "canvas_grid": "#202b33",
        "canvas_edge": "#86c7ff",
        "canvas_edge_preview": "#86c7ff",
        "amp_bg": "#232f38",
        "amp_fg": "#f3f8f0",
    },
    "light": {
        "bg": "#f5f6f8",
        "text": "#21252b",
        "frame": "#c0c7d1",
        "panel": "#ffffff",
        "tab": "#e7ebf0",
        "tab_selected_bg": "#2f6feb",
        "tab_selected_fg": "#ffffff",
        "group_title": "#253347",
        "canvas_bg": "#edf1f6",
        "canvas_grid": "#d0d8e4",
        "canvas_edge": "#1f6feb",
        "canvas_edge_preview": "#1f6feb",
        "amp_bg": "#d7e1ec",
        "amp_fg": "#1f2f42",
    },
    "sunset": {
        "bg": "#2a1d22",
        "text": "#f7e8da",
        "frame": "#7f4a53",
        "panel": "#3a262d",
        "tab": "#4a3038",
        "tab_selected_bg": "#ffb347",
        "tab_selected_fg": "#3a2523",
        "group_title": "#ffcf97",
        "canvas_bg": "#2e1d24",
        "canvas_grid": "#5d3943",
        "canvas_edge": "#ffd166",
        "canvas_edge_preview": "#ffd166",
        "amp_bg": "#5a3031",
        "amp_fg": "#ffe9c4",
    },
    "ocean": {
        "bg": "#0f2430",
        "text": "#def1f6",
        "frame": "#2f6172",
        "panel": "#123544",
        "tab": "#164454",
        "tab_selected_bg": "#2ad4c5",
        "tab_selected_fg": "#0f2831",
        "group_title": "#a5e8df",
        "canvas_bg": "#0d2a36",
        "canvas_grid": "#235062",
        "canvas_edge": "#6ee7ff",
        "canvas_edge_preview": "#6ee7ff",
        "amp_bg": "#1c4a5a",
        "amp_fg": "#ddfbff",
    },
}
PEDAL_COLORS = {
    "cs3": "#67bfe8",
    "sd1": "#e7cc38",
    "bd2": "#2f86d0",
    "ds1": "#ec7f21",
    "ge7": "#abb2bc",
    "eq10": "#4289c0",
    "ch1": "#34a8df",
    "dd3": "#38c5bc",
    "rc30": "#c93c39",
}
PEDAL_TEXT_COLORS = {
    "rc30": "#fff7f7",
}
GE7_BANDS = ["100", "200", "400", "800", "1.6k", "3.2k", "6.4k"]
EQ10_BANDS = ["31.25", "62.5", "125", "250", "500", "1k", "2k", "4k", "8k", "16k"]
AMP_BRAND_COLORS = {
    "orange_rockerverb_mk3": {"bg": "#f28c28", "fg": "#fff7ea"},
    "marshall_jcm800_2203": {"bg": "#1d1c1a", "fg": "#f2d28b"},
    "fender_acoustic_100": {"bg": "#c49b5e", "fg": "#2b2015"},
    "fender_twin_reverb": {"bg": "#12171d", "fg": "#dbe9f7"},
    "vox_ac30": {"bg": "#7b5a34", "fg": "#efe0bf"},
    "mesa_dual_rectifier": {"bg": "#2c1c20", "fg": "#f5d9df"},
}


class PedalBankListWidget(QtWidgets.QListWidget):
    chainPedalReturned = QtCore.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._drag_start_pos = QtCore.QPoint()
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDragDropOverwriteMode(False)
        self.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def startDrag(self, _supported_actions):
        item = self.currentItem()
        if not item:
            return
        pedal_id = item.data(QtCore.Qt.UserRole)
        if not pedal_id:
            return

        drag = QtGui.QDrag(self)
        mime = QtCore.QMimeData()
        mime.setData(PEDAL_MIME_TYPE, pedal_id.encode("utf-8"))
        mime.setData(PEDAL_SOURCE_MIME_TYPE, b"bank")
        mime.setText(PEDAL_LIBRARY.get(pedal_id, ""))
        drag.setMimeData(mime)
        drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction, QtCore.Qt.CopyAction)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & QtCore.Qt.LeftButton):
            super().mouseMoveEvent(event)
            return
        if (event.pos() - self._drag_start_pos).manhattanLength() < QtWidgets.QApplication.startDragDistance():
            super().mouseMoveEvent(event)
            return
        item = self.itemAt(self._drag_start_pos)
        if item:
            self.setCurrentItem(item)
        self.startDrag(QtCore.Qt.CopyAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(PEDAL_MIME_TYPE):
            event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(PEDAL_MIME_TYPE):
            event.acceptProposedAction()
            return
        super().dragMoveEvent(event)

    def dropEvent(self, event):
        if not event.mimeData().hasFormat(PEDAL_MIME_TYPE):
            super().dropEvent(event)
            return
        source = bytes(event.mimeData().data(PEDAL_SOURCE_MIME_TYPE)).decode("utf-8").strip() if event.mimeData().hasFormat(PEDAL_SOURCE_MIME_TYPE) else ""
        if source == "chain":
            pedal_id = bytes(event.mimeData().data(PEDAL_MIME_TYPE)).decode("utf-8").strip()
            if pedal_id:
                self.chainPedalReturned.emit(pedal_id)
            event.acceptProposedAction()
            return
        event.ignore()


class ChainListWidget(QtWidgets.QListWidget):
    pedalDropped = QtCore.pyqtSignal(str, int, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._drag_start_pos = QtCore.QPoint()
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.viewport().setAcceptDrops(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDragDropOverwriteMode(False)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def startDrag(self, _supported_actions):
        item = self.currentItem()
        if not item:
            return
        pedal_id = item.data(QtCore.Qt.UserRole)
        if not pedal_id:
            return
        drag = QtGui.QDrag(self)
        mime = QtCore.QMimeData()
        mime.setData(PEDAL_MIME_TYPE, pedal_id.encode("utf-8"))
        mime.setData(PEDAL_SOURCE_MIME_TYPE, b"chain")
        mime.setText(PEDAL_LIBRARY.get(pedal_id, ""))
        drag.setMimeData(mime)
        drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction, QtCore.Qt.MoveAction)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & QtCore.Qt.LeftButton):
            super().mouseMoveEvent(event)
            return
        if (event.pos() - self._drag_start_pos).manhattanLength() < QtWidgets.QApplication.startDragDistance():
            super().mouseMoveEvent(event)
            return
        item = self.itemAt(self._drag_start_pos)
        if item:
            self.setCurrentItem(item)
            self.startDrag(QtCore.Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(PEDAL_MIME_TYPE):
            event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(PEDAL_MIME_TYPE):
            event.acceptProposedAction()
            return
        super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasFormat(PEDAL_MIME_TYPE):
            pedal_id = bytes(event.mimeData().data(PEDAL_MIME_TYPE)).decode("utf-8").strip()
            source = bytes(event.mimeData().data(PEDAL_SOURCE_MIME_TYPE)).decode("utf-8").strip() if event.mimeData().hasFormat(PEDAL_SOURCE_MIME_TYPE) else "bank"
            if pedal_id:
                row = self.indexAt(event.pos()).row()
                if row < 0:
                    row = self.count()
                self.pedalDropped.emit(pedal_id, row, source or "bank")
            event.acceptProposedAction()
            return
        super().dropEvent(event)


class PedalCanvasWidget(QtWidgets.QWidget):
    pedalDropped = QtCore.pyqtSignal(str, QtCore.QPoint, str)
    pedalMoved = QtCore.pyqtSignal(str, QtCore.QPoint)
    connectionCreated = QtCore.pyqtSignal(str, str)
    pedalDoubleClicked = QtCore.pyqtSignal(str)
    pedalRemoveRequested = QtCore.pyqtSignal(str)
    pedalDisconnectRequested = QtCore.pyqtSignal(str, str)

    PEDAL_SIZE = QtCore.QSize(84, 124)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumSize(430, 320)
        self.setMouseTracking(True)
        self.pedal_ids = []
        self.pedal_positions = {}
        self.connections = []
        self.knob_map = {}
        self.amp_label = "AMP"
        self.amp_model_key = ""
        self.guitar_type = "electric"
        self.guitar_profile_key = "electric_2_knob_toggle"
        self.theme = THEMES["dark"]
        self.dragging_pedal = None
        self.drag_offset = QtCore.QPoint()
        self.link_start = None
        self.preview_link_to = None
        self.guitar_pixmaps = {}
        self.load_guitar_pixmaps()

    def load_guitar_pixmaps(self):
        guitar_dir = Path(__file__).resolve().parent / "assets" / "guitars"
        mapping = {
            "taylor_acoustic": "taylor_cutout_trim.png",
            "electric_2_knob_toggle": "strat_cutout_trim.png",
            "electric_4_knob_toggle": "les_paul_cutout_trim.png",
        }
        for key, filename in mapping.items():
            path = guitar_dir / filename
            pixmap = QtGui.QPixmap(str(path))
            if not pixmap.isNull():
                self.guitar_pixmaps[key] = pixmap

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def set_board_data(
        self,
        pedal_ids,
        positions,
        connections,
        amp_label,
        amp_model_key="",
        guitar_type="electric",
        guitar_profile_key="electric_2_knob_toggle",
        knob_map=None,
    ):
        self.pedal_ids = list(pedal_ids)
        clean_positions = {}
        for pedal_id in self.pedal_ids:
            raw = positions.get(pedal_id, [18, 18])
            clean_positions[pedal_id] = self.clamp_pedal_position(QtCore.QPoint(int(raw[0]), int(raw[1])))
        self.pedal_positions = clean_positions
        self.connections = list(connections)
        self.amp_label = amp_label or "AMP"
        self.amp_model_key = amp_model_key or ""
        self.guitar_type = guitar_type or "electric"
        self.guitar_profile_key = guitar_profile_key or "electric_2_knob_toggle"
        self.knob_map = dict(knob_map or {})
        self.update()

    def amp_rect(self):
        width = 178
        height = 180
        x = 18
        y = max(16, self.height() - height - 16)
        return QtCore.QRect(x, y, width, height)

    def guitar_rect(self):
        width = 160
        height = 230
        x = max(16, self.width() - width - 22)
        y = max(16, self.height() - height - 16)
        if y < 14:
            height = max(146, self.height() - 34)
            y = 14
        return QtCore.QRect(x, y, width, height)

    def pedal_lane_bounds(self):
        left = self.amp_rect().right() + 20
        right = self.guitar_rect().left() - 20
        return left, right

    def pedal_position_bounds(self):
        min_x = 14
        max_x = max(min_x, self.width() - self.PEDAL_SIZE.width() - 14)
        min_y = 14
        max_y = max(min_y, self.height() - self.PEDAL_SIZE.height() - 14)
        return min_x, max_x, min_y, max_y

    def reserved_pedal_exclusion_rects(self):
        return [
            self.amp_rect().adjusted(-10, -10, 10, 10),
            self.guitar_rect().adjusted(-10, -10, 10, 10),
        ]

    def can_place_pedal_at(self, point):
        min_x, max_x, min_y, max_y = self.pedal_position_bounds()
        if point.x() < min_x or point.x() > max_x or point.y() < min_y or point.y() > max_y:
            return False
        rect = QtCore.QRect(point, self.PEDAL_SIZE)
        for reserved in self.reserved_pedal_exclusion_rects():
            if rect.intersects(reserved):
                return False
        return True

    def find_nearest_open_pedal_position(self, desired):
        min_x, max_x, min_y, max_y = self.pedal_position_bounds()
        clamped = QtCore.QPoint(clamp(desired.x(), min_x, max_x), clamp(desired.y(), min_y, max_y))
        if self.can_place_pedal_at(clamped):
            return clamped

        candidate_points = []
        gap = 10
        for reserved in self.reserved_pedal_exclusion_rects():
            candidate_points.extend(
                [
                    QtCore.QPoint(reserved.left() - self.PEDAL_SIZE.width() - gap, clamped.y()),
                    QtCore.QPoint(reserved.right() + gap, clamped.y()),
                    QtCore.QPoint(clamped.x(), reserved.top() - self.PEDAL_SIZE.height() - gap),
                    QtCore.QPoint(clamped.x(), reserved.bottom() + gap),
                ]
            )

        dedupe = set()
        normalized = []
        for raw in candidate_points:
            cand = QtCore.QPoint(clamp(raw.x(), min_x, max_x), clamp(raw.y(), min_y, max_y))
            key = (cand.x(), cand.y())
            if key in dedupe:
                continue
            dedupe.add(key)
            normalized.append(cand)
        normalized.sort(key=lambda pt: abs(pt.x() - clamped.x()) + abs(pt.y() - clamped.y()))
        for cand in normalized:
            if self.can_place_pedal_at(cand):
                return cand

        step = 14
        max_radius = max(self.width(), self.height())
        seen = {(clamped.x(), clamped.y())}
        for radius in range(step, max_radius + step, step):
            for offset in range(-radius, radius + 1, step):
                ring_points = [
                    QtCore.QPoint(clamped.x() + offset, clamped.y() - radius),
                    QtCore.QPoint(clamped.x() + offset, clamped.y() + radius),
                    QtCore.QPoint(clamped.x() - radius, clamped.y() + offset),
                    QtCore.QPoint(clamped.x() + radius, clamped.y() + offset),
                ]
                for raw in ring_points:
                    cand = QtCore.QPoint(clamp(raw.x(), min_x, max_x), clamp(raw.y(), min_y, max_y))
                    key = (cand.x(), cand.y())
                    if key in seen:
                        continue
                    seen.add(key)
                    if self.can_place_pedal_at(cand):
                        return cand
        return clamped

    def amp_input_pos(self):
        rect = self.amp_rect()
        return QtCore.QPoint(rect.right(), rect.center().y())

    def guitar_output_pos(self):
        rect = self.guitar_rect()
        return QtCore.QPoint(rect.left(), rect.center().y() + max(10, rect.height() // 6))

    def pedal_rect(self, pedal_id):
        position = self.pedal_positions.get(pedal_id, QtCore.QPoint(16, 16))
        return QtCore.QRect(position, self.PEDAL_SIZE)

    def pedal_input_pos(self, pedal_id):
        rect = self.pedal_rect(pedal_id)
        return QtCore.QPoint(rect.right(), rect.center().y())

    def pedal_output_pos(self, pedal_id):
        rect = self.pedal_rect(pedal_id)
        return QtCore.QPoint(rect.left(), rect.center().y())

    def pedal_remove_button_rect(self, pedal_id):
        rect = self.pedal_rect(pedal_id)
        return QtCore.QRect(rect.right() - 17, rect.top() + 4, 13, 13)

    def pedal_disconnect_button_rect(self, pedal_id, side):
        rect = self.pedal_rect(pedal_id)
        if side == "output":
            return QtCore.QRect(rect.left() + 1, rect.center().y() - 15, 14, 14)
        return QtCore.QRect(rect.right() - 15, rect.center().y() - 15, 14, 14)

    def clamp_pedal_position(self, point):
        min_x, max_x, min_y, max_y = self.pedal_position_bounds()
        desired = QtCore.QPoint(clamp(point.x(), min_x, max_x), clamp(point.y(), min_y, max_y))
        if self.can_place_pedal_at(desired):
            return desired
        return self.find_nearest_open_pedal_position(desired)

    def pedal_at(self, point):
        for pedal_id in reversed(self.pedal_ids):
            if self.pedal_rect(pedal_id).contains(point):
                return pedal_id
        return None

    def jack_hit(self, point, center, radius=10):
        dx = point.x() - center.x()
        dy = point.y() - center.y()
        return (dx * dx + dy * dy) <= (radius * radius)

    def find_output_source(self, point):
        if self.jack_hit(point, self.guitar_output_pos(), 13):
            return GUITAR_NODE_ID
        for pedal_id in reversed(self.pedal_ids):
            if self.jack_hit(point, self.pedal_output_pos(pedal_id), 11):
                return pedal_id
        return None

    def find_input_target(self, point):
        if self.jack_hit(point, self.amp_input_pos(), 14):
            return AMP_NODE_ID
        for pedal_id in reversed(self.pedal_ids):
            if self.jack_hit(point, self.pedal_input_pos(pedal_id), 11):
                return pedal_id
        return None

    def draw_link(self, painter, start, end, color, width=3, dashed=False):
        path = QtGui.QPainterPath()
        path.moveTo(start)
        delta = max(32, abs(end.x() - start.x()) // 2)
        if start.x() >= end.x():
            c1 = QtCore.QPoint(start.x() - delta, start.y())
            c2 = QtCore.QPoint(end.x() + delta, end.y())
        else:
            c1 = QtCore.QPoint(start.x() + delta, start.y())
            c2 = QtCore.QPoint(end.x() - delta, end.y())
        path.cubicTo(c1, c2, end)
        pen = QtGui.QPen(QtGui.QColor(color), width, QtCore.Qt.DashLine if dashed else QtCore.Qt.SolidLine)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(path)

    def knob_angle(self, value_percent):
        value = clamp(int(round(value_percent if isinstance(value_percent, (int, float)) else 50)), 0, 100)
        absolute_minutes = int(round(7 * 60 + (value / 100.0) * (10 * 60))) % (12 * 60)
        return 90 - (absolute_minutes * 0.5)

    def draw_knob(self, painter, center, value_percent):
        value = clamp(int(round(value_percent if isinstance(value_percent, (int, float)) else 50)), 0, 100)
        knob_rect = QtCore.QRectF(center.x() - 8, center.y() - 8, 16, 16)
        knob_fill = QtGui.QRadialGradient(knob_rect.center(), 8.5)
        knob_fill.setColorAt(0.0, QtGui.QColor("#f9fbff"))
        knob_fill.setColorAt(0.55, QtGui.QColor("#e5ebf3"))
        knob_fill.setColorAt(1.0, QtGui.QColor("#b9c4d2"))
        painter.setPen(QtGui.QPen(QtGui.QColor("#1a2027"), 1.2))
        painter.setBrush(QtGui.QBrush(knob_fill))
        painter.drawEllipse(knob_rect)
        angle_deg = self.knob_angle(value)
        rad = math.radians(angle_deg)
        tip = QtCore.QPoint(
            int(round(center.x() + math.cos(rad) * 7.1)),
            int(round(center.y() - math.sin(rad) * 7.1)),
        )
        painter.setPen(QtGui.QPen(QtGui.QColor("#d42027"), 2.4, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        painter.drawLine(center, tip)
        marker = QtCore.QPointF(
            center.x() + math.cos(rad) * 4.8,
            center.y() - math.sin(rad) * 4.8,
        )
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#ffffff")))
        painter.drawEllipse(marker, 1.9, 1.9)

    def draw_slider_lever(self, painter, track_rect, value_percent, handle_color="#f7f9fc"):
        value = clamp(int(round(value_percent if isinstance(value_percent, (int, float)) else 50)), 0, 100)
        track_fill = QtGui.QLinearGradient(track_rect.topLeft(), track_rect.bottomLeft())
        track_fill.setColorAt(0.0, QtGui.QColor(24, 28, 34, 205))
        track_fill.setColorAt(1.0, QtGui.QColor(9, 12, 15, 210))
        painter.setPen(QtGui.QPen(QtGui.QColor("#0f151c"), 1))
        painter.setBrush(QtGui.QBrush(track_fill))
        painter.drawRoundedRect(track_rect, 2, 2)
        travel = max(1, track_rect.height() - 6)
        y = track_rect.bottom() - int(round((value / 100.0) * travel)) - 3
        handle = QtCore.QRect(track_rect.left() - 2, y, track_rect.width() + 4, 6)
        handle_fill = QtGui.QLinearGradient(handle.topLeft(), handle.bottomLeft())
        handle_fill.setColorAt(0.0, QtGui.QColor("#ffffff"))
        handle_fill.setColorAt(1.0, QtGui.QColor(handle_color))
        painter.setPen(QtGui.QPen(QtGui.QColor("#1c232c"), 1))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(handle_color)))
        painter.setBrush(QtGui.QBrush(handle_fill))
        painter.drawRoundedRect(handle, 2, 2)
        painter.setPen(QtGui.QPen(QtGui.QColor("#d42027"), 1.4))
        painter.drawLine(handle.left() + 1, handle.center().y(), handle.right() - 1, handle.center().y())

    def normalized_face_values(self, pedal_id):
        raw = self.knob_map.get(pedal_id, {})
        if isinstance(raw, (list, tuple)):
            return {"knobs": list(raw)}
        if isinstance(raw, dict):
            return raw
        return {}

    def draw_eq_pedal_face(self, painter, rect, pedal_id, face_values):
        if pedal_id == "ge7":
            slider_values = list(face_values.get("sliders", [50] * len(GE7_BANDS)))
            while len(slider_values) < len(GE7_BANDS):
                slider_values.append(50)
            slider_values.append(face_values.get("level", 50))
            track_count = len(slider_values)
            track_width = 7
            gap = 2
            total_width = track_count * track_width + (track_count - 1) * gap
            if total_width > rect.width() - 8:
                track_width = max(5, (rect.width() - 8 - (track_count - 1) * gap) // track_count)
                total_width = track_count * track_width + (track_count - 1) * gap
            start_x = rect.left() + (rect.width() - total_width) // 2
            top = rect.top() + 36
            track_height = 46
            for idx, value in enumerate(slider_values):
                x = start_x + idx * (track_width + gap)
                self.draw_slider_lever(painter, QtCore.QRect(x, top, track_width, track_height), value, "#f6f8fb")
            painter.setPen(QtGui.QColor("#10141b"))
            font = painter.font()
            font.setPointSize(max(5, font.pointSize() - 3))
            painter.setFont(font)
            level_label_rect = QtCore.QRect(rect.left() + 4, rect.bottom() - 24, rect.width() - 8, 14)
            painter.drawText(level_label_rect, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter, "LVL")
            return

        if pedal_id == "eq10":
            slider_values = list(face_values.get("sliders", [50] * len(EQ10_BANDS)))
            while len(slider_values) < len(EQ10_BANDS):
                slider_values.append(50)
            track_count = len(slider_values)
            track_width = 5
            gap = 1
            total_width = track_count * track_width + (track_count - 1) * gap
            if total_width > rect.width() - 8:
                track_width = max(4, (rect.width() - 8 - (track_count - 1) * gap) // track_count)
                total_width = track_count * track_width + (track_count - 1) * gap
            start_x = rect.left() + (rect.width() - total_width) // 2
            top = rect.top() + 38
            track_height = 44
            for idx, value in enumerate(slider_values):
                x = start_x + idx * (track_width + gap)
                self.draw_slider_lever(painter, QtCore.QRect(x, top, track_width, track_height), value, "#f5f8fd")
            out_rect = QtCore.QRect(rect.left() + 7, rect.top() + 24, 8, 14)
            gain_rect = QtCore.QRect(rect.right() - 15, rect.top() + 24, 8, 14)
            self.draw_slider_lever(painter, out_rect, face_values.get("output", 50), "#f4f7fb")
            self.draw_slider_lever(painter, gain_rect, face_values.get("gain", 50), "#f4f7fb")
            painter.setPen(QtGui.QColor("#0f1d2a"))
            font = painter.font()
            font.setPointSize(max(5, font.pointSize() - 3))
            painter.setFont(font)
            painter.drawText(rect.adjusted(2, 22, -2, -2), QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop, "OUT")
            painter.drawText(rect.adjusted(2, 22, -2, -2), QtCore.Qt.AlignRight | QtCore.Qt.AlignTop, "GAIN")

    def guitar_pixmap(self):
        if self.guitar_type == "acoustic":
            return self.guitar_pixmaps.get("taylor_acoustic")
        if self.guitar_profile_key in self.guitar_pixmaps:
            return self.guitar_pixmaps[self.guitar_profile_key]
        return self.guitar_pixmaps.get("electric_2_knob_toggle")

    def amp_brand_style(self):
        return AMP_BRAND_COLORS.get(self.amp_model_key, {"bg": self.theme["amp_bg"], "fg": self.theme["amp_fg"]})

    def paintEvent(self, _event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.fillRect(self.rect(), QtGui.QColor(self.theme["canvas_bg"]))

        grid_pen = QtGui.QPen(QtGui.QColor(self.theme["canvas_grid"]), 1)
        grid_pen.setCosmetic(True)
        painter.setPen(grid_pen)
        step = 24
        for x in range(0, self.width(), step):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), step):
            painter.drawLine(0, y, self.width(), y)

        guitar_rect = self.guitar_rect()
        painter.setPen(QtGui.QPen(QtGui.QColor(self.theme["frame"]), 2))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.theme["panel"])))
        painter.drawRoundedRect(guitar_rect.adjusted(-3, -3, 3, 3), 10, 10)
        pixmap = self.guitar_pixmap()
        if pixmap and not pixmap.isNull():
            scaled = pixmap.scaled(guitar_rect.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            x = guitar_rect.left() + (guitar_rect.width() - scaled.width()) // 2
            y = guitar_rect.top() + (guitar_rect.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        painter.setPen(QtGui.QColor(self.theme["text"]))
        gfont = painter.font()
        gfont.setBold(True)
        gfont.setPointSize(max(7, gfont.pointSize() - 1))
        painter.setFont(gfont)
        painter.drawText(guitar_rect.adjusted(4, 4, -4, -4), QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter, "Guitar")
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#f6f9ff")))
        painter.drawEllipse(self.guitar_output_pos(), 6, 6)

        amp_rect = self.amp_rect()
        amp_style = self.amp_brand_style()
        painter.setPen(QtGui.QPen(QtGui.QColor(self.theme["frame"]), 2))
        amp_fill = QtGui.QLinearGradient(amp_rect.topLeft(), amp_rect.bottomLeft())
        amp_fill.setColorAt(0.0, QtGui.QColor(amp_style["bg"]).lighter(118))
        amp_fill.setColorAt(1.0, QtGui.QColor(amp_style["bg"]).darker(122))
        painter.setBrush(QtGui.QBrush(amp_fill))
        painter.drawRoundedRect(amp_rect, 13, 13)
        control_strip = QtCore.QRect(amp_rect.left() + 12, amp_rect.top() + 30, amp_rect.width() - 24, 16)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 80), 1))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(18, 22, 28, 170)))
        painter.drawRoundedRect(control_strip, 5, 5)
        for idx in range(6):
            cx = control_strip.left() + 10 + idx * ((control_strip.width() - 20) // 5)
            painter.setPen(QtGui.QPen(QtGui.QColor("#11161d"), 1))
            painter.setBrush(QtGui.QBrush(QtGui.QColor("#d8dde4")))
            painter.drawEllipse(QtCore.QPoint(cx, control_strip.center().y()), 3, 3)
        painter.setPen(QtGui.QColor(amp_style["fg"]))
        amp_font = painter.font()
        amp_font.setBold(True)
        amp_font.setPointSize(max(8, amp_font.pointSize()))
        painter.setFont(amp_font)
        painter.drawText(amp_rect.adjusted(8, 10, -8, -10), QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter, self.amp_label)
        grill = amp_rect.adjusted(14, 54, -14, -14)
        painter.setPen(QtGui.QPen(QtGui.QColor("#1f2429"), 2))
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#2d333a")))
        painter.drawRoundedRect(grill, 8, 8)
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 24), 1))
        for x in range(grill.left() + 4, grill.right(), 6):
            painter.drawLine(x, grill.top() + 2, x, grill.bottom() - 2)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 38), 1))
        for y in range(grill.top() + 4, grill.bottom(), 6):
            painter.drawLine(grill.left() + 2, y, grill.right() - 2, y)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#edf2fb")))
        painter.drawEllipse(self.amp_input_pos(), 7, 7)

        for src, dst in self.connections:
            if src != GUITAR_NODE_ID and src not in self.pedal_ids:
                continue
            if dst != AMP_NODE_ID and dst not in self.pedal_ids:
                continue
            start = self.guitar_output_pos() if src == GUITAR_NODE_ID else self.pedal_output_pos(src)
            end = self.amp_input_pos() if dst == AMP_NODE_ID else self.pedal_input_pos(dst)
            self.draw_link(painter, start, end, self.theme["canvas_edge"], width=3)

        if self.link_start and self.preview_link_to:
            start = self.guitar_output_pos() if self.link_start == GUITAR_NODE_ID else self.pedal_output_pos(self.link_start)
            self.draw_link(
                painter,
                start,
                self.preview_link_to,
                self.theme["canvas_edge_preview"],
                width=2,
                dashed=True,
            )

        for pedal_id in self.pedal_ids:
            rect = self.pedal_rect(pedal_id)
            base = QtGui.QColor(PEDAL_COLORS.get(pedal_id, "#b0b0b0"))
            shade = base.darker(122)
            painter.setPen(QtGui.QPen(QtGui.QColor(self.theme["frame"]), 2))
            gradient = QtGui.QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0.0, base.lighter(124))
            gradient.setColorAt(0.58, base)
            gradient.setColorAt(1.0, shade)
            painter.setBrush(QtGui.QBrush(gradient))
            painter.drawRoundedRect(rect, 10, 10)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 52), 1))
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 9, 9)
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 34), 1))
            painter.drawLine(rect.left() + 10, rect.bottom() - 4, rect.right() - 10, rect.bottom() - 4)

            painter.setPen(QtGui.QColor(PEDAL_TEXT_COLORS.get(pedal_id, "#11171f")))
            tfont = painter.font()
            tfont.setBold(True)
            tfont.setPointSize(max(6, tfont.pointSize() - 2))
            painter.setFont(tfont)
            title = PEDAL_LIBRARY[pedal_id].replace("BOSS ", "")
            painter.drawText(rect.adjusted(4, 5, -4, -4), QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter, title)
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 40), 1))
            painter.drawLine(rect.left() + 8, rect.top() + 20, rect.right() - 8, rect.top() + 20)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(60, 66, 74, 140)))
            painter.drawEllipse(QtCore.QPoint(rect.left() + 11, rect.top() + 11), 1, 1)
            painter.drawEllipse(QtCore.QPoint(rect.right() - 11, rect.top() + 11), 1, 1)

            remove_rect = self.pedal_remove_button_rect(pedal_id)
            painter.setPen(QtGui.QPen(QtGui.QColor("#5d1114"), 1))
            painter.setBrush(QtGui.QBrush(QtGui.QColor("#eb5059")))
            painter.drawRoundedRect(remove_rect, 3, 3)
            painter.setPen(QtGui.QColor("#fff0f0"))
            painter.drawText(remove_rect, QtCore.Qt.AlignCenter, "x")

            for side in ["output", "input"]:
                btn_rect = self.pedal_disconnect_button_rect(pedal_id, side)
                painter.setPen(QtGui.QPen(QtGui.QColor("#1d2831"), 1))
                painter.setBrush(QtGui.QBrush(QtGui.QColor("#f5f7fa")))
                painter.drawRoundedRect(btn_rect, 3, 3)
                painter.setPen(QtGui.QColor("#0f1722"))
                painter.drawText(btn_rect, QtCore.Qt.AlignCenter, "~")

            face_values = self.normalized_face_values(pedal_id)
            if pedal_id in {"ge7", "eq10"}:
                self.draw_eq_pedal_face(painter, rect, pedal_id, face_values)
            else:
                knobs = list(face_values.get("knobs", [50, 50, 50]))
                while len(knobs) < 3:
                    knobs.append(50)
                knob_y = rect.top() + 46
                spacing = (rect.width() - 20) // 3
                for idx in range(3):
                    center = QtCore.QPoint(rect.left() + 10 + spacing * idx, knob_y)
                    self.draw_knob(painter, center, knobs[idx])

            switch_rect = QtCore.QRect(rect.left() + 17, rect.bottom() - 34, rect.width() - 34, 20)
            painter.setPen(QtGui.QPen(QtGui.QColor("#1e2329"), 2))
            switch_fill = QtGui.QLinearGradient(switch_rect.topLeft(), switch_rect.bottomLeft())
            switch_fill.setColorAt(0.0, QtGui.QColor("#f3f6fb"))
            switch_fill.setColorAt(1.0, QtGui.QColor("#c9d1db"))
            painter.setBrush(QtGui.QBrush(switch_fill))
            painter.drawRoundedRect(switch_rect, 6, 6)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 70), 1))
            painter.drawLine(switch_rect.left() + 3, switch_rect.top() + 3, switch_rect.right() - 3, switch_rect.top() + 3)

            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(QtGui.QColor("#f0f5fb")))
            painter.drawEllipse(self.pedal_input_pos(pedal_id), 6, 6)
            painter.drawEllipse(self.pedal_output_pos(pedal_id), 6, 6)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(PEDAL_MIME_TYPE):
            event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(PEDAL_MIME_TYPE):
            event.acceptProposedAction()
            return
        super().dragMoveEvent(event)

    def dropEvent(self, event):
        if not event.mimeData().hasFormat(PEDAL_MIME_TYPE):
            super().dropEvent(event)
            return
        pedal_id = bytes(event.mimeData().data(PEDAL_MIME_TYPE)).decode("utf-8").strip()
        source = bytes(event.mimeData().data(PEDAL_SOURCE_MIME_TYPE)).decode("utf-8").strip() if event.mimeData().hasFormat(PEDAL_SOURCE_MIME_TYPE) else "bank"
        if pedal_id:
            self.pedalDropped.emit(pedal_id, self.clamp_pedal_position(event.pos()), source or "bank")
            event.acceptProposedAction()
            return
        event.ignore()

    def mousePressEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            super().mousePressEvent(event)
            return
        click_pos = event.pos()
        for pedal_id in reversed(self.pedal_ids):
            if self.pedal_remove_button_rect(pedal_id).contains(click_pos):
                self.pedalRemoveRequested.emit(pedal_id)
                return
            if self.pedal_disconnect_button_rect(pedal_id, "output").contains(click_pos):
                self.pedalDisconnectRequested.emit(pedal_id, "output")
                return
            if self.pedal_disconnect_button_rect(pedal_id, "input").contains(click_pos):
                self.pedalDisconnectRequested.emit(pedal_id, "input")
                return
        source = self.find_output_source(click_pos)
        if source:
            self.link_start = source
            self.preview_link_to = click_pos
            self.update()
            return
        pedal_id = self.pedal_at(click_pos)
        if pedal_id:
            self.dragging_pedal = pedal_id
            self.drag_offset = click_pos - self.pedal_positions[pedal_id]
        else:
            self.dragging_pedal = None

    def mouseMoveEvent(self, event):
        if self.link_start:
            self.preview_link_to = event.pos()
            self.update()
            return
        if self.dragging_pedal:
            new_pos = self.clamp_pedal_position(event.pos() - self.drag_offset)
            self.pedal_positions[self.dragging_pedal] = new_pos
            self.update()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.link_start:
            target = self.find_input_target(event.pos())
            if target and target != self.link_start:
                self.connectionCreated.emit(self.link_start, target)
            self.link_start = None
            self.preview_link_to = None
            self.update()
            return
        if event.button() == QtCore.Qt.LeftButton and self.dragging_pedal:
            pedal_id = self.dragging_pedal
            self.dragging_pedal = None
            self.pedalMoved.emit(pedal_id, self.pedal_positions.get(pedal_id, QtCore.QPoint(18, 18)))
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        pedal_id = self.pedal_at(event.pos())
        if pedal_id:
            self.pedalDoubleClicked.emit(pedal_id)
            return
        super().mouseDoubleClickEvent(event)


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def font_pixels_for_preset(preset_key):
    if preset_key in FONT_PRESETS:
        return FONT_PRESETS[preset_key]["px"]
    return FONT_PRESETS["medium"]["px"]


def nearest_font_preset(pixel_size):
    safe_size = clamp(int(round(pixel_size)), 10, 30)
    return min(FONT_PRESET_SPECS, key=lambda spec: abs(spec[2] - safe_size))[0]


def theme_for_key(theme_key):
    return THEMES.get(theme_key, THEMES["dark"])


def sanitize_chain(chain):
    seen = set()
    clean = []
    for pedal_id in chain:
        if pedal_id not in PEDAL_LIBRARY:
            continue
        if pedal_id in seen:
            continue
        seen.add(pedal_id)
        clean.append(pedal_id)
    return clean


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


def pedal_knob_values(pedal_id, settings):
    safe_settings = settings if isinstance(settings, dict) else {}
    if pedal_id == "cs3":
        return {"knobs": [safe_settings.get("sustain", 50), safe_settings.get("tone", 50), safe_settings.get("level", 50)]}
    if pedal_id == "sd1":
        return {"knobs": [safe_settings.get("drive", 50), safe_settings.get("tone", 50), safe_settings.get("level", 50)]}
    if pedal_id == "bd2":
        return {"knobs": [safe_settings.get("gain", 50), safe_settings.get("tone", 50), safe_settings.get("level", 50)]}
    if pedal_id == "ds1":
        return {"knobs": [safe_settings.get("dist", 50), safe_settings.get("tone", 50), safe_settings.get("level", 50)]}
    if pedal_id == "ge7":
        bands = safe_settings.get("bands", {})
        return {
            "sliders": [percent_from_db(bands.get(band, 0), -15, 15) for band in GE7_BANDS],
            "level": percent_from_db(safe_settings.get("level", 0), -15, 15),
        }
    if pedal_id == "eq10":
        bands = safe_settings.get("bands", {})
        return {
            "sliders": [percent_from_db(bands.get(band, 0), -12, 12) for band in EQ10_BANDS],
            "output": percent_from_db(safe_settings.get("volume", 0), -12, 12),
            "gain": percent_from_db(safe_settings.get("gain", 0), -12, 12),
        }
    if pedal_id == "ch1":
        return {"knobs": [safe_settings.get("rate", 50), safe_settings.get("depth", 50), safe_settings.get("effectLevel", 50)]}
    if pedal_id == "dd3":
        return {"knobs": [safe_settings.get("dTime", 50), safe_settings.get("fBack", 50), safe_settings.get("eLevel", 50)]}
    if pedal_id == "rc30":
        return {"knobs": [safe_settings.get("rhythmLevel", 50), safe_settings.get("track1", 50), safe_settings.get("track2", 50)]}
    return {"knobs": [50, 50, 50]}


def unique_list(items):
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def pair_mismatch_count(chain, target):
    target_indices = {pid: idx for idx, pid in enumerate(target)}
    common = [pid for pid in chain if pid in target_indices]
    mismatch = 0
    for i in range(len(common)):
        for j in range(i + 1, len(common)):
            if target_indices[common[i]] > target_indices[common[j]]:
                mismatch += 1
    return mismatch


def evaluate_chain_order(chain, genre_key, guitar_type, style_target, include_notes=False):
    idx = {pid: i for i, pid in enumerate(chain)}
    has = lambda pid: pid in idx
    notes = []
    score = 0

    modern_genres = {"metal", "rock", "pop", "country", "hip-hop"}
    drive_ids = [pid for pid in ["sd1", "bd2", "ds1"] if has(pid)]
    drive_indices = sorted([idx[pid] for pid in drive_ids])
    first_drive = drive_indices[0] if drive_indices else -1
    last_drive = drive_indices[-1] if drive_indices else -1

    target_indices = {pid: i for i, pid in enumerate(style_target)}
    pair_total = 0
    pair_correct = 0
    for i in range(len(chain)):
        for j in range(i + 1, len(chain)):
            left = chain[i]
            right = chain[j]
            if left not in target_indices or right not in target_indices:
                continue
            pair_total += 1
            if target_indices[left] < target_indices[right]:
                pair_correct += 1
    if pair_total:
        ratio = pair_correct / pair_total
        score += int(round(ratio * 34))
        if include_notes:
            notes.append(f"Style-order alignment scored {int(round(ratio * 100))}% against best-practice ordering.")

    def add_rule(condition, weight, pass_note):
        nonlocal score
        if condition:
            score += weight
            if include_notes and pass_note:
                notes.append(pass_note)
        else:
            score -= int(round(weight * 0.72))

    if has("cs3") and drive_indices:
        add_rule(idx["cs3"] < first_drive, 14, "CS-3 is ahead of gain stages for tighter pick response.")

    if has("sd1") and has("ds1"):
        prefer_sd1_first = genre_key in modern_genres or guitar_type == "electric"
        if prefer_sd1_first:
            add_rule(idx["sd1"] < idx["ds1"], 12, "SD-1 is before DS-1 as a focused boost into distortion.")
        else:
            add_rule(idx["ds1"] < idx["sd1"], 8, "DS-1 is before SD-1 for softer vintage clipping.")

    if has("ge7") and drive_indices:
        wants_post = genre_key in modern_genres and guitar_type == "electric"
        add_rule(
            idx["ge7"] > last_drive if wants_post else idx["ge7"] < first_drive,
            10,
            "GE-7 placement matches this style's contour strategy.",
        )

    if has("eq10") and drive_indices:
        wants_post = genre_key in modern_genres and guitar_type == "electric"
        add_rule(
            idx["eq10"] > last_drive if wants_post else idx["eq10"] < first_drive,
            11,
            "10-band EQ placement matches this style's contour strategy.",
        )

    if has("dd3") and drive_indices:
        add_rule(idx["dd3"] > last_drive, 12, "DD-3 is after gain for clearer repeat definition.")

    if has("rc30"):
        add_rule(idx["rc30"] == (len(chain) - 1), 18, "RC-30 is at chain end for stable loop playback.")
        if has("dd3"):
            add_rule(idx["dd3"] < idx["rc30"], 9, "Delay is before RC-30 to print repeats into loops.")

    eq_justification = ""
    if has("ge7") and has("eq10"):
        gap = abs(idx["ge7"] - idx["eq10"])
        if gap == 1:
            score -= 9
            eq_justification = "GE-7 and 10-band are adjacent in your chain; this works but can over-stack filtering."
        else:
            score += 6
            eq_justification = "GE-7 and 10-band are separated to keep each EQ stage distinct and clearer."

    return {
        "score": score,
        "highlights": notes,
        "eq_justification": eq_justification,
    }


_ORDER_CACHE = {}


def run_order_lab(genre_key, chain, guitar_type):
    chain = tuple(sanitize_chain(chain))
    if not chain:
        return {
            "best_chain": [],
            "score": 0,
            "permutations_checked": 0,
            "highlights": [],
            "eq_justification": "",
        }

    cache_key = (genre_key, guitar_type, tuple(sorted(chain)))
    if cache_key in _ORDER_CACHE:
        return copy.deepcopy(_ORDER_CACHE[cache_key])

    target = sanitize_chain(GENRE_PRESETS.get(genre_key, GENRE_PRESETS["metal"])["optimized_chain"])

    best = {
        "chain": list(chain),
        "score": -10**9,
        "mismatch": 10**9,
    }
    checked = 0

    for perm in itertools.permutations(chain):
        checked += 1
        candidate = list(perm)
        evaluation = evaluate_chain_order(candidate, genre_key, guitar_type, target, include_notes=False)
        mismatch = pair_mismatch_count(candidate, target)
        if (
            evaluation["score"] > best["score"]
            or (evaluation["score"] == best["score"] and mismatch < best["mismatch"])
            or (
                evaluation["score"] == best["score"]
                and mismatch == best["mismatch"]
                and "|".join(candidate) < "|".join(best["chain"])
            )
        ):
            best["chain"] = candidate
            best["score"] = evaluation["score"]
            best["mismatch"] = mismatch

    best_eval = evaluate_chain_order(best["chain"], genre_key, guitar_type, target, include_notes=True)
    result = {
        "best_chain": best["chain"],
        "score": best["score"],
        "permutations_checked": checked,
        "highlights": unique_list(best_eval["highlights"])[:5],
        "eq_justification": best_eval["eq_justification"],
    }
    _ORDER_CACHE[cache_key] = copy.deepcopy(result)
    return result


def resolve_guitar_profile(profile_key, guitar_type):
    if profile_key in GUITAR_PROFILES:
        return profile_key
    return AUTO_GUITAR_PROFILE_BY_TYPE[guitar_type]


def resolve_amp_model(genre_key, guitar_type, amp_model):
    if amp_model != "auto" and amp_model in AMP_MODELS:
        return amp_model
    return AUTO_AMP_BY_GENRE.get(guitar_type, AUTO_AMP_BY_GENRE["electric"]).get(genre_key, "fender_twin_reverb")


def preset_note_applies(note, chain_set):
    text = str(note or "").lower().strip()
    if not text:
        return False
    matched = []
    for pedal_id, patterns in ORDER_NOTE_PATTERNS.items():
        if any(pattern in text for pattern in patterns):
            matched.append(pedal_id)
    if not matched:
        return True
    requires_all = ((" and " in text) or (" plus " in text) or (" into " in text)) and (" or " not in text)
    if requires_all:
        return all(pedal in chain_set for pedal in matched)
    return any(pedal in chain_set for pedal in matched)


def filter_preset_notes(notes, chain):
    chain_set = set(sanitize_chain(chain))
    if not chain_set:
        return []
    return [note for note in notes if preset_note_applies(note, chain_set)]


def build_recommendation(genre_key, chain, guitar_type, amp_model, guitar_profile):
    chain = sanitize_chain(chain)
    preset = copy.deepcopy(GENRE_PRESETS.get(genre_key, GENRE_PRESETS["metal"]))
    order_analysis = run_order_lab(genre_key, chain if chain else preset["optimized_chain"], guitar_type)

    recommendation = {
        "label": preset["label"],
        "optimized_chain": order_analysis["best_chain"],
        "order_analysis": order_analysis,
        "pedals": preset["pedals"],
        "amp": preset["amp"],
        "notes": list(filter_preset_notes(preset["notes"], chain)),
        "amp_model_key": None,
        "amp_label": "Amp",
        "guitar": None,
    }

    if not chain:
        recommendation["notes"].append("Add pedals to the chain to get full per-pedal settings.")

    recommendation["notes"].append(
        f"Order Lab checked {order_analysis['permutations_checked']:,} possible layouts for this pedal set."
    )
    if chain and chain != order_analysis["best_chain"]:
        recommendation["notes"].append(
            "Best order for your current pedals: "
            + " -> ".join(PEDAL_LIBRARY[pid] for pid in order_analysis["best_chain"])
            + " -> AMP"
        )

    chain_eval = evaluate_chain_order(chain, genre_key, guitar_type, order_analysis["best_chain"], include_notes=True)
    recommendation["notes"].extend(chain_eval["highlights"])
    if chain_eval["eq_justification"]:
        recommendation["notes"].append(chain_eval["eq_justification"])

    if guitar_type == "acoustic":
        recommendation["amp"]["gain"] = clamp(recommendation["amp"]["gain"] - 18, 0, 100)
        recommendation["amp"]["bass"] = clamp(recommendation["amp"]["bass"] - 6, 0, 100)
        recommendation["amp"]["mid"] = clamp(recommendation["amp"]["mid"] + 4, 0, 100)
        recommendation["notes"].append("Acoustic mode softens gain staging and reduces boom.")

    amp_model_key = resolve_amp_model(genre_key, guitar_type, amp_model)
    amp_profile = AMP_MODELS[amp_model_key]
    recommendation["amp_model_key"] = amp_model_key
    recommendation["amp_label"] = amp_profile["label"]

    merged_amp = {}
    for key in ["gain", "bass", "mid", "treble", "presence", "master"]:
        existing = recommendation["amp"].get(key, 50)
        target = amp_profile["base"][key] + amp_profile["genre_offsets"].get(genre_key, {}).get(key, 0)
        merged_amp[key] = clamp(int(round(existing * 0.42 + target * 0.58)), 0, 100)
    recommendation["amp"].update(merged_amp)
    recommendation["amp"]["modelLabel"] = amp_profile["short_label"]
    recommendation["amp"]["voicing"] = "Acoustic Voice" if amp_profile["type"] == "acoustic" else "Guitar Voice"
    recommendation["notes"].append(amp_profile["note"])

    resolved_profile = resolve_guitar_profile(guitar_profile, guitar_type)
    profile = GUITAR_PROFILES[resolved_profile]
    gsettings = copy.deepcopy(profile["genres"].get(genre_key, profile["genres"].get("rock", {})))
    recommendation["guitar"] = {
        "profileKey": resolved_profile,
        "label": profile["label"],
        "type": profile["type"],
        "controls": profile["controls"],
        "volumeAdvice": profile.get("volume_advice", ""),
        "settings": gsettings,
    }
    recommendation["notes"].append(profile["note"])

    recommendation["notes"] = unique_list(recommendation["notes"])
    return recommendation


def normalize_note_name(note):
    if not note:
        return ""
    key = str(note).strip().upper()
    if key in NOTE_ALIAS_MAP:
        return NOTE_ALIAS_MAP[key]
    if len(key) == 2 and key[1] == "B":
        return f"{key[0]}b"
    return key


def parse_chord_token(token):
    if not isinstance(token, str):
        return None
    clean = token.strip()
    if not clean:
        return None
    match = CHORD_ROOT_RE.match(clean)
    if not match:
        return None
    root_raw = f"{match.group(1)}{match.group(2)}"
    root = normalize_note_name(root_raw)
    suffix = clean[match.end():].strip().lower()
    quality = "major"
    if "dim" in suffix:
        quality = "dim"
    elif suffix.startswith("m") and not suffix.startswith("maj"):
        quality = "minor"
    shorthand = root
    if quality == "minor":
        shorthand = f"{root}m"
    elif quality == "dim":
        shorthand = f"{root}dim"
    return {
        "token": clean,
        "root": root,
        "quality": quality,
        "shorthand": shorthand,
    }


def extract_concert_chords_for_genre(genre_key):
    playbook = STYLE_PLAYBOOK.get(genre_key, STYLE_PLAYBOOK["rock"])
    chords = []
    for progression in playbook.get("concertProgression", []):
        if not isinstance(progression, str):
            continue
        for token in progression.split("-"):
            clean = token.strip()
            if clean:
                chords.append(clean)
    return unique_list(chords)


def determine_best_nashville_key(chord_tokens):
    parsed = [parse_chord_token(token) for token in chord_tokens]
    parsed = [item for item in parsed if item]
    if not parsed:
        return "C"
    best_key = "C"
    best_score = -1
    for key_name, degrees in NASHVILLE_MAJOR_CHART:
        degree_set = set(degrees)
        score = 0
        for chord in parsed:
            if chord["shorthand"] in degree_set:
                score += 2
            elif chord["root"] in degree_set:
                score += 1
        if score > best_score:
            best_score = score
            best_key = key_name
    return best_key


class CircleOfFifthsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 320)
        self.theme = THEMES["dark"]
        self.major_highlights = set()
        self.minor_highlights = set()
        self.dim_highlights = set()

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def set_highlighted_chords(self, chords):
        major = set()
        minor = set()
        dim = set()
        for token in chords:
            parsed = parse_chord_token(token)
            if not parsed:
                continue
            if parsed["quality"] == "minor":
                minor.add(parsed["root"])
            elif parsed["quality"] == "dim":
                dim.add(parsed["root"])
            else:
                major.add(parsed["root"])
        self.major_highlights = major
        self.minor_highlights = minor
        self.dim_highlights = dim
        self.update()

    def draw_ring_node(self, painter, center, radius, label, active=False, is_minor=False):
        normal_bg = QtGui.QColor(self.theme["panel"])
        normal_edge = QtGui.QColor(self.theme["frame"])
        highlight_bg = QtGui.QColor(self.theme["tab_selected_bg"])
        highlight_fg = QtGui.QColor(self.theme["tab_selected_fg"])
        text_color = QtGui.QColor(self.theme["text"])
        if is_minor:
            normal_bg = normal_bg.darker(108)
        painter.setPen(QtGui.QPen(highlight_bg.darker(160) if active else normal_edge, 1.4))
        painter.setBrush(QtGui.QBrush(highlight_bg if active else normal_bg))
        painter.drawEllipse(center, radius, radius)
        painter.setPen(highlight_fg if active else text_color)
        font = painter.font()
        font.setBold(active)
        font.setPointSize(max(8, font.pointSize() - (1 if is_minor else 0)))
        painter.setFont(font)
        painter.drawText(
            QtCore.QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2),
            QtCore.Qt.AlignCenter,
            label,
        )

    def paintEvent(self, _event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        rect = self.rect().adjusted(12, 12, -12, -12)
        center = rect.center()
        outer_radius = max(72, min(rect.width(), rect.height()) // 2 - 28)
        inner_radius = int(round(outer_radius * 0.62))

        painter.setPen(QtGui.QPen(QtGui.QColor(self.theme["frame"]), 1))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawEllipse(center, outer_radius, outer_radius)
        painter.drawEllipse(center, inner_radius, inner_radius)

        for idx, major_key in enumerate(CIRCLE_FIFTHS_MAJOR):
            angle = math.radians(-90 + idx * 30)
            x = center.x() + math.cos(angle) * outer_radius
            y = center.y() + math.sin(angle) * outer_radius
            self.draw_ring_node(
                painter,
                QtCore.QPointF(x, y),
                18,
                major_key,
                active=major_key in self.major_highlights or major_key in self.dim_highlights,
                is_minor=False,
            )

        for idx, minor_key in enumerate(CIRCLE_FIFTHS_MINOR):
            angle = math.radians(-90 + idx * 30)
            x = center.x() + math.cos(angle) * inner_radius
            y = center.y() + math.sin(angle) * inner_radius
            root = minor_key[:-1]
            self.draw_ring_node(
                painter,
                QtCore.QPointF(x, y),
                15,
                minor_key,
                active=root in self.minor_highlights,
                is_minor=True,
            )

        painter.setPen(QtGui.QColor(self.theme["text"]))
        center_font = painter.font()
        center_font.setBold(True)
        center_font.setPointSize(max(8, center_font.pointSize() - 1))
        painter.setFont(center_font)
        painter.drawText(
            QtCore.QRectF(center.x() - 52, center.y() - 26, 104, 52),
            QtCore.Qt.AlignCenter,
            "Circle\nof Fifths",
        )


class PedalArchitectWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pedal Architect (PyQt5)")
        self.resize(1400, 900)

        self.state = {
            "genre": "metal",
            "guitarType": "electric",
            "guitarProfile": AUTO_GUITAR_PROFILE_BY_TYPE["electric"],
            "ampModel": "auto",
            "fontPreset": "medium",
            "theme": "dark",
            "chain": list(DEFAULT_CHAIN),
            "canvasPositions": {},
            "canvasConnections": [],
        }
        self.connected_chain = []

        self._loading_ui = False
        self.load_state()
        self.build_ui()
        self.apply_theme()
        self.render_all()

    def build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        root = QtWidgets.QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        self.build_global_controls(root)

        self.tabs = QtWidgets.QTabWidget()
        root.addWidget(self.tabs)

        self.builder_tab = QtWidgets.QWidget()
        self.settings_tab = QtWidgets.QWidget()
        self.summary_tab = QtWidgets.QWidget()

        self.tabs.addTab(self.builder_tab, "Builder")
        self.tabs.addTab(self.settings_tab, "Rig Settings")
        self.tabs.addTab(self.summary_tab, "Rig Summary")

        self.build_builder_tab()
        self.build_settings_tab()
        self.build_summary_tab()
        self.populate_controls()
        self.bind_builder_events()
        QtCore.QTimer.singleShot(0, self.initialize_splitter_sizes)

    def initialize_splitter_sizes(self):
        if hasattr(self, "builder_splitter"):
            self.builder_splitter.setSizes([320, 560, 520])
        if hasattr(self, "settings_splitter"):
            self.settings_splitter.setSizes([320, 320, 320, 420])

    def build_global_controls(self, root_layout):
        controls = QtWidgets.QFrame()
        controls_layout = QtWidgets.QVBoxLayout(controls)
        controls_layout.setContentsMargins(10, 10, 10, 10)
        controls_layout.setSpacing(8)

        style_row = QtWidgets.QHBoxLayout()
        style_row.setSpacing(8)
        style_label = QtWidgets.QLabel("Style")
        style_label.setMinimumWidth(48)
        self.genre_combo = QtWidgets.QComboBox()
        style_row.addWidget(style_label)
        style_row.addWidget(self.genre_combo, 1)
        controls_layout.addLayout(style_row)

        self.guitar_type_combo = QtWidgets.QComboBox()
        self.guitar_profile_combo = QtWidgets.QComboBox()
        self.amp_combo = QtWidgets.QComboBox()
        self.font_size_combo = QtWidgets.QComboBox()
        self.theme_combo = QtWidgets.QComboBox()
        self.font_size_combo.setView(QtWidgets.QListView())

        dropdown_row = QtWidgets.QHBoxLayout()
        dropdown_row.setSpacing(10)
        self.add_control_column(dropdown_row, "Guitar", self.guitar_type_combo)
        self.add_control_column(dropdown_row, "Guitar Controls", self.guitar_profile_combo)
        self.add_control_column(dropdown_row, "Amp", self.amp_combo)
        self.add_control_column(dropdown_row, "Font Size", self.font_size_combo)
        self.add_control_column(dropdown_row, "Color Scheme", self.theme_combo)
        controls_layout.addLayout(dropdown_row)

        self.optimize_btn = QtWidgets.QPushButton("Optimize For Me")
        self.clean_up_btn = QtWidgets.QPushButton("Clean Up Layout")
        self.auto_wire_btn = QtWidgets.QPushButton("Auto Wire")
        self.clear_cables_btn = QtWidgets.QPushButton("Clear Cables")
        self.reset_btn = QtWidgets.QPushButton("Reset Chain")
        self.save_btn = QtWidgets.QPushButton("Save Offline")

        action_row = QtWidgets.QHBoxLayout()
        action_row.setSpacing(10)
        action_row.addWidget(self.optimize_btn)
        action_row.addWidget(self.clean_up_btn)
        action_row.addWidget(self.auto_wire_btn)
        action_row.addWidget(self.clear_cables_btn)
        action_row.addWidget(self.reset_btn)
        action_row.addStretch(1)
        action_row.addWidget(self.save_btn)
        controls_layout.addLayout(action_row)

        root_layout.addWidget(controls)

    def build_builder_tab(self):
        layout = QtWidgets.QVBoxLayout(self.builder_tab)
        layout.setSpacing(10)

        bank_group = QtWidgets.QGroupBox("Pedal Bank")
        bank_layout = QtWidgets.QVBoxLayout(bank_group)
        self.bank_list = PedalBankListWidget()
        self.bank_list.setAlternatingRowColors(True)
        self.bank_list.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        bank_layout.addWidget(self.bank_list)
        bank_hint = QtWidgets.QLabel("Drag pedals from bank into Active Pedals or directly onto the Board Canvas.")
        bank_hint.setWordWrap(True)
        bank_layout.addWidget(bank_hint)
        bank_layout.addWidget(QtWidgets.QLabel("Active Pedals"))
        self.chain_list = ChainListWidget()
        self.chain_list.setAlternatingRowColors(True)
        self.chain_list.setMinimumHeight(170)
        self.chain_list.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        bank_layout.addWidget(self.chain_list)
        remove_btn = QtWidgets.QPushButton("Remove Selected Pedal")
        bank_layout.addWidget(remove_btn)
        self.remove_chain_btn = remove_btn

        board_group = QtWidgets.QGroupBox("Board Canvas")
        board_layout = QtWidgets.QVBoxLayout(board_group)
        self.board_canvas = PedalCanvasWidget()
        board_layout.addWidget(self.board_canvas, 1)
        board_hint = QtWidgets.QLabel(
            "Pedal input is on the right, output on the left. Drag from output to input to cable. Use x to remove a pedal, or ~ buttons to disconnect that side."
        )
        board_hint.setWordWrap(True)
        board_layout.addWidget(board_hint)
        self.chain_score = QtWidgets.QLabel("Tone Match: --")
        self.chain_summary = QtWidgets.QLabel("")
        self.chain_summary.setWordWrap(True)
        self.chain_score.setStyleSheet("font-weight: 700;")
        board_layout.addWidget(self.chain_score)
        board_layout.addWidget(self.chain_summary)

        right_group = QtWidgets.QGroupBox("Guitar + Amp")
        right_layout = QtWidgets.QVBoxLayout(right_group)
        self.guitar_preview = QtWidgets.QTextEdit()
        self.guitar_preview.setReadOnly(True)
        self.guitar_preview.setPlaceholderText("Guitar controls preview")
        self.guitar_preview.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.amp_preview = QtWidgets.QTextEdit()
        self.amp_preview.setReadOnly(True)
        self.amp_preview.setPlaceholderText("Amp settings preview")
        self.amp_preview.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.playbook_preview = QtWidgets.QTextEdit()
        self.playbook_preview.setReadOnly(True)
        self.playbook_preview.setPlaceholderText("Style progression + solo guide")
        self.playbook_preview.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        right_layout.addWidget(QtWidgets.QLabel("Guitar View"))
        right_layout.addWidget(self.guitar_preview, 1)
        right_layout.addWidget(QtWidgets.QLabel("Amp (Chain End)"))
        right_layout.addWidget(self.amp_preview, 1)
        right_layout.addWidget(QtWidgets.QLabel("Style Playbook"))
        right_layout.addWidget(self.playbook_preview, 2)

        for panel in [bank_group, board_group, right_group]:
            panel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.builder_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.builder_splitter.addWidget(bank_group)
        self.builder_splitter.addWidget(board_group)
        self.builder_splitter.addWidget(right_group)
        self.builder_splitter.setChildrenCollapsible(False)
        self.builder_splitter.setStretchFactor(0, 2)
        self.builder_splitter.setStretchFactor(1, 4)
        self.builder_splitter.setStretchFactor(2, 4)
        layout.addWidget(self.builder_splitter, 1)

    def build_settings_tab(self):
        layout = QtWidgets.QVBoxLayout(self.settings_tab)
        layout.setSpacing(10)

        pedals_group = QtWidgets.QGroupBox("Pedal Settings")
        pedals_layout = QtWidgets.QVBoxLayout(pedals_group)
        self.pedal_cards_container = QtWidgets.QWidget()
        self.pedal_cards_grid = QtWidgets.QGridLayout(self.pedal_cards_container)
        self.pedal_cards_grid.setContentsMargins(4, 4, 4, 4)
        self.pedal_cards_grid.setHorizontalSpacing(8)
        self.pedal_cards_grid.setVerticalSpacing(8)
        for col in range(5):
            self.pedal_cards_grid.setColumnStretch(col, 1)
        pedals_layout.addWidget(self.pedal_cards_container, 1)
        self.pedal_empty_label = QtWidgets.QLabel(
            "No connected signal chain yet.\nAdd pedals and cable them from guitar to amp."
        )
        self.pedal_empty_label.setWordWrap(True)
        pedals_layout.addWidget(self.pedal_empty_label)
        layout.addWidget(pedals_group, 3)

        detail_row = QtWidgets.QHBoxLayout()
        detail_row.setSpacing(10)
        guitar_group, self.guitar_settings_text = self.make_info_panel("Guitar Settings")
        amp_group, self.amp_settings_text = self.make_info_panel("Amp Settings")
        just_group, self.justification_text = self.make_info_panel("Justification")
        detail_row.addWidget(guitar_group, 1)
        detail_row.addWidget(amp_group, 1)
        detail_row.addWidget(just_group, 1)
        layout.addLayout(detail_row, 2)

    def build_summary_tab(self):
        layout = QtWidgets.QVBoxLayout(self.summary_tab)
        summary_group = QtWidgets.QGroupBox("Rig Summary")
        group_layout = QtWidgets.QVBoxLayout(summary_group)
        self.summary_text = QtWidgets.QTextEdit()
        self.summary_text.setReadOnly(True)
        group_layout.addWidget(self.summary_text)
        layout.addWidget(summary_group, 2)

        analysis_row = QtWidgets.QHBoxLayout()
        analysis_row.setSpacing(10)

        circle_group = QtWidgets.QGroupBox("Circle of Fifths")
        circle_layout = QtWidgets.QVBoxLayout(circle_group)
        self.circle_of_fifths = CircleOfFifthsWidget()
        self.circle_hint = QtWidgets.QLabel("Highlighted from suggested concert progression chords.")
        self.circle_hint.setWordWrap(True)
        circle_layout.addWidget(self.circle_of_fifths, 1)
        circle_layout.addWidget(self.circle_hint)
        analysis_row.addWidget(circle_group, 1)

        nashville_group = QtWidgets.QGroupBox("Nashville Number Chart")
        nashville_layout = QtWidgets.QVBoxLayout(nashville_group)
        self.nashville_hint = QtWidgets.QLabel("Best-matching key is highlighted based on the progression above.")
        self.nashville_hint.setWordWrap(True)
        self.nashville_table = QtWidgets.QTableWidget(len(NASHVILLE_MAJOR_CHART), 8)
        self.nashville_table.setHorizontalHeaderLabels(["Key", "1", "2m", "3m", "4", "5", "6m", "7dim"])
        self.nashville_table.verticalHeader().setVisible(False)
        self.nashville_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.nashville_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.nashville_table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.nashville_table.setAlternatingRowColors(True)
        self.nashville_table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.nashville_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        nashville_layout.addWidget(self.nashville_hint)
        nashville_layout.addWidget(self.nashville_table, 1)
        analysis_row.addWidget(nashville_group, 2)

        layout.addLayout(analysis_row, 3)
        self.populate_nashville_table()

    def make_info_panel(self, title):
        group = QtWidgets.QGroupBox(title)
        group_layout = QtWidgets.QVBoxLayout(group)
        text = QtWidgets.QTextEdit()
        text.setReadOnly(True)
        text.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        group_layout.addWidget(text)
        group.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        return group, text

    def clear_layout_widgets(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def build_pedal_settings_card(self, pedal_id, settings):
        frame = QtWidgets.QFrame()
        frame.setObjectName("pedalSettingsCard")
        frame.setMinimumHeight(220)
        frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        content = QtWidgets.QVBoxLayout(frame)
        content.setContentsMargins(10, 10, 10, 10)
        content.setSpacing(6)

        title = QtWidgets.QLabel(PEDAL_LIBRARY[pedal_id])
        title.setObjectName("pedalCardTitle")
        title.setWordWrap(True)
        content.addWidget(title)

        details = QtWidgets.QLabel()
        details.setWordWrap(True)
        details.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        details.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        block = self.format_pedal_block(pedal_id, settings).splitlines()
        details.setText("\n".join(block[1:]) if len(block) > 1 else "Optimized for this rig style.")
        content.addWidget(details, 1)
        return frame

    def populate_nashville_table(self):
        self.nashville_table.clearContents()
        for row, (key_name, degrees) in enumerate(NASHVILLE_MAJOR_CHART):
            values = [key_name] + degrees
            for col, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(value)
                align = QtCore.Qt.AlignCenter if col > 0 else (QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                item.setTextAlignment(align)
                self.nashville_table.setItem(row, col, item)

    def highlight_nashville_key(self, key_name):
        theme = theme_for_key(self.state.get("theme", "dark"))
        normal_bg = QtGui.QColor(theme["panel"])
        normal_fg = QtGui.QColor(theme["text"])
        highlight_bg = QtGui.QColor(theme["tab_selected_bg"])
        highlight_fg = QtGui.QColor(theme["tab_selected_fg"])
        for row in range(self.nashville_table.rowCount()):
            is_match = self.nashville_table.item(row, 0).text() == key_name
            for col in range(self.nashville_table.columnCount()):
                item = self.nashville_table.item(row, col)
                if item is None:
                    continue
                item.setBackground(highlight_bg if is_match else normal_bg)
                item.setForeground(highlight_fg if is_match else normal_fg)

    def add_control_column(self, layout, label_text, widget):
        wrapper_widget = QtWidgets.QWidget()
        wrapper = QtWidgets.QVBoxLayout(wrapper_widget)
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.setSpacing(3)
        label = QtWidgets.QLabel(label_text)
        label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        wrapper.addWidget(label)
        wrapper.addWidget(widget, 1)
        layout.addWidget(wrapper_widget, 1)

    def make_settings_column(self, parent, title):
        group = QtWidgets.QGroupBox(title)
        group_layout = QtWidgets.QVBoxLayout(group)
        text = QtWidgets.QTextEdit()
        text.setReadOnly(True)
        text.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        group_layout.addWidget(text)
        group.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        if isinstance(parent, QtWidgets.QSplitter):
            parent.addWidget(group)
        else:
            parent.addWidget(group, 1)
        return text

    def bind_builder_events(self):
        self.genre_combo.currentIndexChanged.connect(self.on_controls_changed)
        self.guitar_type_combo.currentIndexChanged.connect(self.on_controls_changed)
        self.guitar_profile_combo.currentIndexChanged.connect(self.on_controls_changed)
        self.amp_combo.currentIndexChanged.connect(self.on_controls_changed)
        self.font_size_combo.currentIndexChanged.connect(self.on_font_preset_changed)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)

        self.optimize_btn.clicked.connect(self.optimize_chain)
        self.clean_up_btn.clicked.connect(self.clean_up_layout)
        self.auto_wire_btn.clicked.connect(self.auto_wire_active_pedals)
        self.clear_cables_btn.clicked.connect(self.clear_cables)
        self.reset_btn.clicked.connect(self.reset_chain)
        self.save_btn.clicked.connect(self.persist_state)

        self.bank_list.itemDoubleClicked.connect(self.add_selected_bank_item)
        self.chain_list.itemDoubleClicked.connect(self.remove_selected_chain_item)
        self.chain_list.pedalDropped.connect(self.insert_pedal_into_chain)
        self.bank_list.chainPedalReturned.connect(self.return_chain_pedal_to_bank)
        self.remove_chain_btn.clicked.connect(self.remove_selected_chain_item)
        self.board_canvas.pedalDropped.connect(self.on_canvas_pedal_dropped)
        self.board_canvas.pedalMoved.connect(self.on_canvas_pedal_moved)
        self.board_canvas.connectionCreated.connect(self.on_canvas_connection_created)
        self.board_canvas.pedalDoubleClicked.connect(self.on_canvas_pedal_double_clicked)
        self.board_canvas.pedalRemoveRequested.connect(self.on_canvas_pedal_removed)
        self.board_canvas.pedalDisconnectRequested.connect(self.on_canvas_disconnect_requested)

    def populate_controls(self):
        self._loading_ui = True

        self.genre_combo.clear()
        for genre_key, preset in GENRE_PRESETS.items():
            self.genre_combo.addItem(preset["label"], genre_key)

        self.guitar_type_combo.clear()
        self.guitar_type_combo.addItem("Electric", "electric")
        self.guitar_type_combo.addItem("Acoustic", "acoustic")

        self.guitar_profile_combo.clear()
        for profile_key, profile in GUITAR_PROFILES.items():
            text = f"{profile['label']} ({'Acoustic' if profile['type'] == 'acoustic' else 'Electric'})"
            self.guitar_profile_combo.addItem(text, profile_key)

        self.amp_combo.clear()
        self.amp_combo.addItem("Auto (Best Match)", "auto")
        for amp_key, amp in AMP_MODELS.items():
            self.amp_combo.addItem(amp["label"], amp_key)

        self.theme_combo.clear()
        for theme_key, label in THEME_PRESET_SPECS:
            self.theme_combo.addItem(label, theme_key)

        self.font_size_combo.clear()
        for preset_key, label, pixel_size in FONT_PRESET_SPECS:
            row = self.font_size_combo.count()
            self.font_size_combo.addItem(f"{label}  AaBbCc ({pixel_size}px)", preset_key)
            sample_font = QtGui.QFont(self.font_size_combo.font())
            sample_font.setPointSize(max(8, int(round(pixel_size * 0.72))))
            self.font_size_combo.setItemData(row, sample_font, QtCore.Qt.FontRole)

        self.set_combo_by_data(self.genre_combo, self.state["genre"])
        self.set_combo_by_data(self.guitar_type_combo, self.state["guitarType"])
        self.set_combo_by_data(self.guitar_profile_combo, self.state["guitarProfile"])
        self.set_combo_by_data(self.amp_combo, self.state["ampModel"])
        if not self.set_combo_by_data(self.theme_combo, self.state.get("theme", "dark")):
            self.set_combo_by_data(self.theme_combo, "dark")
        if not self.set_combo_by_data(self.font_size_combo, self.state.get("fontPreset", "medium")):
            self.set_combo_by_data(self.font_size_combo, "medium")

        self._loading_ui = False

    def set_combo_by_data(self, combo, value):
        for idx in range(combo.count()):
            if combo.itemData(idx) == value:
                combo.setCurrentIndex(idx)
                return True
        return False

    def on_controls_changed(self):
        if self._loading_ui:
            return

        self.state["genre"] = self.genre_combo.currentData()
        self.state["guitarType"] = self.guitar_type_combo.currentData()

        profile_key = self.guitar_profile_combo.currentData()
        profile = GUITAR_PROFILES.get(profile_key)
        if profile and profile["type"] == self.state["guitarType"]:
            self.state["guitarProfile"] = profile_key
        else:
            self.state["guitarProfile"] = AUTO_GUITAR_PROFILE_BY_TYPE[self.state["guitarType"]]
            self._loading_ui = True
            self.set_combo_by_data(self.guitar_profile_combo, self.state["guitarProfile"])
            self._loading_ui = False

        self.state["ampModel"] = self.amp_combo.currentData()

        self.render_all()
        self.persist_state(silent=True)

    def on_font_preset_changed(self):
        if self._loading_ui:
            return
        preset_key = self.font_size_combo.currentData()
        if preset_key not in FONT_PRESETS:
            preset_key = "medium"
        self.state["fontPreset"] = preset_key
        self.apply_theme()
        self.persist_state(silent=True)

    def on_theme_changed(self):
        if self._loading_ui:
            return
        theme_key = self.theme_combo.currentData()
        if theme_key not in THEMES:
            theme_key = "dark"
        self.state["theme"] = theme_key
        self.apply_theme()
        self.persist_state(silent=True)

    def update_bank_list(self):
        self.bank_list.clear()
        chain_set = set(self.state["chain"])
        for pedal_id in BANK_ORDER:
            item_text = PEDAL_LIBRARY[pedal_id]
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, pedal_id)
            base = QtGui.QColor(PEDAL_COLORS.get(pedal_id, "#b0b0b0"))
            item.setBackground(base.lighter(115))
            item.setForeground(QtGui.QColor(PEDAL_TEXT_COLORS.get(pedal_id, "#11171f")))
            item.setFlags(
                (item.flags() | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                & ~QtCore.Qt.ItemIsDropEnabled
            )
            if pedal_id in chain_set:
                muted = QtGui.QColor(PEDAL_TEXT_COLORS.get(pedal_id, "#11171f"))
                muted.setAlpha(130)
                item.setForeground(muted)
                item.setText(f"{item_text}  [In chain]")
            self.bank_list.addItem(item)

    def update_chain_list(self):
        self.chain_list.blockSignals(True)
        self.chain_list.clear()
        for pedal_id in self.state["chain"]:
            item = QtWidgets.QListWidgetItem(PEDAL_LIBRARY[pedal_id])
            item.setData(QtCore.Qt.UserRole, pedal_id)
            base = QtGui.QColor(PEDAL_COLORS.get(pedal_id, "#b0b0b0"))
            item.setBackground(base.lighter(115))
            item.setForeground(QtGui.QColor(PEDAL_TEXT_COLORS.get(pedal_id, "#11171f")))
            item.setFlags(
                (item.flags() | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                & ~QtCore.Qt.ItemIsDropEnabled
            )
            self.chain_list.addItem(item)
        self.chain_list.blockSignals(False)

    def collect_layout_slots(self, max_count, x_range=None, y_range=None, right_to_left=False):
        if max_count <= 0:
            return []
        min_x, max_x, min_y, max_y = self.board_canvas.pedal_position_bounds()
        if x_range:
            min_x = clamp(int(x_range[0]), min_x, max_x)
            max_x = clamp(int(x_range[1]), min_x, max_x)
        if y_range:
            min_y = clamp(int(y_range[0]), min_y, max_y)
            max_y = clamp(int(y_range[1]), min_y, max_y)
        if max_x < min_x or max_y < min_y:
            return []

        step_x = self.board_canvas.PEDAL_SIZE.width() + 22
        step_y = self.board_canvas.PEDAL_SIZE.height() + 24
        xs = list(range(min_x, max_x + 1, step_x))
        ys = list(range(min_y, max_y + 1, step_y))
        if right_to_left:
            xs.reverse()

        slots = []
        seen = set()
        for y in ys:
            for x in xs:
                candidate = QtCore.QPoint(x, y)
                key = (candidate.x(), candidate.y())
                if key in seen:
                    continue
                seen.add(key)
                if not self.board_canvas.can_place_pedal_at(candidate):
                    continue
                slots.append(candidate)
                if len(slots) >= max_count:
                    return slots
        return slots

    def collect_horizontal_chain_slots(self, max_count, x_range=None, y_range=None):
        if max_count <= 0:
            return []
        min_x, max_x, min_y, max_y = self.board_canvas.pedal_position_bounds()
        if x_range:
            min_x = clamp(int(x_range[0]), min_x, max_x)
            max_x = clamp(int(x_range[1]), min_x, max_x)
        if y_range:
            min_y = clamp(int(y_range[0]), min_y, max_y)
            max_y = clamp(int(y_range[1]), min_y, max_y)
        if max_x < min_x or max_y < min_y:
            return []

        step_x = self.board_canvas.PEDAL_SIZE.width() + 22
        step_y = self.board_canvas.PEDAL_SIZE.height() + 24
        xs = list(range(max_x, min_x - 1, -step_x))
        center_y = clamp((min_y + max_y) // 2, min_y, max_y)
        row_centers = [center_y]
        for offset in range(step_y, (max_y - min_y) + step_y, step_y):
            down = center_y + offset
            up = center_y - offset
            if down <= max_y:
                row_centers.append(down)
            if up >= min_y:
                row_centers.append(up)
            if down > max_y and up < min_y:
                break

        rows = []
        for y in row_centers:
            row_slots = []
            for x in xs:
                candidate = QtCore.QPoint(x, y)
                if not self.board_canvas.can_place_pedal_at(candidate):
                    continue
                row_slots.append(candidate)
            if row_slots:
                rows.append((row_slots, y))

        rows.sort(key=lambda row_entry: (-len(row_entry[0]), abs(row_entry[1] - center_y)))

        slots = []
        seen = set()
        for row_slots, _y in rows:
            for candidate in row_slots:
                key = (candidate.x(), candidate.y())
                if key in seen:
                    continue
                seen.add(key)
                slots.append(candidate)
                if len(slots) >= max_count:
                    return slots
        return slots

    def choose_slot(self, candidates, used_rects):
        for candidate in candidates:
            candidate_rect = QtCore.QRect(candidate, self.board_canvas.PEDAL_SIZE)
            collision = False
            for used in used_rects:
                if candidate_rect.adjusted(-6, -6, 6, 6).intersects(used):
                    collision = True
                    break
            if not collision:
                return candidate
        return None

    def default_canvas_position_for(self, pedal_id):
        chain = list(self.state["chain"])
        index = chain.index(pedal_id) if pedal_id in chain else len(chain)
        needed = max(24, len(chain) + 8, index + 1)
        min_x, max_x, min_y, max_y = self.board_canvas.pedal_position_bounds()
        slots = self.collect_horizontal_chain_slots(
            needed,
            x_range=(min_x, max_x),
            y_range=(min_y + 90, max_y),
        )
        if index < len(slots):
            return slots[index]
        fallback = QtCore.QPoint(20 + (index % 5) * 16, 20 + (index // 5) * 14)
        return self.board_canvas.clamp_pedal_position(fallback)

    def sanitize_canvas_connections(self, active_chain):
        active_set = set(active_chain)
        cleaned = []
        seen = set()
        for entry in self.state.get("canvasConnections", []):
            if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                continue
            src = str(entry[0])
            dst = str(entry[1])
            valid_src = src in active_set or src == GUITAR_NODE_ID
            if not valid_src:
                continue
            if dst != AMP_NODE_ID and dst not in active_set:
                continue
            if src == dst:
                continue
            key = (src, dst)
            if key in seen:
                continue
            seen.add(key)
            cleaned.append([src, dst])
        self.state["canvasConnections"] = cleaned

    def ensure_canvas_state(self, focus_pedal=None, focus_pos=None):
        chain = sanitize_chain(self.state["chain"])
        self.state["chain"] = chain
        positions = self.state.setdefault("canvasPositions", {})
        for pedal_id in chain:
            if pedal_id == focus_pedal and focus_pos is not None:
                clamped = self.board_canvas.clamp_pedal_position(focus_pos)
                positions[pedal_id] = [clamped.x(), clamped.y()]
            elif pedal_id not in positions:
                default_pos = self.default_canvas_position_for(pedal_id)
                positions[pedal_id] = [default_pos.x(), default_pos.y()]
            else:
                raw = positions[pedal_id]
                if not isinstance(raw, (list, tuple)) or len(raw) != 2:
                    default_pos = self.default_canvas_position_for(pedal_id)
                    positions[pedal_id] = [default_pos.x(), default_pos.y()]
                else:
                    clamped = self.board_canvas.clamp_pedal_position(QtCore.QPoint(int(raw[0]), int(raw[1])))
                    positions[pedal_id] = [clamped.x(), clamped.y()]
        for pedal_id in list(positions.keys()):
            if pedal_id not in chain:
                positions.pop(pedal_id, None)
        self.sanitize_canvas_connections(chain)

    def add_selected_bank_item(self, item=None):
        item = item or self.bank_list.currentItem()
        if not item:
            return
        pedal_id = item.data(QtCore.Qt.UserRole)
        if not pedal_id:
            return
        chain = list(self.state["chain"])
        if pedal_id in chain:
            return
        chain.append(pedal_id)
        self.state["chain"] = chain
        self.ensure_canvas_state(pedal_id)
        self.render_all()
        self.persist_state(silent=True)

    def insert_pedal_into_chain(self, pedal_id, row, source="bank"):
        if pedal_id not in PEDAL_LIBRARY:
            return
        chain = list(self.state["chain"])
        row = clamp(int(row), 0, len(chain))
        if source == "chain" and pedal_id in chain:
            old_index = chain.index(pedal_id)
            chain.pop(old_index)
            if old_index < row:
                row -= 1
        elif pedal_id in chain:
            old_index = chain.index(pedal_id)
            chain.pop(old_index)
            if old_index < row:
                row -= 1
        row = clamp(int(row), 0, len(chain))
        chain.insert(row, pedal_id)
        self.state["chain"] = sanitize_chain(chain)
        self.ensure_canvas_state(pedal_id)
        self.render_all()
        self.persist_state(silent=True)

    def return_chain_pedal_to_bank(self, pedal_id):
        if pedal_id not in self.state["chain"]:
            return
        self.state["chain"] = [pid for pid in self.state["chain"] if pid != pedal_id]
        self.ensure_canvas_state()
        self.render_all()
        self.persist_state(silent=True)

    def remove_selected_chain_item(self, *_args):
        item = self.chain_list.currentItem()
        if not item:
            return
        pedal_id = item.data(QtCore.Qt.UserRole)
        self.return_chain_pedal_to_bank(pedal_id)

    def on_canvas_pedal_dropped(self, pedal_id, pos, source):
        if pedal_id not in PEDAL_LIBRARY:
            return
        if pedal_id not in self.state["chain"]:
            self.state["chain"].append(pedal_id)
        self.ensure_canvas_state(pedal_id, pos)
        if source == "chain":
            self.state["chain"] = [pid for pid in self.state["chain"] if pid != pedal_id] + [pedal_id]
        self.render_all()
        self.persist_state(silent=True)

    def on_canvas_pedal_moved(self, pedal_id, pos):
        if pedal_id not in self.state["chain"]:
            return
        clamped = self.board_canvas.clamp_pedal_position(pos)
        self.state.setdefault("canvasPositions", {})[pedal_id] = [clamped.x(), clamped.y()]
        self.board_canvas.update()
        self.persist_state(silent=True)

    def introduces_cycle(self, connections):
        outgoing = {}
        for src, dst in connections:
            if src == GUITAR_NODE_ID or dst == AMP_NODE_ID:
                continue
            outgoing[src] = dst
        for start in outgoing:
            seen = set()
            cursor = start
            while cursor in outgoing:
                if cursor in seen:
                    return True
                seen.add(cursor)
                cursor = outgoing[cursor]
        return False

    def on_canvas_connection_created(self, src, dst):
        active_set = set(self.state["chain"])
        if src != GUITAR_NODE_ID and src not in active_set:
            return
        if dst != AMP_NODE_ID and dst not in active_set:
            return
        if dst == GUITAR_NODE_ID:
            return
        if src == dst:
            return
        connections = [tuple(item) for item in self.state.get("canvasConnections", []) if len(item) == 2]
        connections = [(s, d) for (s, d) in connections if s != src]
        if dst != AMP_NODE_ID:
            connections = [(s, d) for (s, d) in connections if d != dst]
        if dst == AMP_NODE_ID:
            connections = [(s, d) for (s, d) in connections if d != AMP_NODE_ID]
        candidate = connections + [(src, dst)]
        if self.introduces_cycle(candidate):
            QtWidgets.QMessageBox.warning(self, "Cable Loop Blocked", "That cable would create a signal loop. Try a different target.")
            return
        self.state["canvasConnections"] = [[s, d] for s, d in candidate]
        self.render_all()
        self.persist_state(silent=True)

    def on_canvas_pedal_double_clicked(self, pedal_id):
        self.return_chain_pedal_to_bank(pedal_id)

    def on_canvas_pedal_removed(self, pedal_id):
        self.return_chain_pedal_to_bank(pedal_id)

    def on_canvas_disconnect_requested(self, pedal_id, side):
        connections = [list(item) for item in self.state.get("canvasConnections", []) if isinstance(item, (list, tuple)) and len(item) == 2]
        if side == "input":
            connections = [edge for edge in connections if edge[1] != pedal_id]
        else:
            connections = [edge for edge in connections if edge[0] != pedal_id]
        self.state["canvasConnections"] = connections
        self.render_all()
        self.persist_state(silent=True)

    def compute_connected_chain(self):
        active_set = set(self.state["chain"])
        outgoing = {}
        for item in self.state.get("canvasConnections", []):
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                continue
            src = str(item[0])
            dst = str(item[1])
            if src != GUITAR_NODE_ID and src not in active_set:
                continue
            if dst != AMP_NODE_ID and dst not in active_set:
                continue
            outgoing[src] = dst
        if GUITAR_NODE_ID not in outgoing:
            return []
        cursor = outgoing.get(GUITAR_NODE_ID)
        chain = []
        seen = {GUITAR_NODE_ID}
        while cursor and cursor not in seen:
            if cursor == AMP_NODE_ID:
                return sanitize_chain(chain)
            if cursor not in active_set:
                return []
            chain.append(cursor)
            seen.add(cursor)
            cursor = outgoing.get(cursor)
        return []

    def auto_wire_active_pedals(self):
        chain = sanitize_chain(self.state["chain"])
        if not chain:
            self.state["canvasConnections"] = []
            self.render_all()
            self.persist_state(silent=True)
            return
        auto_connections = [[GUITAR_NODE_ID, chain[0]]]
        for idx in range(len(chain) - 1):
            auto_connections.append([chain[idx], chain[idx + 1]])
        auto_connections.append([chain[-1], AMP_NODE_ID])
        self.state["canvasConnections"] = auto_connections
        self.render_all()
        self.persist_state(silent=True)

    def clear_cables(self):
        self.state["canvasConnections"] = []
        self.render_all()
        self.persist_state(silent=True)

    def clean_up_layout(self):
        chain = sanitize_chain(self.state["chain"])
        if not chain:
            return
        connected = self.compute_connected_chain()
        connected_ids = [pedal_id for pedal_id in chain if pedal_id in connected]
        staged_ids = [pedal_id for pedal_id in chain if pedal_id not in connected]

        min_x, max_x, min_y, max_y = self.board_canvas.pedal_position_bounds()
        signal_slots = self.collect_horizontal_chain_slots(
            max(len(connected_ids) * 3, 16),
            x_range=(min_x, max_x),
            y_range=(min_y + 90, max_y),
        )
        if len(signal_slots) < len(connected_ids):
            signal_slots = self.collect_horizontal_chain_slots(
                max(len(chain) * 3, 18),
                x_range=(min_x, max_x),
                y_range=(min_y, max_y),
            )
        if len(signal_slots) < len(connected_ids):
            signal_slots.extend(
                self.collect_layout_slots(
                    max(len(chain) * 3, 18),
                    x_range=(min_x, max_x),
                    y_range=(min_y, max_y),
                    right_to_left=True,
                )
            )

        parking_y1 = min(max_y, min_y + self.board_canvas.PEDAL_SIZE.height() + 40)
        parking_slots = self.collect_layout_slots(
            max(len(staged_ids) * 4, 12),
            y_range=(min_y, parking_y1),
            right_to_left=False,
        )
        if len(parking_slots) < len(staged_ids):
            right_column_x0 = max(min_x, max_x - self.board_canvas.PEDAL_SIZE.width() - 6)
            parking_slots.extend(
                self.collect_layout_slots(
                    max(len(staged_ids) * 4, 12),
                    x_range=(right_column_x0, max_x),
                    y_range=(min_y, max_y),
                    right_to_left=False,
                )
            )

        fallback_slots = self.collect_layout_slots(max(len(chain) * 4, 24), right_to_left=True)
        positions = self.state.setdefault("canvasPositions", {})
        used_rects = []

        for pedal_id in connected_ids:
            slot = self.choose_slot(signal_slots, used_rects)
            if slot is None:
                slot = self.choose_slot(fallback_slots, used_rects) or self.board_canvas.clamp_pedal_position(QtCore.QPoint(min_x, min_y))
            positions[pedal_id] = [slot.x(), slot.y()]
            used_rects.append(QtCore.QRect(slot, self.board_canvas.PEDAL_SIZE))

        for pedal_id in staged_ids:
            slot = self.choose_slot(parking_slots, used_rects)
            if slot is None:
                slot = self.choose_slot(fallback_slots, used_rects) or self.board_canvas.clamp_pedal_position(QtCore.QPoint(max_x, min_y))
            positions[pedal_id] = [slot.x(), slot.y()]
            used_rects.append(QtCore.QRect(slot, self.board_canvas.PEDAL_SIZE))

        self.render_all()
        self.persist_state(silent=True)

    def optimize_chain(self):
        preset = GENRE_PRESETS[self.state["genre"]]
        seed = self.state["chain"] if self.state["chain"] else preset["optimized_chain"]
        analysis = run_order_lab(self.state["genre"], seed, self.state["guitarType"])
        self.state["chain"] = sanitize_chain(analysis["best_chain"])
        self.ensure_canvas_state()
        self.auto_wire_active_pedals()
        self.clean_up_layout()
        self.render_all()
        self.persist_state(silent=True)
        QtWidgets.QMessageBox.information(
            self,
            "Optimize",
            f"{preset['label']} optimized ({analysis['permutations_checked']:,} layouts checked).",
        )

    def reset_chain(self):
        self.state["chain"] = list(DEFAULT_CHAIN)
        self.ensure_canvas_state()
        self.auto_wire_active_pedals()
        self.clean_up_layout()
        self.render_all()
        self.persist_state(silent=True)

    def render_all(self):
        self.state["chain"] = sanitize_chain(self.state["chain"])
        self.ensure_canvas_state()
        self.connected_chain = self.compute_connected_chain()

        recommendation = build_recommendation(
            self.state["genre"],
            self.connected_chain,
            self.state["guitarType"],
            self.state["ampModel"],
            self.state["guitarProfile"],
        )

        self.update_bank_list()
        self.update_chain_list()
        knob_map = {}
        for pedal_id in self.state["chain"]:
            pedal_settings = recommendation["pedals"].get(pedal_id, {})
            knob_map[pedal_id] = pedal_knob_values(pedal_id, pedal_settings)
        self.board_canvas.set_board_data(
            self.state["chain"],
            self.state.get("canvasPositions", {}),
            self.state.get("canvasConnections", []),
            recommendation["amp_label"],
            recommendation.get("amp_model_key", ""),
            self.state.get("guitarType", "electric"),
            self.state.get("guitarProfile", "electric_2_knob_toggle"),
            knob_map,
        )

        tone_match = self.calculate_tone_match(self.connected_chain, recommendation["optimized_chain"])
        self.chain_score.setText(f"Tone Match: {tone_match}%")
        active_text = ", ".join(PEDAL_LIBRARY[pid] for pid in self.state["chain"]) if self.state["chain"] else "(none)"
        connected_text = self.chain_to_text(self.connected_chain)
        self.chain_summary.setText(f"Connected chain: {connected_text}\nActive pedals: {active_text}")

        self.render_builder_preview(recommendation)
        self.render_settings_tab(recommendation)
        self.render_summary_tab(recommendation)

    def render_builder_preview(self, recommendation):
        guitar = recommendation.get("guitar")
        if guitar:
            rows = [f"{guitar['label']}"]
            for key, value in guitar["settings"].items():
                if key == "note":
                    continue
                rows.append(f"- {key}: {value}")
            if guitar.get("volumeAdvice"):
                rows.append(f"- Volume: {guitar['volumeAdvice']}")
            self.guitar_preview.setPlainText("\n".join(rows))
        else:
            self.guitar_preview.setPlainText("Select a guitar profile.")

        amp = recommendation["amp"]
        amp_lines = [
            f"{recommendation['amp_label']} ({amp.get('voicing', 'Custom')})",
            f"Gain: {quick_knob(amp['gain'])}",
            f"Bass: {quick_knob(amp['bass'])}",
            f"Mid: {quick_knob(amp['mid'])}",
            f"Treble: {quick_knob(amp['treble'])}",
            f"Presence: {quick_knob(amp['presence'])}",
            f"Master: {quick_knob(amp['master'])}",
        ]
        self.amp_preview.setPlainText("\n".join(amp_lines))

        playbook = STYLE_PLAYBOOK.get(self.state["genre"], STYLE_PLAYBOOK["rock"])
        pb_lines = [
            "Heard Chords:",
            *[f"- {line}" for line in playbook.get("concertProgression", [])],
            "",
            "Play These Shapes (Capo 5):",
            *[f"- {line}" for line in playbook.get("capo5Shapes", [])],
            "",
            f"Open Shapes: {', '.join(playbook.get('openShapes', []))}",
            f"Capo Mapping: {playbook.get('capoGuide', '')}",
            f"G-Shape Pentatonic Fret: {playbook.get('pentatonicFret', '')}",
            f"Solo Guide: {playbook.get('soloGuide', '')}",
        ]
        self.playbook_preview.setPlainText("\n".join(pb_lines))

    def render_settings_tab(self, recommendation):
        self.clear_layout_widgets(self.pedal_cards_grid)
        if self.connected_chain:
            self.pedal_empty_label.hide()
            for idx, pedal_id in enumerate(self.connected_chain):
                pedal_settings = recommendation["pedals"].get(pedal_id, {})
                card = self.build_pedal_settings_card(pedal_id, pedal_settings)
                row = idx // 5
                col = idx % 5
                self.pedal_cards_grid.addWidget(card, row, col)
        else:
            self.pedal_empty_label.show()

        guitar = recommendation.get("guitar")
        if guitar:
            g_lines = [guitar["label"]]
            for key, value in guitar["settings"].items():
                if key == "note":
                    continue
                g_lines.append(f"- {key}: {value}")
            if guitar.get("volumeAdvice"):
                g_lines.append(f"- Volume: {guitar['volumeAdvice']}")
            self.guitar_settings_text.setPlainText("\n".join(g_lines))
        else:
            self.guitar_settings_text.setPlainText("No guitar settings.")

        amp = recommendation["amp"]
        a_lines = [
            recommendation["amp_label"],
            f"Voice: {amp.get('voicing', 'Custom')}",
            f"Gain: {quick_knob(amp['gain'])}",
            f"Bass: {quick_knob(amp['bass'])}",
            f"Mid: {quick_knob(amp['mid'])}",
            f"Treble: {quick_knob(amp['treble'])}",
            f"Presence: {quick_knob(amp['presence'])}",
            f"Master: {quick_knob(amp['master'])}",
        ]
        self.amp_settings_text.setPlainText("\n".join(a_lines))

        self.justification_text.setPlainText("\n".join(f"- {line}" for line in recommendation["notes"]))

    def format_pedal_block(self, pedal_id, settings):
        title = PEDAL_LIBRARY[pedal_id]
        lines = [title]

        if pedal_id in {"sd1", "bd2", "ds1"}:
            for key in sorted(settings.keys()):
                value = settings[key]
                if isinstance(value, (int, float)):
                    lines.append(f"- {key}: {quick_knob(value)}")
                else:
                    lines.append(f"- {key}: {value}")
            return "\n".join(lines)

        if pedal_id == "cs3":
            for key in ["sustain", "attack", "tone", "level"]:
                value = settings.get(key, 50)
                lines.append(f"- {key}: {quick_knob(value)}")
            return "\n".join(lines)

        if pedal_id in {"ge7", "eq10"}:
            mode = settings.get("mode", "Contour")
            lines.append(f"- mode: {mode}")
            if "level" in settings:
                lines.append(f"- level: {db_value(settings['level'])}")
            if "volume" in settings:
                lines.append(f"- output: {db_value(settings['volume'])}")
            if "gain" in settings:
                lines.append(f"- gain: {db_value(settings['gain'])}")
            for band, value in settings.get("bands", {}).items():
                lines.append(f"- {band} Hz: {db_value(value)}")
            return "\n".join(lines)

        if pedal_id == "ch1":
            for key in ["effectLevel", "eq", "rate", "depth"]:
                lines.append(f"- {key}: {quick_knob(settings.get(key, 50))}")
            return "\n".join(lines)

        if pedal_id == "dd3":
            lines.append(f"- mode: {settings.get('mode', '320 ms')}")
            for key in ["eLevel", "fBack", "dTime"]:
                lines.append(f"- {key}: {quick_knob(settings.get(key, 50))}")
            return "\n".join(lines)

        if pedal_id == "rc30":
            for key in ["rhythmType", "rhythmLevel", "track1", "track2", "quantize"]:
                lines.append(f"- {key}: {settings.get(key)}")
            return "\n".join(lines)

        for key, value in settings.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def render_summary_tab(self, recommendation):
        amp = recommendation["amp"]
        unpatched = [pid for pid in self.state["chain"] if pid not in self.connected_chain]
        style_chords = extract_concert_chords_for_genre(self.state["genre"])
        best_key = determine_best_nashville_key(style_chords)
        bullets = [
            f"- Style: {recommendation['label']}",
            f"- Guitar: {'Acoustic' if self.state['guitarType'] == 'acoustic' else 'Electric'} | Profile: {recommendation['guitar']['label'] if recommendation.get('guitar') else 'Default'}",
            f"- Amp: {recommendation['amp_label']} ({amp.get('voicing', 'Custom')})",
            f"- Amp Dial: Gain {quick_knob(amp['gain'])}, Bass {quick_knob(amp['bass'])}, Mid {quick_knob(amp['mid'])}, Treble {quick_knob(amp['treble'])}, Presence {quick_knob(amp['presence'])}, Master {quick_knob(amp['master'])}",
            f"- Signal Chain: {self.chain_to_text(self.connected_chain)}",
            f"- Suggested Key Center: {best_key} (from concert progression analysis)",
        ]
        for pedal_id in self.connected_chain:
            bullets.append(f"- {PEDAL_LIBRARY[pedal_id]} active in chain")
        if unpatched:
            bullets.append("- Not currently chained to amp: " + ", ".join(PEDAL_LIBRARY[pid] for pid in unpatched))

        self.summary_text.setPlainText("\n".join(bullets))
        self.circle_of_fifths.set_highlighted_chords(style_chords)
        if style_chords:
            self.circle_hint.setText("Highlighted chords: " + ", ".join(style_chords))
        else:
            self.circle_hint.setText("No style progression chords available.")
        self.highlight_nashville_key(best_key)
        self.nashville_hint.setText(f"Best-matching key highlighted: {best_key}")

    def calculate_tone_match(self, chain, optimized_chain):
        if not chain:
            return 0
        common = [pid for pid in chain if pid in optimized_chain]
        if not common:
            return 0

        pair_total = 0
        pair_correct = 0
        for i in range(len(common)):
            for j in range(i + 1, len(common)):
                pair_total += 1
                if optimized_chain.index(common[i]) < optimized_chain.index(common[j]):
                    pair_correct += 1

        order_score = 100 if pair_total == 0 else (pair_correct / pair_total) * 100
        missing = max(0, len(optimized_chain) - len(common))
        missing_penalty = (missing / max(1, len(optimized_chain))) * 34
        return max(0, int(round(order_score - missing_penalty)))

    def chain_to_text(self, chain):
        if not chain:
            return "Guitar -> (empty) -> AMP"
        return "Guitar -> " + " -> ".join(PEDAL_LIBRARY[pid] for pid in chain) + " -> AMP"

    def load_state(self):
        if not STATE_FILE.exists():
            return
        try:
            payload = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return

        genre = payload.get("genre")
        if genre in GENRE_PRESETS:
            self.state["genre"] = genre

        guitar_type = payload.get("guitarType")
        if guitar_type in {"electric", "acoustic"}:
            self.state["guitarType"] = guitar_type

        guitar_profile = payload.get("guitarProfile")
        if guitar_profile in GUITAR_PROFILES:
            self.state["guitarProfile"] = guitar_profile

        amp_model = payload.get("ampModel")
        if amp_model == "auto" or amp_model in AMP_MODELS:
            self.state["ampModel"] = amp_model

        theme_key = payload.get("theme")
        if theme_key in THEMES:
            self.state["theme"] = theme_key

        font_preset = payload.get("fontPreset")
        if font_preset in FONT_PRESETS:
            self.state["fontPreset"] = font_preset
        else:
            font_size = payload.get("fontSize")
            if isinstance(font_size, (int, float)):
                self.state["fontPreset"] = nearest_font_preset(font_size)

        chain = payload.get("chain")
        if isinstance(chain, list):
            self.state["chain"] = sanitize_chain(chain)

        canvas_positions = payload.get("canvasPositions")
        if isinstance(canvas_positions, dict):
            clean_positions = {}
            for key, value in canvas_positions.items():
                if key in PEDAL_LIBRARY and isinstance(value, (list, tuple)) and len(value) == 2:
                    clean_positions[key] = [int(value[0]), int(value[1])]
            self.state["canvasPositions"] = clean_positions

        canvas_connections = payload.get("canvasConnections")
        if isinstance(canvas_connections, list):
            clean_connections = []
            for item in canvas_connections:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    src = str(item[0])
                    dst = str(item[1])
                    if (src in PEDAL_LIBRARY or src == GUITAR_NODE_ID) and (dst in PEDAL_LIBRARY or dst == AMP_NODE_ID):
                        clean_connections.append([src, dst])
            self.state["canvasConnections"] = clean_connections

    def persist_state(self, silent=False):
        payload = {
            "genre": self.state["genre"],
            "guitarType": self.state["guitarType"],
            "guitarProfile": self.state["guitarProfile"],
            "ampModel": self.state["ampModel"],
            "theme": self.state["theme"],
            "fontPreset": self.state["fontPreset"],
            "fontSize": font_pixels_for_preset(self.state["fontPreset"]),
            "chain": self.state["chain"],
            "canvasPositions": self.state.get("canvasPositions", {}),
            "canvasConnections": self.state.get("canvasConnections", []),
        }
        STATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if not silent:
            QtWidgets.QMessageBox.information(self, "Saved", "Saved locally on this device.")

    def apply_theme(self):
        preset_key = self.state.get("fontPreset", "medium")
        font_size = font_pixels_for_preset(preset_key)
        theme = theme_for_key(self.state.get("theme", "dark"))
        self.setStyleSheet(
            f"""
            QWidget {{ background: {theme["bg"]}; color: {theme["text"]}; font-family: 'Trebuchet MS'; font-size: {font_size}px; }}
            QTabWidget::pane {{ border: 1px solid {theme["frame"]}; border-radius: 8px; }}
            QTabBar::tab {{ background: {theme["tab"]}; border: 1px solid {theme["frame"]}; border-bottom: none; padding: 8px 14px; margin-right: 4px; border-top-left-radius: 8px; border-top-right-radius: 8px; }}
            QTabBar::tab:selected {{ background: {theme["tab_selected_bg"]}; color: {theme["tab_selected_fg"]}; font-weight: 700; }}
            QGroupBox {{ border: 1px solid {theme["frame"]}; border-radius: 8px; margin-top: 8px; font-weight: 700; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {theme["group_title"]}; }}
            QComboBox, QListWidget, QTextEdit, QPushButton {{ background: {theme["panel"]}; border: 1px solid {theme["frame"]}; border-radius: 6px; padding: 5px; }}
            QFrame#pedalSettingsCard {{ background: {theme["panel"]}; border: 1px solid {theme["frame"]}; border-radius: 8px; }}
            QLabel#pedalCardTitle {{ font-weight: 700; color: {theme["group_title"]}; }}
            QPushButton:hover {{ border: 1px solid {theme["tab_selected_bg"]}; }}
            QLabel {{ color: {theme["text"]}; }}
            """
        )
        if hasattr(self, "board_canvas"):
            self.board_canvas.set_theme(theme)
        if hasattr(self, "circle_of_fifths"):
            self.circle_of_fifths.set_theme(theme)
        if hasattr(self, "nashville_table"):
            key_name = determine_best_nashville_key(extract_concert_chords_for_genre(self.state.get("genre", "rock")))
            self.highlight_nashville_key(key_name)


def main():
    app = QtWidgets.QApplication([])
    window = PedalArchitectWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
