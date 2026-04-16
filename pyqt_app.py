#!/usr/bin/env python3
"""Pedal Architect desktop app (PyQt5).

Branch: py_app
"""

import copy
import itertools
import json
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


class ReorderListWidget(QtWidgets.QListWidget):
    orderChanged = QtCore.pyqtSignal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.orderChanged.emit()


class PedalBankListWidget(QtWidgets.QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.setDefaultDropAction(QtCore.Qt.CopyAction)

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
        mime.setText(PEDAL_LIBRARY.get(pedal_id, ""))
        drag.setMimeData(mime)
        drag.exec_(QtCore.Qt.CopyAction)


class ChainListWidget(ReorderListWidget):
    bankPedalDropped = QtCore.pyqtSignal(str, int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)

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
            if pedal_id:
                row = self.indexAt(event.pos()).row()
                if row < 0:
                    row = self.count()
                self.bankPedalDropped.emit(pedal_id, row)
            event.acceptProposedAction()
            return
        super().dropEvent(event)


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


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
            "fontSize": 12,
            "chain": list(DEFAULT_CHAIN),
        }

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

    def build_builder_tab(self):
        layout = QtWidgets.QVBoxLayout(self.builder_tab)
        layout.setSpacing(10)

        controls = QtWidgets.QFrame()
        controls_layout = QtWidgets.QHBoxLayout(controls)
        controls_layout.setContentsMargins(8, 8, 8, 8)
        controls_layout.setSpacing(10)

        self.genre_combo = QtWidgets.QComboBox()
        self.guitar_type_combo = QtWidgets.QComboBox()
        self.guitar_profile_combo = QtWidgets.QComboBox()
        self.amp_combo = QtWidgets.QComboBox()
        self.font_size_spin = QtWidgets.QSpinBox()
        self.font_size_spin.setRange(10, 24)
        self.font_size_spin.setSingleStep(1)
        self.font_size_spin.setSuffix(" px")

        self.add_labeled_control(controls_layout, "Style", self.genre_combo)
        self.add_labeled_control(controls_layout, "Guitar", self.guitar_type_combo)
        self.add_labeled_control(controls_layout, "Guitar Controls", self.guitar_profile_combo)
        self.add_labeled_control(controls_layout, "Amp", self.amp_combo)
        self.add_labeled_control(controls_layout, "Font Size", self.font_size_spin)

        self.optimize_btn = QtWidgets.QPushButton("Optimize For Me")
        self.reset_btn = QtWidgets.QPushButton("Reset Chain")
        self.save_btn = QtWidgets.QPushButton("Save Offline")

        controls_layout.addWidget(self.optimize_btn)
        controls_layout.addWidget(self.reset_btn)
        controls_layout.addWidget(self.save_btn)

        layout.addWidget(controls)

        body = QtWidgets.QHBoxLayout()
        body.setSpacing(10)

        bank_group = QtWidgets.QGroupBox("Pedal Bank")
        bank_layout = QtWidgets.QVBoxLayout(bank_group)
        self.bank_list = PedalBankListWidget()
        self.bank_list.setAlternatingRowColors(True)
        bank_layout.addWidget(self.bank_list)

        chain_group = QtWidgets.QGroupBox("Signal Chain")
        chain_layout = QtWidgets.QVBoxLayout(chain_group)
        self.chain_list = ChainListWidget()
        self.chain_list.setAlternatingRowColors(True)
        chain_layout.addWidget(self.chain_list)
        self.chain_score = QtWidgets.QLabel("Tone Match: --")
        self.chain_summary = QtWidgets.QLabel("")
        self.chain_score.setStyleSheet("font-weight: 700;")
        chain_layout.addWidget(self.chain_score)
        chain_layout.addWidget(self.chain_summary)
        remove_btn = QtWidgets.QPushButton("Remove Selected Pedal")
        chain_layout.addWidget(remove_btn)
        self.remove_chain_btn = remove_btn

        right_group = QtWidgets.QGroupBox("Guitar + Amp")
        right_layout = QtWidgets.QVBoxLayout(right_group)
        self.guitar_preview = QtWidgets.QTextEdit()
        self.guitar_preview.setReadOnly(True)
        self.guitar_preview.setPlaceholderText("Guitar controls preview")
        self.amp_preview = QtWidgets.QTextEdit()
        self.amp_preview.setReadOnly(True)
        self.amp_preview.setPlaceholderText("Amp settings preview")
        self.playbook_preview = QtWidgets.QTextEdit()
        self.playbook_preview.setReadOnly(True)
        self.playbook_preview.setPlaceholderText("Style progression + solo guide")
        right_layout.addWidget(QtWidgets.QLabel("Guitar View"))
        right_layout.addWidget(self.guitar_preview, 1)
        right_layout.addWidget(QtWidgets.QLabel("Amp (Chain End)"))
        right_layout.addWidget(self.amp_preview, 1)
        right_layout.addWidget(QtWidgets.QLabel("Style Playbook"))
        right_layout.addWidget(self.playbook_preview, 2)

        body.addWidget(bank_group, 1)
        body.addWidget(chain_group, 2)
        body.addWidget(right_group, 2)

        layout.addLayout(body, 1)

        self.populate_controls()
        self.bind_builder_events()

    def build_settings_tab(self):
        layout = QtWidgets.QHBoxLayout(self.settings_tab)
        layout.setSpacing(10)

        self.pedals_settings_text = self.make_settings_column(layout, "Pedals")
        self.guitar_settings_text = self.make_settings_column(layout, "Guitar")
        self.amp_settings_text = self.make_settings_column(layout, "Amp")
        self.justification_text = self.make_settings_column(layout, "Justification")

    def build_summary_tab(self):
        layout = QtWidgets.QVBoxLayout(self.summary_tab)
        group = QtWidgets.QGroupBox("Rig Summary")
        group_layout = QtWidgets.QVBoxLayout(group)
        self.summary_text = QtWidgets.QTextEdit()
        self.summary_text.setReadOnly(True)
        group_layout.addWidget(self.summary_text)
        layout.addWidget(group)

    def add_labeled_control(self, layout, label_text, widget):
        wrapper = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(label_text)
        label.setMinimumWidth(96)
        wrapper.addWidget(label)
        wrapper.addWidget(widget, 1)
        layout.addLayout(wrapper)

    def make_settings_column(self, layout, title):
        group = QtWidgets.QGroupBox(title)
        group_layout = QtWidgets.QVBoxLayout(group)
        text = QtWidgets.QTextEdit()
        text.setReadOnly(True)
        group_layout.addWidget(text)
        layout.addWidget(group, 1)
        return text

    def bind_builder_events(self):
        self.genre_combo.currentIndexChanged.connect(self.on_controls_changed)
        self.guitar_type_combo.currentIndexChanged.connect(self.on_controls_changed)
        self.guitar_profile_combo.currentIndexChanged.connect(self.on_controls_changed)
        self.amp_combo.currentIndexChanged.connect(self.on_controls_changed)
        self.font_size_spin.valueChanged.connect(self.on_font_size_changed)

        self.optimize_btn.clicked.connect(self.optimize_chain)
        self.reset_btn.clicked.connect(self.reset_chain)
        self.save_btn.clicked.connect(self.persist_state)

        self.bank_list.itemDoubleClicked.connect(self.add_selected_bank_item)
        self.chain_list.itemDoubleClicked.connect(self.remove_selected_chain_item)
        self.chain_list.orderChanged.connect(self.chain_reordered)
        self.chain_list.bankPedalDropped.connect(self.insert_pedal_into_chain)
        self.remove_chain_btn.clicked.connect(self.remove_selected_chain_item)

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

        self.set_combo_by_data(self.genre_combo, self.state["genre"])
        self.set_combo_by_data(self.guitar_type_combo, self.state["guitarType"])
        self.set_combo_by_data(self.guitar_profile_combo, self.state["guitarProfile"])
        self.set_combo_by_data(self.amp_combo, self.state["ampModel"])
        self.font_size_spin.setValue(clamp(int(self.state.get("fontSize", 12)), 10, 24))

        self._loading_ui = False

    def set_combo_by_data(self, combo, value):
        for idx in range(combo.count()):
            if combo.itemData(idx) == value:
                combo.setCurrentIndex(idx)
                return

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

    def on_font_size_changed(self, value):
        if self._loading_ui:
            return
        self.state["fontSize"] = clamp(int(value), 10, 24)
        self.apply_theme()
        self.persist_state(silent=True)

    def update_bank_list(self):
        self.bank_list.clear()
        chain_set = set(self.state["chain"])
        for pedal_id in BANK_ORDER:
            item_text = PEDAL_LIBRARY[pedal_id]
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, pedal_id)
            if pedal_id in chain_set:
                item.setForeground(QtGui.QColor("#98A39A"))
                item.setText(f"{item_text}  [In chain]")
            self.bank_list.addItem(item)

    def update_chain_list(self):
        self.chain_list.blockSignals(True)
        self.chain_list.clear()
        for pedal_id in self.state["chain"]:
            item = QtWidgets.QListWidgetItem(PEDAL_LIBRARY[pedal_id])
            item.setData(QtCore.Qt.UserRole, pedal_id)
            self.chain_list.addItem(item)
        self.chain_list.blockSignals(False)

    def chain_reordered(self):
        self.state["chain"] = self.current_chain_from_widget()
        self.render_all()
        self.persist_state(silent=True)

    def current_chain_from_widget(self):
        chain = []
        for i in range(self.chain_list.count()):
            item = self.chain_list.item(i)
            pedal_id = item.data(QtCore.Qt.UserRole)
            if pedal_id:
                chain.append(pedal_id)
        return sanitize_chain(chain)

    def add_selected_bank_item(self, item=None):
        item = item or self.bank_list.currentItem()
        if not item:
            return
        pedal_id = item.data(QtCore.Qt.UserRole)
        if not pedal_id:
            return
        if pedal_id in self.state["chain"]:
            return
        self.state["chain"].append(pedal_id)
        self.render_all()
        self.persist_state(silent=True)

    def insert_pedal_into_chain(self, pedal_id, row):
        if pedal_id not in PEDAL_LIBRARY:
            return
        chain = list(self.state["chain"])
        row = clamp(int(row), 0, len(chain))
        if pedal_id in chain:
            old_index = chain.index(pedal_id)
            chain.pop(old_index)
            if old_index < row:
                row -= 1
        row = clamp(int(row), 0, len(chain))
        chain.insert(row, pedal_id)
        self.state["chain"] = sanitize_chain(chain)
        self.render_all()
        self.persist_state(silent=True)

    def remove_selected_chain_item(self, *_args):
        item = self.chain_list.currentItem()
        if not item:
            return
        pedal_id = item.data(QtCore.Qt.UserRole)
        if pedal_id in self.state["chain"]:
            self.state["chain"].remove(pedal_id)
            self.render_all()
            self.persist_state(silent=True)

    def optimize_chain(self):
        preset = GENRE_PRESETS[self.state["genre"]]
        seed = self.state["chain"] if self.state["chain"] else preset["optimized_chain"]
        analysis = run_order_lab(self.state["genre"], seed, self.state["guitarType"])
        self.state["chain"] = sanitize_chain(analysis["best_chain"])
        self.render_all()
        self.persist_state(silent=True)
        QtWidgets.QMessageBox.information(
            self,
            "Optimize",
            f"{preset['label']} optimized ({analysis['permutations_checked']:,} layouts checked).",
        )

    def reset_chain(self):
        self.state["chain"] = list(DEFAULT_CHAIN)
        self.render_all()
        self.persist_state(silent=True)

    def render_all(self):
        self.state["chain"] = sanitize_chain(self.state["chain"])

        recommendation = build_recommendation(
            self.state["genre"],
            self.state["chain"],
            self.state["guitarType"],
            self.state["ampModel"],
            self.state["guitarProfile"],
        )

        self.update_bank_list()
        self.update_chain_list()

        tone_match = self.calculate_tone_match(self.state["chain"], recommendation["optimized_chain"])
        self.chain_score.setText(f"Tone Match: {tone_match}%")
        self.chain_summary.setText(self.chain_to_text(self.state["chain"]))

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
        pedal_lines = []
        for pedal_id in self.state["chain"]:
            pedal_settings = recommendation["pedals"].get(pedal_id, {})
            pedal_lines.append(self.format_pedal_block(pedal_id, pedal_settings))
        self.pedals_settings_text.setPlainText("\n\n".join(pedal_lines) if pedal_lines else "No pedals in chain.")

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
        bullets = [
            f"- Style: {recommendation['label']}",
            f"- Guitar: {'Acoustic' if self.state['guitarType'] == 'acoustic' else 'Electric'} | Profile: {recommendation['guitar']['label'] if recommendation.get('guitar') else 'Default'}",
            f"- Amp: {recommendation['amp_label']} ({amp.get('voicing', 'Custom')})",
            f"- Amp Dial: Gain {quick_knob(amp['gain'])}, Bass {quick_knob(amp['bass'])}, Mid {quick_knob(amp['mid'])}, Treble {quick_knob(amp['treble'])}, Presence {quick_knob(amp['presence'])}, Master {quick_knob(amp['master'])}",
            f"- Signal Chain: {self.chain_to_text(self.state['chain'])}",
        ]
        for pedal_id in self.state["chain"]:
            bullets.append(f"- {PEDAL_LIBRARY[pedal_id]} active in chain")

        self.summary_text.setPlainText("\n".join(bullets))

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
            return "(empty) -> AMP"
        return " -> ".join(PEDAL_LIBRARY[pid] for pid in chain) + " -> AMP"

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

        font_size = payload.get("fontSize")
        if isinstance(font_size, (int, float)):
            self.state["fontSize"] = clamp(int(font_size), 10, 24)

        chain = payload.get("chain")
        if isinstance(chain, list):
            self.state["chain"] = sanitize_chain(chain)

    def persist_state(self, silent=False):
        payload = {
            "genre": self.state["genre"],
            "guitarType": self.state["guitarType"],
            "guitarProfile": self.state["guitarProfile"],
            "ampModel": self.state["ampModel"],
            "fontSize": self.state["fontSize"],
            "chain": self.state["chain"],
        }
        STATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if not silent:
            QtWidgets.QMessageBox.information(self, "Saved", "Saved locally on this device.")

    def apply_theme(self):
        font_size = clamp(int(self.state.get("fontSize", 12)), 10, 24)
        self.setStyleSheet(
            f"""
            QWidget {{ background: #11161a; color: #e9efe4; font-family: 'Trebuchet MS'; font-size: {font_size}px; }}
            QTabWidget::pane { border: 1px solid #354047; border-radius: 8px; }
            QTabBar::tab { background: #1d252b; border: 1px solid #364149; border-bottom: none; padding: 8px 14px; margin-right: 4px; border-top-left-radius: 8px; border-top-right-radius: 8px; }
            QTabBar::tab:selected { background: #d6fd73; color: #1a230f; font-weight: 700; }
            QGroupBox { border: 1px solid #3b4750; border-radius: 8px; margin-top: 8px; font-weight: 700; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #d6e2cb; }
            QComboBox, QSpinBox, QListWidget, QTextEdit, QPushButton { background: #161f25; border: 1px solid #3a464e; border-radius: 6px; padding: 5px; }
            QPushButton:hover { border: 1px solid #6c7a85; }
            QLabel { color: #cfd8c9; }
            """
        )


def main():
    app = QtWidgets.QApplication([])
    window = PedalArchitectWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
