#!/usr/bin/env python3
"""Pedal Architect desktop app (PyQt5).

Branch: py_app
"""

import copy
import hashlib
import heapq
import itertools
import json
import math
import os
import random
import re
import socket
import sys
import urllib.error
import urllib.request
import uuid
from collections import deque
from datetime import datetime
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets
from data.theory_data import CAGED_SHAPES, SCALE_LIBRARY
from functions.runtime_helpers import (
    clamp as util_clamp,
    db_value as util_db_value,
    percent_from_db as util_percent_from_db,
    quick_knob as util_quick_knob,
    to_clock as util_to_clock,
)
from ui.theme_presets import THEMES, THEME_PRESET_SPECS


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

PEDAL_REFERENCE = {
    "cs3": {
        "name": "BOSS CS-3 Compression Sustainer",
        "summary": "Smooths level spikes and adds sustain so picking feels even and articulate.",
        "controls": ["Level", "Tone", "Attack", "Sustain"],
        "configure": [
            "Start with sustain near noon, then raise only until notes bloom without pumping.",
            "Use attack around noon for balanced transient response.",
            "Trim tone if top-end gets too sharp after compression.",
        ],
        "possibilities": [
            "Country snap with fast attack and moderate sustain.",
            "Lead sustain before gain pedals.",
            "Clean rhythm leveling for loop layers.",
        ],
        "placement": [
            "Usually first or near first, before overdrive/distortion.",
            "After gain is possible, but tends to raise hiss and flatten dynamics.",
        ],
    },
    "sd1": {
        "name": "BOSS SD-1 Super OverDrive",
        "summary": "Asymmetrical-clipping overdrive that tightens lows and emphasizes musical mids.",
        "controls": ["Drive", "Tone", "Level"],
        "configure": [
            "For boost use: Drive low, Level high, Tone just above noon.",
            "For standalone crunch: Drive to noon-ish and Level near unity.",
            "Reduce Tone slightly with bright pickups or bright amps.",
        ],
        "possibilities": [
            "Classic mid-push rhythm tone.",
            "Tight front-end boost into DS-1/high-gain amps.",
            "Low-gain always-on edge-of-breakup texture.",
        ],
        "placement": [
            "Commonly before DS-1 or amp distortion as a tightening boost.",
            "Can follow BD-2 when you want extra focus and sustain.",
        ],
    },
    "bd2": {
        "name": "BOSS BD-2 Blues Driver",
        "summary": "Touch-sensitive overdrive with wide gain range from mild grit to aggressive breakup.",
        "controls": ["Gain", "Tone", "Level"],
        "configure": [
            "Start with Gain between 10 and 1 o'clock for dynamic breakup.",
            "Use Tone near noon and adjust for pickup brightness.",
            "Set Level to match or slightly lift solo volume.",
        ],
        "possibilities": [
            "Always-on tube-like feel.",
            "Stack with SD-1 for thicker lead voice.",
            "Blues and classic-rock core overdrive.",
        ],
        "placement": [
            "Usually before modulation/time effects.",
            "Relative position vs SD-1 changes whether tone is smoother or tighter.",
        ],
    },
    "ds1": {
        "name": "BOSS DS-1 Distortion",
        "summary": "Hard-edged distortion with strong attack and long sustain for heavier rhythm/lead tones.",
        "controls": ["Dist", "Tone", "Level"],
        "configure": [
            "Set Dist for required saturation first, then tame highs with Tone.",
            "For tighter stacks, run SD-1 before DS-1 with low SD-1 drive.",
            "Keep Level high enough to cut in mix without overloading later stages.",
        ],
        "possibilities": [
            "Primary distortion for rock/metal/grunge.",
            "Lead boost stage when stacked with SD-1/BD-2.",
            "Aggressive rhythm with pre-EQ tightening.",
        ],
        "placement": [
            "Typically after compressor and before modulation/delay.",
            "Before SD-1 can soften attack and add focused mids from SD-1 output.",
        ],
    },
    "ge7": {
        "name": "BOSS GE-7 Equalizer",
        "summary": "Seven-band EQ plus level slider for precision tone contour and clean boost/cut.",
        "controls": ["100, 200, 400, 800, 1.6k, 3.2k, 6.4k sliders", "Level slider"],
        "configure": [
            "Cut 100/200 Hz to tighten boomy rigs.",
            "Boost 800 Hz-1.6 kHz for mix cut and lead focus.",
            "Use Level slider for clean pre/post gain boost.",
        ],
        "possibilities": [
            "Pre-drive sculpt to change how distortion clips.",
            "Post-drive polish for final mix contour.",
            "Feedback/problem-frequency control for acoustic setups.",
        ],
        "placement": [
            "Before gain for feel/clip-shape changes.",
            "After gain for final tonal balancing.",
            "When paired with 10-band, split stages pre/post for best clarity.",
        ],
    },
    "eq10": {
        "name": "10-Band EQ",
        "summary": "High-resolution frequency shaping with dedicated output/gain control for advanced contouring.",
        "controls": ["31.25 to 16k sliders", "Output", "Gain"],
        "configure": [
            "Start with subtle moves (1-3 dB equivalent) and refine by ear.",
            "Use output/gain controls carefully to avoid added noise.",
            "Trim extreme highs/lows first, then shape mids for articulation.",
        ],
        "possibilities": [
            "Master post-drive tonal sculpting.",
            "Pre-drive voicing to influence saturation character.",
            "Genre switching via saved curve ideas (scooped, mid-forward, bright-clean).",
        ],
        "placement": [
            "Commonly post-drive for final polish.",
            "Can run pre-drive if you want deliberate clip-profile changes.",
        ],
    },
    "ch1": {
        "name": "BOSS CH-1 Super Chorus",
        "summary": "Shimmering chorus for width and movement with controllable EQ focus.",
        "controls": ["Effect Level", "EQ", "Rate", "Depth"],
        "configure": [
            "Set depth/rate lower for subtle widening, higher for obvious swirl.",
            "Use EQ to keep chorus from getting too dark or too brittle.",
            "Balance Effect Level so dry attack remains clear.",
        ],
        "possibilities": [
            "Wide pop cleans and ambient rhythm textures.",
            "Post-gain lead thickening.",
            "Stereo spread (when used in stereo rigs).",
        ],
        "placement": [
            "Most often after gain and before delay/looper.",
            "Before DD-3 usually yields cleaner, more musical repeats.",
        ],
    },
    "dd3": {
        "name": "BOSS DD-3 Digital Delay",
        "summary": "Clear digital repeats from slapback to long rhythmic echoes.",
        "controls": ["E.Level", "F.Back", "D.Time", "Mode"],
        "configure": [
            "Set D.Time and mode first for musical subdivision/space.",
            "Use Feedback modestly unless ambient wash is desired.",
            "Blend E.Level so repeats support rather than mask picking.",
        ],
        "possibilities": [
            "Country slapback and classic rock echoes.",
            "Rhythmic dotted-note textures in pop/ambient contexts.",
            "Pre-looper repeats to print rhythmic movement into loops.",
        ],
        "placement": [
            "Usually near end of chain, after gain/modulation.",
            "Before RC-30 if you want repeats baked into loop recordings.",
        ],
    },
    "rc30": {
        "name": "BOSS RC-30 Loop Station",
        "summary": "Dual-track stereo looper for layered performance, practice, writing, and arrangement.",
        "controls": ["Track 1 level", "Track 2 level", "Rhythm level", "Rhythm type", "Quantize", "Phrase memory"],
        "configure": [
            "Set track levels so overdubs stay balanced over time.",
            "Use quantize/count-in when tight rhythmic loops matter.",
            "Match rhythm level to context; too high can mask guitar dynamics.",
            "Keep loop output below clipping and leave headroom for live playing.",
        ],
        "possibilities": [
            "Dual-part arrangements (rhythm + lead layers).",
            "Verse/chorus style loop building with separate tracks.",
            "Practice engine for timing, improvisation, and harmony.",
            "Live solo performance with progressive overdubs.",
        ],
        "placement": [
            "Best at end of chain when you want loops to capture final tone.",
            "Place earlier only when intentionally processing loop playback downstream.",
        ],
        "advanced": [
            "Track architecture: Track 1 and Track 2 can be balanced independently.",
            "Rhythm engine: choose rhythm type and level to create timing reference without DAW.",
            "Quantize behavior: improves loop seam accuracy for tighter starts/ends.",
            "Phrase memory workflow: save and recall loop ideas for practice/songwriting.",
            "Input planning: guitar/mic/aux paths can be gain-staged differently before recording.",
            "Live reliability: assign predictable record/overdub/playback habits and keep output conservative.",
        ],
    },
}

BANK_ORDER = ["cs3", "sd1", "bd2", "ds1", "ge7", "eq10", "ch1", "dd3", "rc30"]
DEFAULT_CHAIN = ["ge7", "sd1", "ds1", "eq10", "rc30"]

GENRE_PRESETS = {
    "metal": {
        "label": "Metal",
        "optimized_chain": ["cs3", "ge7", "sd1", "ds1", "eq10", "dd3", "rc30"],
        "amp": {"gain": 70, "bass": 58, "mid": 40, "treble": 63, "presence": 62, "master": 56},
        "pedals": {
            "cs3": {"level": 62, "tone": 46, "attack": 64, "sustain": 58},
            "sd1": {"drive": 16, "tone": 61, "level": 82},
            "bd2": {"gain": 24, "tone": 52, "level": 54},
            "ds1": {"dist": 73, "tone": 57, "level": 58},
            "ge7": {"mode": "Pre-drive tighten", "level": 2, "bands": {"100": -4, "200": -2, "400": 0, "800": 2, "1.6k": 1, "3.2k": 3, "6.4k": 2}},
            "eq10": {"mode": "Post-drive sculpt", "volume": 4, "gain": 2, "bands": {"31.25": -4, "62.5": -2, "125": 3, "250": 1, "500": -3, "1k": -1, "2k": 3, "4k": 4, "8k": 1, "16k": -2}},
            "ch1": {"effectLevel": 24, "eq": 55, "rate": 24, "depth": 28},
            "dd3": {"eLevel": 34, "fBack": 22, "dTime": 36, "mode": "320 ms"},
            "rc30": {"rhythmType": "Rock 1", "rhythmLevel": 16, "track1": 70, "track2": 66, "quantize": "On"},
        },
        "notes": [
            "Use SD-1 as a front boost to tighten palm-muted riffs.",
            "Split EQ staging works best here: GE-7 and 10-band should be split pre/post gain for final contour.",
        ],
    },
    "rock": {
        "label": "Rock",
        "optimized_chain": ["cs3", "ge7", "bd2", "sd1", "ds1", "ch1", "dd3", "rc30"],
        "amp": {"gain": 62, "bass": 55, "mid": 57, "treble": 58, "presence": 56, "master": 60},
        "pedals": {
            "cs3": {"level": 58, "tone": 49, "attack": 54, "sustain": 49},
            "sd1": {"drive": 30, "tone": 55, "level": 66},
            "bd2": {"gain": 42, "tone": 54, "level": 61},
            "ds1": {"dist": 50, "tone": 57, "level": 59},
            "ge7": {"mode": "Pre-drive focus", "level": 1, "bands": {"100": -2, "200": 0, "400": 1, "800": 2, "1.6k": 2, "3.2k": 1, "6.4k": 0}},
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
        "optimized_chain": ["cs3", "ge7", "bd2", "sd1", "ch1", "dd3", "rc30"],
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
        "optimized_chain": ["cs3", "ge7", "sd1", "ch1", "dd3", "rc30"],
        "amp": {"gain": 42, "bass": 50, "mid": 52, "treble": 63, "presence": 60, "master": 64},
        "pedals": {
            "cs3": {"level": 61, "tone": 54, "attack": 52, "sustain": 42},
            "sd1": {"drive": 16, "tone": 57, "level": 60},
            "bd2": {"gain": 28, "tone": 56, "level": 56},
            "ds1": {"dist": 30, "tone": 60, "level": 50},
            "ge7": {"mode": "Pre-drive clean shape", "level": 1, "bands": {"100": -4, "200": -2, "400": 0, "800": 1, "1.6k": 2, "3.2k": 2, "6.4k": 1}},
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
        "optimized_chain": ["cs3", "ge7", "sd1", "ch1", "dd3", "rc30"],
        "amp": {"gain": 36, "bass": 48, "mid": 54, "treble": 66, "presence": 65, "master": 65},
        "pedals": {
            "cs3": {"level": 63, "tone": 57, "attack": 58, "sustain": 44},
            "sd1": {"drive": 14, "tone": 61, "level": 58},
            "bd2": {"gain": 22, "tone": 57, "level": 55},
            "ds1": {"dist": 20, "tone": 56, "level": 47},
            "ge7": {"mode": "Pre-drive twang focus", "level": 2, "bands": {"100": -5, "200": -3, "400": -1, "800": 1, "1.6k": 2, "3.2k": 3, "6.4k": 1}},
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
        "optimized_chain": ["cs3", "ge7", "bd2", "sd1", "dd3", "rc30"],
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
        "label": "Acoustic",
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
        "label": "2 knob electric",
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
        "label": "4 knob electric",
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
        "concertProgression": ["Em - C - G - D", "Am - F - C - G"],
        "progressionPool": [
            "Em - C - G - D",
            "Am - F - C - G",
            "Em - D - C - D",
            "Bm - G - D - A",
            "F#m - D - A - E",
            "Dm - Bb - F - C",
            "Em - C - D - Em",
            "Cm - Ab - Eb - Bb",
            "C - Bb - Ab - Bb",
            "E5 - G5 - A5 - C5",
            "B5 - A5 - G5 - A5",
            "Bm - A - G - F#",
        ],
        "popularTop3": [
            "Em - C - G - D",
            "Am - F - C - G",
            "Bm - G - D - A",
        ],
        "capo5Shapes": ["Em - C - G - D", "Em - D - C - D"],
        "openShapes": ["Em", "C", "G", "D", "Am"],
        "capoGuide": "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
        "pentatonicFret": "G-shape minor pentatonic root area at the 8th fret (relative to nut).",
        "soloGuide": "Work the 8th-10th fret pocket with aggressive bends and short repeating motifs.",
    },
    "rock": {
        "concertProgression": ["C - G - Am - F", "G - D - Em - C"],
        "progressionPool": [
            "C - G - Am - F",
            "G - D - Em - C",
            "D - A - Bm - G",
            "A - E - F#m - D",
            "E - B - C#m - A",
            "D - G - A - G",
            "G - C - D - C",
            "A - D - E - D",
            "E - D - A - E",
            "Bm - G - D - A",
            "F - C - Dm - Bb",
            "C - F - G - F",
        ],
        "popularTop3": [
            "C - G - Am - F",
            "G - D - Em - C",
            "D - A - Bm - G",
        ],
        "capo5Shapes": ["G - D - Em - C", "A - D - E - D"],
        "openShapes": ["G", "D", "Em", "C", "A", "E"],
        "capoGuide": "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
        "pentatonicFret": "G-shape minor pentatonic root area at the 8th fret.",
        "soloGuide": "Target chord tones from the 8th-fret G-shape box and resolve on downbeats.",
    },
    "classic-rock": {
        "concertProgression": ["D - G - A - G", "A - D - E - D"],
        "progressionPool": [
            "D - G - A - G",
            "A - D - E - D",
            "E - A - B - A",
            "G - C - D - C",
            "A - E - D - A",
            "C - F - G - F",
            "D - C - G - D",
            "E - D - A - E",
            "G - D - C - G",
            "A7 - D7 - E7 - D7",
            "D7 - G7 - A7 - G7",
            "Bm - A - G - A",
        ],
        "popularTop3": [
            "D - G - A - G",
            "A - D - E - D",
            "E - A - B - A",
        ],
        "capo5Shapes": ["A - D - E - D", "G - C - D - C"],
        "openShapes": ["A", "D", "E", "G", "C"],
        "capoGuide": "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
        "pentatonicFret": "G-shape minor pentatonic root area around the 8th fret.",
        "soloGuide": "Use 8th-fret box bends and vibrato for vintage lead phrasing.",
    },
    "pop": {
        "concertProgression": ["C - G - Am - F", "G - D - Em - C"],
        "progressionPool": [
            "C - G - Am - F",
            "G - D - Em - C",
            "D - A - Bm - G",
            "A - E - F#m - D",
            "F - C - Dm - Bb",
            "F - C - Dm - Bbmaj7",
            "C - Am - F - G",
            "G - Em - C - D",
            "E - B - C#m - A",
            "Bb - F - Gm - Eb",
            "Dm - Bb - F - C",
            "C - F - Am - G",
        ],
        "popularTop3": [
            "C - G - Am - F",
            "G - D - Em - C",
            "D - A - Bm - G",
        ],
        "capo5Shapes": ["G - D - Em - C", "C - G - Am - Fmaj7"],
        "openShapes": ["C", "G", "Am", "Fmaj7", "D", "Em", "Cadd9"],
        "capoGuide": "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
        "pentatonicFret": "G-shape major/minor pentatonic pocket centered near fret 8.",
        "soloGuide": "Keep melodies in the 8th-fret box short, hooky, and rhythm-aware.",
    },
    "country": {
        "concertProgression": ["G - C - D - G", "D - G - A - D"],
        "progressionPool": [
            "G - C - D - G",
            "D - G - A - D",
            "A - D - E - A",
            "E - A - B - E",
            "C - F - G - C",
            "G - Em - C - D",
            "D - Bm - G - A",
            "A - F#m - D - E",
            "G - D - C - G",
            "E - B - A - E",
            "C - G - F - C",
            "D - A - G - D",
        ],
        "popularTop3": [
            "G - C - D - G",
            "D - G - A - D",
            "A - D - E - A",
        ],
        "capo5Shapes": ["G - C - D - G", "D - G - A - D"],
        "openShapes": ["G", "C", "D", "A", "Em"],
        "capoGuide": "Exact mapping: concert C-F-G becomes G-C-D shapes with capo on fret 5.",
        "pentatonicFret": "G-shape pentatonic home position at the 8th fret.",
        "soloGuide": "Use 8th-fret double-stops, quick slides, and bends into chord tones.",
    },
    "hip-hop": {
        "concertProgression": ["Am7 - Fmaj7 - C - Gsus2", "Dm7 - C - Bbmaj7 - Am7"],
        "progressionPool": [
            "Am7 - Fmaj7 - C - Gsus2",
            "Dm7 - C - Bbmaj7 - Am7",
            "Em7 - Cmaj7 - G - Dsus2",
            "Fm7 - Dbmaj7 - Ab - Eb",
            "Cm7 - Abmaj7 - Eb - Bb",
            "Bm7 - Gmaj7 - D - A",
            "Am7 - G - Fmaj7 - Em7",
            "Dm7 - Bbmaj7 - F - C",
            "Em9 - Cmaj7 - G6 - Dadd9",
            "Cm7 - Bb - Abmaj7 - Gm7",
            "F#m7 - Dmaj7 - A - E",
            "Gm7 - Ebmaj7 - Bb - F",
        ],
        "popularTop3": [
            "Am7 - Fmaj7 - C - Gsus2",
            "Dm7 - C - Bbmaj7 - Am7",
            "Em7 - Cmaj7 - G - Dsus2",
        ],
        "capo5Shapes": ["Em7 - Cmaj7 - G - Dsus2", "Am7 - G - Fmaj7 - Em7"],
        "openShapes": ["Em7", "Cmaj7", "G", "Dsus2", "Am7", "Fmaj7"],
        "capoGuide": "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
        "pentatonicFret": "G-shape minor pentatonic around fret 8 (A-minor feel with capo 5).",
        "soloGuide": "Use sparse 8th-fret pocket phrases, rhythmic rests, and short slides.",
    },
    "blues": {
        "concertProgression": ["A7 - D7 - E7 - D7", "E7 - A7 - B7 - A7"],
        "progressionPool": [
            "A7 - D7 - E7 - D7",
            "E7 - A7 - B7 - A7",
            "D7 - G7 - A7 - G7",
            "G7 - C7 - D7 - C7",
            "A7 - A7 - D7 - A7",
            "E7 - D7 - A7 - E7",
            "C7 - F7 - G7 - F7",
            "B7 - E7 - F#7 - E7",
            "A7 - D9 - E9 - D9",
            "E7 - A7 - E7 - B7",
            "G7 - G7 - C7 - G7",
            "D7 - A7 - G7 - D7",
        ],
        "popularTop3": [
            "A7 - D7 - E7 - D7",
            "E7 - A7 - B7 - A7",
            "D7 - G7 - A7 - G7",
        ],
        "capo5Shapes": ["E7 - A7 - B7 - A7", "A7 - D7 - E7 - D7"],
        "openShapes": ["E7", "A7", "B7", "D7", "G"],
        "capoGuide": "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
        "pentatonicFret": "G-shape minor pentatonic around the 8th fret with blue-note passing tones.",
        "soloGuide": "Target roots and b5 color tones in the 8th-fret box on turnarounds.",
    },
}

CRAZY_SCALE_LIBRARY = {
    "hungarian_minor": {
        "name": "Hungarian Minor",
        "formula": "1 2 b3 #4 5 b6 7",
        "intervals": [0, 2, 3, 6, 7, 8, 11],
        "why": "Tense minor color with a raised fourth for dramatic lead movement.",
    },
    "phrygian_dominant": {
        "name": "Phrygian Dominant",
        "formula": "1 b2 3 4 5 b6 b7",
        "intervals": [0, 1, 4, 5, 7, 8, 10],
        "why": "Exotic dominant tension that still resolves strongly to the tonic.",
    },
    "double_harmonic_major": {
        "name": "Double Harmonic Major",
        "formula": "1 b2 3 4 5 b6 7",
        "intervals": [0, 1, 4, 5, 7, 8, 11],
        "why": "Wide-interval dramatic sound that keeps a major third center.",
    },
    "lydian_dominant": {
        "name": "Lydian Dominant",
        "formula": "1 2 3 #4 5 6 b7",
        "intervals": [0, 2, 4, 6, 7, 9, 10],
        "why": "Bright #4 color with dominant pull; great for modern fusion flavors.",
    },
    "harmonic_minor": {
        "name": "Harmonic Minor",
        "formula": "1 2 b3 4 5 b6 7",
        "intervals": [0, 2, 3, 5, 7, 8, 11],
        "why": "Minor scale with a leading tone for strong melodic resolution.",
    },
    "whole_tone": {
        "name": "Whole Tone",
        "formula": "1 2 3 #4 #5 b7",
        "intervals": [0, 2, 4, 6, 8, 10],
        "why": "Symmetrical floating sound for unexpected modern transitions.",
    },
}

CRAZY_SCALE_BY_GENRE = {
    "metal": ["hungarian_minor", "phrygian_dominant", "double_harmonic_major", "harmonic_minor"],
    "rock": ["harmonic_minor", "lydian_dominant", "phrygian_dominant", "hungarian_minor"],
    "classic-rock": ["harmonic_minor", "lydian_dominant", "whole_tone"],
    "pop": ["lydian_dominant", "whole_tone", "harmonic_minor"],
    "country": ["lydian_dominant", "harmonic_minor", "whole_tone"],
    "hip-hop": ["phrygian_dominant", "whole_tone", "lydian_dominant", "hungarian_minor"],
    "blues": ["phrygian_dominant", "harmonic_minor", "whole_tone"],
}

USUAL_KEYS_BY_GENRE = {
    "metal": ["E", "D", "A", "C", "B"],
    "rock": ["E", "A", "D", "G", "C"],
    "classic-rock": ["A", "E", "D", "G", "C"],
    "pop": ["C", "G", "D", "A", "F"],
    "country": ["G", "D", "A", "E", "C"],
    "hip-hop": ["Am", "Em", "Dm", "F", "C"],
    "blues": ["E", "A", "G", "C", "D"],
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

if getattr(sys, "frozen", False):
    APP_ROOT = Path(sys.executable).resolve().parent
else:
    APP_ROOT = Path(__file__).resolve().parent

STATE_FILE = APP_ROOT / ".pedal_architect_py_state.json"
APP_CONFIG_FILENAME = "pyqt_app_config.json"
APP_CONFIG_FILE = APP_ROOT / APP_CONFIG_FILENAME
SECRETS_CONFIG_FILE = APP_ROOT / ".secrets" / APP_CONFIG_FILENAME
FEEDBACK_LIMITER_FILE = APP_ROOT / ".pedal_architect_feedback_limits.json"
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
# Theme definitions are sourced from `ui/theme_presets.py`.
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
PEDAL_IMAGE_FILES = {
    "cs3": "cs3.png",
    "sd1": "sd1.png",
    "bd2": "bd2.png",
    "ds1": "ds1.png",
    "ge7": "ge7.png",
    "eq10": "eq10.png",
    "ch1": "ch1.png",
    "dd3": "dd3.png",
    "rc30": "rc30.png",
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

DEFAULT_APP_CONFIG = {
    "feedback": {
        "enabled": True,
        "webhook_url": "",
        "timeout_sec": 8,
        "limiter": {
            "max_per_day": 24,
            "max_per_user_per_day": 4,
            "max_per_user_total": 40,
            "hard_limit_total": 5000,
        },
    },
    "donate": {
        "paypal_url": "",
        "venmo_url": "",
        "zelle_handle": "",
    },
}

def pedal_asset_path(filename):
    return Path(__file__).resolve().parent / "assets" / "pedals" / filename


NOTE_TO_PITCH_CLASS = {
    "C": 0,
    "Db": 1,
    "D": 2,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "Ab": 8,
    "A": 9,
    "Bb": 10,
    "B": 11,
}
PITCH_CLASS_CANONICAL = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
PITCH_CLASS_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SHARP_KEY_SIGNATURES = {"G", "D", "A", "E", "B", "F#", "C#"}
STANDARD_TUNING_PCS_TOP_TO_BOTTOM = [4, 11, 7, 2, 9, 4]  # E, B, G, D, A, E
STANDARD_TUNING_PCS_LOW_TO_HIGH = list(reversed(STANDARD_TUNING_PCS_TOP_TO_BOTTOM))
# CAGED shape and scale data are sourced from `data/theory_data.py`.


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
    PEDAL_JACK_INSET = 6
    PEDAL_JACK_RADIUS = 4
    PEDAL_ROUTE_PADDING = 2
    JACK_OUTSET = 4
    CONTROL_BUTTON_SIZE = 18
    CONTROL_BUTTON_GAP = 3
    DRAG_FRAME_MS = 12

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
        self.drag_pending_pos = None
        self.drag_update_timer = QtCore.QTimer(self)
        self.drag_update_timer.setSingleShot(True)
        self.drag_update_timer.timeout.connect(self.flush_drag_position)
        self.link_start = None
        self.preview_link_to = None
        self.guitar_pixmaps = {}
        self.pedal_pixmaps = {}
        self.load_guitar_pixmaps()
        self.load_pedal_pixmaps()

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

    def load_pedal_pixmaps(self):
        for pedal_id, filename in PEDAL_IMAGE_FILES.items():
            path = pedal_asset_path(filename)
            pixmap = QtGui.QPixmap(str(path))
            if not pixmap.isNull():
                self.pedal_pixmaps[pedal_id] = pixmap

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
        return QtCore.QPoint(rect.right() + self.JACK_OUTSET, rect.center().y())

    def guitar_output_pos(self):
        rect = self.guitar_rect()
        return QtCore.QPoint(rect.left() - self.JACK_OUTSET, rect.center().y() + max(10, rect.height() // 6))

    def pedal_rect(self, pedal_id):
        position = self.pedal_positions.get(pedal_id, QtCore.QPoint(16, 16))
        return QtCore.QRect(position, self.PEDAL_SIZE)

    def pedal_input_pos(self, pedal_id):
        rect = self.pedal_rect(pedal_id)
        return QtCore.QPoint(rect.right() + self.JACK_OUTSET, rect.center().y())

    def pedal_output_pos(self, pedal_id):
        rect = self.pedal_rect(pedal_id)
        return QtCore.QPoint(rect.left() - self.JACK_OUTSET, rect.center().y())

    def pedal_remove_button_rect(self, pedal_id):
        rect = self.pedal_rect(pedal_id)
        size = self.CONTROL_BUTTON_SIZE
        return QtCore.QRect(rect.right() - size - 4, rect.top() + 4, size, size)

    def pedal_connect_button_rect(self, pedal_id, side):
        rect = self.pedal_rect(pedal_id)
        size = self.CONTROL_BUTTON_SIZE
        x = rect.left() + 2 if side == "output" else rect.right() - size - 2
        y = rect.center().y() - size - (self.CONTROL_BUTTON_GAP // 2)
        return QtCore.QRect(x, y, size, size)

    def pedal_disconnect_button_rect(self, pedal_id, side):
        rect = self.pedal_connect_button_rect(pedal_id, side)
        return QtCore.QRect(rect.left(), rect.bottom() + self.CONTROL_BUTTON_GAP, rect.width(), rect.height())

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

    def jack_hit(self, point, center, radius=11):
        dx = point.x() - center.x()
        dy = point.y() - center.y()
        return (dx * dx + dy * dy) <= (radius * radius)

    def find_output_source(self, point):
        if self.jack_hit(point, self.guitar_output_pos(), 13):
            return GUITAR_NODE_ID
        for pedal_id in reversed(self.pedal_ids):
            if self.pedal_connect_button_rect(pedal_id, "output").contains(point):
                return pedal_id
            if self.jack_hit(point, self.pedal_output_pos(pedal_id), 12):
                return pedal_id
        return None

    def find_input_target(self, point):
        if self.jack_hit(point, self.amp_input_pos(), 14):
            return AMP_NODE_ID
        for pedal_id in reversed(self.pedal_ids):
            if self.pedal_connect_button_rect(pedal_id, "input").contains(point):
                return pedal_id
            if self.jack_hit(point, self.pedal_input_pos(pedal_id), 12):
                return pedal_id
        return None

    def flush_drag_position(self):
        if not self.dragging_pedal:
            self.drag_pending_pos = None
            return
        if self.drag_pending_pos is None:
            return
        pedal_id = self.dragging_pedal
        new_pos = self.drag_pending_pos
        self.drag_pending_pos = None
        current = self.pedal_positions.get(pedal_id)
        if current is None or current != new_pos:
            self.pedal_positions[pedal_id] = new_pos
            self.update()

    def draw_flow_markers(self, painter, points, color, spacing=46):
        if len(points) < 2:
            return
        base = QtGui.QColor(color)
        luminance = (0.2126 * base.redF()) + (0.7152 * base.greenF()) + (0.0722 * base.blueF())
        fill_color = base.lighter(165) if luminance < 0.45 else base.darker(165)
        outline_color = base.darker(210) if luminance > 0.45 else base.lighter(190)
        fill_color.setAlpha(190)
        outline_color.setAlpha(145)
        painter.setPen(QtGui.QPen(outline_color, 0.9))
        painter.setBrush(QtGui.QBrush(fill_color))

        for idx in range(len(points) - 1):
            p1 = points[idx]
            p2 = points[idx + 1]
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            seg_len = abs(dx) + abs(dy)
            if seg_len < 24:
                continue
            marker_count = max(1, seg_len // spacing)
            for marker_idx in range(marker_count):
                t = float(marker_idx + 1) / float(marker_count + 1)
                mx = p1.x() + int(round(dx * t))
                my = p1.y() + int(round(dy * t))
                if abs(dx) >= abs(dy):
                    if dx >= 0:
                        tri = QtGui.QPolygonF(
                            [
                                QtCore.QPointF(mx + 4.5, my),
                                QtCore.QPointF(mx - 2.8, my - 3.2),
                                QtCore.QPointF(mx - 2.8, my + 3.2),
                            ]
                        )
                    else:
                        tri = QtGui.QPolygonF(
                            [
                                QtCore.QPointF(mx - 4.5, my),
                                QtCore.QPointF(mx + 2.8, my - 3.2),
                                QtCore.QPointF(mx + 2.8, my + 3.2),
                            ]
                        )
                else:
                    if dy >= 0:
                        tri = QtGui.QPolygonF(
                            [
                                QtCore.QPointF(mx, my + 4.5),
                                QtCore.QPointF(mx - 3.2, my - 2.8),
                                QtCore.QPointF(mx + 3.2, my - 2.8),
                            ]
                        )
                    else:
                        tri = QtGui.QPolygonF(
                            [
                                QtCore.QPointF(mx, my - 4.5),
                                QtCore.QPointF(mx - 3.2, my + 2.8),
                                QtCore.QPointF(mx + 3.2, my + 2.8),
                            ]
                        )
                painter.drawPolygon(tri)

    def draw_link(self, painter, points, color, width=3, dashed=False, flow_markers=False):
        if len(points) < 2:
            return
        line_color = QtGui.QColor(color)
        under_color = QtGui.QColor(line_color)
        under_color = under_color.darker(165)
        under_color.setAlpha(120 if not dashed else 70)

        under_pen = QtGui.QPen(under_color, width + (1 if not dashed else 0), QtCore.Qt.DashLine if dashed else QtCore.Qt.SolidLine)
        under_pen.setCapStyle(QtCore.Qt.RoundCap)
        under_pen.setJoinStyle(QtCore.Qt.RoundJoin)
        painter.setPen(under_pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        path = QtGui.QPainterPath(points[0])
        for point in points[1:]:
            path.lineTo(point)
        painter.drawPath(path)
        pen = QtGui.QPen(line_color, width, QtCore.Qt.DashLine if dashed else QtCore.Qt.SolidLine)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)
        if flow_markers and not dashed:
            self.draw_flow_markers(painter, points, line_color)

    def quick_connection_path(self, start, end):
        stub = 14
        start_stub = QtCore.QPoint(start.x() - stub, start.y())
        end_stub = QtCore.QPoint(end.x() + stub, end.y())
        mid_y = int(round((start_stub.y() + end_stub.y()) / 2.0))
        return [
            start,
            start_stub,
            QtCore.QPoint(start_stub.x(), mid_y),
            QtCore.QPoint(end_stub.x(), mid_y),
            end_stub,
            end,
        ]

    def segment_intersects_rect(self, p1, p2, rect):
        if p1.x() == p2.x():
            x = p1.x()
            y1, y2 = sorted((p1.y(), p2.y()))
            return rect.left() <= x <= rect.right() and y1 <= rect.bottom() and y2 >= rect.top()
        if p1.y() == p2.y():
            y = p1.y()
            x1, x2 = sorted((p1.x(), p2.x()))
            return rect.top() <= y <= rect.bottom() and x1 <= rect.right() and x2 >= rect.left()
        return QtCore.QLineF(p1, p2).intersects(QtCore.QLineF(rect.topLeft(), rect.bottomRight()))[0] != QtCore.QLineF.NoIntersection

    def polyline_hits_obstacles(self, points, obstacles):
        if len(points) < 2:
            return False
        for idx in range(len(points) - 1):
            p1 = points[idx]
            p2 = points[idx + 1]
            for rect in obstacles:
                if self.segment_intersects_rect(p1, p2, rect):
                    return True
        return False

    def path_segments(self, points):
        segments = []
        if len(points) < 2:
            return segments
        for idx in range(len(points) - 1):
            p1 = points[idx]
            p2 = points[idx + 1]
            if p1.x() == p2.x():
                segments.append(
                    {
                        "ori": "v",
                        "x": p1.x(),
                        "y1": min(p1.y(), p2.y()),
                        "y2": max(p1.y(), p2.y()),
                    }
                )
            elif p1.y() == p2.y():
                segments.append(
                    {
                        "ori": "h",
                        "y": p1.y(),
                        "x1": min(p1.x(), p2.x()),
                        "x2": max(p1.x(), p2.x()),
                    }
                )
        return segments

    def parallel_segment_penalty(self, p1, p2, wire_segments, lane_padding=12):
        if not wire_segments:
            return 0
        penalty = 0
        if p1.x() == p2.x():
            x = p1.x()
            y1 = min(p1.y(), p2.y())
            y2 = max(p1.y(), p2.y())
            for seg in wire_segments:
                if seg.get("ori") != "v":
                    continue
                overlap = min(y2, seg["y2"]) - max(y1, seg["y1"])
                if overlap < 0:
                    continue
                delta = abs(x - seg["x"])
                if delta == 0:
                    penalty += 50000
                elif delta <= lane_padding:
                    penalty += (lane_padding - delta + 1) * 2600
        elif p1.y() == p2.y():
            y = p1.y()
            x1 = min(p1.x(), p2.x())
            x2 = max(p1.x(), p2.x())
            for seg in wire_segments:
                if seg.get("ori") != "h":
                    continue
                overlap = min(x2, seg["x2"]) - max(x1, seg["x1"])
                if overlap < 0:
                    continue
                delta = abs(y - seg["y"])
                if delta == 0:
                    penalty += 50000
                elif delta <= lane_padding:
                    penalty += (lane_padding - delta + 1) * 2600
        return penalty

    def path_parallel_penalty(self, points, wire_segments):
        if not wire_segments or len(points) < 2:
            return 0
        total = 0
        for idx in range(len(points) - 1):
            total += self.parallel_segment_penalty(points[idx], points[idx + 1], wire_segments)
        return total

    def route_grid_path(self, start_stub, end_stub, obstacles, min_x, max_x, min_y, max_y, wire_segments=None):
        step = 6
        wire_segments = wire_segments or []

        def snap(value, lo, hi):
            snapped = int(round(value / step) * step)
            return clamp(snapped, lo, hi)

        def is_blocked(x, y):
            point = QtCore.QPoint(x, y)
            for rect in obstacles:
                if rect.contains(point):
                    return True
            return False

        def nearest_free(x, y):
            if not is_blocked(x, y):
                return (x, y)
            seen = {(x, y)}
            frontier = deque([(x, y)])
            while frontier:
                cx, cy = frontier.popleft()
                for dx, dy in ((step, 0), (-step, 0), (0, step), (0, -step)):
                    nx = clamp(cx + dx, min_x, max_x)
                    ny = clamp(cy + dy, min_y, max_y)
                    key = (nx, ny)
                    if key in seen:
                        continue
                    seen.add(key)
                    if not is_blocked(nx, ny):
                        return key
                    frontier.append(key)
            return (x, y)

        sx = snap(start_stub.x(), min_x, max_x)
        sy = snap(start_stub.y(), min_y, max_y)
        ex = snap(end_stub.x(), min_x, max_x)
        ey = snap(end_stub.y(), min_y, max_y)
        start = nearest_free(sx, sy)
        goal = nearest_free(ex, ey)

        def heuristic(node):
            return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

        open_heap = []
        heapq.heappush(open_heap, (heuristic(start), 0, start))
        came_from = {}
        g_score = {start: 0}
        closed = set()

        while open_heap:
            _, current_cost, current = heapq.heappop(open_heap)
            if current in closed:
                continue
            if current == goal:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                points = [QtCore.QPoint(x, y) for x, y in path]
                return points
            closed.add(current)
            cx, cy = current
            for dx, dy in ((step, 0), (-step, 0), (0, step), (0, -step)):
                nx = clamp(cx + dx, min_x, max_x)
                ny = clamp(cy + dy, min_y, max_y)
                neighbor = (nx, ny)
                if neighbor in closed or is_blocked(nx, ny):
                    continue
                move_penalty = self.parallel_segment_penalty(QtCore.QPoint(cx, cy), QtCore.QPoint(nx, ny), wire_segments)
                if move_penalty >= 50000:
                    continue
                tentative = current_cost + step + move_penalty
                if tentative < g_score.get(neighbor, 1 << 30):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    heapq.heappush(open_heap, (tentative + heuristic(neighbor), tentative, neighbor))
        return []

    def connection_obstacles(self, source_node=None, target_node=None):
        obstacles = []
        if source_node != GUITAR_NODE_ID and target_node != GUITAR_NODE_ID:
            obstacles.append(self.guitar_rect().adjusted(-8, -8, 8, 8))
        if source_node != AMP_NODE_ID and target_node != AMP_NODE_ID:
            obstacles.append(self.amp_rect().adjusted(-8, -8, 8, 8))
        for pedal_id in self.pedal_ids:
            base = self.pedal_rect(pedal_id)
            padded = base.adjusted(-self.PEDAL_ROUTE_PADDING, -self.PEDAL_ROUTE_PADDING, self.PEDAL_ROUTE_PADDING, self.PEDAL_ROUTE_PADDING)
            if pedal_id == source_node:
                left_safe = int(round(base.width() * 0.32))
                guard = base.adjusted(left_safe, 1, -1, -1)
                obstacles.append(guard)
            elif pedal_id == target_node:
                right_safe = int(round(base.width() * 0.32))
                guard = base.adjusted(1, 1, -right_safe, -1)
                obstacles.append(guard)
            else:
                obstacles.append(padded)
        return obstacles

    def build_connection_path(self, start, end, source_node=None, target_node=None, wire_segments=None):
        wire_segments = wire_segments or []
        stub = 14
        start_stub = QtCore.QPoint(start.x() - stub, start.y())
        end_stub = QtCore.QPoint(end.x() + stub, end.y())
        start_anchors = [
            start_stub,
            QtCore.QPoint(start.x(), clamp(start.y() - stub, 8, max(8, self.height() - 8))),
            QtCore.QPoint(start.x(), clamp(start.y() + stub, 8, max(8, self.height() - 8))),
        ]
        end_anchors = [
            end_stub,
            QtCore.QPoint(end.x(), clamp(end.y() - stub, 8, max(8, self.height() - 8))),
            QtCore.QPoint(end.x(), clamp(end.y() + stub, 8, max(8, self.height() - 8))),
            end,
        ]
        obstacles = self.connection_obstacles(source_node, target_node)
        min_y = 8
        max_y = max(min_y, self.height() - 8)
        min_x = 8
        max_x = max(min_x, self.width() - 8)

        def dedupe_points(points):
            out = []
            for pt in points:
                if not out or pt != out[-1]:
                    out.append(pt)
            return out

        def dedupe_anchor_points(points):
            unique = []
            seen = set()
            for pt in points:
                key = (pt.x(), pt.y())
                if key in seen:
                    continue
                seen.add(key)
                unique.append(QtCore.QPoint(pt.x(), pt.y()))
            return unique

        def path_length(points):
            total = 0
            for i in range(len(points) - 1):
                total += abs(points[i + 1].x() - points[i].x()) + abs(points[i + 1].y() - points[i].y())
            return total

        def has_exact_axis_overlap(points, minimum_overlap=3):
            if len(points) < 2 or not wire_segments:
                return False
            segments = self.path_segments(points)
            for seg in segments:
                for existing in wire_segments:
                    if seg.get("ori") != existing.get("ori"):
                        continue
                    if seg.get("ori") == "h":
                        if seg["y"] != existing["y"]:
                            continue
                        overlap = min(seg["x2"], existing["x2"]) - max(seg["x1"], existing["x1"])
                    else:
                        if seg["x"] != existing["x"]:
                            continue
                        overlap = min(seg["y2"], existing["y2"]) - max(seg["y1"], existing["y1"])
                    if overlap >= minimum_overlap:
                        return True
            return False

        lane_padding = 12

        def nudge_lane(value, orientation):
            if not wire_segments:
                return value
            lo, hi = (min_y, max_y) if orientation == "h" else (min_x, max_x)
            lane = clamp(int(value), lo, hi)
            for _ in range(10):
                moved = False
                for seg in wire_segments:
                    if seg.get("ori") != orientation:
                        continue
                    taken = seg["y"] if orientation == "h" else seg["x"]
                    delta = lane - int(taken)
                    if abs(delta) <= lane_padding:
                        shift = lane_padding + 1 - abs(delta)
                        if shift <= 0:
                            shift = lane_padding
                        lane = clamp(lane + (shift if delta >= 0 else -shift), lo, hi)
                        moved = True
                if not moved:
                    break
            return lane

        candidates = []
        x_offsets = [0, -14, 14, -28, 28, -42, 42]
        start_x_candidates = []
        end_x_candidates = []
        seen_start_x = set()
        seen_end_x = set()
        for offset in x_offsets:
            sx = nudge_lane(clamp(start_stub.x() + offset, min_x, max_x), "v")
            ex = nudge_lane(clamp(end_stub.x() + offset, min_x, max_x), "v")
            if sx not in seen_start_x:
                seen_start_x.add(sx)
                start_x_candidates.append(sx)
            if ex not in seen_end_x:
                seen_end_x.add(ex)
                end_x_candidates.append(ex)

        y_candidates = {clamp(start_stub.y(), min_y, max_y), clamp(end_stub.y(), min_y, max_y)}
        y_candidates.add(clamp((start.y() + end.y()) // 2, min_y, max_y))
        if obstacles:
            top = min(rect.top() for rect in obstacles)
            bottom = max(rect.bottom() for rect in obstacles)
            y_candidates.update(
                {
                    clamp(top - 18, min_y, max_y),
                    clamp(bottom + 18, min_y, max_y),
                }
            )
            for rect in obstacles:
                y_candidates.add(clamp(rect.top() - 14, min_y, max_y))
                y_candidates.add(clamp(rect.bottom() + 14, min_y, max_y))
        else:
            y_candidates.update(
                {
                    clamp(start_stub.y() - 32, min_y, max_y),
                    clamp(start_stub.y() + 32, min_y, max_y),
                    clamp(end_stub.y() - 32, min_y, max_y),
                    clamp(end_stub.y() + 32, min_y, max_y),
                }
            )

        for sx in start_x_candidates:
            for ex in end_x_candidates:
                for y in sorted(y_candidates):
                    y_lane = nudge_lane(y, "h")
                    candidates.append(
                        [
                            start,
                            QtCore.QPoint(sx, start.y()),
                            QtCore.QPoint(sx, y_lane),
                            QtCore.QPoint(ex, y_lane),
                            QtCore.QPoint(ex, end.y()),
                            end,
                        ]
                    )

        candidates.append(
            [
                start,
                start_stub,
                QtCore.QPoint(end_stub.x(), start_stub.y()),
                end_stub,
                end,
            ]
        )

        valid = []
        for points in candidates:
            pts = dedupe_points(points)
            if len(pts) < 2:
                continue
            if self.polyline_hits_obstacles(pts, obstacles):
                continue
            if has_exact_axis_overlap(pts):
                continue
            valid.append((self.path_parallel_penalty(pts, wire_segments), path_length(pts), pts))

        best_candidate = None
        if valid:
            valid.sort(key=lambda item: (item[0], item[1]))
            best_candidate = valid[0]

        best_grid = None
        for grid_start in dedupe_anchor_points(start_anchors):
            for grid_target in dedupe_anchor_points(end_anchors):
                grid_path = self.route_grid_path(grid_start, grid_target, obstacles, min_x, max_x, min_y, max_y, wire_segments=wire_segments)
                if not grid_path:
                    continue
                routed = dedupe_points([start] + grid_path + [end])
                if self.polyline_hits_obstacles(routed, obstacles):
                    continue
                if has_exact_axis_overlap(routed):
                    continue
                routed_score = (self.path_parallel_penalty(routed, wire_segments), path_length(routed))
                if best_grid is None or routed_score < (best_grid[0], best_grid[1]):
                    best_grid = (routed_score[0], routed_score[1], routed)

        if best_grid is not None:
            if best_candidate is None or (best_grid[0], best_grid[1]) < (best_candidate[0], best_candidate[1]):
                return best_grid[2]

        if best_candidate is not None:
            return best_candidate[2]

        return dedupe_points(
            [
                start,
                start_stub,
                QtCore.QPoint(end_stub.x(), start_stub.y()),
                end_stub,
                end,
            ]
        )

    def knob_angle(self, value_percent):
        value = clamp(int(round(value_percent if isinstance(value_percent, (int, float)) else 50)), 0, 100)
        absolute_minutes = int(round(7 * 60 + (value / 100.0) * (10 * 60))) % (12 * 60)
        return 90 - (absolute_minutes * 0.5)

    def draw_knob(self, painter, center, value_percent):
        value = clamp(int(round(value_percent if isinstance(value_percent, (int, float)) else 50)), 0, 100)
        angle_deg = self.knob_angle(value)
        rad = math.radians(angle_deg)
        tip = QtCore.QPoint(
            int(round(center.x() + math.cos(rad) * 7.2)),
            int(round(center.y() - math.sin(rad) * 7.2)),
        )
        painter.setPen(QtGui.QPen(QtGui.QColor("#d42027"), 2.6, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        painter.drawLine(center, tip)
        marker = QtCore.QPointF(
            center.x() + math.cos(rad) * 4.8,
            center.y() - math.sin(rad) * 4.8,
        )
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#ffffff")))
        painter.drawEllipse(marker, 2.1, 2.1)

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

    def pedal_pixmap(self, pedal_id):
        return self.pedal_pixmaps.get(pedal_id)

    def amp_brand_style(self):
        return AMP_BRAND_COLORS.get(self.amp_model_key, {"bg": self.theme["amp_bg"], "fg": self.theme["amp_fg"]})

    def paintEvent(self, _event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, not bool(self.dragging_pedal))
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
        painter.drawEllipse(self.guitar_output_pos(), 5, 5)

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
        painter.drawEllipse(self.amp_input_pos(), 5, 5)

        connection_paths = []
        if self.dragging_pedal:
            for src, dst in self.connections:
                if src != GUITAR_NODE_ID and src not in self.pedal_ids:
                    continue
                if dst != AMP_NODE_ID and dst not in self.pedal_ids:
                    continue
                start = self.guitar_output_pos() if src == GUITAR_NODE_ID else self.pedal_output_pos(src)
                end = self.amp_input_pos() if dst == AMP_NODE_ID else self.pedal_input_pos(dst)
                connection_paths.append(self.quick_connection_path(start, end))
            for path_points in connection_paths:
                self.draw_link(painter, path_points, self.theme["canvas_edge"], width=3, flow_markers=False)
        else:
            wire_segments = []
            for src, dst in self.connections:
                if src != GUITAR_NODE_ID and src not in self.pedal_ids:
                    continue
                if dst != AMP_NODE_ID and dst not in self.pedal_ids:
                    continue
                start = self.guitar_output_pos() if src == GUITAR_NODE_ID else self.pedal_output_pos(src)
                end = self.amp_input_pos() if dst == AMP_NODE_ID else self.pedal_input_pos(dst)
                path_points = self.build_connection_path(start, end, src, dst, wire_segments=wire_segments)
                connection_paths.append(path_points)
                wire_segments.extend(self.path_segments(path_points))
            for path_points in connection_paths:
                self.draw_link(painter, path_points, self.theme["canvas_edge"], width=3, flow_markers=True)

        if self.link_start and self.preview_link_to:
            start = self.guitar_output_pos() if self.link_start == GUITAR_NODE_ID else self.pedal_output_pos(self.link_start)
            preview_points = [start, QtCore.QPoint(start.x() - 16, start.y()), QtCore.QPoint(self.preview_link_to.x(), start.y()), self.preview_link_to]
            self.draw_link(
                painter,
                preview_points,
                self.theme["canvas_edge_preview"],
                width=2,
                dashed=True,
            )

        for pedal_id in self.pedal_ids:
            rect = self.pedal_rect(pedal_id)
            painter.setPen(QtGui.QPen(QtGui.QColor(self.theme["frame"]), 2))
            base = QtGui.QColor(PEDAL_COLORS.get(pedal_id, "#b0b0b0"))
            shade = base.darker(122)
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
                connect_rect = self.pedal_connect_button_rect(pedal_id, side)
                disconnect_rect = self.pedal_disconnect_button_rect(pedal_id, side)

                painter.setPen(QtGui.QPen(QtGui.QColor("#0e5f2c"), 1))
                painter.setBrush(QtGui.QBrush(QtGui.QColor("#37c96c")))
                painter.drawRoundedRect(connect_rect, 4, 4)
                painter.setPen(QtGui.QColor("#ecfff2"))
                painter.drawText(connect_rect, QtCore.Qt.AlignCenter, "L")

                painter.setPen(QtGui.QPen(QtGui.QColor("#6b1117"), 1))
                painter.setBrush(QtGui.QBrush(QtGui.QColor("#eb5059")))
                painter.drawRoundedRect(disconnect_rect, 4, 4)
                painter.setPen(QtGui.QColor("#fff1f1"))
                painter.drawText(disconnect_rect, QtCore.Qt.AlignCenter, "-")

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
            painter.drawEllipse(self.pedal_input_pos(pedal_id), self.PEDAL_JACK_RADIUS, self.PEDAL_JACK_RADIUS)
            painter.drawEllipse(self.pedal_output_pos(pedal_id), self.PEDAL_JACK_RADIUS, self.PEDAL_JACK_RADIUS)

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
            if self.pedal_connect_button_rect(pedal_id, "output").contains(click_pos):
                self.link_start = pedal_id
                self.preview_link_to = click_pos
                self.update()
                return
            if self.pedal_connect_button_rect(pedal_id, "input").contains(click_pos):
                if self.link_start and self.link_start != pedal_id:
                    self.connectionCreated.emit(self.link_start, pedal_id)
                    self.link_start = None
                    self.preview_link_to = None
                    self.update()
                return
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
            self.drag_pending_pos = None
        else:
            self.dragging_pedal = None

    def mouseMoveEvent(self, event):
        if self.link_start:
            self.preview_link_to = event.pos()
            self.update()
            return
        if self.dragging_pedal:
            new_pos = self.clamp_pedal_position(event.pos() - self.drag_offset)
            current = self.pedal_positions.get(self.dragging_pedal)
            if current == new_pos and self.drag_pending_pos is None:
                return
            self.drag_pending_pos = new_pos
            if not self.drag_update_timer.isActive():
                self.drag_update_timer.start(self.DRAG_FRAME_MS)
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
            if self.drag_update_timer.isActive():
                self.drag_update_timer.stop()
            self.flush_drag_position()
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
    return util_clamp(value, min_value, max_value)


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
    return util_to_clock(percent)


def quick_knob(value):
    return util_quick_knob(value)


def db_value(value):
    return util_db_value(value)


def percent_from_db(value, low=-12, high=12):
    return util_percent_from_db(value, low=low, high=high)


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

    if has("ge7") and has("eq10") and drive_indices:
        add_rule(
            idx["ge7"] < first_drive,
            11,
            "GE-7 is before gain so it can shape what the drive stages clip.",
        )
        add_rule(
            idx["eq10"] > last_drive,
            11,
            "10-band EQ is after gain for final contour and mix placement.",
        )
    else:
        if has("ge7") and drive_indices:
            wants_post = genre_key in {"metal", "hip-hop"} and guitar_type == "electric"
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

    if has("ch1") and drive_indices:
        add_rule(idx["ch1"] > last_drive, 8, "CH-1 is after gain so chorus modulation stays clear.")

    if has("dd3") and drive_indices:
        add_rule(idx["dd3"] > last_drive, 12, "DD-3 is after gain for clearer repeat definition.")
    if has("ch1") and has("dd3"):
        add_rule(idx["ch1"] < idx["dd3"], 6, "CH-1 feeds DD-3 so chorus texture repeats naturally.")

    if has("rc30"):
        add_rule(idx["rc30"] == (len(chain) - 1), 18, "RC-30 is at chain end for stable loop playback.")
        if has("dd3"):
            add_rule(idx["dd3"] < idx["rc30"], 9, "Delay is before RC-30 to print repeats into loops.")

    eq_justification = ""
    if has("ge7") and has("eq10"):
        gap = abs(idx["ge7"] - idx["eq10"])
        if drive_indices and idx["ge7"] < first_drive and idx["eq10"] > last_drive:
            score += 10
            eq_justification = "GE-7 is pre-drive while 10-band is post-drive, giving two distinct EQ stages."
        elif gap == 1:
            score -= 12
            eq_justification = "GE-7 and 10-band are adjacent; split them apart for clearer, less compounded filtering."
        else:
            score += 4
            eq_justification = "GE-7 and 10-band are separated to keep each EQ stage distinct."

    return {
        "score": score,
        "highlights": notes,
        "eq_justification": eq_justification,
    }


def apply_order_dependent_pedal_tuning(recommendation, chain, genre_key, guitar_type):
    chain = sanitize_chain(chain)
    if not chain:
        return

    idx = {pid: i for i, pid in enumerate(chain)}
    has = lambda pid: pid in idx and pid in recommendation["pedals"]
    notes = recommendation["notes"]
    pedals = recommendation["pedals"]

    drive_ids = [pid for pid in ["sd1", "bd2", "ds1"] if pid in idx]
    drive_indices = sorted(idx[pid] for pid in drive_ids)
    first_drive = drive_indices[0] if drive_indices else -1
    last_drive = drive_indices[-1] if drive_indices else -1

    def nudge_pct(value, delta):
        return clamp(int(round(value + delta)), 0, 100)

    def nudge_db(value, delta):
        return max(-15, min(15, int(round(value + delta))))

    if has("sd1") and has("ds1"):
        sd1 = pedals["sd1"]
        ds1 = pedals["ds1"]
        if idx["sd1"] < idx["ds1"]:
            sd1["drive"] = min(sd1.get("drive", 25), 28)
            sd1["level"] = nudge_pct(sd1.get("level", 60), 6)
            ds1["dist"] = nudge_pct(ds1.get("dist", 50), 4)
            notes.append("SD-1 feeds DS-1, so SD-1 is tuned as a boost and DS-1 carries the main saturation.")
        else:
            ds1["dist"] = max(ds1.get("dist", 45) - 8, 18)
            sd1["drive"] = nudge_pct(sd1.get("drive", 30), 6)
            sd1["tone"] = nudge_pct(sd1.get("tone", 50), -4)
            notes.append("DS-1 into SD-1 is treated as smoother clipping into a focused mid push.")

    if has("cs3") and drive_indices:
        cs3 = pedals["cs3"]
        if idx["cs3"] < first_drive:
            cs3["attack"] = nudge_pct(cs3.get("attack", 50), 3)
            cs3["sustain"] = nudge_pct(cs3.get("sustain", 50), 2)
            notes.append("CS-3 before drive keeps attack defined while adding sustain.")
        else:
            cs3["sustain"] = nudge_pct(cs3.get("sustain", 50), -6)
            notes.append("CS-3 after drive is softened to avoid over-compression noise buildup.")

    if has("ge7"):
        ge7 = pedals["ge7"]
        bands = ge7.setdefault("bands", {})
        if drive_indices and idx["ge7"] < first_drive:
            ge7["mode"] = "Pre-drive focus"
            bands["100"] = nudge_db(bands.get("100", 0), -1)
            bands["200"] = nudge_db(bands.get("200", 0), -1)
            bands["800"] = nudge_db(bands.get("800", 0), 1)
            bands["1.6k"] = nudge_db(bands.get("1.6k", 0), 1)
        elif drive_indices and idx["ge7"] > last_drive:
            ge7["mode"] = "Post-drive shape"
            bands["3.2k"] = nudge_db(bands.get("3.2k", 0), 1)
            bands["6.4k"] = nudge_db(bands.get("6.4k", 0), -1)

    if has("eq10"):
        eq10 = pedals["eq10"]
        bands = eq10.setdefault("bands", {})
        if drive_indices and idx["eq10"] > last_drive:
            eq10["mode"] = "Post-drive sculpt"
            eq10["volume"] = nudge_db(eq10.get("volume", 0), 1)
            bands["8k"] = nudge_db(bands.get("8k", 0), -1)
            bands["16k"] = nudge_db(bands.get("16k", 0), -1)
        elif drive_indices and idx["eq10"] < first_drive:
            eq10["mode"] = "Pre-drive push"
            bands["125"] = nudge_db(bands.get("125", 0), 1)
            bands["250"] = nudge_db(bands.get("250", 0), 1)
            bands["4k"] = nudge_db(bands.get("4k", 0), -1)

    if has("ch1") and has("dd3") and idx["ch1"] > idx["dd3"]:
        ch1 = pedals["ch1"]
        ch1["depth"] = nudge_pct(ch1.get("depth", 40), -6)
        notes.append("CH-1 is after DD-3 here, so chorus depth is reduced to keep repeats intelligible.")
    elif has("ch1") and has("dd3"):
        notes.append("CH-1 before DD-3 keeps repeats wide without washing out pick attack.")

    if has("rc30") and idx["rc30"] != len(chain) - 1:
        rc30 = pedals["rc30"]
        rc30["rhythmLevel"] = nudge_pct(rc30.get("rhythmLevel", 16), -3)
        notes.append("RC-30 is not last in chain, so loop rhythm level is trimmed to reduce downstream coloration.")

    drive_count = len(drive_ids)
    if drive_count >= 2:
        recommendation["amp"]["gain"] = nudge_pct(recommendation["amp"].get("gain", 50), -4)
        notes.append("Multiple gain pedals are active, so amp gain is trimmed to preserve note separation.")
    elif drive_count == 0 and guitar_type == "electric" and genre_key in {"rock", "classic-rock", "blues"}:
        recommendation["amp"]["gain"] = nudge_pct(recommendation["amp"].get("gain", 50), 4)
        notes.append("No drive pedals detected, so amp gain is raised slightly to keep sustain musical.")


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

    apply_order_dependent_pedal_tuning(recommendation, chain, genre_key, guitar_type)

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
    progressions = playbook.get("popularTop3") or playbook.get("concertProgression", [])
    if not progressions:
        progressions = playbook.get("progressionPool", [])
    chords = []
    for progression in progressions:
        if not isinstance(progression, str):
            continue
        for token in progression.split("-"):
            clean = token.strip()
            if clean:
                chords.append(clean)
    return unique_list(chords)


def sample_style_progressions(genre_key, count=2):
    playbook = STYLE_PLAYBOOK.get(genre_key, STYLE_PLAYBOOK["rock"])
    pool = [item for item in playbook.get("progressionPool", []) if isinstance(item, str) and item.strip()]
    if not pool:
        pool = [item for item in playbook.get("concertProgression", []) if isinstance(item, str) and item.strip()]
    pool = unique_list(pool)
    if not pool:
        return []
    if len(pool) <= count:
        return pool
    return random.sample(pool, count)


def sample_popular_progression(genre_key):
    playbook = STYLE_PLAYBOOK.get(genre_key, STYLE_PLAYBOOK["rock"])
    top = [item for item in playbook.get("popularTop3", []) if isinstance(item, str) and item.strip()]
    if top:
        return random.choice(top)
    fallback = playbook.get("concertProgression", [])
    for item in fallback:
        if isinstance(item, str) and item.strip():
            return item
    return ""


def split_progression_tokens(progression):
    if not isinstance(progression, str):
        return []
    return [part.strip() for part in progression.split("-") if isinstance(part, str) and part.strip()]


def transpose_chord_root_for_capo(chord_token, capo_fret=5):
    if not isinstance(chord_token, str):
        return ""
    match = CHORD_ROOT_RE.match(chord_token.strip())
    if not match:
        return chord_token.strip()
    root_raw = f"{match.group(1)}{match.group(2)}"
    root = normalize_note_name(root_raw)
    if root not in NOTE_TO_PITCH_CLASS:
        return chord_token.strip()
    suffix = chord_token.strip()[match.end():]
    target_pc = (NOTE_TO_PITCH_CLASS[root] - int(capo_fret)) % 12
    shape_root = PITCH_CLASS_CANONICAL[target_pc]
    return f"{shape_root}{suffix}"


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


def nashville_degrees_for_key(key_name):
    for name, degrees in NASHVILLE_MAJOR_CHART:
        if name == key_name:
            return list(degrees)
    return []


def major_key_for_selection(token):
    parsed = parse_chord_token(token)
    if not parsed:
        return ""
    if parsed["quality"] == "minor":
        minor_token = f"{parsed['root']}m"
        if minor_token in CIRCLE_FIFTHS_MINOR:
            idx = CIRCLE_FIFTHS_MINOR.index(minor_token)
            return CIRCLE_FIFTHS_MAJOR[idx]
    return parsed["root"]


def usual_keys_for_genre(genre_key):
    keys = USUAL_KEYS_BY_GENRE.get(genre_key, USUAL_KEYS_BY_GENRE.get("rock", []))
    return unique_list([key for key in keys if key])


def major_usual_keys_for_genre(genre_key):
    majors = []
    for key in usual_keys_for_genre(genre_key):
        major = major_key_for_selection(key)
        if major:
            majors.append(major)
    return unique_list(majors)


def config_path_candidates():
    candidates = []
    override = str(os.getenv("PEDAL_ARCHITECT_CONFIG", "") or "").strip()
    if override:
        candidates.append(Path(override).expanduser())
    candidates.extend(
        [
            SECRETS_CONFIG_FILE,
            Path.cwd() / ".secrets" / APP_CONFIG_FILENAME,
            APP_CONFIG_FILE,
            Path.cwd() / APP_CONFIG_FILENAME,
        ]
    )
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", "")
        if meipass:
            candidates.append(Path(meipass) / APP_CONFIG_FILENAME)
        candidates.append(APP_ROOT.parent / "Resources" / APP_CONFIG_FILENAME)
        candidates.append(APP_ROOT.parent.parent / "Resources" / APP_CONFIG_FILENAME)
    deduped = []
    seen = set()
    for path in candidates:
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(path)
    return deduped


def deep_merge_dict(base, overrides):
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge_dict(base[key], value)
        else:
            base[key] = value
    return base


def pitch_class_for_key_name(key_name):
    if not key_name:
        return NOTE_TO_PITCH_CLASS["C"]
    major = major_key_for_selection(key_name)
    if not major:
        parsed = parse_chord_token(str(key_name))
        major = parsed["root"] if parsed else normalize_note_name(str(key_name))
    return NOTE_TO_PITCH_CLASS.get(major, NOTE_TO_PITCH_CLASS["C"])


def preferred_root_fret(root_pitch_class):
    candidates = [fret for fret in range(0, 25) if (STANDARD_TUNING_PCS_LOW_TO_HIGH[0] + fret) % 12 == root_pitch_class]
    for fret in candidates:
        if 4 <= fret <= 10:
            return fret
    for fret in candidates:
        if 1 <= fret <= 15:
            return fret
    return candidates[0] if candidates else 0


def key_row_for_name(key_name):
    for row_name, degrees in NASHVILLE_MAJOR_CHART:
        if row_name == key_name:
            return row_name, list(degrees)
    return "C", list(NASHVILLE_MAJOR_CHART[0][1])


def display_note_for_pitch_class(pitch_class, key_name):
    major_key = major_key_for_selection(key_name) or "C"
    use_sharps = major_key in SHARP_KEY_SIGNATURES
    names = PITCH_CLASS_SHARP if use_sharps else PITCH_CLASS_CANONICAL
    return names[int(pitch_class) % 12]


def caged_window_start(root_fret, shape_key, scale_family):
    shape = CAGED_SHAPES.get(shape_key, CAGED_SHAPES["g"])
    offset_key = "major_start_offset" if scale_family == "major" else "minor_start_offset"
    start = int(root_fret) + int(shape.get(offset_key, 0))
    while start < 0:
        start += 12
    while start > 11:
        start -= 12
    size = max(4, int(shape.get("window_size", 5)))
    return start, size


class PentatonicNeckWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(520, 260)
        self.theme = THEMES["dark"]
        self.key_name = "C"
        self.shape_key = "g"
        self.scale_key = "minor_pentatonic"
        self.start_fret = 0
        self.end_fret = 5
        self.shape_fret_start = 0
        self.shape_fret_end = 5
        self.shape_highlight_frets = set()
        self.note_points = []
        self.update_pattern()

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def set_selection(self, key_name, shape_key, scale_key=None):
        self.key_name = key_name if key_name else "C"
        self.shape_key = shape_key if shape_key in CAGED_SHAPES else "g"
        if scale_key in SCALE_LIBRARY:
            self.scale_key = scale_key
        self.update_pattern()
        self.update()

    def current_scale(self):
        return SCALE_LIBRARY.get(self.scale_key, SCALE_LIBRARY["minor_pentatonic"])

    def update_pattern(self):
        scale = self.current_scale()
        root_pc = pitch_class_for_key_name(self.key_name)
        root_fret = preferred_root_fret(root_pc)
        start = 0
        end = 15
        intervals = set(scale.get("intervals", []))
        scale_family = str(scale.get("family", "minor"))
        shape_start, shape_window = caged_window_start(root_fret, self.shape_key, scale_family)
        shape_end = shape_start + shape_window

        points = []
        for string_idx, open_pc in enumerate(STANDARD_TUNING_PCS_TOP_TO_BOTTOM):
            for fret in range(start, end + 1):
                interval = (open_pc + fret - root_pc) % 12
                if interval not in intervals:
                    continue
                pitch_class = (open_pc + fret) % 12
                points.append(
                    {
                        "string_idx": string_idx,
                        "fret": fret,
                        "is_root": interval == 0,
                        "note": display_note_for_pitch_class(pitch_class, self.key_name),
                    }
                )

        clamped_start = clamp(shape_start, start, end)
        clamped_end = clamp(shape_end, start, end)
        highlight_frets = set(range(min(clamped_start, clamped_end), max(clamped_start, clamped_end) + 1))

        self.start_fret = start
        self.end_fret = end
        self.shape_highlight_frets = highlight_frets
        if highlight_frets:
            self.shape_fret_start = min(highlight_frets)
            self.shape_fret_end = max(highlight_frets)
        else:
            self.shape_fret_start = start
            self.shape_fret_end = end
        self.note_points = points

    def summary_text(self):
        shape_label = CAGED_SHAPES.get(self.shape_key, CAGED_SHAPES["g"])["label"]
        scale = self.current_scale()
        return f"{self.key_name} {scale['label']} • {shape_label} • shape frets {self.shape_fret_start}-{self.shape_fret_end}"

    def contrast_text(self, color):
        # Relative luminance approximation for readable note labels.
        luminance = (0.299 * color.red()) + (0.587 * color.green()) + (0.114 * color.blue())
        return QtGui.QColor("#101418") if luminance > 170 else QtGui.QColor("#f7f9ff")

    def ensure_root_note_contrast(self, root_color, note_color):
        lightness_delta = abs(root_color.lightness() - note_color.lightness())
        channel_delta = abs(root_color.red() - note_color.red()) + abs(root_color.green() - note_color.green()) + abs(root_color.blue() - note_color.blue())
        if lightness_delta >= 50 or channel_delta >= 160:
            return root_color
        if note_color.lightness() < 132:
            return QtGui.QColor("#ff5a5a")
        return QtGui.QColor("#b1172b")

    def paintEvent(self, _event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)

        panel = self.rect().adjusted(8, 8, -8, -8)
        painter.setPen(QtGui.QPen(QtGui.QColor(self.theme["frame"]), 1.8))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.theme["panel"])))
        painter.drawRoundedRect(panel, 8, 8)

        fretboard = panel.adjusted(44, 26, -18, -44)
        strings = 6
        fret_count = max(3, self.end_fret - self.start_fret + 1)
        string_gap = fretboard.height() / max(1, strings - 1)
        fret_gap = fretboard.width() / max(1, fret_count)

        # Highlight selected CAGED-shape fret columns.
        shape_fill = QtGui.QColor(self.theme.get("tab_selected_bg", self.theme.get("positive", "#66d17a")))
        shape_fill.setAlpha(38)
        shape_edge = QtGui.QColor(shape_fill)
        shape_edge.setAlpha(125)
        shape_edge = shape_edge.darker(120)
        painter.setPen(QtGui.QPen(shape_edge, 1.0))
        painter.setBrush(QtGui.QBrush(shape_fill))
        for fret in sorted(self.shape_highlight_frets):
            idx = fret - self.start_fret
            if idx < 0 or idx >= fret_count:
                continue
            left = fretboard.left() + idx * fret_gap + 1.2
            width = max(4.0, fret_gap - 2.4)
            rect = QtCore.QRectF(left, fretboard.top() + 1.2, width, max(10.0, fretboard.height() - 2.4))
            painter.drawRoundedRect(rect, 3.5, 3.5)

        # Strings
        for idx in range(strings):
            y = fretboard.top() + idx * string_gap
            thickness = 1.2 + (idx * 0.25)
            painter.setPen(QtGui.QPen(QtGui.QColor(self.theme["frame"]).lighter(130), thickness))
            painter.drawLine(QtCore.QPointF(fretboard.left(), y), QtCore.QPointF(fretboard.right(), y))

        # Frets
        for fret_idx in range(fret_count + 1):
            x = fretboard.left() + fret_idx * fret_gap
            is_nut = self.start_fret == 0 and fret_idx == 0
            width = 3.2 if is_nut else 1.3
            color = QtGui.QColor(self.theme["group_title"]).darker(108) if is_nut else QtGui.QColor(self.theme["frame"])
            painter.setPen(QtGui.QPen(color, width))
            painter.drawLine(QtCore.QPointF(x, fretboard.top()), QtCore.QPointF(x, fretboard.bottom()))

        # Dot markers on common frets for orientation
        marker_frets = {3, 5, 7, 9, 12, 15}
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.theme["frame"]).lighter(130)))
        for fret in range(self.start_fret, self.end_fret + 1):
            if fret not in marker_frets:
                continue
            idx = fret - self.start_fret
            if idx < 0 or idx >= fret_count:
                continue
            x = fretboard.left() + (idx + 0.5) * fret_gap
            y = fretboard.center().y()
            painter.drawEllipse(QtCore.QPointF(x, y), 3.6, 3.6)

        # Notes
        root_fill = QtGui.QColor(self.theme.get("root_note", self.theme["tab_selected_bg"]))
        scale_fill = QtGui.QColor(self.theme.get("scale_note", self.theme.get("positive", "#66d17a")))
        root_fill = self.ensure_root_note_contrast(root_fill, scale_fill)
        note_text_size = 11
        for point in self.note_points:
            idx = point["fret"] - self.start_fret
            if idx < 0 or idx >= fret_count:
                continue
            x = fretboard.left() + (idx + 0.5) * fret_gap
            y = fretboard.top() + point["string_idx"] * string_gap
            radius = 14.0 if point["is_root"] else 12.0
            fill = QtGui.QColor(root_fill if point["is_root"] else scale_fill)
            fg = self.contrast_text(fill)
            painter.setPen(QtGui.QPen(fill.darker(170), 1.2))
            painter.setBrush(QtGui.QBrush(fill))
            painter.drawEllipse(QtCore.QPointF(x, y), radius, radius)
            painter.setPen(fg)
            font = painter.font()
            font.setBold(True)
            font.setPointSize(note_text_size)
            painter.setFont(font)
            painter.drawText(
                QtCore.QRectF(x - radius, y - radius, radius * 2, radius * 2),
                QtCore.Qt.AlignCenter,
                point["note"],
            )

        # String labels
        painter.setPen(QtGui.QColor(self.theme["text"]))
        label_font = painter.font()
        label_font.setBold(True)
        label_font.setPointSize(note_text_size)
        painter.setFont(label_font)
        string_labels = ["e", "B", "G", "D", "A", "E"]
        for idx, label in enumerate(string_labels):
            y = fretboard.top() + idx * string_gap
            painter.drawText(QtCore.QRectF(panel.left() + 4, y - 12, 26, 24), QtCore.Qt.AlignCenter, label)

        # Fret labels (larger and bolder)
        fret_font = painter.font()
        fret_font.setBold(True)
        fret_font.setPointSize(note_text_size)
        painter.setFont(fret_font)
        for idx in range(fret_count):
            fret = self.start_fret + idx
            x = fretboard.left() + (idx + 0.5) * fret_gap
            box = QtCore.QRectF(x - 18, fretboard.bottom() + 8, 36, 24)
            if fret in self.shape_highlight_frets:
                box_fill = QtGui.QColor(self.theme.get("tab_selected_bg", self.theme["panel"])).lighter(155)
                box_fill.setAlpha(225)
                painter.setPen(QtGui.QPen(QtGui.QColor(self.theme.get("tab_selected_bg", self.theme["frame"])).darker(132), 1.2))
                painter.setBrush(QtGui.QBrush(box_fill))
                painter.drawRoundedRect(box, 4, 4)
                painter.setPen(self.contrast_text(box_fill))
            else:
                painter.setPen(QtGui.QPen(QtGui.QColor(self.theme["frame"]), 1))
                painter.setBrush(QtGui.QBrush(QtGui.QColor(self.theme["panel"]).lighter(110)))
                painter.drawRoundedRect(box, 4, 4)
                painter.setPen(QtGui.QColor(self.theme["text"]))
            painter.drawText(box, QtCore.Qt.AlignCenter, str(fret))

class CircleOfFifthsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(250, 230)
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
        font.setPointSize(11)
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
        center_font.setPointSize(11)
        painter.setFont(center_font)
        painter.drawText(
            QtCore.QRectF(center.x() - 52, center.y() - 26, 104, 52),
            QtCore.Qt.AlignCenter,
            "Circle\nof Fifths",
        )


class TheoryPanelSubWindow(QtWidgets.QMdiSubWindow):
    restored_from_minimize = QtCore.pyqtSignal(str)
    minimized_changed = QtCore.pyqtSignal(str, bool)
    geometry_changed = QtCore.pyqtSignal(str)

    def __init__(self, panel_key, parent=None):
        super().__init__(parent)
        self.panel_key = panel_key

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange and hasattr(event, "oldState"):
            old_state = event.oldState()
            super().changeEvent(event)
            new_state = self.windowState()
            was_minimized = bool(old_state & QtCore.Qt.WindowMinimized)
            is_minimized = bool(new_state & QtCore.Qt.WindowMinimized)
            if was_minimized != is_minimized:
                self.minimized_changed.emit(self.panel_key, is_minimized)
            if was_minimized and not is_minimized:
                self.restored_from_minimize.emit(self.panel_key)
            if not is_minimized:
                self.geometry_changed.emit(self.panel_key)
            return
        super().changeEvent(event)

    def moveEvent(self, event):
        super().moveEvent(event)
        if not (self.windowState() & QtCore.Qt.WindowMinimized):
            self.geometry_changed.emit(self.panel_key)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not (self.windowState() & QtCore.Qt.WindowMinimized):
            self.geometry_changed.emit(self.panel_key)


class PedalShowcaseWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 360)
        self.theme = THEMES["dark"]
        self.pedal_id = BANK_ORDER[0]
        self.face_values = {"knobs": [50, 50, 50]}
        self.pedal_pixmaps = {}
        self.load_pedal_pixmaps()

    def load_pedal_pixmaps(self):
        for pedal_id, filename in PEDAL_IMAGE_FILES.items():
            path = pedal_asset_path(filename)
            pixmap = QtGui.QPixmap(str(path))
            if not pixmap.isNull():
                self.pedal_pixmaps[pedal_id] = pixmap

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def set_pedal(self, pedal_id, face_values=None):
        self.pedal_id = pedal_id if pedal_id in PEDAL_LIBRARY else BANK_ORDER[0]
        self.face_values = face_values if isinstance(face_values, dict) else {"knobs": [50, 50, 50]}
        self.update()

    def knob_angle(self, value_percent):
        value = clamp(int(round(value_percent if isinstance(value_percent, (int, float)) else 50)), 0, 100)
        absolute_minutes = int(round(7 * 60 + (value / 100.0) * (10 * 60))) % (12 * 60)
        return 90 - (absolute_minutes * 0.5)

    def draw_knob(self, painter, center, value_percent, radius=15):
        value = clamp(int(round(value_percent if isinstance(value_percent, (int, float)) else 50)), 0, 100)
        angle_deg = self.knob_angle(value)
        rad = math.radians(angle_deg)
        tip = QtCore.QPointF(
            center.x() + math.cos(rad) * (radius - 2.0),
            center.y() - math.sin(rad) * (radius - 2.0),
        )
        painter.setPen(QtGui.QPen(QtGui.QColor("#d42027"), 2.8, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        painter.drawLine(center, tip)
        marker = QtCore.QPointF(
            center.x() + math.cos(rad) * (radius * 0.62),
            center.y() - math.sin(rad) * (radius * 0.62),
        )
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#ffffff")))
        painter.drawEllipse(marker, 2.6, 2.6)

    def draw_slider_lever(self, painter, track_rect, value_percent, handle_color="#f7f9fc"):
        value = clamp(int(round(value_percent if isinstance(value_percent, (int, float)) else 50)), 0, 100)
        track_fill = QtGui.QLinearGradient(track_rect.topLeft(), track_rect.bottomLeft())
        track_fill.setColorAt(0.0, QtGui.QColor(24, 28, 34, 210))
        track_fill.setColorAt(1.0, QtGui.QColor(9, 12, 15, 216))
        painter.setPen(QtGui.QPen(QtGui.QColor("#0f151c"), 1))
        painter.setBrush(QtGui.QBrush(track_fill))
        painter.drawRoundedRect(track_rect, 2, 2)
        travel = max(1, track_rect.height() - 6)
        y = track_rect.bottom() - int(round((value / 100.0) * travel)) - 3
        handle = QtCore.QRect(track_rect.left() - 2, y, track_rect.width() + 4, 7)
        handle_fill = QtGui.QLinearGradient(handle.topLeft(), handle.bottomLeft())
        handle_fill.setColorAt(0.0, QtGui.QColor("#ffffff"))
        handle_fill.setColorAt(1.0, QtGui.QColor(handle_color))
        painter.setPen(QtGui.QPen(QtGui.QColor("#1c232c"), 1))
        painter.setBrush(QtGui.QBrush(handle_fill))
        painter.drawRoundedRect(handle, 2, 2)
        painter.setPen(QtGui.QPen(QtGui.QColor("#d42027"), 1.5))
        painter.drawLine(handle.left() + 1, handle.center().y(), handle.right() - 1, handle.center().y())

    def draw_eq_face(self, painter, rect):
        if self.pedal_id == "ge7":
            slider_values = list(self.face_values.get("sliders", [50] * len(GE7_BANDS)))
            while len(slider_values) < len(GE7_BANDS):
                slider_values.append(50)
            slider_values.append(self.face_values.get("level", 50))
            track_count = len(slider_values)
            left = rect.left() + int(round(rect.width() * 0.16))
            right = rect.left() + int(round(rect.width() * 0.84))
            top = rect.top() + int(round(rect.height() * 0.15))
            track_height = int(round(rect.height() * 0.24))
            span = max(1, right - left)
            for idx, value in enumerate(slider_values):
                x = left + int(round((idx / max(1, track_count - 1)) * span))
                self.draw_slider_lever(painter, QtCore.QRect(x - 4, top, 8, track_height), value, "#f6f8fb")
            return

        slider_values = list(self.face_values.get("sliders", [50] * len(EQ10_BANDS)))
        while len(slider_values) < len(EQ10_BANDS):
            slider_values.append(50)
        left = rect.left() + int(round(rect.width() * 0.13))
        right = rect.left() + int(round(rect.width() * 0.87))
        top = rect.top() + int(round(rect.height() * 0.25))
        track_height = int(round(rect.height() * 0.27))
        span = max(1, right - left)
        for idx, value in enumerate(slider_values):
            x = left + int(round((idx / max(1, len(slider_values) - 1)) * span))
            self.draw_slider_lever(painter, QtCore.QRect(x - 3, top, 6, track_height), value, "#f5f8fd")

        out_rect = QtCore.QRect(
            rect.left() + int(round(rect.width() * 0.07)),
            rect.top() + int(round(rect.height() * 0.25)),
            9,
            int(round(rect.height() * 0.12)),
        )
        gain_rect = QtCore.QRect(
            rect.left() + int(round(rect.width() * 0.91)) - 9,
            rect.top() + int(round(rect.height() * 0.25)),
            9,
            int(round(rect.height() * 0.12)),
        )
        self.draw_slider_lever(painter, out_rect, self.face_values.get("output", 50), "#f4f7fb")
        self.draw_slider_lever(painter, gain_rect, self.face_values.get("gain", 50), "#f4f7fb")

    def draw_rc30_face(self, painter, rect):
        knobs = list(self.face_values.get("knobs", [50, 50, 50]))
        while len(knobs) < 3:
            knobs.append(50)
        top_y = rect.top() + int(round(rect.height() * 0.20))
        centers = [
            QtCore.QPointF(rect.left() + rect.width() * 0.13, top_y),
            QtCore.QPointF(rect.left() + rect.width() * 0.28, top_y),
            QtCore.QPointF(rect.left() + rect.width() * 0.79, top_y),
        ]
        for center, value in zip(centers, knobs):
            self.draw_knob(painter, center, value, radius=14)

        meter_track_w = int(round(rect.width() * 0.065))
        meter_h = int(round(rect.height() * 0.24))
        meter_top = rect.top() + int(round(rect.height() * 0.62))
        t1_rect = QtCore.QRect(rect.left() + int(round(rect.width() * 0.20)), meter_top, meter_track_w, meter_h)
        t2_rect = QtCore.QRect(rect.left() + int(round(rect.width() * 0.66)), meter_top, meter_track_w, meter_h)
        for idx, mrect in enumerate([t1_rect, t2_rect]):
            painter.setPen(QtGui.QPen(QtGui.QColor("#16202b"), 1))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(14, 20, 26, 210)))
            painter.drawRoundedRect(mrect, 3, 3)
            value = clamp(int(round(knobs[idx + 1])), 0, 100)
            fill_h = int(round((value / 100.0) * (mrect.height() - 4)))
            fill_rect = QtCore.QRect(mrect.left() + 2, mrect.bottom() - 2 - fill_h, mrect.width() - 4, fill_h)
            meter_grad = QtGui.QLinearGradient(fill_rect.topLeft(), fill_rect.bottomLeft())
            meter_grad.setColorAt(0.0, QtGui.QColor("#ffd874"))
            meter_grad.setColorAt(1.0, QtGui.QColor("#f2534d"))
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(meter_grad))
            painter.drawRoundedRect(fill_rect, 2, 2)

    def paintEvent(self, _event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.fillRect(self.rect(), QtGui.QColor(self.theme["canvas_bg"]))

        glow = QtGui.QRadialGradient(self.rect().center(), max(self.width(), self.height()) * 0.55)
        glow.setColorAt(0.0, QtGui.QColor(255, 255, 255, 24))
        glow.setColorAt(1.0, QtGui.QColor(0, 0, 0, 0))
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(glow))
        painter.drawRect(self.rect())

        card_w = min(260, self.width() - 36)
        card_h = min(310, self.height() - 36)
        card_rect = QtCore.QRect(
            self.rect().center().x() - card_w // 2,
            self.rect().center().y() - card_h // 2,
            card_w,
            card_h,
        )
        painter.setPen(QtGui.QPen(QtGui.QColor(self.theme["frame"]), 2))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.theme["panel"])))
        painter.drawRoundedRect(card_rect, 14, 14)
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 56), 1))
        painter.drawRoundedRect(card_rect.adjusted(2, 2, -2, -2), 12, 12)

        painter.setPen(QtGui.QColor(self.theme["group_title"]))
        tfont = painter.font()
        tfont.setBold(True)
        tfont.setPointSize(max(10, tfont.pointSize() + 1))
        painter.setFont(tfont)
        title = PEDAL_LIBRARY.get(self.pedal_id, "Pedal")
        painter.drawText(card_rect.adjusted(8, 10, -8, -8), QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter, title)

        image_area = card_rect.adjusted(10, 34, -10, -24)
        draw_rect = image_area
        pixmap = self.pedal_pixmaps.get(self.pedal_id)
        if pixmap and not pixmap.isNull():
            scaled = pixmap.scaled(image_area.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            draw_rect = QtCore.QRect(
                image_area.left() + (image_area.width() - scaled.width()) // 2,
                image_area.top() + (image_area.height() - scaled.height()) // 2,
                scaled.width(),
                scaled.height(),
            )
            painter.drawPixmap(draw_rect, scaled)
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor(self.theme["frame"]), 1))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(self.theme["canvas_bg"])))
            painter.drawRoundedRect(draw_rect, 8, 8)

        if self.pedal_id in {"ge7", "eq10"}:
            self.draw_eq_face(painter, draw_rect)
        elif self.pedal_id == "rc30":
            self.draw_rc30_face(painter, draw_rect)
        else:
            knobs = list(self.face_values.get("knobs", [50, 50, 50]))
            while len(knobs) < 3:
                knobs.append(50)
            knob_y = draw_rect.top() + int(round(draw_rect.height() * 0.18))
            spacing = draw_rect.width() / 4.0
            for idx in range(3):
                center = QtCore.QPointF(draw_rect.left() + spacing * (idx + 1), knob_y)
                self.draw_knob(painter, center, knobs[idx], radius=14)

        jack_y = draw_rect.center().y()
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#f2f6fc")))
        painter.drawEllipse(QtCore.QPointF(draw_rect.left() + 8, jack_y), 4.0, 4.0)
        painter.drawEllipse(QtCore.QPointF(draw_rect.right() - 8, jack_y), 4.0, 4.0)

        painter.setPen(QtGui.QColor(self.theme["group_title"]))
        f = painter.font()
        f.setBold(True)
        f.setPointSize(max(8, f.pointSize() - 1))
        painter.setFont(f)
        painter.drawText(
            card_rect.adjusted(10, card_rect.height() - 24, -10, -2),
            QtCore.Qt.AlignCenter,
            "OUT  < signal flow >  IN",
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
            "theoryScale": "minor_pentatonic",
            "theoryShape": "g",
            "pedalReference": BANK_ORDER[0],
            "chain": list(DEFAULT_CHAIN),
            "canvasPositions": {},
            "canvasConnections": [],
            "theoryPanelLayout": {},
            "theoryPanelRows": 2,
        }
        self.connected_chain = []
        self.last_recommendation = None
        self.summary_selected_key = ""
        self.summary_best_key = "C"
        self.summary_style_chords = []
        self.summary_usual_keys = []
        self.summary_usual_major_keys = []
        self.style_progression_cache = {}
        self.crazy_payload_cache = {}
        self.app_config = self.load_app_config()
        self.feedback_limits_state = self.load_feedback_limiter_state()
        self.feedback_user_id = self.feedback_user_hash()
        self._theory_snap_timers = {}
        self._applying_theory_layout = False

        self._loading_ui = False
        self.load_state()
        self.build_ui()
        self.apply_theme()
        self.render_all()

    def build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        root = QtWidgets.QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        self.build_global_controls(root)

        self.tabs = QtWidgets.QTabWidget()
        root.addWidget(self.tabs)

        self.pedals_tab, self.pedals_tab_content = self.make_scrollable_tab()
        self.builder_tab, self.builder_tab_content = self.make_scrollable_tab()
        self.rig_setup_tab, self.rig_setup_tab_content = self.make_scrollable_tab()
        self.theory_tab, self.theory_tab_content = self.make_scrollable_tab()
        self.feedback_tab, self.feedback_tab_content = self.make_scrollable_tab()

        self.tabs.addTab(self.pedals_tab, "Pedals")
        self.tabs.addTab(self.builder_tab, "Builder")
        self.tabs.addTab(self.rig_setup_tab, "Rig Setup")
        self.tabs.addTab(self.theory_tab, "Theory")
        self.tabs.addTab(self.feedback_tab, "Feedback")

        self.build_builder_tab()
        self.build_pedals_tab()
        self.build_rig_setup_tab()
        self.build_theory_tab()
        self.build_feedback_tab()
        self.populate_controls()
        self.bind_builder_events()
        QtCore.QTimer.singleShot(0, self.initialize_splitter_sizes)

    def make_scrollable_tab(self):
        page = QtWidgets.QWidget()
        page_layout = QtWidgets.QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        content = QtWidgets.QWidget()
        scroll.setWidget(content)
        page_layout.addWidget(scroll)
        return page, content

    def initialize_splitter_sizes(self):
        if hasattr(self, "builder_splitter"):
            total_width = max(self.builder_splitter.width(), 920)
            left_width = clamp(int(total_width * 0.30), 260, 420)
            self.builder_splitter.setSizes([left_width, max(520, total_width - left_width)])

    def build_global_controls(self, root_layout):
        controls = QtWidgets.QFrame()
        controls_layout = QtWidgets.QHBoxLayout(controls)
        controls_layout.setContentsMargins(10, 10, 10, 8)
        controls_layout.setSpacing(10)
        controls_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.genre_combo = QtWidgets.QComboBox()
        self.genre_combo.setMinimumWidth(150)
        self.genre_combo.setMaximumWidth(220)

        style_wrap = QtWidgets.QGroupBox("Style")
        style_wrap.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        style_wrap.setMinimumWidth(210)
        style_layout = QtWidgets.QVBoxLayout(style_wrap)
        style_layout.setContentsMargins(8, 8, 8, 8)
        style_layout.setSpacing(6)
        style_layout.addWidget(self.genre_combo)

        self.guitar_type_electric = QtWidgets.QRadioButton("Electric")
        self.guitar_type_acoustic = QtWidgets.QRadioButton("Acoustic")
        self.guitar_type_group = QtWidgets.QButtonGroup(self)
        self.guitar_type_group.addButton(self.guitar_type_electric)
        self.guitar_type_group.addButton(self.guitar_type_acoustic)

        guitar_wrap = QtWidgets.QGroupBox("Guitar")
        guitar_wrap.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        guitar_wrap.setMinimumWidth(150)
        guitar_layout = QtWidgets.QVBoxLayout(guitar_wrap)
        guitar_layout.setContentsMargins(8, 8, 8, 8)
        guitar_layout.setSpacing(6)
        guitar_layout.addWidget(self.guitar_type_electric)
        guitar_layout.addWidget(self.guitar_type_acoustic)
        guitar_layout.addStretch(1)

        self.guitar_controls_stack = QtWidgets.QStackedWidget()
        electric_controls_page = QtWidgets.QWidget()
        electric_controls_layout = QtWidgets.QVBoxLayout(electric_controls_page)
        electric_controls_layout.setContentsMargins(0, 0, 0, 0)
        electric_controls_layout.setSpacing(6)
        self.profile_electric_2 = QtWidgets.QRadioButton("2 knob electric")
        self.profile_electric_4 = QtWidgets.QRadioButton("4 knob electric")
        self.profile_electric_2.setProperty("profileKey", "electric_2_knob_toggle")
        self.profile_electric_4.setProperty("profileKey", "electric_4_knob_toggle")
        self.electric_profile_group = QtWidgets.QButtonGroup(self)
        self.electric_profile_group.addButton(self.profile_electric_2)
        self.electric_profile_group.addButton(self.profile_electric_4)
        electric_controls_layout.addWidget(self.profile_electric_2)
        electric_controls_layout.addWidget(self.profile_electric_4)

        acoustic_controls_page = QtWidgets.QWidget()
        acoustic_controls_layout = QtWidgets.QVBoxLayout(acoustic_controls_page)
        acoustic_controls_layout.setContentsMargins(0, 0, 0, 0)
        acoustic_controls_layout.setSpacing(6)
        self.acoustic_controls_text = QtWidgets.QLineEdit("Acoustic (Taylor ES2)")
        self.acoustic_controls_text.setReadOnly(True)
        self.acoustic_controls_text.setMinimumWidth(220)
        acoustic_controls_layout.addWidget(self.acoustic_controls_text)

        self.guitar_controls_stack.addWidget(electric_controls_page)
        self.guitar_controls_stack.addWidget(acoustic_controls_page)
        self.guitar_controls_stack.setMinimumWidth(240)
        self.guitar_controls_stack.setMaximumWidth(460)
        self.guitar_controls_stack.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

        controls_wrap = QtWidgets.QGroupBox("Guitar Controls")
        controls_wrap.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        controls_wrap.setMinimumWidth(250)
        controls_sub_layout = QtWidgets.QVBoxLayout(controls_wrap)
        controls_sub_layout.setContentsMargins(8, 8, 8, 8)
        controls_sub_layout.setSpacing(6)
        controls_sub_layout.addWidget(self.guitar_controls_stack)

        self.amp_combo = QtWidgets.QComboBox()
        self.amp_combo.setMinimumWidth(180)
        self.amp_combo.setMaximumWidth(240)
        amp_wrap = QtWidgets.QGroupBox("Amp")
        amp_wrap.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        amp_wrap.setMinimumWidth(230)
        amp_layout = QtWidgets.QVBoxLayout(amp_wrap)
        amp_layout.setContentsMargins(8, 8, 8, 8)
        amp_layout.setSpacing(6)
        amp_layout.addWidget(self.amp_combo)

        self.font_size_combo = QtWidgets.QComboBox()
        self.theme_combo = QtWidgets.QComboBox()
        self.font_size_combo.setView(QtWidgets.QListView())

        self.optimize_btn = QtWidgets.QPushButton("Optimize For Me")
        self.optimize_btn.setMinimumWidth(130)
        self.save_btn = QtWidgets.QPushButton("Save Offline")
        self.settings_btn = QtWidgets.QToolButton()
        self.settings_btn.setText("⚙")
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setFixedSize(34, 34)
        self.settings_btn.setAutoRaise(False)

        self.settings_dialog = QtWidgets.QDialog(self)
        self.settings_dialog.setWindowTitle("Settings")
        self.settings_dialog.setModal(False)
        settings_layout = QtWidgets.QVBoxLayout(self.settings_dialog)
        settings_layout.setContentsMargins(12, 12, 12, 12)
        settings_layout.setSpacing(8)
        settings_form = QtWidgets.QFormLayout()
        settings_form.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        settings_form.setFormAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        settings_form.addRow("Font Size", self.font_size_combo)
        settings_form.addRow("Color Scheme", self.theme_combo)
        settings_layout.addLayout(settings_form)
        settings_close_row = QtWidgets.QHBoxLayout()
        settings_close_row.addStretch(1)
        settings_close_btn = QtWidgets.QPushButton("Close")
        settings_close_btn.clicked.connect(self.settings_dialog.hide)
        settings_close_row.addWidget(settings_close_btn)
        settings_layout.addLayout(settings_close_row)

        controls_layout.addWidget(style_wrap, 0, QtCore.Qt.AlignTop)
        controls_layout.addWidget(guitar_wrap, 0, QtCore.Qt.AlignTop)
        controls_layout.addWidget(controls_wrap, 0, QtCore.Qt.AlignTop)
        controls_layout.addWidget(amp_wrap, 0, QtCore.Qt.AlignTop)
        controls_layout.addStretch(1)
        controls_layout.addWidget(self.optimize_btn)
        controls_layout.addWidget(self.save_btn)
        controls_layout.addWidget(self.settings_btn)

        root_layout.addWidget(controls)

    def build_builder_tab(self):
        layout = QtWidgets.QVBoxLayout(self.builder_tab_content)
        layout.setContentsMargins(6, 6, 6, 6)
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
            "Pedal input is on the right, output on the left. Drag from output to input to cable. Use x to remove a pedal, green L side buttons to start/target links, and red - side buttons to disconnect that side."
        )
        board_hint.setWordWrap(True)
        board_layout.addWidget(board_hint)
        self.chain_score = QtWidgets.QLabel("Tone Match: --")
        self.chain_summary = QtWidgets.QLabel("")
        self.chain_summary.setWordWrap(True)
        self.chain_score.setStyleSheet("font-weight: 700;")
        board_layout.addWidget(self.chain_score)
        board_layout.addWidget(self.chain_summary)

        for panel in [bank_group, board_group]:
            panel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.builder_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.builder_splitter.addWidget(bank_group)
        self.builder_splitter.addWidget(board_group)
        self.builder_splitter.setChildrenCollapsible(False)
        self.builder_splitter.setStretchFactor(0, 3)
        self.builder_splitter.setStretchFactor(1, 7)
        layout.addWidget(self.builder_splitter, 1)

        self.clean_up_btn = QtWidgets.QPushButton("Tidy UP")
        self.auto_wire_btn = QtWidgets.QPushButton("Auto Wire")
        self.clear_cables_btn = QtWidgets.QPushButton("Clear Cables")
        self.reset_btn = QtWidgets.QPushButton("Reset Chain")
        builder_actions = QtWidgets.QHBoxLayout()
        builder_actions.setSpacing(8)
        builder_actions.addWidget(self.clean_up_btn)
        builder_actions.addWidget(self.auto_wire_btn)
        builder_actions.addWidget(self.clear_cables_btn)
        builder_actions.addWidget(self.reset_btn)
        builder_actions.addStretch(1)
        layout.addLayout(builder_actions)

    def build_pedals_tab(self):
        layout = QtWidgets.QVBoxLayout(self.pedals_tab_content)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(10)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        selector_group = QtWidgets.QGroupBox("Pedal Selector")
        selector_layout = QtWidgets.QVBoxLayout(selector_group)
        selector_hint = QtWidgets.QLabel("Select a pedal to inspect behavior, setup strategy, and advanced options.")
        selector_hint.setWordWrap(True)
        selector_layout.addWidget(selector_hint)
        self.pedal_selector_list = QtWidgets.QListWidget()
        self.pedal_selector_list.setAlternatingRowColors(True)
        self.pedal_selector_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        for pedal_id in BANK_ORDER:
            item = QtWidgets.QListWidgetItem(PEDAL_LIBRARY[pedal_id])
            item.setData(QtCore.Qt.UserRole, pedal_id)
            base = QtGui.QColor(PEDAL_COLORS.get(pedal_id, "#b0b0b0"))
            item.setBackground(base.lighter(115))
            item.setForeground(QtGui.QColor(PEDAL_TEXT_COLORS.get(pedal_id, "#11171f")))
            self.pedal_selector_list.addItem(item)
        selector_layout.addWidget(self.pedal_selector_list, 1)
        splitter.addWidget(selector_group)

        visual_group = QtWidgets.QGroupBox("Pedal Visual")
        visual_layout = QtWidgets.QVBoxLayout(visual_group)
        self.pedal_showcase = PedalShowcaseWidget()
        self.pedal_visual_hint = QtWidgets.QLabel("Visual pointer/levers update from current style and rig recommendation.")
        self.pedal_visual_hint.setWordWrap(True)
        visual_layout.addWidget(self.pedal_showcase, 1)
        visual_layout.addWidget(self.pedal_visual_hint)
        splitter.addWidget(visual_group)

        details_group = QtWidgets.QGroupBox("Pedal Guide")
        details_layout = QtWidgets.QVBoxLayout(details_group)
        self.pedal_details_text = QtWidgets.QTextEdit()
        self.pedal_details_text.setReadOnly(True)
        details_layout.addWidget(self.pedal_details_text, 1)
        splitter.addWidget(details_group)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 4)
        layout.addWidget(splitter, 1)

        self.pedal_selector_list.currentItemChanged.connect(self.on_pedal_reference_changed)
        selected = self.state.get("pedalReference", BANK_ORDER[0])
        selected_row = 0
        for idx in range(self.pedal_selector_list.count()):
            if self.pedal_selector_list.item(idx).data(QtCore.Qt.UserRole) == selected:
                selected_row = idx
                break
        self.pedal_selector_list.setCurrentRow(selected_row)

    def build_rig_setup_tab(self):
        layout = QtWidgets.QVBoxLayout(self.rig_setup_tab_content)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

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
        summary_group = QtWidgets.QGroupBox("Rig Summary")
        summary_layout = QtWidgets.QVBoxLayout(summary_group)
        self.summary_text = QtWidgets.QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(96)
        summary_layout.addWidget(self.summary_text)
        layout.addWidget(summary_group, 1)

    def build_theory_tab(self):
        layout = QtWidgets.QVBoxLayout(self.theory_tab_content)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        pentatonic_group = QtWidgets.QGroupBox("Scale + CAGED Chart")
        pentatonic_layout = QtWidgets.QVBoxLayout(pentatonic_group)
        pentatonic_layout.setSpacing(6)
        top_controls = QtWidgets.QHBoxLayout()
        top_controls.setSpacing(8)
        scale_label = QtWidgets.QLabel("Scale")
        scale_font = QtGui.QFont(scale_label.font())
        scale_font.setBold(True)
        scale_label.setFont(scale_font)
        top_controls.addWidget(scale_label)
        self.scale_type_combo = QtWidgets.QComboBox()
        self.scale_type_combo.setMinimumHeight(34)
        for scale_key in ["minor_pentatonic", "major_pentatonic", "minor_blues", "major_scale", "natural_minor", "mixolydian"]:
            self.scale_type_combo.addItem(SCALE_LIBRARY[scale_key]["label"], scale_key)
        self.set_combo_by_data(self.scale_type_combo, self.state.get("theoryScale", "minor_pentatonic"))
        top_controls.addWidget(self.scale_type_combo, 1)
        shape_label = QtWidgets.QLabel("CAGED Shape")
        shape_font = QtGui.QFont(shape_label.font())
        shape_font.setBold(True)
        shape_label.setFont(shape_font)
        top_controls.addWidget(shape_label)
        self.pentatonic_shape_combo = QtWidgets.QComboBox()
        self.pentatonic_shape_combo.setMinimumHeight(34)
        for shape_key in ["c", "a", "g", "e", "d"]:
            self.pentatonic_shape_combo.addItem(CAGED_SHAPES[shape_key]["label"], shape_key)
        self.set_combo_by_data(self.pentatonic_shape_combo, self.state.get("theoryShape", "g"))
        top_controls.addWidget(self.pentatonic_shape_combo, 1)
        pentatonic_layout.addLayout(top_controls)

        self.pentatonic_hint = QtWidgets.QLabel("15-fret map for selected key.")
        self.pentatonic_hint.setWordWrap(False)
        pentatonic_layout.addWidget(self.pentatonic_hint)
        self.pentatonic_neck = PentatonicNeckWidget()
        self.pentatonic_neck.setMinimumHeight(200)
        pentatonic_layout.addWidget(self.pentatonic_neck, 1)
        layout.addWidget(pentatonic_group, 2)

        theory_grid_host = QtWidgets.QWidget()
        theory_grid = QtWidgets.QGridLayout(theory_grid_host)
        theory_grid.setContentsMargins(0, 0, 0, 0)
        theory_grid.setHorizontalSpacing(8)
        theory_grid.setVerticalSpacing(8)
        theory_grid.setColumnStretch(0, 1)
        theory_grid.setColumnStretch(1, 1)
        theory_grid.setRowStretch(0, 1)
        theory_grid.setRowStretch(1, 1)

        nashville_group = QtWidgets.QGroupBox("Nashville Number Chart")
        nashville_layout = QtWidgets.QVBoxLayout(nashville_group)
        nashville_layout.setContentsMargins(8, 8, 8, 8)
        nashville_layout.setSpacing(6)
        self.nashville_hint = QtWidgets.QLabel("Select a row to drive highlights and scale context.")
        self.nashville_hint.setWordWrap(False)
        self.nashville_table = QtWidgets.QTableWidget(len(NASHVILLE_MAJOR_CHART), 8)
        self.nashville_table.setHorizontalHeaderLabels(["Key", "1", "2m", "3m", "4", "5", "6m", "7dim"])
        self.nashville_table.verticalHeader().setVisible(False)
        self.nashville_table.verticalHeader().setDefaultSectionSize(20)
        self.nashville_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.nashville_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.nashville_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.nashville_table.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.nashville_table.setAlternatingRowColors(True)
        self.nashville_table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.nashville_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.usual_keys_label = QtWidgets.QLabel("")
        self.usual_keys_label.setObjectName("usualKeysLabel")
        self.usual_keys_label.setWordWrap(True)
        nashville_layout.addWidget(self.nashville_hint)
        nashville_layout.addWidget(self.usual_keys_label)
        nashville_layout.addWidget(self.nashville_table, 1)
        theory_grid.addWidget(nashville_group, 0, 0)

        circle_group = QtWidgets.QGroupBox("Circle of Fifths")
        circle_layout = QtWidgets.QVBoxLayout(circle_group)
        circle_layout.setContentsMargins(8, 8, 8, 8)
        circle_layout.setSpacing(6)
        self.circle_of_fifths = CircleOfFifthsWidget()
        self.circle_hint = QtWidgets.QLabel("Highlights follow the selected Nashville row.")
        self.circle_hint.setWordWrap(True)
        circle_layout.addWidget(self.circle_of_fifths, 1)
        circle_layout.addWidget(self.circle_hint)
        theory_grid.addWidget(circle_group, 0, 1)

        playbook_group = QtWidgets.QGroupBox("Style Playbook")
        playbook_layout = QtWidgets.QVBoxLayout(playbook_group)
        playbook_layout.setContentsMargins(8, 8, 8, 8)
        self.playbook_preview = QtWidgets.QTextEdit()
        self.playbook_preview.setReadOnly(True)
        playbook_layout.addWidget(self.playbook_preview, 1)
        theory_grid.addWidget(playbook_group, 1, 0)

        crazy_group = QtWidgets.QGroupBox("Creative Theory")
        crazy_layout = QtWidgets.QVBoxLayout(crazy_group)
        crazy_layout.setContentsMargins(8, 8, 8, 8)
        crazy_layout.setSpacing(8)
        self.crazy_btn = QtWidgets.QPushButton("Lets get Crazy")
        self.crazy_btn.setMinimumHeight(32)
        crazy_layout.addWidget(self.crazy_btn, 0, QtCore.Qt.AlignLeft)
        crazy_content_row = QtWidgets.QHBoxLayout()
        crazy_content_row.setSpacing(8)
        self.crazy_progression_text = QtWidgets.QTextEdit()
        self.crazy_progression_text.setReadOnly(True)
        self.crazy_scale_text = QtWidgets.QTextEdit()
        self.crazy_scale_text.setReadOnly(True)
        crazy_content_row.addWidget(self.crazy_progression_text, 1)
        crazy_content_row.addWidget(self.crazy_scale_text, 1)
        crazy_layout.addLayout(crazy_content_row, 1)
        theory_grid.addWidget(crazy_group, 1, 1)

        layout.addWidget(theory_grid_host, 3)

        self.populate_nashville_table()
        self.nashville_table.itemSelectionChanged.connect(self.on_nashville_selection_changed)
        self.pentatonic_shape_combo.currentIndexChanged.connect(self.on_pentatonic_shape_changed)
        self.scale_type_combo.currentIndexChanged.connect(self.on_scale_type_changed)
        self.crazy_btn.clicked.connect(self.on_lets_get_crazy)

    def create_theory_panel(self, panel_key, title, widget):
        subwindow = TheoryPanelSubWindow(panel_key)
        subwindow.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        subwindow.setWindowFlags(
            QtCore.Qt.SubWindow
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowSystemMenuHint
            | QtCore.Qt.WindowMinimizeButtonHint
        )
        subwindow.setWidget(widget)
        subwindow.setWindowTitle(title)
        subwindow.setOption(QtWidgets.QMdiSubWindow.RubberBandMove, True)
        subwindow.setOption(QtWidgets.QMdiSubWindow.RubberBandResize, True)
        self.theory_workspace.addSubWindow(subwindow)
        self.theory_panels[panel_key] = subwindow
        subwindow.restored_from_minimize.connect(self.on_theory_panel_restored)
        subwindow.minimized_changed.connect(self.on_theory_panel_minimized_changed)
        subwindow.geometry_changed.connect(self.on_theory_panel_geometry_changed)
        snap_timer = QtCore.QTimer(self)
        snap_timer.setSingleShot(True)
        snap_timer.timeout.connect(lambda key=panel_key: self.snap_theory_panel_to_zone(key))
        self._theory_snap_timers[panel_key] = snap_timer
        subwindow.show()

    def theory_panel_default_slots(self):
        return {
            "nashville": {"mode": "quarter", "row": 0, "col": 0},
            "circle": {"mode": "quarter", "row": 1, "col": 0},
            "playbook": {"mode": "quarter", "row": 0, "col": 1},
            "crazy": {"mode": "quarter", "row": 1, "col": 1},
        }

    def theory_zone_rects(self, rows=None):
        if not hasattr(self, "theory_workspace"):
            return {}
        rows = max(2, int(rows if rows is not None else getattr(self, "theory_grid_rows", 2)))
        viewport = self.theory_workspace.viewport().rect().adjusted(8, 8, -8, -8)
        if viewport.width() < 100 or viewport.height() < 100:
            return {}
        gap = 8
        col_w = max(240, (viewport.width() - gap) // 2)
        if not hasattr(self, "theory_base_row_height"):
            self.theory_base_row_height = max(150, (max(360, viewport.height()) - gap) // 2)
        row_h = int(max(120, self.theory_base_row_height))
        needed_h = rows * row_h + max(0, rows - 1) * gap
        self.theory_workspace.setMinimumHeight(max(360, needed_h + 16))
        left = viewport.left()
        top = viewport.top()
        full_w = col_w * 2 + gap
        quarter = {}
        half = {}
        for row in range(rows):
            y = top + row * (row_h + gap)
            quarter[(row, 0)] = QtCore.QRect(left, y, col_w, row_h)
            quarter[(row, 1)] = QtCore.QRect(left + col_w + gap, y, col_w, row_h)
            half[row] = QtCore.QRect(left, y, full_w, row_h)
        return {
            "quarter": quarter,
            "half": half,
            "meta": {
                "rows": rows,
                "gap": gap,
                "col_w": col_w,
                "row_h": row_h,
                "left": left,
                "top": top,
                "full_w": full_w,
            },
        }

    def theory_panel_rect_for_slot(self, slot, zones):
        if not slot or not zones:
            return QtCore.QRect()
        mode = slot.get("mode", "quarter")
        row = max(0, int(slot.get("row", 0)))
        if mode == "half":
            return zones["half"].get(row, QtCore.QRect())
        col = 0 if int(slot.get("col", 0)) <= 0 else 1
        return zones["quarter"].get((row, col), QtCore.QRect())

    def theory_panel_slot_from_geometry(self, panel_rect):
        zones = self.theory_zone_rects()
        if not zones:
            return {"mode": "quarter", "row": 0, "col": 0}
        meta = zones["meta"]
        center = panel_rect.center()
        row_step = max(1, meta["row_h"] + meta["gap"])
        row = clamp(int(round((center.y() - meta["top"]) / float(row_step))), 0, max(0, meta["rows"] - 1))
        if panel_rect.width() >= int(meta["full_w"] * 0.74):
            return {"mode": "half", "row": row}
        col = 0 if center.x() < (meta["left"] + meta["col_w"]) else 1
        return {"mode": "quarter", "row": row, "col": col}

    def theory_active_panel_keys(self):
        keys = []
        for key, subwindow in self.theory_panels.items():
            if subwindow.windowState() & QtCore.Qt.WindowMinimized:
                continue
            keys.append(key)
        return keys

    def normalize_theory_slot(self, slot, fallback=None):
        fallback = fallback or {"mode": "quarter", "row": 0, "col": 0}
        base_mode = "half" if fallback.get("mode") == "half" else "quarter"
        base_row = max(0, int(fallback.get("row", 0)))
        base_col = 0 if int(fallback.get("col", 0)) <= 0 else 1
        mode = base_mode
        row = base_row
        col = base_col
        if isinstance(slot, dict):
            mode = "half" if slot.get("mode") == "half" else "quarter"
            try:
                row = int(slot.get("row", base_row))
            except Exception:
                row = base_row
            try:
                col = int(slot.get("col", base_col))
            except Exception:
                col = base_col
        row = max(0, row)
        if mode == "half":
            return {"mode": "half", "row": row}
        return {"mode": "quarter", "row": row, "col": 0 if col <= 0 else 1}

    def theory_slot_cells(self, slot):
        normalized = self.normalize_theory_slot(slot)
        row = int(normalized.get("row", 0))
        if normalized.get("mode") == "half":
            return [(row, 0), (row, 1)]
        col = 0 if int(normalized.get("col", 0)) <= 0 else 1
        return [(row, col)]

    def place_theory_slot(self, slot, occupied_cells):
        normalized = self.normalize_theory_slot(slot)
        mode = normalized.get("mode", "quarter")
        row = int(normalized.get("row", 0))
        if mode == "half":
            while (row, 0) in occupied_cells or (row, 1) in occupied_cells:
                row += 1
            return {"mode": "half", "row": row}

        preferred_col = 0 if int(normalized.get("col", 0)) <= 0 else 1
        alt_col = 1 - preferred_col
        if (row, preferred_col) not in occupied_cells:
            return {"mode": "quarter", "row": row, "col": preferred_col}
        if (row, alt_col) not in occupied_cells:
            return {"mode": "quarter", "row": row, "col": alt_col}
        while True:
            row += 1
            if (row, preferred_col) not in occupied_cells:
                return {"mode": "quarter", "row": row, "col": preferred_col}
            if (row, alt_col) not in occupied_cells:
                return {"mode": "quarter", "row": row, "col": alt_col}

    def resolve_theory_panel_slots(self, lead_key=None, compact_quarters=False):
        if not hasattr(self, "theory_panels"):
            return False
        active_keys = self.theory_active_panel_keys()
        if not active_keys:
            self.theory_grid_rows = 2
            return False

        defaults = self.theory_panel_default_slots()
        for key in self.theory_panels.keys():
            fallback = defaults.get(key, {"mode": "quarter", "row": 0, "col": 0})
            self.theory_panel_slots[key] = self.normalize_theory_slot(self.theory_panel_slots.get(key), fallback)

        ordered = sorted(
            active_keys,
            key=lambda key: (
                int(self.theory_panel_slots.get(key, {}).get("row", 0)),
                0 if self.theory_panel_slots.get(key, {}).get("mode") == "half" else 1,
                int(self.theory_panel_slots.get(key, {}).get("col", 0)),
                key,
            ),
        )
        if lead_key in ordered:
            ordered.remove(lead_key)
            ordered.insert(0, lead_key)

        placed = {}
        occupied_cells = set()
        for key in ordered:
            slot = self.place_theory_slot(self.theory_panel_slots.get(key), occupied_cells)
            placed[key] = slot
            for cell in self.theory_slot_cells(slot):
                occupied_cells.add(cell)

        if compact_quarters and ordered and all(placed[key].get("mode") == "quarter" for key in ordered):
            compacted = {}
            for idx, key in enumerate(ordered):
                compacted[key] = {"mode": "quarter", "row": idx // 2, "col": idx % 2}
            placed = compacted

        changed = False
        max_row = 1
        for key, slot in placed.items():
            previous = self.theory_panel_slots.get(key)
            if previous != slot:
                changed = True
            self.theory_panel_slots[key] = slot
            max_row = max(max_row, int(slot.get("row", 0)))

        self.theory_grid_rows = max(2, max_row + 1)
        return changed

    def theory_slot_conflicts(self, panel_key, candidate_slot):
        target_cells = set(self.theory_slot_cells(candidate_slot))
        for other_key, subwindow in self.theory_panels.items():
            if other_key == panel_key:
                continue
            if subwindow.windowState() & QtCore.Qt.WindowMinimized:
                continue
            other_slot = self.theory_panel_slots.get(other_key, self.theory_panel_default_slots().get(other_key, {"mode": "quarter", "row": 0, "col": 0}))
            other_cells = set(self.theory_slot_cells(other_slot))
            if target_cells.intersection(other_cells):
                return True
        return False

    def normalize_quarter_layout_if_needed(self):
        active_keys = self.theory_active_panel_keys()
        if not active_keys:
            self.theory_grid_rows = 2
            return
        if not all(self.normalize_theory_slot(self.theory_panel_slots.get(key)).get("mode") == "quarter" for key in active_keys):
            return
        self.resolve_theory_panel_slots(compact_quarters=True)

    def layout_theory_panels_from_slots(self):
        zones = self.theory_zone_rects()
        if not zones:
            return
        self._applying_theory_layout = True
        try:
            for key, subwindow in self.theory_panels.items():
                if subwindow.windowState() & QtCore.Qt.WindowMinimized:
                    continue
                slot = self.theory_panel_slots.get(key, self.theory_panel_default_slots().get(key, {"mode": "quarter", "row": 0, "col": 0}))
                rect = self.theory_panel_rect_for_slot(slot, zones)
                if rect.isNull():
                    continue
                subwindow.showNormal()
                subwindow.setGeometry(rect)
        finally:
            self._applying_theory_layout = False
        self.arrange_minimized_theory_panels()

    def snap_theory_panel_to_zone(self, panel_key):
        if self._applying_theory_layout:
            return
        subwindow = self.theory_panels.get(panel_key)
        if not subwindow or (subwindow.windowState() & QtCore.Qt.WindowMinimized):
            return
        defaults = self.theory_panel_default_slots()
        candidate = self.normalize_theory_slot(self.theory_panel_slot_from_geometry(subwindow.geometry()), defaults.get(panel_key, {"mode": "quarter", "row": 0, "col": 0}))
        had_conflict = self.theory_slot_conflicts(panel_key, candidate)
        if had_conflict:
            occupied_rows = [int(self.normalize_theory_slot(self.theory_panel_slots.get(key), defaults.get(key)).get("row", 0)) for key in self.theory_active_panel_keys() if key != panel_key]
            next_row = max([int(getattr(self, "theory_grid_rows", 2)) - 1] + occupied_rows) + 1
            candidate["row"] = next_row
        self.theory_panel_slots[panel_key] = candidate
        self.resolve_theory_panel_slots(lead_key=panel_key, compact_quarters=(not had_conflict))
        self.layout_theory_panels_from_slots()
        self.persist_theory_panel_layout()

    def on_theory_panel_geometry_changed(self, panel_key):
        if self._applying_theory_layout:
            return
        subwindow = self.theory_panels.get(panel_key)
        if not subwindow or (subwindow.windowState() & QtCore.Qt.WindowMinimized):
            return
        timer = self._theory_snap_timers.get(panel_key)
        if timer:
            timer.start(150)

    def on_theory_panel_minimized_changed(self, _panel_key, is_minimized):
        if is_minimized:
            self.arrange_minimized_theory_panels()
        self.resolve_theory_panel_slots(compact_quarters=True)
        self.layout_theory_panels_from_slots()
        self.persist_theory_panel_layout()

    def arrange_minimized_theory_panels(self):
        if not hasattr(self, "theory_panels") or not hasattr(self, "theory_workspace"):
            return
        viewport = self.theory_workspace.viewport().rect().adjusted(6, 6, -6, -6)
        minimized = [
            sub for key, sub in sorted(self.theory_panels.items())
            if sub.windowState() & QtCore.Qt.WindowMinimized
        ]
        if not minimized:
            return
        tab_w = 170
        tab_h = 28
        gap = 6
        x = viewport.left()
        y = viewport.top()
        for sub in minimized:
            if x + tab_w > viewport.right() and x > viewport.left():
                x = viewport.left()
                y += tab_h + gap
            sub.setGeometry(QtCore.QRect(x, y, tab_w, tab_h))
            sub.raise_()
            x += tab_w + gap

    def capture_theory_panel_layout(self):
        if not hasattr(self, "theory_panels"):
            return {}
        layout = {}
        for key, subwindow in self.theory_panels.items():
            minimized = bool(subwindow.windowState() & QtCore.Qt.WindowMinimized)
            rect = subwindow.normalGeometry() if minimized else subwindow.geometry()
            if rect.isNull():
                rect = subwindow.geometry()
            layout[key] = {
                "x": int(rect.x()),
                "y": int(rect.y()),
                "w": int(max(120, rect.width())),
                "h": int(max(100, rect.height())),
                "minimized": minimized,
                "slot": dict(self.theory_panel_slots.get(key, {})),
            }
        return layout

    def apply_saved_theory_panel_layout(self):
        saved = self.state.get("theoryPanelLayout")
        if not isinstance(saved, dict) or not saved:
            return False
        if not hasattr(self, "theory_panels"):
            return False
        self.theory_grid_rows = max(2, int(self.state.get("theoryPanelRows", 2) or 2))
        applied = False
        defaults = self.theory_panel_default_slots()
        for key, subwindow in self.theory_panels.items():
            payload = saved.get(key)
            if not isinstance(payload, dict):
                continue
            slot = payload.get("slot")
            if isinstance(slot, dict) and slot.get("mode") in {"quarter", "half"}:
                parsed = self.normalize_theory_slot(slot, defaults.get(key, {"mode": "quarter", "row": 0, "col": 0}))
                self.theory_panel_slots[key] = parsed
                applied = True
            else:
                try:
                    x = int(payload.get("x", 0))
                    y = int(payload.get("y", 0))
                    w = int(payload.get("w", 300))
                    h = int(payload.get("h", 220))
                except Exception:
                    continue
                inferred = self.normalize_theory_slot(
                    self.theory_panel_slot_from_geometry(QtCore.QRect(x, y, w, h)),
                    defaults.get(key, {"mode": "quarter", "row": 0, "col": 0}),
                )
                self.theory_panel_slots[key] = inferred
                applied = True

        self.resolve_theory_panel_slots(compact_quarters=False)
        self.layout_theory_panels_from_slots()
        for key, subwindow in self.theory_panels.items():
            payload = saved.get(key)
            if isinstance(payload, dict) and bool(payload.get("minimized", False)):
                subwindow.showMinimized()
        self.resolve_theory_panel_slots(compact_quarters=True)
        self.layout_theory_panels_from_slots()
        self.arrange_minimized_theory_panels()
        return applied

    def persist_theory_panel_layout(self):
        self.state["theoryPanelRows"] = int(max(2, getattr(self, "theory_grid_rows", 2)))
        self.state["theoryPanelLayout"] = self.capture_theory_panel_layout()
        self.persist_state(silent=True)

    def reset_theory_panel_layout(self, panel_key=None):
        if not hasattr(self, "theory_panels"):
            return
        defaults = self.theory_panel_default_slots()
        if panel_key is None:
            self.theory_grid_rows = 2
            self.theory_panel_slots = dict(defaults)
        else:
            self.theory_panel_slots[panel_key] = dict(defaults.get(panel_key, {"mode": "quarter", "row": 0, "col": 0}))
        self.resolve_theory_panel_slots(lead_key=panel_key, compact_quarters=True)
        self.layout_theory_panels_from_slots()
        self.persist_theory_panel_layout()

    def on_theory_panel_restored(self, panel_key):
        QtCore.QTimer.singleShot(0, lambda key=panel_key: self.snap_theory_panel_to_zone(key))

    def build_feedback_tab(self):
        layout = QtWidgets.QVBoxLayout(self.feedback_tab_content)
        layout.setSpacing(10)
        layout.setContentsMargins(6, 6, 6, 6)

        top_row = QtWidgets.QHBoxLayout()
        top_row.setSpacing(10)

        feedback_group = QtWidgets.QGroupBox("Feedback")
        feedback_layout = QtWidgets.QVBoxLayout(feedback_group)
        form_layout = QtWidgets.QFormLayout()
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        form_layout.setFormAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(10)
        form_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        self.feedback_name_input = QtWidgets.QLineEdit()
        self.feedback_name_input.setPlaceholderText("Name (optional)")
        self.feedback_email_input = QtWidgets.QLineEdit()
        self.feedback_email_input.setPlaceholderText("Email (optional)")
        self.feedback_rating_combo = QtWidgets.QComboBox()
        for text, value in [("5 - Excellent", 5), ("4 - Good", 4), ("3 - Okay", 3), ("2 - Needs work", 2), ("1 - Rough", 1)]:
            self.feedback_rating_combo.addItem(text, value)
        self.feedback_type_combo = QtWidgets.QComboBox()
        for label, key in [
            ("Tone Recommendation", "tone"),
            ("UI / UX", "ui"),
            ("Feature Request", "feature"),
            ("Bug Report", "bug"),
            ("General", "general"),
        ]:
            self.feedback_type_combo.addItem(label, key)
        self.feedback_message_input = QtWidgets.QTextEdit()
        self.feedback_message_input.setPlaceholderText("Tell us what worked, what did not, and what to improve.")
        self.feedback_message_input.setMinimumHeight(180)
        self.feedback_message_input.setMaximumHeight(220)
        for widget in [self.feedback_name_input, self.feedback_email_input, self.feedback_rating_combo, self.feedback_type_combo]:
            widget.setMinimumHeight(34)
            widget.setMinimumWidth(360)
        self.feedback_message_input.setMinimumWidth(360)

        form_layout.addRow("Name", self.feedback_name_input)
        form_layout.addRow("Email", self.feedback_email_input)
        form_layout.addRow("Rating", self.feedback_rating_combo)
        form_layout.addRow("Type", self.feedback_type_combo)
        form_layout.addRow("Message", self.feedback_message_input)
        feedback_layout.addLayout(form_layout)

        submit_row = QtWidgets.QHBoxLayout()
        self.feedback_submit_btn = QtWidgets.QPushButton("Submit Feedback")
        self.feedback_submit_btn.setMinimumHeight(36)
        self.feedback_submit_btn.setMinimumWidth(170)
        self.feedback_status_label = QtWidgets.QLabel("")
        self.feedback_status_label.setWordWrap(True)
        self.feedback_status_label.setMinimumHeight(36)
        submit_row.addWidget(self.feedback_submit_btn)
        submit_row.addWidget(self.feedback_status_label, 1)
        feedback_layout.addLayout(submit_row)

        self.feedback_limit_label = QtWidgets.QLabel("")
        self.feedback_limit_label.setWordWrap(True)
        feedback_layout.addWidget(self.feedback_limit_label)
        top_row.addWidget(feedback_group, 4)

        donate_group = QtWidgets.QGroupBox("Support Development")
        donate_layout = QtWidgets.QVBoxLayout(donate_group)
        donate_layout.addWidget(QtWidgets.QLabel("Choose a method and open/send directly:"))
        donate_row = QtWidgets.QHBoxLayout()
        donate_row.setSpacing(8)
        self.donate_method_combo = QtWidgets.QComboBox()
        for label, key in [("PayPal", "paypal"), ("Venmo", "venmo"), ("Zelle", "zelle")]:
            self.donate_method_combo.addItem(label, key)
        self.donate_btn = QtWidgets.QPushButton("Donate")
        self.donate_method_combo.setMinimumHeight(34)
        self.donate_btn.setMinimumHeight(34)
        donate_row.addWidget(self.donate_method_combo, 1)
        donate_row.addWidget(self.donate_btn)
        donate_layout.addLayout(donate_row)
        self.donate_details_label = QtWidgets.QLabel("")
        self.donate_details_label.setWordWrap(True)
        donate_layout.addWidget(self.donate_details_label)
        donate_layout.addStretch(1)
        top_row.addWidget(donate_group, 2)

        layout.addLayout(top_row, 1)

        self.feedback_submit_btn.clicked.connect(self.submit_feedback)
        self.donate_btn.clicked.connect(self.handle_donate)

    def make_info_panel(self, title):
        group = QtWidgets.QGroupBox(title)
        group_layout = QtWidgets.QVBoxLayout(group)
        text = QtWidgets.QTextEdit()
        text.setReadOnly(True)
        text.setMinimumHeight(78)
        text.setMaximumHeight(160)
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
        frame.setMinimumHeight(180)
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

    def table_row_for_key(self, key_name):
        for row in range(self.nashville_table.rowCount()):
            item = self.nashville_table.item(row, 0)
            if item and item.text() == key_name:
                return row
        return -1

    def selected_nashville_key(self):
        model = self.nashville_table.selectionModel()
        if not model:
            return ""
        rows = model.selectedRows()
        if not rows:
            return ""
        row = rows[0].row()
        item = self.nashville_table.item(row, 0)
        return item.text() if item else ""

    def set_nashville_selected_key(self, key_name):
        row = self.table_row_for_key(key_name)
        self.nashville_table.blockSignals(True)
        self.nashville_table.clearSelection()
        if row >= 0:
            self.nashville_table.selectRow(row)
            self.nashville_table.setCurrentCell(row, 0)
        self.nashville_table.blockSignals(False)

    def highlight_nashville_key(self, key_name, usual_major_keys=None):
        theme = theme_for_key(self.state.get("theme", "dark"))
        normal_bg = QtGui.QColor(theme["panel"])
        normal_fg = QtGui.QColor(theme["text"])
        positive_bg = QtGui.QColor(theme.get("positive", "#66d17a"))
        positive_bg.setAlpha(80)
        highlight_bg = QtGui.QColor(theme["tab_selected_bg"])
        highlight_fg = QtGui.QColor(theme["tab_selected_fg"])
        usual_set = set(usual_major_keys or [])
        for row in range(self.nashville_table.rowCount()):
            key_item = self.nashville_table.item(row, 0)
            row_key = key_item.text() if key_item else ""
            is_match = row_key == key_name
            is_usual = row_key in usual_set
            for col in range(self.nashville_table.columnCount()):
                item = self.nashville_table.item(row, col)
                if item is None:
                    continue
                if is_match:
                    item.setBackground(highlight_bg)
                    item.setForeground(highlight_fg)
                elif is_usual:
                    item.setBackground(positive_bg)
                    item.setForeground(normal_fg)
                else:
                    item.setBackground(normal_bg)
                    item.setForeground(normal_fg)
                font = item.font()
                font.setBold(is_match or is_usual)
                item.setFont(font)

    def update_summary_key_visuals(self, selected_key):
        if not selected_key:
            return
        self.summary_selected_key = selected_key
        selected_chords = nashville_degrees_for_key(selected_key)
        if selected_chords:
            self.circle_of_fifths.set_highlighted_chords(selected_chords)
            self.circle_hint.setText(f"Selected key {selected_key} highlights: " + ", ".join(selected_chords))
        else:
            self.circle_of_fifths.set_highlighted_chords(self.summary_style_chords)
            self.circle_hint.setText("Highlighted chords: " + ", ".join(self.summary_style_chords))

        self.highlight_nashville_key(selected_key, self.summary_usual_major_keys)
        if selected_key == self.summary_best_key:
            self.nashville_hint.setText(f"Selected key: {selected_key} (matches suggested key)")
        else:
            self.nashville_hint.setText(
                f"Suggested key: {self.summary_best_key} | Selected key: {selected_key}"
            )
        self.refresh_theory_panel(selected_key)

    def on_nashville_selection_changed(self):
        selected_key = self.selected_nashville_key()
        if not selected_key:
            return
        self.update_summary_key_visuals(selected_key)

    def on_pentatonic_shape_changed(self):
        if hasattr(self, "pentatonic_shape_combo"):
            selected = self.pentatonic_shape_combo.currentData()
            if selected in CAGED_SHAPES:
                self.state["theoryShape"] = selected
        self.refresh_theory_panel(self.selected_theory_key())
        self.persist_state(silent=True)

    def on_scale_type_changed(self):
        if hasattr(self, "scale_type_combo"):
            selected = self.scale_type_combo.currentData()
            if selected in SCALE_LIBRARY:
                self.state["theoryScale"] = selected
        self.refresh_theory_panel(self.selected_theory_key())
        self.persist_state(silent=True)

    def selected_theory_key(self):
        selected = self.selected_nashville_key()
        if selected:
            return selected
        if self.summary_selected_key:
            return self.summary_selected_key
        if self.summary_best_key:
            return self.summary_best_key
        return "C"

    def build_key_toolkit_lines(self, key_name, scale_key="minor_pentatonic"):
        key_label, degrees = key_row_for_name(key_name)
        scale = SCALE_LIBRARY.get(scale_key, SCALE_LIBRARY["minor_pentatonic"])
        if len(degrees) < 7:
            return [
                f"Key Center: {key_label} major",
                f"Scale: {scale['label']} ({scale['formula']})",
            ]
        one, two, three, four, five, six, seven = degrees
        return [
            f"Key Center: {key_label} major",
            f"Scale: {scale['label']} ({scale['formula']})",
            f"Relative Minor: {six}",
            "Diatonic Triads: " + ", ".join(degrees),
            f"Cadence (I-IV-V): {one} - {four} - {five}",
            f"Cadence (ii-V-I): {two} - {five} - {one}",
            f"Pop Turnaround (vi-IV-I-V): {six} - {four} - {one} - {five}",
            f"Solo Target: use {six} or {key_label} pentatonic color over these chords.",
        ]

    def refresh_theory_panel(self, key_name):
        if not hasattr(self, "pentatonic_neck"):
            return
        active_key = key_name or "C"
        if self.table_row_for_key(active_key) < 0:
            active_key = self.summary_best_key or "C"
        shape_key = "g"
        if hasattr(self, "pentatonic_shape_combo"):
            shape_key = self.pentatonic_shape_combo.currentData() or "g"
        scale_key = "minor_pentatonic"
        if hasattr(self, "scale_type_combo"):
            scale_key = self.scale_type_combo.currentData() or "minor_pentatonic"
        scale = SCALE_LIBRARY.get(scale_key, SCALE_LIBRARY["minor_pentatonic"])
        self.pentatonic_neck.set_selection(active_key, shape_key, scale_key)
        self.pentatonic_hint.setText(
            f"{self.pentatonic_neck.summary_text()}  |  Formula: {scale.get('formula', '')}"
        )

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
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.genre_combo.currentIndexChanged.connect(self.on_controls_changed)
        self.guitar_type_electric.toggled.connect(self.on_controls_changed)
        self.guitar_type_acoustic.toggled.connect(self.on_controls_changed)
        self.profile_electric_2.toggled.connect(self.on_controls_changed)
        self.profile_electric_4.toggled.connect(self.on_controls_changed)
        self.amp_combo.currentIndexChanged.connect(self.on_controls_changed)
        self.font_size_combo.currentIndexChanged.connect(self.on_font_preset_changed)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        self.settings_btn.clicked.connect(self.open_settings_dialog)

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

    def on_tab_changed(self, _index):
        if not hasattr(self, "tabs") or not hasattr(self, "theory_tab"):
            return
        if self.tabs.currentWidget() is self.theory_tab and hasattr(self, "theory_panels"):
            if not getattr(self, "_theory_panels_initialized", False):
                if not self.apply_saved_theory_panel_layout():
                    self.reset_theory_panel_layout()
                self.arrange_minimized_theory_panels()
                self._theory_panels_initialized = True
            else:
                self.arrange_minimized_theory_panels()

    def populate_controls(self):
        self._loading_ui = True

        self.genre_combo.clear()
        for genre_key, preset in GENRE_PRESETS.items():
            self.genre_combo.addItem(preset["label"], genre_key)

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
        self.set_combo_by_data(self.amp_combo, self.state["ampModel"])
        if not self.set_combo_by_data(self.theme_combo, self.state.get("theme", "dark")):
            self.set_combo_by_data(self.theme_combo, "dark")
        if not self.set_combo_by_data(self.font_size_combo, self.state.get("fontPreset", "medium")):
            self.set_combo_by_data(self.font_size_combo, "medium")

        guitar_type = self.state.get("guitarType", "electric")
        if guitar_type == "acoustic":
            self.guitar_type_acoustic.setChecked(True)
        else:
            self.guitar_type_electric.setChecked(True)

        profile_key = self.state.get("guitarProfile", AUTO_GUITAR_PROFILE_BY_TYPE.get(guitar_type, "electric_2_knob_toggle"))
        if guitar_type == "acoustic":
            self.state["guitarProfile"] = "taylor_acoustic"
        elif profile_key == "electric_4_knob_toggle":
            self.profile_electric_4.setChecked(True)
        else:
            self.profile_electric_2.setChecked(True)
        self.update_guitar_controls_mode()

        self._loading_ui = False

    def set_combo_by_data(self, combo, value):
        for idx in range(combo.count()):
            if combo.itemData(idx) == value:
                combo.setCurrentIndex(idx)
                return True
        return False

    def update_guitar_controls_mode(self):
        is_acoustic = self.guitar_type_acoustic.isChecked()
        self.guitar_controls_stack.setCurrentIndex(1 if is_acoustic else 0)
        self.profile_electric_2.setEnabled(not is_acoustic)
        self.profile_electric_4.setEnabled(not is_acoustic)
        self.update_control_box_geometry()

    def update_control_box_geometry(self):
        if not hasattr(self, "guitar_controls_stack"):
            return
        metrics = QtGui.QFontMetrics(self.font())
        acoustic_text_width = metrics.horizontalAdvance("Acoustic (Taylor ES2)") + 28
        electric_text_width = max(
            metrics.horizontalAdvance("2 knob electric"),
            metrics.horizontalAdvance("4 knob electric"),
        ) + 34
        stack_width = clamp(max(acoustic_text_width, electric_text_width, 220), 220, 360)
        self.guitar_controls_stack.setMinimumWidth(stack_width)
        self.guitar_controls_stack.setMaximumWidth(stack_width + 120)
        field_width = clamp(stack_width - 18, 200, 420)
        if hasattr(self, "acoustic_controls_text"):
            self.acoustic_controls_text.setMinimumWidth(field_width)
            self.acoustic_controls_text.setMaximumWidth(16777215)
        h_electric = self.profile_electric_2.sizeHint().height() + self.profile_electric_4.sizeHint().height() + 10
        h_acoustic = self.acoustic_controls_text.sizeHint().height() + 10 if hasattr(self, "acoustic_controls_text") else h_electric
        self.guitar_controls_stack.setMinimumHeight(max(h_electric, h_acoustic, 48))

    def selected_profile_key(self):
        if self.guitar_type_acoustic.isChecked():
            return "taylor_acoustic"
        if self.profile_electric_4.isChecked():
            return "electric_4_knob_toggle"
        return "electric_2_knob_toggle"

    def open_settings_dialog(self):
        if not hasattr(self, "settings_dialog"):
            return
        self.settings_dialog.adjustSize()
        anchor = self.settings_btn.mapToGlobal(QtCore.QPoint(self.settings_btn.width(), self.settings_btn.height()))
        self.settings_dialog.move(anchor.x() - self.settings_dialog.width(), anchor.y() + 4)
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def on_controls_changed(self):
        if self._loading_ui:
            return

        previous_genre = self.state.get("genre", "rock")
        self.state["genre"] = self.genre_combo.currentData()
        self.state["guitarType"] = "acoustic" if self.guitar_type_acoustic.isChecked() else "electric"
        self.state["guitarProfile"] = self.selected_profile_key()
        self.update_guitar_controls_mode()

        self.state["ampModel"] = self.amp_combo.currentData()

        if self.state["genre"] != previous_genre:
            self.clear_style_progression_cache(self.state["genre"])
            self.clear_crazy_payload_cache(self.state["genre"])

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
            if not self.board_canvas.can_place_pedal_at(candidate):
                continue
            candidate_rect = QtCore.QRect(candidate, self.board_canvas.PEDAL_SIZE)
            collision = False
            for used in used_rects:
                if candidate_rect.adjusted(-6, -6, 6, 6).intersects(used):
                    collision = True
                    break
            if not collision:
                return candidate
        return None

    def centered_cleanup_slots(self, count, max_per_row=4):
        if count <= 0:
            return []
        pedal_w = self.board_canvas.PEDAL_SIZE.width()
        pedal_h = self.board_canvas.PEDAL_SIZE.height()
        min_x, max_x, min_y, max_y = self.board_canvas.pedal_position_bounds()
        lane_left, lane_right = self.board_canvas.pedal_lane_bounds()

        area_left = clamp(lane_left + 6, min_x, max_x)
        area_right = clamp(lane_right - pedal_w - 6, area_left, max_x)
        if area_right <= area_left:
            area_left, area_right = min_x, max_x
        available_h = max(1, max_y - min_y + pedal_h)

        def columns_for_width(width_px):
            cols_cap = max(1, min(max_per_row, count))
            gap_x_seed = 22
            return max(1, min(cols_cap, int((width_px + gap_x_seed) // (pedal_w + gap_x_seed))))

        available_w = max(1, area_right - area_left + pedal_w)
        cols = columns_for_width(available_w)
        rows = max(1, math.ceil(count / cols))

        # If the center lane cannot fit all pedals by height, widen to full board.
        if rows * pedal_h > available_h:
            area_left, area_right = min_x, max_x
            available_w = max(1, area_right - area_left + pedal_w)
            cols = columns_for_width(available_w)
            rows = max(1, math.ceil(count / cols))

        if rows > 1:
            gap_y = max(0, min(48, (available_h - rows * pedal_h) // (rows - 1)))
        else:
            gap_y = 0
        total_h = rows * pedal_h + max(0, rows - 1) * gap_y
        start_y = clamp(int(round(((min_y + max_y) / 2.0) - (total_h / 2.0))), min_y, max_y)

        slots = []
        remaining = count
        for row in range(rows):
            row_cols = min(cols, remaining)
            if row_cols <= 1:
                row_gap_x = 0
            else:
                row_gap_x = max(14, (available_w - row_cols * pedal_w) // (row_cols - 1))
            row_w = row_cols * pedal_w + max(0, row_cols - 1) * row_gap_x
            row_start_x = clamp(area_left + max(0, (available_w - row_w) // 2), area_left, area_right)
            y = start_y + row * (pedal_h + gap_y)
            for col in range(row_cols):
                x = row_start_x + (row_cols - 1 - col) * (pedal_w + row_gap_x)
                slots.append(QtCore.QPoint(x, y))
            remaining -= row_cols
        return slots

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
        used_rects = []
        fallback_slots = self.collect_layout_slots(max(len(chain) * 6, 32), right_to_left=True)
        for pedal_id in chain:
            if pedal_id == focus_pedal and focus_pos is not None:
                clamped = self.board_canvas.clamp_pedal_position(focus_pos)
                point = QtCore.QPoint(clamped.x(), clamped.y())
            elif pedal_id not in positions:
                default_pos = self.default_canvas_position_for(pedal_id)
                point = QtCore.QPoint(default_pos.x(), default_pos.y())
            else:
                raw = positions[pedal_id]
                if not isinstance(raw, (list, tuple)) or len(raw) != 2:
                    default_pos = self.default_canvas_position_for(pedal_id)
                    point = QtCore.QPoint(default_pos.x(), default_pos.y())
                else:
                    clamped = self.board_canvas.clamp_pedal_position(QtCore.QPoint(int(raw[0]), int(raw[1])))
                    point = QtCore.QPoint(clamped.x(), clamped.y())

            slot = self.choose_slot([point] + fallback_slots, used_rects)
            if slot is None:
                slot = self.board_canvas.find_nearest_open_pedal_position(point)
            positions[pedal_id] = [slot.x(), slot.y()]
            used_rects.append(QtCore.QRect(slot, self.board_canvas.PEDAL_SIZE))
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
        centered_slots = self.centered_cleanup_slots(len(chain), max_per_row=4)
        fallback_slots = self.collect_layout_slots(max(len(chain) * 6, 32), right_to_left=True)
        ordered_candidates = []
        seen = set()

        def append_slots(slots):
            for slot in slots:
                if not self.board_canvas.can_place_pedal_at(slot):
                    continue
                key = (slot.x(), slot.y())
                if key in seen:
                    continue
                seen.add(key)
                ordered_candidates.append(slot)

        append_slots(centered_slots)
        if ordered_candidates:
            last_y = ordered_candidates[-1].y()
            append_slots([slot for slot in fallback_slots if slot.y() >= last_y])
            append_slots([slot for slot in fallback_slots if slot.y() < last_y])
        else:
            append_slots(fallback_slots)

        positions = self.state.setdefault("canvasPositions", {})
        used_rects = []

        min_x, _max_x, min_y, _max_y = self.board_canvas.pedal_position_bounds()
        for pedal_id in chain:
            slot = self.choose_slot(ordered_candidates, used_rects)
            if slot is None:
                slot = self.board_canvas.find_nearest_open_pedal_position(QtCore.QPoint(min_x, min_y))
            else:
                ordered_candidates = [item for item in ordered_candidates if item.x() != slot.x() or item.y() != slot.y()]
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
        message = f"{preset['label']} optimized ({analysis['permutations_checked']:,} layouts checked)."
        outside_builder = hasattr(self, "tabs") and self.tabs.currentWidget() is not self.builder_tab
        if outside_builder:
            dialog = QtWidgets.QMessageBox(self)
            dialog.setWindowTitle("Optimize")
            dialog.setText(message)
            dialog.setInformativeText("Build order preview shown for the optimized chain.")
            dialog.setIconPixmap(self.build_chain_preview_pixmap(self.state["chain"]))
            dialog.exec_()
        else:
            QtWidgets.QMessageBox.information(self, "Optimize", message)

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
        self.last_recommendation = recommendation

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
        self.render_pedals_tab(recommendation)
        self.render_rig_setup_tab(recommendation)
        self.render_summary_tab(recommendation)
        self.render_feedback_tab()

    def build_chain_preview_pixmap(self, chain):
        safe_chain = [pid for pid in chain if pid in PEDAL_LIBRARY]
        nodes = [("GTR", "#d2d6dc", "#1a1f28")]
        for pedal_id in safe_chain:
            color = PEDAL_COLORS.get(pedal_id, "#b0b7c5")
            text_color = PEDAL_TEXT_COLORS.get(pedal_id, "#121720")
            nodes.append((PEDAL_LIBRARY[pedal_id].replace("BOSS ", ""), color, text_color))
        amp_color = AMP_BRAND_COLORS.get(self.last_recommendation.get("amp_model_key", ""), {"bg": "#323a45", "fg": "#f2f4f7"}) if self.last_recommendation else {"bg": "#323a45", "fg": "#f2f4f7"}
        nodes.append(("AMP", amp_color["bg"], amp_color["fg"]))

        cell_w = 78
        cell_h = 38
        gap = 20
        width = max(180, 18 + len(nodes) * cell_w + max(0, len(nodes) - 1) * gap + 12)
        height = 72
        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(QtGui.QColor(0, 0, 0, 0))
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        x = 12
        y = 17
        for idx, (label, bg, fg) in enumerate(nodes):
            rect = QtCore.QRect(x, y, cell_w, cell_h)
            painter.setPen(QtGui.QPen(QtGui.QColor("#1a1f28"), 1))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(bg)))
            painter.drawRoundedRect(rect, 7, 7)
            painter.setPen(QtGui.QColor(fg))
            font = painter.font()
            font.setBold(True)
            font.setPointSize(max(7, font.pointSize() - 1))
            painter.setFont(font)
            painter.drawText(rect.adjusted(4, 2, -4, -2), QtCore.Qt.AlignCenter, label)
            if idx < len(nodes) - 1:
                x1 = rect.right() + 2
                x2 = x1 + gap - 6
                mid_y = rect.center().y()
                painter.setPen(QtGui.QPen(QtGui.QColor("#6fa9ff"), 2))
                painter.drawLine(x1, mid_y, x2, mid_y)
                arrow = QtGui.QPolygon(
                    [
                        QtCore.QPoint(x2, mid_y),
                        QtCore.QPoint(x2 - 5, mid_y - 4),
                        QtCore.QPoint(x2 - 5, mid_y + 4),
                    ]
                )
                painter.setBrush(QtGui.QBrush(QtGui.QColor("#6fa9ff")))
                painter.drawPolygon(arrow)
            x += cell_w + gap
        painter.end()
        return pixmap

    def render_builder_preview(self, recommendation):
        guitar = recommendation.get("guitar")
        if guitar and hasattr(self, "guitar_preview"):
            rows = [f"{guitar['label']}"]
            for key, value in guitar["settings"].items():
                if key == "note":
                    continue
                rows.append(f"- {key}: {value}")
            if guitar.get("volumeAdvice"):
                rows.append(f"- Volume: {guitar['volumeAdvice']}")
            self.guitar_preview.setPlainText("\n".join(rows))
        elif hasattr(self, "guitar_preview"):
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
        if hasattr(self, "amp_preview"):
            self.amp_preview.setPlainText("\n".join(amp_lines))

        self.render_theory_playbook()

    def clear_style_progression_cache(self, genre_key=None):
        if genre_key:
            self.style_progression_cache.pop(genre_key, None)
            return
        self.style_progression_cache.clear()

    def current_style_progressions(self, genre_key):
        if genre_key in self.style_progression_cache:
            return self.style_progression_cache[genre_key]
        random_set = sample_style_progressions(genre_key, count=2)
        popular_pick = sample_popular_progression(genre_key)
        payload = {
            "random_set": random_set,
            "popular_pick": popular_pick,
        }
        self.style_progression_cache[genre_key] = payload
        return payload

    def render_theory_playbook(self):
        if not hasattr(self, "playbook_preview"):
            return
        genre_key = self.state.get("genre", "rock")
        playbook = STYLE_PLAYBOOK.get(genre_key, STYLE_PLAYBOOK["rock"])
        picks = self.current_style_progressions(genre_key)
        random_set = picks.get("random_set", [])
        popular_pick = picks.get("popular_pick", "")
        if len(random_set) < 2:
            fallback = sample_style_progressions(genre_key, count=2)
            for item in fallback:
                if item not in random_set:
                    random_set.append(item)
                if len(random_set) >= 2:
                    break
        lines = [
            "Random Progressions (refreshes when style changes):",
        ]
        if random_set:
            lines.extend([f"- {idx}. {prog}" for idx, prog in enumerate(random_set[:2], start=1)])
        else:
            lines.append("- (no progression data)")
        lines.extend(
            [
                "",
                "Popular Progression (top-3 list):",
                f"- {popular_pick or '(no popular progression configured)'}",
                "",
                "Capo 5 Shapes:",
            ]
        )
        lines.extend(f"- {line}" for line in playbook.get("capo5Shapes", []))
        lines.extend(
            [
                "",
                f"Open Shapes: {', '.join(playbook.get('openShapes', []))}",
                f"Capo Mapping: {playbook.get('capoGuide', '')}",
                f"G-Shape Pentatonic Fret: {playbook.get('pentatonicFret', '')}",
                f"Solo Guide: {playbook.get('soloGuide', '')}",
            ]
        )
        self.playbook_preview.setPlainText("\n".join(lines))
        self.render_crazy_payload()

    def clear_crazy_payload_cache(self, genre_key=None):
        if genre_key:
            self.crazy_payload_cache.pop(genre_key, None)
            return
        self.crazy_payload_cache.clear()

    def progression_key_center(self, progression):
        tokens = split_progression_tokens(progression)
        if not tokens:
            return "C"
        first = parse_chord_token(tokens[0])
        if first and first.get("root") in NOTE_TO_PITCH_CLASS:
            return first["root"]
        return determine_best_nashville_key(tokens)

    def progression_capo_shapes(self, progression, capo_fret=5):
        shapes = [transpose_chord_root_for_capo(token, capo_fret) for token in split_progression_tokens(progression)]
        return " - ".join([token for token in shapes if token])

    def make_crazy_payload(self, genre_key):
        playbook = STYLE_PLAYBOOK.get(genre_key, STYLE_PLAYBOOK["rock"])
        pool = [item for item in playbook.get("progressionPool", []) if isinstance(item, str) and item.strip()]
        popular = [item for item in playbook.get("popularTop3", []) if isinstance(item, str) and item.strip()]
        under_used = [item for item in pool if item not in popular]
        candidates = under_used if under_used else (pool if pool else [sample_popular_progression(genre_key)])
        progression = random.choice([item for item in candidates if item] or ["C - Am - F - G"])
        capo_shapes = self.progression_capo_shapes(progression, 5)
        key_center = self.progression_key_center(progression)
        scale_keys = CRAZY_SCALE_BY_GENRE.get(genre_key, list(CRAZY_SCALE_LIBRARY.keys()))
        scale_key = random.choice(scale_keys if scale_keys else list(CRAZY_SCALE_LIBRARY.keys()))
        scale = CRAZY_SCALE_LIBRARY.get(scale_key, CRAZY_SCALE_LIBRARY["harmonic_minor"])
        root_pc = NOTE_TO_PITCH_CLASS.get(key_center, NOTE_TO_PITCH_CLASS["C"])
        notes = [display_note_for_pitch_class((root_pc + interval) % 12, key_center) for interval in scale["intervals"]]
        return {
            "progression": progression,
            "capo_shapes": capo_shapes,
            "key_center": key_center,
            "scale_name": scale["name"],
            "scale_formula": scale["formula"],
            "scale_notes": notes,
            "scale_why": scale["why"],
        }

    def current_crazy_payload(self, genre_key):
        if genre_key in self.crazy_payload_cache:
            return self.crazy_payload_cache[genre_key]
        payload = self.make_crazy_payload(genre_key)
        self.crazy_payload_cache[genre_key] = payload
        return payload

    def render_crazy_payload(self):
        if not hasattr(self, "crazy_progression_text") or not hasattr(self, "crazy_scale_text"):
            return
        genre_key = self.state.get("genre", "rock")
        payload = self.current_crazy_payload(genre_key)
        left_lines = [
            "Under-utilized Progression:",
            f"- {payload.get('progression', '')}",
            "",
            "Capo 5 Shape Mapping:",
            f"- {payload.get('capo_shapes', '')}",
            "",
            f"Key Center Guess: {payload.get('key_center', 'C')}",
        ]
        right_lines = [
            "Unusual But Correct Scale:",
            f"- {payload.get('scale_name', '')}",
            f"- Formula: {payload.get('scale_formula', '')}",
            f"- Notes: {', '.join(payload.get('scale_notes', []))}",
            "",
            payload.get("scale_why", ""),
        ]
        self.crazy_progression_text.setPlainText("\n".join(left_lines))
        self.crazy_scale_text.setPlainText("\n".join(right_lines))

    def on_lets_get_crazy(self):
        genre_key = self.state.get("genre", "rock")
        self.crazy_payload_cache[genre_key] = self.make_crazy_payload(genre_key)
        self.render_crazy_payload()

    def current_pedal_reference_id(self):
        if not hasattr(self, "pedal_selector_list"):
            return BANK_ORDER[0]
        item = self.pedal_selector_list.currentItem()
        if not item:
            fallback = self.state.get("pedalReference", BANK_ORDER[0])
            return fallback if fallback in PEDAL_LIBRARY else BANK_ORDER[0]
        pedal_id = item.data(QtCore.Qt.UserRole)
        return pedal_id if pedal_id in PEDAL_LIBRARY else BANK_ORDER[0]

    def build_pedal_reference_text(self, pedal_id, recommendation):
        info = PEDAL_REFERENCE.get(pedal_id, {})
        settings = recommendation["pedals"].get(pedal_id, {})
        lines = [info.get("name", PEDAL_LIBRARY.get(pedal_id, pedal_id))]

        summary = info.get("summary", "")
        if summary:
            lines.extend(["", "What It Does", f"- {summary}"])

        controls = list(info.get("controls", []))
        if controls:
            lines.append("")
            lines.append("Controls")
            for entry in controls:
                lines.append(f"- {entry}")

        configure = list(info.get("configure", []))
        if configure:
            lines.append("")
            lines.append("How To Configure")
            for entry in configure:
                lines.append(f"- {entry}")

        possibilities = list(info.get("possibilities", []))
        if possibilities:
            lines.append("")
            lines.append("Possibilities")
            for entry in possibilities:
                lines.append(f"- {entry}")

        placement = list(info.get("placement", []))
        if placement:
            lines.append("")
            lines.append("Placement Options")
            for entry in placement:
                lines.append(f"- {entry}")

        advanced = list(info.get("advanced", []))
        if advanced:
            lines.append("")
            lines.append("Advanced Workflow")
            for entry in advanced:
                lines.append(f"- {entry}")

        lines.append("")
        lines.append("Current Suggested Settings (from active style + chain)")
        block = self.format_pedal_block(pedal_id, settings).splitlines()
        for row in block[1:] if len(block) > 1 else []:
            lines.append(row)
        if len(block) <= 1:
            lines.append("- Add this pedal to your connected chain to get active values.")

        if pedal_id in self.connected_chain:
            idx = self.connected_chain.index(pedal_id) + 1
            lines.append("")
            lines.append(f"Connected Position: {idx} / {len(self.connected_chain)} in active signal path.")
        else:
            lines.append("")
            lines.append("Connected Position: Not currently in the active guitar-to-amp path.")

        return "\n".join(lines)

    def render_pedals_tab(self, recommendation):
        if not hasattr(self, "pedal_selector_list"):
            return
        pedal_id = self.current_pedal_reference_id()
        self.state["pedalReference"] = pedal_id
        settings = recommendation["pedals"].get(pedal_id, {})
        face_values = pedal_knob_values(pedal_id, settings)
        if hasattr(self, "pedal_showcase"):
            self.pedal_showcase.set_pedal(pedal_id, face_values)
        if hasattr(self, "pedal_details_text"):
            self.pedal_details_text.setPlainText(self.build_pedal_reference_text(pedal_id, recommendation))

    def on_pedal_reference_changed(self, _current, _previous):
        pedal_id = self.current_pedal_reference_id()
        self.state["pedalReference"] = pedal_id
        recommendation = self.last_recommendation
        if recommendation is None:
            recommendation = build_recommendation(
                self.state["genre"],
                self.connected_chain,
                self.state["guitarType"],
                self.state["ampModel"],
                self.state["guitarProfile"],
            )
            self.last_recommendation = recommendation
        self.render_pedals_tab(recommendation)
        self.persist_state(silent=True)

    def render_rig_setup_tab(self, recommendation):
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
        usual_keys = usual_keys_for_genre(self.state["genre"])
        usual_major_keys = major_usual_keys_for_genre(self.state["genre"])
        self.summary_style_chords = style_chords
        self.summary_best_key = best_key
        self.summary_usual_keys = usual_keys
        self.summary_usual_major_keys = usual_major_keys

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
        if usual_keys:
            self.usual_keys_label.setText("Usual Keys: " + "  •  ".join(usual_keys))
        else:
            self.usual_keys_label.setText("Usual Keys: (none)")

        active_key = self.summary_selected_key if self.table_row_for_key(self.summary_selected_key) >= 0 else best_key
        if not active_key:
            active_key = best_key
        self.set_nashville_selected_key(active_key)
        self.update_summary_key_visuals(active_key)

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

    def load_app_config(self):
        config = copy.deepcopy(DEFAULT_APP_CONFIG)
        for path in config_path_candidates():
            if not path.exists():
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(payload, dict):
                deep_merge_dict(config, payload)
                break
        return config

    def feedback_user_hash(self):
        raw = f"{socket.gethostname()}|{uuid.getnode():012x}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def load_feedback_limiter_state(self):
        fallback = {"total": 0, "daily": {}, "users": {}}
        if not FEEDBACK_LIMITER_FILE.exists():
            return fallback
        try:
            payload = json.loads(FEEDBACK_LIMITER_FILE.read_text(encoding="utf-8"))
        except Exception:
            return fallback
        if not isinstance(payload, dict):
            return fallback
        total = payload.get("total", 0)
        daily = payload.get("daily", {})
        users = payload.get("users", {})
        return {
            "total": int(total) if isinstance(total, (int, float)) else 0,
            "daily": daily if isinstance(daily, dict) else {},
            "users": users if isinstance(users, dict) else {},
        }

    def persist_feedback_limiter_state(self):
        FEEDBACK_LIMITER_FILE.write_text(json.dumps(self.feedback_limits_state, indent=2), encoding="utf-8")

    def feedback_limits(self):
        feedback_cfg = self.app_config.get("feedback", {})
        limiter = feedback_cfg.get("limiter", {})
        return {
            "max_per_day": max(0, int(limiter.get("max_per_day", 0) or 0)),
            "max_per_user_per_day": max(0, int(limiter.get("max_per_user_per_day", 0) or 0)),
            "max_per_user_total": max(0, int(limiter.get("max_per_user_total", 0) or 0)),
            "hard_limit_total": max(0, int(limiter.get("hard_limit_total", 0) or 0)),
        }

    def feedback_day_key(self):
        return datetime.now().strftime("%Y-%m-%d")

    def user_feedback_counters(self, user_id):
        users = self.feedback_limits_state.setdefault("users", {})
        user_state = users.setdefault(user_id, {"total": 0, "daily": {}})
        if not isinstance(user_state.get("daily"), dict):
            user_state["daily"] = {}
        if not isinstance(user_state.get("total"), (int, float)):
            user_state["total"] = 0
        return user_state

    def check_feedback_limit(self, user_id):
        limits = self.feedback_limits()
        day = self.feedback_day_key()
        total = int(self.feedback_limits_state.get("total", 0))
        daily_total = int(self.feedback_limits_state.setdefault("daily", {}).get(day, 0))
        user_state = self.user_feedback_counters(user_id)
        user_total = int(user_state.get("total", 0))
        user_daily = int(user_state.setdefault("daily", {}).get(day, 0))

        if limits["hard_limit_total"] and total >= limits["hard_limit_total"]:
            return False, "Global feedback cap reached."
        if limits["max_per_day"] and daily_total >= limits["max_per_day"]:
            return False, "Daily feedback limit reached."
        if limits["max_per_user_per_day"] and user_daily >= limits["max_per_user_per_day"]:
            return False, "You reached your daily submission limit."
        if limits["max_per_user_total"] and user_total >= limits["max_per_user_total"]:
            return False, "You reached your account submission limit."
        return True, ""

    def increment_feedback_limit(self, user_id):
        day = self.feedback_day_key()
        self.feedback_limits_state["total"] = int(self.feedback_limits_state.get("total", 0)) + 1
        daily = self.feedback_limits_state.setdefault("daily", {})
        daily[day] = int(daily.get(day, 0)) + 1
        user_state = self.user_feedback_counters(user_id)
        user_state["total"] = int(user_state.get("total", 0)) + 1
        user_daily = user_state.setdefault("daily", {})
        user_daily[day] = int(user_daily.get(day, 0)) + 1
        self.persist_feedback_limiter_state()

    def set_feedback_status(self, text, success=False):
        if not hasattr(self, "feedback_status_label"):
            return
        self.feedback_status_label.setText(text)
        theme = theme_for_key(self.state.get("theme", "dark"))
        color = theme.get("positive", "#66d17a") if success else "#f19090"
        self.feedback_status_label.setStyleSheet(f"color: {color}; font-weight: 700;")

    def update_feedback_limit_label(self):
        if not hasattr(self, "feedback_limit_label"):
            return
        feedback_cfg = self.app_config.get("feedback", {})
        limits = self.feedback_limits()
        webhook = str(feedback_cfg.get("webhook_url", "") or "").strip()
        enabled = bool(feedback_cfg.get("enabled", True)) and bool(webhook)
        day = self.feedback_day_key()
        user_state = self.user_feedback_counters(self.feedback_user_id)
        day_total = int(self.feedback_limits_state.setdefault("daily", {}).get(day, 0))
        user_day_total = int(user_state.setdefault("daily", {}).get(day, 0))
        user_total = int(user_state.get("total", 0))

        def remaining(limit, used):
            if not limit:
                return "∞"
            return str(max(0, limit - used))

        lines = [
            f"Webhook: {'Configured' if webhook else 'Not configured'}",
            f"Feedback Enabled: {'Yes' if enabled else 'No'}",
            "Limits - "
            f"Day Remaining: {remaining(limits['max_per_day'], day_total)} | "
            f"Your Day Remaining: {remaining(limits['max_per_user_per_day'], user_day_total)} | "
            f"Your Total Remaining: {remaining(limits['max_per_user_total'], user_total)}",
        ]
        self.feedback_limit_label.setText("\n".join(lines))

    def render_feedback_tab(self):
        if not hasattr(self, "donate_details_label"):
            return
        donate_cfg = self.app_config.get("donate", {})
        paypal = str(donate_cfg.get("paypal_url", "") or "").strip()
        venmo = str(donate_cfg.get("venmo_url", "") or "").strip()
        zelle = str(donate_cfg.get("zelle_handle", "") or "").strip()
        lines = [
            f"PayPal: {'Configured' if paypal else 'Not configured'}",
            f"Venmo: {'Configured' if venmo else 'Not configured'}",
            f"Zelle: {'Configured' if zelle else 'Not configured'}",
        ]
        self.donate_details_label.setText("\n".join(lines))
        self.update_feedback_limit_label()

    def handle_donate(self):
        method = self.donate_method_combo.currentData() if hasattr(self, "donate_method_combo") else "paypal"
        donate_cfg = self.app_config.get("donate", {})
        target_map = {
            "paypal": str(donate_cfg.get("paypal_url", "") or "").strip(),
            "venmo": str(donate_cfg.get("venmo_url", "") or "").strip(),
            "zelle": str(donate_cfg.get("zelle_handle", "") or "").strip(),
        }
        target = target_map.get(method, "")
        if not target:
            self.set_feedback_status(f"{method.title()} is not configured yet.", success=False)
            return
        if method in {"paypal", "venmo"}:
            if not QtGui.QDesktopServices.openUrl(QtCore.QUrl(target)):
                self.set_feedback_status(f"Could not open {method.title()} link.", success=False)
                return
            self.set_feedback_status(f"Opened {method.title()}.", success=True)
            return
        QtWidgets.QApplication.clipboard().setText(target)
        self.set_feedback_status("Zelle destination copied to clipboard.", success=True)

    def submit_feedback(self):
        message = self.feedback_message_input.toPlainText().strip() if hasattr(self, "feedback_message_input") else ""
        if len(message) < 8:
            self.set_feedback_status("Please enter at least a short message before submitting.", success=False)
            return

        feedback_cfg = self.app_config.get("feedback", {})
        webhook = str(feedback_cfg.get("webhook_url", "") or "").strip()
        if not feedback_cfg.get("enabled", True) or not webhook:
            self.set_feedback_status("Feedback webhook is not configured for this build.", success=False)
            return

        allowed, reason = self.check_feedback_limit(self.feedback_user_id)
        if not allowed:
            self.set_feedback_status(reason, success=False)
            return

        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user": self.feedback_user_id,
            "rating": int(self.feedback_rating_combo.currentData() or 0),
            "type": str(self.feedback_type_combo.currentData() or "general"),
            "name": self.feedback_name_input.text().strip(),
            "email": self.feedback_email_input.text().strip(),
            "message": message,
            "context": {
                "genre": self.state.get("genre"),
                "guitarType": self.state.get("guitarType"),
                "guitarProfile": self.state.get("guitarProfile"),
                "ampModel": self.state.get("ampModel"),
                "theme": self.state.get("theme"),
                "connectedChain": list(self.connected_chain),
            },
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            webhook,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        timeout_sec = max(2, int(feedback_cfg.get("timeout_sec", 8) or 8))
        try:
            with urllib.request.urlopen(request, timeout=timeout_sec) as response:
                status = int(response.getcode() or 200)
        except urllib.error.URLError as exc:
            self.set_feedback_status(f"Submit failed: {exc}", success=False)
            return
        except Exception as exc:
            self.set_feedback_status(f"Submit failed: {exc}", success=False)
            return

        if status < 200 or status >= 300:
            self.set_feedback_status(f"Submit failed: HTTP {status}", success=False)
            return

        self.increment_feedback_limit(self.feedback_user_id)
        self.feedback_message_input.clear()
        self.set_feedback_status("Feedback sent. Thank you.", success=True)
        self.update_feedback_limit_label()

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

        theory_scale = payload.get("theoryScale")
        if theory_scale in SCALE_LIBRARY:
            self.state["theoryScale"] = theory_scale

        theory_shape = payload.get("theoryShape")
        if theory_shape in CAGED_SHAPES:
            self.state["theoryShape"] = theory_shape

        pedal_reference = payload.get("pedalReference")
        if pedal_reference in PEDAL_LIBRARY:
            self.state["pedalReference"] = pedal_reference

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

        theory_panel_layout = payload.get("theoryPanelLayout")
        if isinstance(theory_panel_layout, dict):
            clean_layout = {}
            for key in ["nashville", "circle", "playbook", "crazy"]:
                entry = theory_panel_layout.get(key)
                if not isinstance(entry, dict):
                    continue
                try:
                    cleaned_entry = {
                        "x": int(entry.get("x", 0)),
                        "y": int(entry.get("y", 0)),
                        "w": int(entry.get("w", 300)),
                        "h": int(entry.get("h", 220)),
                        "minimized": bool(entry.get("minimized", False)),
                    }
                    slot = entry.get("slot")
                    if isinstance(slot, dict) and slot.get("mode") in {"quarter", "half"}:
                        parsed_slot = {"mode": slot.get("mode", "quarter"), "row": int(slot.get("row", 0))}
                        if parsed_slot["mode"] == "quarter":
                            parsed_slot["col"] = 0 if int(slot.get("col", 0)) <= 0 else 1
                        cleaned_entry["slot"] = parsed_slot
                    clean_layout[key] = cleaned_entry
                except Exception:
                    continue
            self.state["theoryPanelLayout"] = clean_layout

        theory_panel_rows = payload.get("theoryPanelRows")
        if isinstance(theory_panel_rows, (int, float)):
            self.state["theoryPanelRows"] = max(2, int(theory_panel_rows))

    def persist_state(self, silent=False):
        if hasattr(self, "theory_panels"):
            self.state["theoryPanelRows"] = int(max(2, getattr(self, "theory_grid_rows", self.state.get("theoryPanelRows", 2))))
            self.state["theoryPanelLayout"] = self.capture_theory_panel_layout()
        payload = {
            "genre": self.state["genre"],
            "guitarType": self.state["guitarType"],
            "guitarProfile": self.state["guitarProfile"],
            "ampModel": self.state["ampModel"],
            "theme": self.state["theme"],
            "theoryScale": self.state.get("theoryScale", "minor_pentatonic"),
            "theoryShape": self.state.get("theoryShape", "g"),
            "pedalReference": self.state.get("pedalReference", BANK_ORDER[0]),
            "fontPreset": self.state["fontPreset"],
            "fontSize": font_pixels_for_preset(self.state["fontPreset"]),
            "chain": self.state["chain"],
            "canvasPositions": self.state.get("canvasPositions", {}),
            "canvasConnections": self.state.get("canvasConnections", []),
            "theoryPanelLayout": self.state.get("theoryPanelLayout", {}),
            "theoryPanelRows": int(max(2, self.state.get("theoryPanelRows", 2))),
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
            QComboBox, QListWidget, QTextEdit, QPushButton, QToolButton, QLineEdit, QTableWidget {{ background: {theme["panel"]}; border: 1px solid {theme["frame"]}; border-radius: 6px; padding: 5px; }}
            QFrame#pedalSettingsCard {{ background: {theme["panel"]}; border: 1px solid {theme["frame"]}; border-radius: 8px; }}
            QLabel#pedalCardTitle {{ font-weight: 700; color: {theme["group_title"]}; }}
            QLabel#usualKeysLabel {{ color: {theme.get("positive", "#66d17a")}; font-weight: 700; }}
            QPushButton:hover {{ border: 1px solid {theme["tab_selected_bg"]}; }}
            QLabel {{ color: {theme["text"]}; }}
            """
        )
        if hasattr(self, "board_canvas"):
            self.board_canvas.set_theme(theme)
        if hasattr(self, "circle_of_fifths"):
            self.circle_of_fifths.set_theme(theme)
        if hasattr(self, "pentatonic_neck"):
            self.pentatonic_neck.set_theme(theme)
        if hasattr(self, "pedal_showcase"):
            self.pedal_showcase.set_theme(theme)
        if hasattr(self, "nashville_table"):
            active_key = self.summary_selected_key or self.summary_best_key
            if not active_key:
                active_key = determine_best_nashville_key(extract_concert_chords_for_genre(self.state.get("genre", "rock")))
            usual_major = self.summary_usual_major_keys or major_usual_keys_for_genre(self.state.get("genre", "rock"))
            self.highlight_nashville_key(active_key, usual_major)
        if hasattr(self, "feedback_limit_label"):
            self.update_feedback_limit_label()
        self.update_control_box_geometry()


def main():
    app = QtWidgets.QApplication([])
    window = PedalArchitectWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
