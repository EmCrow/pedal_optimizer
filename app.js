if (!window.APP_DATA) {
  throw new Error("APP_DATA missing. Make sure data/config.js loads before app.js");
}

const {
  PEDAL_LIBRARY,
  BANK_ORDER,
  EQ10_BANDS,
  GE7_BANDS,
  GENRE_PRESETS,
  DEFAULT_CHAIN,
  STORAGE_KEY,
  AMP_MODELS,
  ORDER_RULES,
  AUTO_AMP_BY_GENRE,
  GUITAR_PROFILES,
  AUTO_GUITAR_PROFILE_BY_TYPE,
  STYLE_PLAYBOOK,
} = window.APP_DATA;

const GUITAR_NODE_ID = "__guitar__";
const AMP_NODE_ID = "__amp__";
const FEEDBACK_LIMITER_KEY = "pedal_architect_feedback_limits_v1";

const FONT_PRESET_SPECS = [
  ["small", "Small", 12],
  ["medium", "Medium", 14],
  ["large", "Large", 16],
  ["xl", "XL", 19],
];

const THEME_PRESET_SPECS = [
  ["dark", "Dark"],
  ["light", "Light"],
  ["sunset", "Sunset"],
  ["ocean", "Ocean"],
  ["prism", "Prism (Floyd)"],
  ["brown_sound", "Brown Sound (VH)"],
  ["paisley", "Paisley Prairie"],
  ["monokai_npp", "Notepad++ Monokai"],
  ["obsidian_npp", "Notepad++ Obsidian"],
  ["twilight_npp", "Notepad++ Twilight"],
  ["deep_black_npp", "Notepad++ Deep Black"],
  ["zenburn_npp", "Notepad++ Zenburn"],
];

const THEMES = {
  dark: {
    bg: "#11161a",
    text: "#e9efe4",
    frame: "#3a464e",
    panel: "#161f25",
    tab: "#1d252b",
    tabSelectedBg: "#d6fd73",
    tabSelectedFg: "#1a230f",
    groupTitle: "#d6e2cb",
    canvasBg: "#0f1418",
    canvasGrid: "#202b33",
    canvasEdge: "#86c7ff",
    canvasPreview: "#86c7ff",
    ampBg: "#232f38",
    ampFg: "#f3f8f0",
    positive: "#66d17a",
    rootNote: "#ff5c63",
    scaleNote: "#66d17a",
  },
  light: {
    bg: "#f5f6f8",
    text: "#21252b",
    frame: "#c0c7d1",
    panel: "#ffffff",
    tab: "#e7ebf0",
    tabSelectedBg: "#2f6feb",
    tabSelectedFg: "#ffffff",
    groupTitle: "#253347",
    canvasBg: "#edf1f6",
    canvasGrid: "#d0d8e4",
    canvasEdge: "#1f6feb",
    canvasPreview: "#1f6feb",
    ampBg: "#d7e1ec",
    ampFg: "#1f2f42",
    positive: "#1f8a3d",
    rootNote: "#d61f35",
    scaleNote: "#1f8a3d",
  },
  sunset: {
    bg: "#2a1d22",
    text: "#f7e8da",
    frame: "#7f4a53",
    panel: "#3a262d",
    tab: "#4a3038",
    tabSelectedBg: "#ffb347",
    tabSelectedFg: "#3a2523",
    groupTitle: "#ffcf97",
    canvasBg: "#2e1d24",
    canvasGrid: "#5d3943",
    canvasEdge: "#ffd166",
    canvasPreview: "#ffd166",
    ampBg: "#5a3031",
    ampFg: "#ffe9c4",
    positive: "#9ce26a",
    rootNote: "#ff5c66",
    scaleNote: "#9ce26a",
  },
  ocean: {
    bg: "#0f2430",
    text: "#def1f6",
    frame: "#2f6172",
    panel: "#123544",
    tab: "#164454",
    tabSelectedBg: "#2ad4c5",
    tabSelectedFg: "#0f2831",
    groupTitle: "#a5e8df",
    canvasBg: "#0d2a36",
    canvasGrid: "#235062",
    canvasEdge: "#6ee7ff",
    canvasPreview: "#6ee7ff",
    ampBg: "#1c4a5a",
    ampFg: "#ddfbff",
    positive: "#58d39e",
    rootNote: "#ff6a73",
    scaleNote: "#58d39e",
  },
  prism: {
    bg: "#11101b",
    text: "#f5f4ff",
    frame: "#544f73",
    panel: "#1a1830",
    tab: "#242147",
    tabSelectedBg: "#74efff",
    tabSelectedFg: "#111327",
    groupTitle: "#f6d7ff",
    canvasBg: "#120f22",
    canvasGrid: "#2f2a56",
    canvasEdge: "#ffd268",
    canvasPreview: "#ffd268",
    ampBg: "#2d2541",
    ampFg: "#fff3de",
    positive: "#8cffaa",
    rootNote: "#ff7f4f",
    scaleNote: "#8cffaa",
  },
  brown_sound: {
    bg: "#1a1110",
    text: "#ffe7d2",
    frame: "#6f3f37",
    panel: "#291716",
    tab: "#3a1e1b",
    tabSelectedBg: "#e03e31",
    tabSelectedFg: "#fff6ec",
    groupTitle: "#ffb184",
    canvasBg: "#1f1211",
    canvasGrid: "#4a2a26",
    canvasEdge: "#ff8a3b",
    canvasPreview: "#ff8a3b",
    ampBg: "#41231e",
    ampFg: "#ffe9d1",
    positive: "#ffd166",
    rootNote: "#ff5148",
    scaleNote: "#ffd166",
  },
  paisley: {
    bg: "#f4efe3",
    text: "#243033",
    frame: "#9fb4a9",
    panel: "#fffdf7",
    tab: "#e3efe8",
    tabSelectedBg: "#3e8f68",
    tabSelectedFg: "#effff4",
    groupTitle: "#3f5d55",
    canvasBg: "#ecf4ef",
    canvasGrid: "#c5dbd1",
    canvasEdge: "#2f6a90",
    canvasPreview: "#2f6a90",
    ampBg: "#d4e6dc",
    ampFg: "#1f3f37",
    positive: "#2c9d68",
    rootNote: "#d63d5a",
    scaleNote: "#2c9d68",
  },
  monokai_npp: {
    bg: "#272822",
    text: "#f8f8f2",
    frame: "#555747",
    panel: "#2e2f28",
    tab: "#35362f",
    tabSelectedBg: "#a6e22e",
    tabSelectedFg: "#1f2513",
    groupTitle: "#f0ffb8",
    canvasBg: "#23241f",
    canvasGrid: "#3a3c33",
    canvasEdge: "#66d9ef",
    canvasPreview: "#66d9ef",
    ampBg: "#3a3c33",
    ampFg: "#f8f8f2",
    positive: "#66d9ef",
    rootNote: "#fd5e7f",
    scaleNote: "#66d9ef",
  },
  obsidian_npp: {
    bg: "#293134",
    text: "#e0e2e4",
    frame: "#465056",
    panel: "#313b3f",
    tab: "#364146",
    tabSelectedBg: "#ffd479",
    tabSelectedFg: "#2a2f31",
    groupTitle: "#f6e3bd",
    canvasBg: "#242c2f",
    canvasGrid: "#3a454a",
    canvasEdge: "#8ec5ff",
    canvasPreview: "#8ec5ff",
    ampBg: "#3a454a",
    ampFg: "#f2f5f7",
    positive: "#7bc79e",
    rootNote: "#ff6c6c",
    scaleNote: "#7bc79e",
  },
  twilight_npp: {
    bg: "#141414",
    text: "#f7f7f7",
    frame: "#545454",
    panel: "#1f1f1f",
    tab: "#2a2a2a",
    tabSelectedBg: "#ffcc66",
    tabSelectedFg: "#201b12",
    groupTitle: "#ffdba0",
    canvasBg: "#111111",
    canvasGrid: "#2c2c2c",
    canvasEdge: "#82aaff",
    canvasPreview: "#82aaff",
    ampBg: "#2a2a2a",
    ampFg: "#f6f6f6",
    positive: "#99d090",
    rootNote: "#ff5e73",
    scaleNote: "#99d090",
  },
  deep_black_npp: {
    bg: "#050505",
    text: "#f2f2f2",
    frame: "#323232",
    panel: "#0f0f0f",
    tab: "#1a1a1a",
    tabSelectedBg: "#ffae42",
    tabSelectedFg: "#1d1508",
    groupTitle: "#ffd594",
    canvasBg: "#050505",
    canvasGrid: "#1c1c1c",
    canvasEdge: "#58b7ff",
    canvasPreview: "#58b7ff",
    ampBg: "#1a1a1a",
    ampFg: "#f2f2f2",
    positive: "#7cd992",
    rootNote: "#ff5a66",
    scaleNote: "#7cd992",
  },
  zenburn_npp: {
    bg: "#3f3f3f",
    text: "#dcdccc",
    frame: "#6a7169",
    panel: "#4a4a4a",
    tab: "#545b54",
    tabSelectedBg: "#8faf9f",
    tabSelectedFg: "#1f2621",
    groupTitle: "#d7d7af",
    canvasBg: "#383838",
    canvasGrid: "#525252",
    canvasEdge: "#93e0e3",
    canvasPreview: "#93e0e3",
    ampBg: "#545b54",
    ampFg: "#ececd0",
    positive: "#9fc59f",
    rootNote: "#df6f7a",
    scaleNote: "#9fc59f",
  },
};

const CAGED_SHAPES = {
  c: { label: "C Shape", minor_start_offset: 5, major_start_offset: 2, window_size: 5 },
  a: { label: "A Shape", minor_start_offset: 7, major_start_offset: 4, window_size: 5 },
  g: { label: "G Shape", minor_start_offset: 10, major_start_offset: 7, window_size: 5 },
  e: { label: "E Shape", minor_start_offset: 0, major_start_offset: -3, window_size: 5 },
  d: { label: "D Shape", minor_start_offset: 3, major_start_offset: 0, window_size: 5 },
};

const SCALE_LIBRARY = {
  minor_pentatonic: {
    label: "Minor Pentatonic",
    intervals: [0, 3, 5, 7, 10],
    formula: "1 b3 4 5 b7",
    family: "minor",
  },
  major_pentatonic: {
    label: "Major Pentatonic",
    intervals: [0, 2, 4, 7, 9],
    formula: "1 2 3 5 6",
    family: "major",
  },
  minor_blues: {
    label: "Minor Blues",
    intervals: [0, 3, 5, 6, 7, 10],
    formula: "1 b3 4 b5 5 b7",
    family: "minor",
  },
  major_scale: {
    label: "Major Scale (Ionian)",
    intervals: [0, 2, 4, 5, 7, 9, 11],
    formula: "1 2 3 4 5 6 7",
    family: "major",
  },
  natural_minor: {
    label: "Natural Minor (Aeolian)",
    intervals: [0, 2, 3, 5, 7, 8, 10],
    formula: "1 2 b3 4 5 b6 b7",
    family: "minor",
  },
  mixolydian: {
    label: "Mixolydian",
    intervals: [0, 2, 4, 5, 7, 9, 10],
    formula: "1 2 3 4 5 6 b7",
    family: "major",
  },
};

const CRAZY_SCALE_LIBRARY = {
  hungarian_minor: {
    name: "Hungarian Minor",
    formula: "1 2 b3 #4 5 b6 7",
    intervals: [0, 2, 3, 6, 7, 8, 11],
    why: "Tense minor color with a raised fourth for dramatic lead movement.",
  },
  phrygian_dominant: {
    name: "Phrygian Dominant",
    formula: "1 b2 3 4 5 b6 b7",
    intervals: [0, 1, 4, 5, 7, 8, 10],
    why: "Exotic dominant tension that still resolves strongly to the tonic.",
  },
  double_harmonic_major: {
    name: "Double Harmonic Major",
    formula: "1 b2 3 4 5 b6 7",
    intervals: [0, 1, 4, 5, 7, 8, 11],
    why: "Wide-interval dramatic sound that keeps a major third center.",
  },
  lydian_dominant: {
    name: "Lydian Dominant",
    formula: "1 2 3 #4 5 6 b7",
    intervals: [0, 2, 4, 6, 7, 9, 10],
    why: "Bright #4 color with dominant pull; great for modern fusion flavors.",
  },
  harmonic_minor: {
    name: "Harmonic Minor",
    formula: "1 2 b3 4 5 b6 7",
    intervals: [0, 2, 3, 5, 7, 8, 11],
    why: "Minor scale with a leading tone for strong melodic resolution.",
  },
  whole_tone: {
    name: "Whole Tone",
    formula: "1 2 3 #4 #5 b7",
    intervals: [0, 2, 4, 6, 8, 10],
    why: "Symmetrical floating sound for unexpected modern transitions.",
  },
};

const CRAZY_SCALE_BY_GENRE = {
  metal: ["hungarian_minor", "phrygian_dominant", "double_harmonic_major", "harmonic_minor"],
  rock: ["harmonic_minor", "lydian_dominant", "phrygian_dominant", "hungarian_minor"],
  "classic-rock": ["harmonic_minor", "lydian_dominant", "whole_tone"],
  pop: ["lydian_dominant", "whole_tone", "harmonic_minor"],
  country: ["lydian_dominant", "harmonic_minor", "whole_tone"],
  "hip-hop": ["phrygian_dominant", "whole_tone", "lydian_dominant", "hungarian_minor"],
  blues: ["phrygian_dominant", "harmonic_minor", "whole_tone"],
};

const USUAL_KEYS_BY_GENRE = {
  metal: ["E", "D", "A", "C", "B"],
  rock: ["E", "A", "D", "G", "C"],
  "classic-rock": ["A", "E", "D", "G", "C"],
  pop: ["C", "G", "D", "A", "F"],
  country: ["G", "D", "A", "E", "C"],
  "hip-hop": ["Am", "Em", "Dm", "F", "C"],
  blues: ["E", "A", "G", "C", "D"],
};

const CIRCLE_FIFTHS_MAJOR = ["C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F"];
const CIRCLE_FIFTHS_MINOR = ["Am", "Em", "Bm", "F#m", "C#m", "G#m", "Ebm", "Bbm", "Fm", "Cm", "Gm", "Dm"];
const CIRCLE_FIFTHS_MAJOR_DISPLAY = {
  "F#": "F#/Gb",
  Db: "Db/C#",
  Ab: "Ab/G#",
  Eb: "Eb/D#",
  Bb: "Bb/A#",
};
const CIRCLE_FIFTHS_MINOR_DISPLAY = {
  "F#m": "F#m/Gbm",
  "C#m": "C#m/Dbm",
  "G#m": "G#m/Abm",
  Ebm: "Ebm/D#m",
  Bbm: "Bbm/A#m",
};

const NASHVILLE_MAJOR_CHART = [
  ["C", ["C", "Dm", "Em", "F", "G", "Am", "Bdim"]],
  ["G", ["G", "Am", "Bm", "C", "D", "Em", "F#dim"]],
  ["D", ["D", "Em", "F#m", "G", "A", "Bm", "C#dim"]],
  ["A", ["A", "Bm", "C#m", "D", "E", "F#m", "G#dim"]],
  ["E", ["E", "F#m", "G#m", "A", "B", "C#m", "D#dim"]],
  ["B", ["B", "C#m", "D#m", "E", "F#", "G#m", "A#dim"]],
  ["F#", ["F#", "G#m", "A#m", "B", "C#", "D#m", "Fdim"]],
  ["Db", ["Db", "Ebm", "Fm", "Gb", "Ab", "Bbm", "Cdim"]],
  ["Ab", ["Ab", "Bbm", "Cm", "Db", "Eb", "Fm", "Gdim"]],
  ["Eb", ["Eb", "Fm", "Gm", "Ab", "Bb", "Cm", "Ddim"]],
  ["Bb", ["Bb", "Cm", "Dm", "Eb", "F", "Gm", "Adim"]],
  ["F", ["F", "Gm", "Am", "Bb", "C", "Dm", "Edim"]],
];

const NOTE_ALIAS_MAP = {
  CB: "B",
  "B#": "C",
  DB: "Db",
  "C#": "Db",
  "D#": "Eb",
  EB: "Eb",
  "E#": "F",
  FB: "E",
  "F#": "F#",
  GB: "F#",
  "G#": "Ab",
  AB: "Ab",
  "A#": "Bb",
  BB: "Bb",
};

const NOTE_TO_PITCH_CLASS = {
  C: 0,
  Db: 1,
  D: 2,
  Eb: 3,
  E: 4,
  F: 5,
  "F#": 6,
  G: 7,
  Ab: 8,
  A: 9,
  Bb: 10,
  B: 11,
};

const PITCH_CLASS_CANONICAL = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"];
const PITCH_CLASS_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const SHARP_KEY_SIGNATURES = new Set(["G", "D", "A", "E", "B", "F#", "C#"]);
const STANDARD_TUNING_PCS_LOW_TO_HIGH = [4, 9, 2, 7, 11, 4];
const CHORD_ROOT_RE = /^\s*([A-Ga-g])([#b]?)/;

const PEDAL_REFERENCE = {
  cs3: {
    name: "BOSS CS-3 Compression Sustainer",
    summary: "Smooths level spikes and adds sustain so picking feels even and articulate.",
    controls: ["Level", "Tone", "Attack", "Sustain"],
    configure: [
      "Start with sustain near noon, then raise only until notes bloom without pumping.",
      "Use attack around noon for balanced transient response.",
      "Trim tone if top-end gets too sharp after compression.",
    ],
    possibilities: [
      "Country snap with fast attack and moderate sustain.",
      "Lead sustain before gain pedals.",
      "Clean rhythm leveling for loop layers.",
    ],
    placement: [
      "Usually first or near first, before overdrive/distortion.",
      "After gain is possible, but tends to raise hiss and flatten dynamics.",
    ],
  },
  sd1: {
    name: "BOSS SD-1 Super OverDrive",
    summary: "Asymmetrical clipping overdrive that tightens lows and emphasizes musical mids.",
    controls: ["Drive", "Tone", "Level"],
    configure: [
      "For boost use: Drive low, Level high, Tone just above noon.",
      "For standalone crunch: Drive to noon-ish and Level near unity.",
      "Reduce Tone slightly with bright pickups or bright amps.",
    ],
    possibilities: [
      "Classic mid-push rhythm tone.",
      "Tight front-end boost into DS-1/high-gain amps.",
      "Low-gain always-on edge-of-breakup texture.",
    ],
    placement: [
      "Commonly before DS-1 or amp distortion as a tightening boost.",
      "Can follow BD-2 when you want extra focus and sustain.",
    ],
  },
  bd2: {
    name: "BOSS BD-2 Blues Driver",
    summary: "Touch-sensitive overdrive with wide gain range from mild grit to aggressive breakup.",
    controls: ["Gain", "Tone", "Level"],
    configure: [
      "Start with Gain between 10 and 1 o'clock for dynamic breakup.",
      "Use Tone near noon and adjust for pickup brightness.",
      "Set Level to match or slightly lift solo volume.",
    ],
    possibilities: ["Always-on tube-like feel.", "Stack with SD-1 for thicker lead voice.", "Blues and classic-rock core overdrive."],
    placement: [
      "Usually before modulation/time effects.",
      "Relative position vs SD-1 changes whether tone is smoother or tighter.",
    ],
  },
  ds1: {
    name: "BOSS DS-1 Distortion",
    summary: "Hard-edged distortion with strong attack and long sustain for heavier rhythm and lead tones.",
    controls: ["Dist", "Tone", "Level"],
    configure: [
      "Set Dist for required saturation first, then tame highs with Tone.",
      "For tighter stacks, run SD-1 before DS-1 with low SD-1 drive.",
      "Keep Level high enough to cut in mix without overloading later stages.",
    ],
    possibilities: ["Primary distortion for rock/metal/grunge.", "Lead boost stage when stacked with SD-1/BD-2.", "Aggressive rhythm with pre-EQ tightening."],
    placement: [
      "Typically after compressor and before modulation/delay.",
      "Before SD-1 can soften attack and add focused mids from SD-1 output.",
    ],
  },
  ge7: {
    name: "BOSS GE-7 Equalizer",
    summary: "Seven-band EQ plus level slider for precision contour and clean boost/cut.",
    controls: ["100, 200, 400, 800, 1.6k, 3.2k, 6.4k sliders", "Level slider"],
    configure: [
      "Cut 100/200 Hz to tighten boomy rigs.",
      "Boost 800 Hz-1.6 kHz for mix cut and lead focus.",
      "Use Level slider for clean pre/post gain boost.",
    ],
    possibilities: ["Pre-drive sculpt to change clipping behavior.", "Post-drive polish for final contour.", "Feedback/problem-frequency control for acoustic setups."],
    placement: [
      "Before gain for feel and clip-shape changes.",
      "After gain for final tonal balancing.",
      "When paired with 10-band, split stages pre/post for best clarity.",
    ],
  },
  eq10: {
    name: "10-Band EQ",
    summary: "High-resolution frequency shaping with dedicated output/gain controls.",
    controls: ["31.25 to 16k sliders", "Output", "Gain"],
    configure: [
      "Start with subtle moves (1-3 dB equivalent) and refine by ear.",
      "Use output/gain controls carefully to avoid added noise.",
      "Trim extreme highs/lows first, then shape mids for articulation.",
    ],
    possibilities: ["Master post-drive tonal sculpting.", "Pre-drive voicing to influence saturation.", "Genre switching via saved curve ideas."],
    placement: ["Commonly post-drive for final polish.", "Can run pre-drive for deliberate clip-profile changes."],
  },
  ch1: {
    name: "BOSS CH-1 Super Chorus",
    summary: "Shimmering chorus for width and movement with controllable EQ focus.",
    controls: ["Effect Level", "EQ", "Rate", "Depth"],
    configure: [
      "Set depth/rate lower for subtle widening, higher for obvious swirl.",
      "Use EQ to keep chorus from getting too dark or brittle.",
      "Balance Effect Level so dry attack remains clear.",
    ],
    possibilities: ["Wide pop cleans and ambient rhythm textures.", "Post-gain lead thickening.", "Stereo spread in stereo rigs."],
    placement: ["Most often after gain and before delay/looper.", "Before DD-3 usually yields cleaner repeats."],
  },
  dd3: {
    name: "BOSS DD-3 Digital Delay",
    summary: "Clear digital repeats from slapback to long rhythmic echoes.",
    controls: ["E.Level", "F.Back", "D.Time", "Mode"],
    configure: [
      "Set D.Time and mode first for rhythmic subdivision/space.",
      "Use Feedback modestly unless ambient wash is desired.",
      "Blend E.Level so repeats support rather than mask picking.",
    ],
    possibilities: ["Country slapback and classic rock echoes.", "Rhythmic dotted-note textures.", "Pre-looper repeats baked into loops."],
    placement: ["Usually near chain end, after gain/modulation.", "Before RC-30 if repeats should print into loops."],
  },
  rc30: {
    name: "BOSS RC-30 Loop Station",
    summary: "Dual-track stereo looper for layered performance, practice, writing, and arrangement.",
    controls: ["Track 1 level", "Track 2 level", "Rhythm level", "Rhythm type", "Quantize", "Phrase memory"],
    configure: [
      "Set track levels so overdubs stay balanced over time.",
      "Use quantize/count-in when tight loop seams matter.",
      "Match rhythm level to context; too high can mask dynamics.",
      "Keep loop output below clipping and leave headroom for live playing.",
    ],
    possibilities: [
      "Dual-part arrangements (rhythm + lead).",
      "Verse/chorus loop building with separate tracks.",
      "Practice engine for timing, improvisation, and harmony.",
      "Live solo performance with progressive overdubs.",
    ],
    placement: [
      "Best at chain end when loops should capture final tone.",
      "Place earlier only when intentionally processing loop playback downstream.",
    ],
    advanced: [
      "Track architecture: Track 1 and Track 2 can be balanced independently.",
      "Rhythm engine: choose rhythm type and level for timing reference without DAW.",
      "Quantize behavior: improves seam accuracy for tighter starts and ends.",
      "Phrase memory workflow: save and recall loop ideas for practice/songwriting.",
    ],
  },
};

const APP_CONFIG_DEFAULTS = {
  feedback: {
    enabled: true,
    webhook_url: "",
    timeout_sec: 8,
    limiter: {
      max_per_day: 24,
      max_per_user_per_day: 4,
      max_per_user_total: 40,
      hard_limit_total: 5000,
    },
  },
  donate: {
    paypal_url: "",
    venmo_url: "",
    zelle_handle: "",
  },
};

const APP_CONFIG = deepMerge(APP_CONFIG_DEFAULTS, window.APP_DATA?.APP_CONFIG || {});

const STYLE_PLAYBOOK_FALLBACK = {
  metal: {
    concertProgression: ["Em - C - G - D", "Am - F - C - G"],
    progressionPool: [
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
    popularTop3: ["Em - C - G - D", "Am - F - C - G", "Bm - G - D - A"],
    capo5Shapes: ["Em - C - G - D", "Em - D - C - D"],
    openShapes: ["Em", "C", "G", "D", "Am"],
    capoGuide: "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
    pentatonicFret: "G-shape minor pentatonic root area at the 8th fret (relative to nut).",
    soloGuide: "Work the 8th-10th fret pocket with aggressive bends and short repeating motifs.",
  },
  rock: {
    concertProgression: ["C - G - Am - F", "G - D - Em - C"],
    progressionPool: [
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
    popularTop3: ["C - G - Am - F", "G - D - Em - C", "D - A - Bm - G"],
    capo5Shapes: ["G - D - Em - C", "A - D - E - D"],
    openShapes: ["G", "D", "Em", "C", "A", "E"],
    capoGuide: "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
    pentatonicFret: "G-shape minor pentatonic root area at the 8th fret.",
    soloGuide: "Target chord tones from the 8th-fret G-shape box and resolve on downbeats.",
  },
  "classic-rock": {
    concertProgression: ["D - G - A - G", "A - D - E - D"],
    progressionPool: [
      "D - G - A - G",
      "A - D - E - D",
      "E - A - B - A",
      "G - C - D - C",
      "A - E - D - A",
      "C - F - G - F",
      "D - C - G - D",
      "E - D - A - E",
      "G - D - C - G",
      "A - G - D - A",
      "B - A - E - B",
      "C - G - F - C",
    ],
    popularTop3: ["D - G - A - G", "A - D - E - D", "G - C - D - C"],
    capo5Shapes: ["A - D - E - D", "G - C - D - C"],
    openShapes: ["A", "D", "E", "G", "C"],
    capoGuide: "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
    pentatonicFret: "G-shape minor pentatonic root area around the 8th fret.",
    soloGuide: "Use 8th-fret box bends and vibrato for vintage lead phrasing.",
  },
  pop: {
    concertProgression: ["C - G - Am - F", "F - C - Dm - Bbmaj7"],
    progressionPool: [
      "C - G - Am - F",
      "F - C - Dm - Bbmaj7",
      "G - D - Em - C",
      "D - A - Bm - G",
      "A - E - F#m - D",
      "E - B - C#m - A",
      "F - G - Em - Am",
      "Bb - F - Gm - Eb",
      "C - Am - F - G",
      "G - Em - C - D",
      "D - Bm - G - A",
      "E - C#m - A - B",
    ],
    popularTop3: ["C - G - Am - F", "G - D - Em - C", "D - A - Bm - G"],
    capo5Shapes: ["G - D - Em - C", "C - G - Am - Fmaj7"],
    openShapes: ["C", "G", "Am", "Fmaj7", "D", "Em", "Cadd9"],
    capoGuide: "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
    pentatonicFret: "G-shape major/minor pentatonic pocket centered near fret 8.",
    soloGuide: "Keep melodies in the 8th-fret box short, hooky, and rhythm-aware.",
  },
  country: {
    concertProgression: ["C - F - G - C", "G - C - D - G"],
    progressionPool: [
      "C - F - G - C",
      "G - C - D - G",
      "D - G - A - D",
      "A - D - E - A",
      "E - A - B - E",
      "G - D - C - G",
      "C - G - F - C",
      "D - A - G - D",
      "A - E - D - A",
      "E - B - A - E",
      "G - Em - C - D",
      "D - Bm - G - A",
    ],
    popularTop3: ["G - C - D - G", "D - G - A - D", "A - D - E - A"],
    capo5Shapes: ["G - C - D - G", "D - G - A - D"],
    openShapes: ["G", "C", "D", "A", "Em"],
    capoGuide: "Exact mapping: concert C-F-G becomes G-C-D shapes with capo on fret 5.",
    pentatonicFret: "G-shape pentatonic home position at the 8th fret.",
    soloGuide: "Use 8th-fret double-stops, quick slides, and bends into chord tones.",
  },
  "hip-hop": {
    concertProgression: ["Am7 - Fmaj7 - C - Gsus2", "Dm7 - C - Bbmaj7 - Am7"],
    progressionPool: [
      "Am7 - Fmaj7 - C - Gsus2",
      "Dm7 - C - Bbmaj7 - Am7",
      "Em7 - Cmaj7 - G - Dsus2",
      "Fm7 - Dbmaj7 - Ab - Eb",
      "Bm7 - Gmaj7 - D - A",
      "Cm7 - Abmaj7 - Eb - Bb",
      "Am7 - G - Fmaj7 - Em7",
      "Dm7 - Bbmaj7 - F - C",
      "Em7 - D - Cmaj7 - Bm7",
      "Fm7 - Eb - Dbmaj7 - Cm7",
      "Gm7 - F - Ebmaj7 - Dm7",
      "Bm7 - A - Gmaj7 - F#m7",
    ],
    popularTop3: ["Am7 - Fmaj7 - C - Gsus2", "Dm7 - C - Bbmaj7 - Am7", "Em7 - Cmaj7 - G - Dsus2"],
    capo5Shapes: ["Em7 - Cmaj7 - G - Dsus2", "Am7 - G - Fmaj7 - Em7"],
    openShapes: ["Em7", "Cmaj7", "G", "Dsus2", "Am7", "Fmaj7"],
    capoGuide: "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
    pentatonicFret: "G-shape minor pentatonic around fret 8 (A-minor feel with capo 5).",
    soloGuide: "Use sparse 8th-fret pocket phrases, rhythmic rests, and short slides.",
  },
  blues: {
    concertProgression: ["A7 - D7 - E7 - D7", "D7 - G7 - A7 - G7"],
    progressionPool: [
      "A7 - D7 - E7 - D7",
      "D7 - G7 - A7 - G7",
      "E7 - A7 - B7 - A7",
      "G7 - C7 - D7 - C7",
      "C7 - F7 - G7 - F7",
      "B7 - E7 - F#7 - E7",
      "A7 - E7 - D7 - A7",
      "D7 - A7 - G7 - D7",
      "E7 - B7 - A7 - E7",
      "G7 - D7 - C7 - G7",
      "C7 - G7 - F7 - C7",
      "F7 - C7 - Bb7 - F7",
    ],
    popularTop3: ["A7 - D7 - E7 - D7", "D7 - G7 - A7 - G7", "E7 - A7 - B7 - A7"],
    capo5Shapes: ["E7 - A7 - B7 - A7", "A7 - D7 - E7 - D7"],
    openShapes: ["E7", "A7", "B7", "D7", "G"],
    capoGuide: "Capo rule: to sound C-F-G with capo on fret 5, play G-C-D open shapes.",
    pentatonicFret: "G-shape minor pentatonic around the 8th fret with blue-note passing tones.",
    soloGuide: "Target roots and b5 color tones in the 8th-fret box on turnarounds.",
  },
};

const state = {
  genre: "metal",
  guitarType: "electric",
  guitarProfile: AUTO_GUITAR_PROFILE_BY_TYPE.electric || "electric_2_knob_toggle",
  ampModel: "auto",
  chain: [...DEFAULT_CHAIN],
  connectedChain: [],
  canvasPositions: {},
  canvasConnections: [],
  theme: "dark",
  fontPreset: "medium",
  theoryScale: "minor_pentatonic",
  theoryShape: "g",
  selectedTheoryKey: "",
  pedalReference: BANK_ORDER[0],
};

const runtime = {
  lastRecommendation: null,
  styleProgressionCache: new Map(),
  crazyPayloadCache: new Map(),
  boardInitialized: false,
  lastBoardSize: { width: 980, height: 560 },
  selectedNodeId: "",
  selectedEdgeIndex: -1,
  connectionHistory: [],
  draggingPedalId: null,
  draggingOffset: { x: 0, y: 0 },
  linkStart: null,
  linkPreview: null,
  feedbackUserId: buildFeedbackUserId(),
  feedbackLimitsState: loadFeedbackLimiterState(),
};

const orderLabCache = new Map();
const PEDAL_NOTE_PATTERNS = {
  cs3: ["cs-3", "cs3", "compression sustainer", "compressor", "compress"],
  sd1: ["sd-1", "sd1", "super overdrive", "overdrive"],
  bd2: ["bd-2", "bd2", "blues driver"],
  ds1: ["ds-1", "ds1", "distortion"],
  ge7: ["ge-7", "ge7"],
  eq10: ["10-band", "10 band", "10-band eq", "eq10", "10 channel"],
  ch1: ["ch-1", "ch1", "chorus"],
  dd3: ["dd-3", "dd3", "delay"],
  rc30: ["rc-30", "rc30", "loop station", "looper", "loop"],
};

const PEDAL_SIZE = { width: 96, height: 144 };
const PEDAL_JACK_OUTSET = 4;
const PEDAL_ROUTE_PADDING = 2;
const DRAG_MIME = "application/x-pedal-architect";

const elements = {
  tabButtons: Array.from(document.querySelectorAll(".tab-btn[data-tab-target]")),
  tabPedals: document.getElementById("tabPedals"),
  tabBuilder: document.getElementById("tabBuilder"),
  tabRig: document.getElementById("tabRig"),
  tabTheory: document.getElementById("tabTheory"),
  tabFeedback: document.getElementById("tabFeedback"),

  genreSelect: document.getElementById("genreSelect"),
  guitarElectricRadio: document.getElementById("guitarElectricRadio"),
  guitarAcousticRadio: document.getElementById("guitarAcousticRadio"),
  profileTwoKnob: document.getElementById("profileTwoKnob"),
  profileFourKnob: document.getElementById("profileFourKnob"),
  electricProfileGroup: document.getElementById("electricProfileGroup"),
  acousticProfileLine: document.getElementById("acousticProfileLine"),
  ampSelect: document.getElementById("ampSelect"),
  optimizeBtn: document.getElementById("optimizeBtn"),
  saveBtn: document.getElementById("saveBtn"),
  settingsBtn: document.getElementById("settingsBtn"),
  settingsMenu: document.getElementById("settingsMenu"),
  closeSettingsBtn: document.getElementById("closeSettingsBtn"),
  fontSizeSelect: document.getElementById("fontSizeSelect"),
  themeSelect: document.getElementById("themeSelect"),

  pedalSelector: document.getElementById("pedalSelector"),
  pedalShowcase: document.getElementById("pedalShowcase"),
  pedalDetails: document.getElementById("pedalDetails"),

  pedalBank: document.getElementById("pedalBank"),
  activeChain: document.getElementById("activeChain"),
  boardCanvas: document.getElementById("boardCanvas"),
  boardNodes: document.getElementById("boardNodes"),
  boardCableLayer: document.getElementById("boardCableLayer"),
  chainScore: document.getElementById("chainScore"),
  chainSummary: document.getElementById("chainSummary"),
  cleanUpBtn: document.getElementById("cleanUpBtn"),
  autoWireBtn: document.getElementById("autoWireBtn"),
  clearCablesBtn: document.getElementById("clearCablesBtn"),
  resetBtn: document.getElementById("resetBtn"),

  rigGuitarPreview: document.getElementById("rigGuitarPreview"),
  rigAmpPreview: document.getElementById("rigAmpPreview"),
  rigPedalCards: document.getElementById("rigPedalCards"),
  rigPedalEmpty: document.getElementById("rigPedalEmpty"),
  guitarSettingsOutput: document.getElementById("guitarSettingsOutput"),
  ampSettingsOutput: document.getElementById("ampSettingsOutput"),
  guidanceList: document.getElementById("guidanceList"),
  summaryOutput: document.getElementById("summaryOutput"),

  circleOfFifths: document.getElementById("circleOfFifths"),
  circleHint: document.getElementById("circleHint"),
  nashvilleHint: document.getElementById("nashvilleHint"),
  usualKeys: document.getElementById("usualKeys"),
  nashvilleTableBody: document.getElementById("nashvilleTableBody"),
  scaleTypeSelect: document.getElementById("scaleTypeSelect"),
  cagedShapeSelect: document.getElementById("cagedShapeSelect"),
  scaleHint: document.getElementById("scaleHint"),
  neckChart: document.getElementById("neckChart"),
  keyToolkit: document.getElementById("keyToolkit"),
  stylePlaybook: document.getElementById("stylePlaybook"),
  crazyBtn: document.getElementById("crazyBtn"),
  crazyProgression: document.getElementById("crazyProgression"),
  crazyScale: document.getElementById("crazyScale"),

  feedbackForm: document.getElementById("feedbackForm"),
  feedbackName: document.getElementById("feedbackName"),
  feedbackEmail: document.getElementById("feedbackEmail"),
  feedbackRating: document.getElementById("feedbackRating"),
  feedbackType: document.getElementById("feedbackType"),
  feedbackMessage: document.getElementById("feedbackMessage"),
  feedbackStatus: document.getElementById("feedbackStatus"),
  feedbackLimitInfo: document.getElementById("feedbackLimitInfo"),
  donateMethod: document.getElementById("donateMethod"),
  donateBtn: document.getElementById("donateBtn"),
  donateDetails: document.getElementById("donateDetails"),

  toast: document.getElementById("toast"),
};

loadSavedState();
init();

function init() {
  normalizeStateSelections();
  populateControls();
  bindEvents();
  applyTheme();
  ensureCanvasState();
  setActiveTab("pedals");
  renderAll();
}

function normalizeStateSelections() {
  state.genre = GENRE_PRESETS[state.genre] ? state.genre : "metal";
  state.guitarType = state.guitarType === "acoustic" ? "acoustic" : "electric";
  if (!GUITAR_PROFILES[state.guitarProfile]) {
    state.guitarProfile = AUTO_GUITAR_PROFILE_BY_TYPE[state.guitarType] || "electric_2_knob_toggle";
  }
  const profile = GUITAR_PROFILES[state.guitarProfile];
  if (profile && profile.type !== state.guitarType) {
    state.guitarType = profile.type;
  }
  if (state.ampModel !== "auto" && !AMP_MODELS[state.ampModel]) {
    state.ampModel = "auto";
  }
  if (!THEMES[state.theme]) {
    state.theme = "dark";
  }
  if (!FONT_PRESET_SPECS.find(([key]) => key === state.fontPreset)) {
    state.fontPreset = "medium";
  }
  if (!SCALE_LIBRARY[state.theoryScale]) {
    state.theoryScale = "minor_pentatonic";
  }
  if (!CAGED_SHAPES[state.theoryShape]) {
    state.theoryShape = "g";
  }
  if (!PEDAL_LIBRARY[state.pedalReference]) {
    state.pedalReference = BANK_ORDER[0];
  }
  state.chain = sanitizeChain(Array.isArray(state.chain) ? state.chain : DEFAULT_CHAIN);
}

function populateControls() {
  elements.genreSelect.innerHTML = Object.entries(GENRE_PRESETS)
    .map(([key, preset]) => `<option value="${key}">${preset.label}</option>`)
    .join("");
  elements.genreSelect.value = state.genre;

  elements.ampSelect.innerHTML = [
    `<option value="auto">Auto (Best Match)</option>`,
    ...Object.entries(AMP_MODELS).map(([key, amp]) => `<option value="${key}">${amp.label}</option>`),
  ].join("");
  elements.ampSelect.value = state.ampModel;

  elements.themeSelect.innerHTML = THEME_PRESET_SPECS.map(
    ([key, label]) => `<option value="${key}">${label}</option>`,
  ).join("");
  elements.themeSelect.value = state.theme;

  elements.fontSizeSelect.innerHTML = FONT_PRESET_SPECS.map(
    ([key, label, size]) => `<option value="${key}">${label}  AaBbCc (${size}px)</option>`,
  ).join("");
  elements.fontSizeSelect.value = state.fontPreset;

  elements.scaleTypeSelect.innerHTML = Object.entries(SCALE_LIBRARY)
    .map(([key, scale]) => `<option value="${key}">${scale.label}</option>`)
    .join("");
  elements.scaleTypeSelect.value = state.theoryScale;

  elements.cagedShapeSelect.innerHTML = ["c", "a", "g", "e", "d"]
    .map((key) => `<option value="${key}">${CAGED_SHAPES[key].label}</option>`)
    .join("");
  elements.cagedShapeSelect.value = state.theoryShape;

  syncTopControlRadios();
  renderPedalSelector();
  renderNashvilleTableSkeleton();
}

function bindEvents() {
  elements.tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      setActiveTab(button.dataset.tabTarget || "pedals");
    });
  });

  elements.genreSelect.addEventListener("change", () => {
    state.genre = elements.genreSelect.value;
    runtime.styleProgressionCache.delete(state.genre);
    runtime.crazyPayloadCache.delete(state.genre);
    renderAll();
    persistState();
  });

  elements.guitarElectricRadio.addEventListener("change", onGuitarTypeChange);
  elements.guitarAcousticRadio.addEventListener("change", onGuitarTypeChange);
  elements.profileTwoKnob.addEventListener("change", onGuitarProfileChange);
  elements.profileFourKnob.addEventListener("change", onGuitarProfileChange);

  elements.ampSelect.addEventListener("change", () => {
    state.ampModel = AMP_MODELS[elements.ampSelect.value] ? elements.ampSelect.value : "auto";
    renderAll();
    persistState();
  });

  elements.optimizeBtn.addEventListener("click", optimizeChain);
  elements.saveBtn.addEventListener("click", () => {
    persistState();
    showToast("Saved locally on this device.");
  });
  elements.resetBtn.addEventListener("click", resetChain);
  elements.cleanUpBtn.addEventListener("click", () => {
    cleanUpLayout();
    renderAll();
    persistState();
  });
  elements.autoWireBtn.addEventListener("click", () => {
    autoWireActivePedals();
    renderAll();
    persistState();
  });
  elements.clearCablesBtn.addEventListener("click", () => {
    clearCables();
    renderAll();
    persistState();
  });

  elements.settingsBtn.addEventListener("click", () => {
    elements.settingsMenu.hidden = !elements.settingsMenu.hidden;
  });
  elements.closeSettingsBtn.addEventListener("click", () => {
    elements.settingsMenu.hidden = true;
  });
  elements.themeSelect.addEventListener("change", () => {
    state.theme = THEMES[elements.themeSelect.value] ? elements.themeSelect.value : "dark";
    applyTheme();
    renderAll();
    persistState();
  });
  elements.fontSizeSelect.addEventListener("change", () => {
    state.fontPreset = FONT_PRESET_SPECS.find(([key]) => key === elements.fontSizeSelect.value)
      ? elements.fontSizeSelect.value
      : "medium";
    applyTheme();
    renderAll();
    persistState();
  });

  document.addEventListener("click", (event) => {
    if (!elements.settingsMenu.hidden) {
      const insideMenu = elements.settingsMenu.contains(event.target);
      const onCog = elements.settingsBtn.contains(event.target);
      if (!insideMenu && !onCog) {
        elements.settingsMenu.hidden = true;
      }
    }
  });

  bindPedalSelectorEvents();
  bindChainListEvents();
  bindBoardEvents();
  bindTheoryEvents();
  bindFeedbackEvents();

  window.addEventListener("resize", () => {
    ensureCanvasState();
    renderBoard(runtime.lastRecommendation);
  });
}

function onGuitarTypeChange() {
  state.guitarType = elements.guitarAcousticRadio.checked ? "acoustic" : "electric";
  if (state.guitarType === "acoustic") {
    state.guitarProfile = "taylor_acoustic";
  } else if (!GUITAR_PROFILES[state.guitarProfile] || GUITAR_PROFILES[state.guitarProfile].type !== "electric") {
    state.guitarProfile = "electric_2_knob_toggle";
  }
  syncTopControlRadios();
  renderAll();
  persistState();
}

function onGuitarProfileChange() {
  if (state.guitarType === "acoustic") {
    state.guitarProfile = "taylor_acoustic";
  } else {
    state.guitarProfile = elements.profileFourKnob.checked
      ? "electric_4_knob_toggle"
      : "electric_2_knob_toggle";
  }
  syncTopControlRadios();
  renderAll();
  persistState();
}

function syncTopControlRadios() {
  const acoustic = state.guitarType === "acoustic";
  elements.guitarAcousticRadio.checked = acoustic;
  elements.guitarElectricRadio.checked = !acoustic;

  elements.profileTwoKnob.disabled = acoustic;
  elements.profileFourKnob.disabled = acoustic;
  elements.electricProfileGroup.classList.toggle("disabled", acoustic);
  elements.acousticProfileLine.classList.toggle("active", acoustic);

  if (!acoustic) {
    elements.profileFourKnob.checked = state.guitarProfile === "electric_4_knob_toggle";
    elements.profileTwoKnob.checked = !elements.profileFourKnob.checked;
  }

  elements.ampSelect.value = state.ampModel;
}

function bindPedalSelectorEvents() {
  elements.pedalSelector.addEventListener("click", (event) => {
    const button = event.target.closest(".pedal-selector-item");
    if (!button) {
      return;
    }
    const pedalId = button.dataset.pedalId;
    if (!PEDAL_LIBRARY[pedalId]) {
      return;
    }
    state.pedalReference = pedalId;
    renderPedalSelector();
    renderPedalsTab(runtime.lastRecommendation);
    persistState();
  });
}

function bindChainListEvents() {
  elements.pedalBank.addEventListener("dragstart", onListDragStart);

  elements.pedalBank.addEventListener("dragover", (event) => event.preventDefault());
  elements.pedalBank.addEventListener("drop", onPedalBankDrop);

  document.addEventListener("dragend", () => {
    clearDropTargets();
    document.querySelectorAll(".dragging").forEach((node) => node.classList.remove("dragging"));
  });

  elements.activeChain.addEventListener("click", (event) => {
    const remove = event.target.closest("[data-remove-pedal]");
    if (!remove) {
      return;
    }
    const pedalId = remove.dataset.removePedal;
    returnChainPedalToBank(pedalId);
  });

  elements.pedalBank.addEventListener("click", (event) => {
    const tile = event.target.closest(".pedal-list-item[data-pedal-id]");
    if (!tile) {
      return;
    }
    const pedalId = tile.dataset.pedalId;
    if (!PEDAL_LIBRARY[pedalId]) {
      return;
    }
    showToast(`Drag ${PEDAL_LIBRARY[pedalId].model} onto the canvas to place it.`);
  });
}

function onListDragStart(event) {
  const startEl = eventElementTarget(event);
  const node = startEl
    ? startEl.closest(".pedal-list-item[draggable='true'], .pedal-item[draggable='true']")
    : null;
  if (!node) {
    return;
  }
  const origin = node.dataset.origin;
  const pedalId = node.dataset.pedalId;
  if (!origin || !pedalId) {
    return;
  }
  const payload = {
    origin,
    pedalId,
  };
  if (origin === "chain") {
    payload.index = Number(node.dataset.index);
  }
  event.dataTransfer.effectAllowed = "move";
  const serialized = JSON.stringify(payload);
  event.dataTransfer.setData(DRAG_MIME, serialized);
  event.dataTransfer.setData("text/plain", serialized);
  node.classList.add("dragging");
}

function eventElementTarget(event) {
  const raw = event?.target;
  if (raw instanceof Element) {
    return raw;
  }
  if (raw && raw.parentElement instanceof Element) {
    return raw.parentElement;
  }
  return null;
}

function parseDragPayload(event) {
  const data = event?.dataTransfer;
  if (!data) {
    return null;
  }
  const raw = data.getData(DRAG_MIME) || data.getData("text/plain");
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function onActiveChainDragOver(event) {
  event.preventDefault();
  const targetEl = eventElementTarget(event);
  const target =
    (targetEl ? targetEl.closest("[data-drop-index]") : null) ||
    nearestDropTarget(elements.activeChain, event.clientX, event.clientY);
  if (target) {
    clearDropTargets();
    target.classList.add("active-target");
  }
}

function onActiveChainDragLeave(event) {
  if (!event.currentTarget.contains(event.relatedTarget)) {
    clearDropTargets();
  }
}

function onActiveChainDrop(event) {
  event.preventDefault();
  const payload = parseDragPayload(event);
  if (!payload || !PEDAL_LIBRARY[payload.pedalId]) {
    clearDropTargets();
    return;
  }

  const targetEl = eventElementTarget(event);
  const target =
    (targetEl ? targetEl.closest("[data-drop-index]") : null) ||
    elements.activeChain.querySelector(".active-target") ||
    nearestDropTarget(elements.activeChain, event.clientX, event.clientY);
  const index = target ? Number(target.dataset.dropIndex) : state.chain.length;
  clearDropTargets();

  if (!Number.isInteger(index)) {
    return;
  }

  insertPedalIntoChain(payload.pedalId, index, payload.origin || "bank", payload.index);
}

function onPedalBankDrop(event) {
  event.preventDefault();
  const payload = parseDragPayload(event);
  if (!payload || payload.origin !== "chain") {
    return;
  }
  returnChainPedalToBank(payload.pedalId);
}

function nearestDropTarget(container, x, y) {
  const targets = Array.from(container.querySelectorAll("[data-drop-index]"));
  if (!targets.length) {
    return null;
  }
  let closest = null;
  let bestDistance = Infinity;
  targets.forEach((target) => {
    const rect = target.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const d = Math.hypot(cx - x, cy - y);
    if (d < bestDistance) {
      bestDistance = d;
      closest = target;
    }
  });
  return closest;
}

function clearDropTargets() {
  document
    .querySelectorAll(".active-target")
    .forEach((node) => node.classList.remove("active-target"));
}

function insertPedalIntoChain(pedalId, row, source = "bank", sourceIndex = null) {
  if (!PEDAL_LIBRARY[pedalId]) {
    return;
  }

  const chain = [...state.chain];
  let nextRow = clamp(Number(row) || 0, 0, chain.length);

  if (source === "chain" && chain.includes(pedalId)) {
    const oldIndex = chain.indexOf(pedalId);
    chain.splice(oldIndex, 1);
    if (oldIndex < nextRow) {
      nextRow -= 1;
    }
  } else if (chain.includes(pedalId)) {
    showToast(`${PEDAL_LIBRARY[pedalId].model} is already active.`);
    return;
  }

  if (source === "chain" && Number.isInteger(sourceIndex) && sourceIndex >= 0 && sourceIndex < state.chain.length) {
    nextRow = clamp(nextRow, 0, chain.length);
  }

  chain.splice(nextRow, 0, pedalId);
  state.chain = sanitizeChain(chain);
  ensureCanvasState(pedalId);
  renderAll();
  persistState();
}

function returnChainPedalToBank(pedalId) {
  if (!state.chain.includes(pedalId)) {
    return;
  }
  const hadConnections = state.canvasConnections.some((edge) => edge[0] === pedalId || edge[1] === pedalId);
  if (hadConnections) {
    snapshotConnections();
  }
  state.chain = state.chain.filter((id) => id !== pedalId);
  state.canvasConnections = state.canvasConnections.filter(
    (edge) => edge[0] !== pedalId && edge[1] !== pedalId,
  );
  if (runtime.selectedNodeId === pedalId) {
    runtime.selectedNodeId = "";
  }
  runtime.selectedEdgeIndex = -1;
  delete state.canvasPositions[pedalId];
  ensureCanvasState();
  renderAll();
  persistState();
}

function bindBoardEvents() {
  elements.boardCanvas.addEventListener("dragover", (event) => {
    event.preventDefault();
  });

  elements.boardCanvas.addEventListener("drop", (event) => {
    event.preventDefault();
    const payload = parseDragPayload(event);
    if (!payload || !PEDAL_LIBRARY[payload.pedalId]) {
      return;
    }
    const boardPoint = toBoardPoint(event.clientX, event.clientY);
    if (!boardPoint) {
      return;
    }
    if (!state.chain.includes(payload.pedalId)) {
      state.chain.push(payload.pedalId);
    } else if (payload.origin === "chain") {
      state.chain = [...state.chain.filter((id) => id !== payload.pedalId), payload.pedalId];
    }
    ensureCanvasState(payload.pedalId, boardPoint);
    if (!state.canvasConnections.length) {
      state.canvasConnections = anchorConnectionsToEndpoints(state.canvasConnections);
    }
    runtime.selectedNodeId = payload.pedalId;
    runtime.selectedEdgeIndex = -1;
    renderAll();
    persistState();
  });

  elements.boardCableLayer.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target.closest("polyline[data-edge-index]") : null;
    if (!target) {
      runtime.selectedEdgeIndex = -1;
      renderBoard(runtime.lastRecommendation);
      return;
    }
    runtime.selectedNodeId = "";
    runtime.selectedEdgeIndex = Number(target.dataset.edgeIndex);
    renderBoard(runtime.lastRecommendation);
  });

  elements.boardNodes.addEventListener("click", (event) => {
    const remove = event.target.closest("[data-remove-pedal]");
    if (remove) {
      returnChainPedalToBank(remove.dataset.removePedal);
      return;
    }
    const disconnect = event.target.closest("[data-disconnect]");
    if (disconnect) {
      const pedalId = disconnect.dataset.pedalId;
      const side = disconnect.dataset.disconnect;
      snapshotConnections();
      if (side === "input") {
        state.canvasConnections = state.canvasConnections.filter((edge) => edge[1] !== pedalId);
      } else {
        state.canvasConnections = state.canvasConnections.filter((edge) => edge[0] !== pedalId);
      }
      runtime.selectedEdgeIndex = -1;
      renderAll();
      persistState();
      showToast("Disconnected cable side.");
      return;
    }

    const selectedNode = event.target.closest(".board-pedal[data-pedal-id], .board-guitar[data-node-id], .board-amp[data-node-id]");
    if (selectedNode) {
      runtime.selectedEdgeIndex = -1;
      runtime.selectedNodeId = selectedNode.dataset.pedalId || selectedNode.dataset.nodeId || "";
      renderBoard(runtime.lastRecommendation);
      return;
    }

    runtime.selectedNodeId = "";
    runtime.selectedEdgeIndex = -1;
    renderBoard(runtime.lastRecommendation);
  });

  elements.boardCanvas.addEventListener("click", (event) => {
    if (event.target === elements.boardCanvas || event.target === elements.boardNodes) {
      runtime.selectedNodeId = "";
      runtime.selectedEdgeIndex = -1;
      renderBoard(runtime.lastRecommendation);
    }
  });

  elements.boardNodes.addEventListener("pointerdown", (event) => {
    const outputJack = event.target.closest(".jack.output");
    if (outputJack) {
      const nodeId = outputJack.dataset.nodeId;
      if (nodeId) {
        runtime.selectedNodeId = nodeId;
        runtime.selectedEdgeIndex = -1;
        runtime.linkStart = nodeId;
        runtime.linkPreview = toBoardPoint(event.clientX, event.clientY);
        renderBoardCables();
        event.preventDefault();
      }
      return;
    }

    const pedal = event.target.closest(".board-pedal");
    if (!pedal) {
      return;
    }

    if (
      event.target.closest(".jack") ||
      event.target.closest(".pedal-remove") ||
      event.target.closest(".pedal-disconnect")
    ) {
      return;
    }

    const pedalId = pedal.dataset.pedalId;
    if (!pedalId || !state.canvasPositions[pedalId]) {
      return;
    }
    runtime.selectedNodeId = pedalId;
    runtime.selectedEdgeIndex = -1;

    const boardPoint = toBoardPoint(event.clientX, event.clientY);
    if (!boardPoint) {
      return;
    }

    const current = state.canvasPositions[pedalId];
    runtime.draggingPedalId = pedalId;
    runtime.draggingOffset = {
      x: boardPoint.x - current[0],
      y: boardPoint.y - current[1],
    };
    pedal.setPointerCapture(event.pointerId);
    event.preventDefault();
  });

  document.addEventListener("pointermove", (event) => {
    if (runtime.linkStart) {
      runtime.linkPreview = toBoardPoint(event.clientX, event.clientY);
      renderBoardCables();
      return;
    }

    if (!runtime.draggingPedalId) {
      return;
    }

    const boardPoint = toBoardPoint(event.clientX, event.clientY);
    if (!boardPoint) {
      return;
    }

    const next = clampPedalPosition({
      x: boardPoint.x - runtime.draggingOffset.x,
      y: boardPoint.y - runtime.draggingOffset.y,
    });
    state.canvasPositions[runtime.draggingPedalId] = [next.x, next.y];
    renderBoard(runtime.lastRecommendation);
  });

  document.addEventListener("pointerup", (event) => {
    if (runtime.linkStart) {
      const target = document.elementFromPoint(event.clientX, event.clientY)?.closest(".jack.input");
      if (target) {
        onCanvasConnectionCreated(runtime.linkStart, target.dataset.nodeId);
      }
      runtime.linkStart = null;
      runtime.linkPreview = null;
      renderBoardCables();
      persistState();
      return;
    }

    if (runtime.draggingPedalId) {
      runtime.draggingPedalId = null;
      persistState();
    }
  });

  document.addEventListener("keydown", (event) => {
    const target = event.target instanceof Element ? event.target : null;
    if (
      target &&
      (target.closest("input, textarea, select") ||
        target.isContentEditable)
    ) {
      return;
    }

    if (event.key === "Delete" || event.key === "Backspace") {
      if (deleteSelectedConnection()) {
        event.preventDefault();
      }
      return;
    }

    const undoChord = (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "z";
    if (undoChord) {
      undoConnectionMutation();
      event.preventDefault();
    }
  });
}

function toBoardPoint(clientX, clientY) {
  const rect = elements.boardCanvas.getBoundingClientRect();
  if (!rect.width || !rect.height) {
    return null;
  }
  return {
    x: Math.round(clientX - rect.left),
    y: Math.round(clientY - rect.top),
  };
}

function boardBounds() {
  if (!elements.boardCanvas) {
    return { width: runtime.lastBoardSize.width, height: runtime.lastBoardSize.height };
  }

  const rect = elements.boardCanvas.getBoundingClientRect();
  let width = Math.round(rect.width || elements.boardCanvas.clientWidth || 0);
  let height = Math.round(rect.height || elements.boardCanvas.clientHeight || 0);

  // Hidden tabs can report zero geometry; keep practical dimensions for layout math.
  if (width <= 0) {
    width = runtime.lastBoardSize.width || 980;
  }
  if (height <= 0) {
    height = runtime.lastBoardSize.height || 560;
  }

  width = Math.max(280, width);
  height = Math.max(240, height);
  runtime.lastBoardSize = { width, height };
  return { width, height };
}

function sideNodeWidthCap() {
  const { width } = boardBounds();
  const edgePad = 16;
  const centerLane = Math.max(72, Math.round(PEDAL_SIZE.width * 0.78));
  return Math.max(74, Math.floor((width - edgePad * 2 - centerLane) / 2));
}

function ampRect() {
  const { width, height } = boardBounds();
  const sideCap = sideNodeWidthCap();
  const ampWidth = clamp(Math.round(width * 0.26), 84, sideCap);
  const ampHeight = clamp(Math.round(height * 0.36), 170, 240);
  return {
    x: 18,
    y: Math.max(16, height - ampHeight - 16),
    width: ampWidth,
    height: ampHeight,
  };
}

function guitarRect() {
  const { width, height } = boardBounds();
  const sideCap = sideNodeWidthCap();
  const w = clamp(Math.round(width * 0.22), 82, sideCap);
  let h = clamp(Math.round(height * 0.56), 220, 310);
  let y = Math.max(16, height - h - 16);
  if (y < 14) {
    h = Math.max(170, height - 30);
    y = 14;
  }
  return {
    x: Math.max(16, width - w - 22),
    y,
    width: w,
    height: h,
  };
}

function pedalPositionBounds() {
  const { width, height } = boardBounds();
  return {
    minX: 14,
    maxX: Math.max(14, width - PEDAL_SIZE.width - 14),
    minY: 14,
    maxY: Math.max(14, height - PEDAL_SIZE.height - 14),
  };
}

function reservedPedalExclusionRects() {
  return [
    expandRect(ampRect(), 10),
    expandRect(guitarRect(), 10),
  ];
}

function canPlacePedalAt(point) {
  const bounds = pedalPositionBounds();
  if (point.x < bounds.minX || point.x > bounds.maxX || point.y < bounds.minY || point.y > bounds.maxY) {
    return false;
  }
  const rect = {
    x: point.x,
    y: point.y,
    width: PEDAL_SIZE.width,
    height: PEDAL_SIZE.height,
  };
  return !reservedPedalExclusionRects().some((reserved) => rectsIntersect(rect, reserved));
}

function clampPedalPosition(point) {
  const bounds = pedalPositionBounds();
  const desired = {
    x: clamp(point.x, bounds.minX, bounds.maxX),
    y: clamp(point.y, bounds.minY, bounds.maxY),
  };
  if (canPlacePedalAt(desired)) {
    return desired;
  }
  return findNearestOpenPedalPosition(desired);
}

function findNearestOpenPedalPosition(desired) {
  const bounds = pedalPositionBounds();
  const clamped = {
    x: clamp(desired.x, bounds.minX, bounds.maxX),
    y: clamp(desired.y, bounds.minY, bounds.maxY),
  };
  if (canPlacePedalAt(clamped)) {
    return clamped;
  }

  const candidates = [];
  const gap = 10;
  reservedPedalExclusionRects().forEach((reserved) => {
    candidates.push({ x: reserved.x - PEDAL_SIZE.width - gap, y: clamped.y });
    candidates.push({ x: reserved.x + reserved.width + gap, y: clamped.y });
    candidates.push({ x: clamped.x, y: reserved.y - PEDAL_SIZE.height - gap });
    candidates.push({ x: clamped.x, y: reserved.y + reserved.height + gap });
  });

  const seen = new Set();
  const normalized = [];
  candidates.forEach((raw) => {
    const point = {
      x: clamp(raw.x, bounds.minX, bounds.maxX),
      y: clamp(raw.y, bounds.minY, bounds.maxY),
    };
    const key = `${point.x}:${point.y}`;
    if (!seen.has(key)) {
      seen.add(key);
      normalized.push(point);
    }
  });

  normalized.sort(
    (a, b) =>
      Math.abs(a.x - clamped.x) + Math.abs(a.y - clamped.y) - (Math.abs(b.x - clamped.x) + Math.abs(b.y - clamped.y)),
  );

  for (const point of normalized) {
    if (canPlacePedalAt(point)) {
      return point;
    }
  }

  const step = 14;
  const maxRadius = Math.max(boardBounds().width, boardBounds().height);
  for (let radius = step; radius <= maxRadius + step; radius += step) {
    for (let offset = -radius; offset <= radius; offset += step) {
      const ring = [
        { x: clamped.x + offset, y: clamped.y - radius },
        { x: clamped.x + offset, y: clamped.y + radius },
        { x: clamped.x - radius, y: clamped.y + offset },
        { x: clamped.x + radius, y: clamped.y + offset },
      ];
      for (const raw of ring) {
        const point = {
          x: clamp(raw.x, bounds.minX, bounds.maxX),
          y: clamp(raw.y, bounds.minY, bounds.maxY),
        };
        if (canPlacePedalAt(point)) {
          return point;
        }
      }
    }
  }

  return clamped;
}

function pedalRect(pedalId) {
  const pos = state.canvasPositions[pedalId] || [16, 16];
  return {
    x: Number(pos[0]) || 16,
    y: Number(pos[1]) || 16,
    width: PEDAL_SIZE.width,
    height: PEDAL_SIZE.height,
  };
}

function pedalInputPos(pedalId) {
  const rect = pedalRect(pedalId);
  return {
    x: rect.x + rect.width + PEDAL_JACK_OUTSET,
    y: Math.round(rect.y + rect.height / 2),
  };
}

function pedalOutputPos(pedalId) {
  const rect = pedalRect(pedalId);
  return {
    x: rect.x - PEDAL_JACK_OUTSET,
    y: Math.round(rect.y + rect.height / 2),
  };
}

function ampInputPos() {
  const rect = ampRect();
  return {
    x: rect.x + rect.width + PEDAL_JACK_OUTSET,
    y: Math.round(rect.y + rect.height / 2),
  };
}

function guitarOutputPos() {
  const rect = guitarRect();
  return {
    x: rect.x - PEDAL_JACK_OUTSET,
    y: Math.round(rect.y + rect.height / 2 + Math.max(10, rect.height / 6)),
  };
}

function ensureCanvasState(focusPedal = null, focusPos = null) {
  state.chain = sanitizeChain(state.chain);

  state.chain.forEach((pedalId) => {
    if (focusPedal === pedalId && focusPos) {
      const clamped = clampPedalPosition(focusPos);
      state.canvasPositions[pedalId] = [clamped.x, clamped.y];
      return;
    }
    const raw = state.canvasPositions[pedalId];
    if (!Array.isArray(raw) || raw.length !== 2) {
      const fallback = defaultCanvasPositionFor(pedalId);
      state.canvasPositions[pedalId] = [fallback.x, fallback.y];
      return;
    }
    const clamped = clampPedalPosition({ x: Number(raw[0]), y: Number(raw[1]) });
    state.canvasPositions[pedalId] = [clamped.x, clamped.y];
  });

  Object.keys(state.canvasPositions).forEach((pedalId) => {
    if (!state.chain.includes(pedalId)) {
      delete state.canvasPositions[pedalId];
    }
  });

  sanitizeCanvasConnections();
}

function sanitizeCanvasConnections() {
  const activeSet = new Set(state.chain);
  const seen = new Set();
  const clean = [];
  (state.canvasConnections || []).forEach((entry) => {
    if (!Array.isArray(entry) || entry.length !== 2) {
      return;
    }
    const src = String(entry[0]);
    const dst = String(entry[1]);
    if (src === dst) {
      return;
    }
    const validSrc = src === GUITAR_NODE_ID || activeSet.has(src);
    const validDst = dst === AMP_NODE_ID || activeSet.has(dst);
    if (!validSrc || !validDst) {
      return;
    }
    const key = `${src}->${dst}`;
    if (seen.has(key)) {
      return;
    }
    seen.add(key);
    clean.push([src, dst]);
  });
  state.canvasConnections = clean;
}

function defaultCanvasPositionFor(pedalId) {
  const index = state.chain.indexOf(pedalId);
  const slots = collectHorizontalChainSlots(Math.max(18, state.chain.length * 3));
  if (Number.isInteger(index) && index >= 0 && index < slots.length) {
    return slots[index];
  }
  return clampPedalPosition({ x: 20 + ((index >= 0 ? index : 0) % 5) * 16, y: 24 + Math.floor((index >= 0 ? index : 0) / 5) * 14 });
}

function collectLayoutSlots(maxCount, options = {}) {
  if (maxCount <= 0) {
    return [];
  }

  const bounds = pedalPositionBounds();
  let minX = bounds.minX;
  let maxX = bounds.maxX;
  let minY = bounds.minY;
  let maxY = bounds.maxY;

  if (options.xRange) {
    minX = clamp(Number(options.xRange[0]), bounds.minX, bounds.maxX);
    maxX = clamp(Number(options.xRange[1]), minX, bounds.maxX);
  }
  if (options.yRange) {
    minY = clamp(Number(options.yRange[0]), bounds.minY, bounds.maxY);
    maxY = clamp(Number(options.yRange[1]), minY, bounds.maxY);
  }

  const stepX = PEDAL_SIZE.width + 22;
  const stepY = PEDAL_SIZE.height + 24;
  const xs = [];
  const ys = [];
  for (let x = minX; x <= maxX; x += stepX) {
    xs.push(x);
  }
  for (let y = minY; y <= maxY; y += stepY) {
    ys.push(y);
  }
  if (options.rightToLeft) {
    xs.reverse();
  }

  const slots = [];
  ys.forEach((y) => {
    xs.forEach((x) => {
      const point = { x, y };
      if (canPlacePedalAt(point)) {
        slots.push(point);
      }
    });
  });
  return slots.slice(0, maxCount);
}

function collectHorizontalChainSlots(maxCount, options = {}) {
  if (maxCount <= 0) {
    return [];
  }

  const bounds = pedalPositionBounds();
  let minX = bounds.minX;
  let maxX = bounds.maxX;
  let minY = bounds.minY;
  let maxY = bounds.maxY;

  if (options.xRange) {
    minX = clamp(Number(options.xRange[0]), bounds.minX, bounds.maxX);
    maxX = clamp(Number(options.xRange[1]), minX, bounds.maxX);
  }
  if (options.yRange) {
    minY = clamp(Number(options.yRange[0]), bounds.minY, bounds.maxY);
    maxY = clamp(Number(options.yRange[1]), minY, bounds.maxY);
  }

  const stepX = PEDAL_SIZE.width + 22;
  const stepY = PEDAL_SIZE.height + 24;
  const xs = [];
  for (let x = maxX; x >= minX; x -= stepX) {
    xs.push(x);
  }

  const centerY = clamp(Math.round((minY + maxY) / 2), minY, maxY);
  const rowCenters = [centerY];
  for (let offset = stepY; offset <= maxY - minY + stepY; offset += stepY) {
    const down = centerY + offset;
    const up = centerY - offset;
    if (down <= maxY) {
      rowCenters.push(down);
    }
    if (up >= minY) {
      rowCenters.push(up);
    }
    if (down > maxY && up < minY) {
      break;
    }
  }

  const rows = [];
  rowCenters.forEach((y) => {
    const rowSlots = [];
    xs.forEach((x) => {
      const point = { x, y };
      if (canPlacePedalAt(point)) {
        rowSlots.push(point);
      }
    });
    if (rowSlots.length) {
      rows.push({ slots: rowSlots, y });
    }
  });

  rows.sort((a, b) => b.slots.length - a.slots.length || Math.abs(a.y - centerY) - Math.abs(b.y - centerY));

  const out = [];
  rows.forEach((row) => {
    row.slots.forEach((slot) => {
      out.push(slot);
    });
  });

  return out.slice(0, maxCount);
}

function chooseSlot(candidates, usedRects) {
  for (const candidate of candidates) {
    const candidateRect = {
      x: candidate.x,
      y: candidate.y,
      width: PEDAL_SIZE.width,
      height: PEDAL_SIZE.height,
    };
    const collides = usedRects.some((used) => rectsIntersect(expandRect(candidateRect, 6), used));
    if (!collides) {
      return candidate;
    }
  }
  return null;
}

function cleanUpLayout() {
  const chain = sanitizeChain(state.chain);
  if (!chain.length) {
    return;
  }

  const connected = computeConnectedChain();
  const connectedIds = chain.filter((pedalId) => connected.includes(pedalId));
  const stagedIds = chain.filter((pedalId) => !connected.includes(pedalId));
  const bounds = pedalPositionBounds();

  let signalSlots = collectHorizontalChainSlots(Math.max(connectedIds.length * 3, 16), {
    xRange: [bounds.minX, bounds.maxX],
    yRange: [bounds.minY + 90, bounds.maxY],
  });
  if (signalSlots.length < connectedIds.length) {
    signalSlots = collectHorizontalChainSlots(Math.max(chain.length * 3, 18));
  }

  const parkingY1 = Math.min(bounds.maxY, bounds.minY + PEDAL_SIZE.height + 40);
  let parkingSlots = collectLayoutSlots(Math.max(stagedIds.length * 4, 12), {
    yRange: [bounds.minY, parkingY1],
  });
  if (parkingSlots.length < stagedIds.length) {
    const rightColumnX0 = Math.max(bounds.minX, bounds.maxX - PEDAL_SIZE.width - 6);
    parkingSlots = parkingSlots.concat(
      collectLayoutSlots(Math.max(stagedIds.length * 4, 12), {
        xRange: [rightColumnX0, bounds.maxX],
        yRange: [bounds.minY, bounds.maxY],
      }),
    );
  }

  const fallbackSlots = collectLayoutSlots(Math.max(chain.length * 4, 24), { rightToLeft: true });
  const usedRects = [];

  connectedIds.forEach((pedalId) => {
    let slot = chooseSlot(signalSlots, usedRects);
    if (!slot) {
      slot = chooseSlot(fallbackSlots, usedRects) || clampPedalPosition({ x: bounds.minX, y: bounds.minY });
    }
    state.canvasPositions[pedalId] = [slot.x, slot.y];
    usedRects.push({ x: slot.x, y: slot.y, width: PEDAL_SIZE.width, height: PEDAL_SIZE.height });
  });

  stagedIds.forEach((pedalId) => {
    let slot = chooseSlot(parkingSlots, usedRects);
    if (!slot) {
      slot = chooseSlot(fallbackSlots, usedRects) || clampPedalPosition({ x: bounds.maxX, y: bounds.minY });
    }
    state.canvasPositions[pedalId] = [slot.x, slot.y];
    usedRects.push({ x: slot.x, y: slot.y, width: PEDAL_SIZE.width, height: PEDAL_SIZE.height });
  });
}

function clearCables() {
  if (state.canvasConnections.length) {
    snapshotConnections();
  }
  state.canvasConnections = [];
  runtime.selectedEdgeIndex = -1;
}

function autoWireActivePedals() {
  const chain = sanitizeChain(state.chain);
  if (!chain.length) {
    state.canvasConnections = [];
    return;
  }
  const connections = [[GUITAR_NODE_ID, chain[0]]];
  for (let i = 0; i < chain.length - 1; i += 1) {
    connections.push([chain[i], chain[i + 1]]);
  }
  connections.push([chain[chain.length - 1], AMP_NODE_ID]);
  state.canvasConnections = connections;
}

function resetChain() {
  state.chain = [...DEFAULT_CHAIN];
  ensureCanvasState();
  clearCables();
  cleanUpLayout();
  renderAll();
  persistState();
  showToast("Chain reset to default layout.");
}

function optimizeChain() {
  const preset = GENRE_PRESETS[state.genre] || GENRE_PRESETS.metal;
  const seed = state.chain.length ? state.chain : preset.optimizedChain;
  const analysis = runOrderLab(state.genre, seed, state.guitarType);
  state.chain = sanitizeChain(analysis.bestChain);
  ensureCanvasState();
  autoWireActivePedals();
  cleanUpLayout();
  renderAll();
  persistState();

  const message = `${preset.label} optimized (${formatNumber(analysis.permutationsChecked)} layouts checked).`;
  if (!elements.tabBuilder.classList.contains("active")) {
    showToast(message, { chain: state.chain });
  } else {
    showToast(message);
  }
}

function computeConnectedChain() {
  const activeSet = new Set(state.chain);
  const outgoing = {};
  (state.canvasConnections || []).forEach((edge) => {
    if (!Array.isArray(edge) || edge.length !== 2) {
      return;
    }
    const src = String(edge[0]);
    const dst = String(edge[1]);
    if (src !== GUITAR_NODE_ID && !activeSet.has(src)) {
      return;
    }
    if (dst !== AMP_NODE_ID && !activeSet.has(dst)) {
      return;
    }
    outgoing[src] = dst;
  });

  if (!outgoing[GUITAR_NODE_ID]) {
    return [];
  }

  const chain = [];
  const seen = new Set([GUITAR_NODE_ID]);
  let cursor = outgoing[GUITAR_NODE_ID];
  while (cursor && !seen.has(cursor)) {
    if (cursor === AMP_NODE_ID) {
      return sanitizeChain(chain);
    }
    if (!activeSet.has(cursor)) {
      return [];
    }
    chain.push(cursor);
    seen.add(cursor);
    cursor = outgoing[cursor];
  }
  return [];
}

function computeReachableChainFromGuitar() {
  const activeSet = new Set(state.chain);
  const outgoing = {};
  (state.canvasConnections || []).forEach((edge) => {
    if (!Array.isArray(edge) || edge.length !== 2) {
      return;
    }
    const src = String(edge[0]);
    const dst = String(edge[1]);
    if (src !== GUITAR_NODE_ID && !activeSet.has(src)) {
      return;
    }
    if (dst !== AMP_NODE_ID && !activeSet.has(dst)) {
      return;
    }
    outgoing[src] = dst;
  });

  if (!outgoing[GUITAR_NODE_ID]) {
    return [];
  }

  const chain = [];
  const seen = new Set([GUITAR_NODE_ID]);
  let cursor = outgoing[GUITAR_NODE_ID];

  while (cursor && !seen.has(cursor)) {
    if (cursor === AMP_NODE_ID) {
      break;
    }
    if (!activeSet.has(cursor)) {
      break;
    }
    chain.push(cursor);
    seen.add(cursor);
    cursor = outgoing[cursor];
  }

  return sanitizeChain(chain);
}

function introducesCycle(connections) {
  const outgoing = {};
  connections.forEach(([src, dst]) => {
    if (src === GUITAR_NODE_ID || dst === AMP_NODE_ID) {
      return;
    }
    outgoing[src] = dst;
  });

  for (const start of Object.keys(outgoing)) {
    const seen = new Set();
    let cursor = start;
    while (outgoing[cursor]) {
      if (seen.has(cursor)) {
        return true;
      }
      seen.add(cursor);
      cursor = outgoing[cursor];
    }
  }
  return false;
}

function nextConnectionsForLink(src, dst) {
  if (!src || !dst || src === dst || dst === GUITAR_NODE_ID) {
    return null;
  }
  const activeSet = new Set(state.chain);
  if (src !== GUITAR_NODE_ID && !activeSet.has(src)) {
    return null;
  }
  if (dst !== AMP_NODE_ID && !activeSet.has(dst)) {
    return null;
  }

  let candidate = (state.canvasConnections || [])
    .filter((edge) => Array.isArray(edge) && edge.length === 2)
    .map((edge) => [String(edge[0]), String(edge[1])]);

  candidate = candidate.filter(([s]) => s !== src);
  if (dst !== AMP_NODE_ID) {
    candidate = candidate.filter(([, d]) => d !== dst);
  } else {
    candidate = candidate.filter(([, d]) => d !== AMP_NODE_ID);
  }
  candidate.push([src, dst]);

  if (introducesCycle(candidate)) {
    return null;
  }
  return candidate;
}

function anchorConnectionsToEndpoints(connections) {
  const activeChain = sanitizeChain(state.chain);
  if (!activeChain.length) {
    return [];
  }

  const activeSet = new Set(activeChain);
  let clean = (connections || [])
    .filter((edge) => Array.isArray(edge) && edge.length === 2)
    .map((edge) => [String(edge[0]), String(edge[1])])
    .filter(([src, dst]) => (src === GUITAR_NODE_ID || activeSet.has(src)) && (dst === AMP_NODE_ID || activeSet.has(dst)));

  const incoming = {};
  const outgoing = {};
  clean.forEach(([src, dst]) => {
    outgoing[src] = dst;
    incoming[dst] = src;
  });

  let start = outgoing[GUITAR_NODE_ID];
  if (!start || !activeSet.has(start)) {
    const heads = activeChain.filter((pedalId) => !incoming[pedalId]);
    start = heads[0] || activeChain[0];
  }

  clean = clean.filter(([src, dst]) => src !== GUITAR_NODE_ID && dst !== start);
  clean.push([GUITAR_NODE_ID, start]);

  const outgoingAfter = {};
  clean.forEach(([src, dst]) => {
    outgoingAfter[src] = dst;
  });

  const seen = new Set([GUITAR_NODE_ID]);
  let cursor = start;
  let tail = start;
  while (cursor && !seen.has(cursor)) {
    seen.add(cursor);
    tail = cursor;
    const next = outgoingAfter[cursor];
    if (!next || next === AMP_NODE_ID || !activeSet.has(next)) {
      break;
    }
    cursor = next;
  }

  clean = clean.filter(([src, dst]) => dst !== AMP_NODE_ID && src !== tail);
  clean.push([tail, AMP_NODE_ID]);

  if (introducesCycle(clean)) {
    return connections || [];
  }
  return clean;
}

function onCanvasConnectionCreated(src, dst) {
  let candidate = nextConnectionsForLink(src, dst);
  if (!candidate) {
    showToast("Cable loop blocked. Try a different target.");
    return;
  }
  candidate = anchorConnectionsToEndpoints(candidate);

  snapshotConnections();
  state.canvasConnections = candidate;
  runtime.selectedEdgeIndex = -1;
  runtime.selectedNodeId = "";
  renderAll();
}

function setActiveTab(tabKey) {
  const safe = ["pedals", "builder", "rig", "theory", "feedback"].includes(tabKey)
    ? tabKey
    : "pedals";

  const paneMap = {
    pedals: elements.tabPedals,
    builder: elements.tabBuilder,
    rig: elements.tabRig,
    theory: elements.tabTheory,
    feedback: elements.tabFeedback,
  };

  elements.tabButtons.forEach((button) => {
    const active = button.dataset.tabTarget === safe;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", active ? "true" : "false");
  });

  Object.entries(paneMap).forEach(([key, pane]) => {
    if (!pane) {
      return;
    }
    const active = key === safe;
    pane.classList.toggle("active", active);
    pane.hidden = !active;
  });

  if (safe === "builder") {
    const refreshBuilder = () => {
      ensureCanvasState();
      if (needsBoardAutoLayout()) {
        cleanUpLayout();
      }
      renderAll();
    };

    if (!runtime.boardInitialized) {
      bootstrapBoardLayout();
      runtime.boardInitialized = true;
      persistState();
    }
    requestAnimationFrame(() => requestAnimationFrame(refreshBuilder));
  }
}

function renderAll() {
  state.chain = sanitizeChain(state.chain);
  ensureCanvasState();
  state.connectedChain = computeConnectedChain();
  const effectiveSignalChain = state.connectedChain.length ? state.connectedChain : state.chain;

  const recommendation = buildRecommendation(
    state.genre,
    effectiveSignalChain,
    state.guitarType,
    state.ampModel,
    state.guitarProfile,
  );

  runtime.lastRecommendation = recommendation;

  renderPedalBank(recommendation);
  renderActiveChain(recommendation);
  renderBoard(recommendation);
  renderPedalsTab(recommendation);
  renderRigSetupTab(recommendation);
  renderTheoryTab(recommendation);
  renderFeedbackTab();

  const match = calculateChainScore(effectiveSignalChain, recommendation.optimizedChain);
  elements.chainScore.textContent = `Tone Match: ${match}%`;
  const connectedText = state.connectedChain.length
    ? state.connectedChain.map((id) => PEDAL_LIBRARY[id].model).join(" -> ")
    : "(none)";
  const activeText = state.chain.length ? state.chain.map((id) => PEDAL_LIBRARY[id].model).join(", ") : "(none)";
  elements.chainSummary.textContent = `Connected chain: ${connectedText} | Active pedals: ${activeText}`;
}

function renderPedalSelector() {
  elements.pedalSelector.innerHTML = BANK_ORDER.map((pedalId) => {
    const active = pedalId === state.pedalReference;
    return `
      <button type="button" class="pedal-selector-item ${active ? "active" : ""}" data-pedal-id="${pedalId}">
        ${PEDAL_LIBRARY[pedalId].model}
      </button>
    `;
  }).join("");
}

function renderPedalBank(recommendation) {
  elements.pedalBank.innerHTML = BANK_ORDER.map((pedalId) => {
    const inChain = state.chain.includes(pedalId);
    return renderPedalListItem({
      pedalId,
      origin: "bank",
      index: -1,
      draggable: !inChain,
      disabled: inChain,
      inChain,
      settings: recommendation?.pedals?.[pedalId] || {},
    });
  }).join("");
}

function renderActiveChain(recommendation) {
  if (!state.chain.length) {
    elements.activeChain.innerHTML = `<p class="active-chain-hint">No pedals placed yet. Drag from Bank to Canvas.</p>`;
    return;
  }

  const rows = state.chain
    .map(
      (pedalId, index) => `
        <div class="chain-slot">
          ${renderPedalListItem({
            pedalId,
            origin: "chain",
            index,
            draggable: false,
            disabled: false,
            inChain: false,
            connected: state.connectedChain.includes(pedalId),
            settings: recommendation?.pedals?.[pedalId] || {},
            removable: true,
          })}
        </div>
      `,
    )
    .join("");

  elements.activeChain.innerHTML = `
    ${rows}
    <p class="active-chain-hint">Canvas cables define the live signal path.</p>
  `;
}

function renderPedalListItem({
  pedalId,
  origin,
  index = -1,
  draggable = false,
  disabled = false,
  inChain = false,
  connected = false,
  settings = null,
  removable = false,
}) {
  const pedal = PEDAL_LIBRARY[pedalId];
  if (!pedal) {
    return "";
  }

  const settingsLine = briefSettingsLine(pedalId, settings || {});
  const chainState = origin === "chain" ? (connected ? "Connected" : "Not Wired") : (inChain ? "Active" : "Bank");
  return `
    <article
      class="pedal-list-item ${origin === "chain" ? "chain" : ""} ${disabled ? "disabled" : ""} ${inChain ? "in-chain" : ""} ${connected ? "connected" : ""}"
      data-origin="${origin}"
      data-index="${index}"
      data-pedal-id="${pedalId}"
      draggable="${draggable ? "true" : "false"}"
      aria-label="${pedal.model} pedal"
    >
      <div class="list-chip">${pedal.brand}</div>
      <div class="list-main">
        <div class="list-model">${pedal.model}</div>
        <div class="list-sub">${settingsLine} • ${chainState}</div>
      </div>
      <div class="list-actions">
        ${removable ? `<button class="remove-btn" data-remove-pedal="${pedalId}">Remove</button>` : `<span class="list-hint">${inChain ? "Active" : "Bank"}</span>`}
      </div>
    </article>
  `;
}

function renderBoard(recommendation) {
  if (!elements.boardCanvas || !elements.boardNodes) {
    return;
  }

  const amp = ampRect();
  const guitar = guitarRect();
  const linkSource = runtime.linkStart || "";
  const inputClassFor = (targetId) => {
    if (!linkSource) {
      return "";
    }
    return nextConnectionsForLink(linkSource, targetId) ? " link-valid" : " link-invalid";
  };

  const guitarProfile = recommendation?.guitar?.profileKey || state.guitarProfile;
  const guitarImage =
    guitarProfile === "taylor_acoustic"
      ? "assets/guitars/taylor_cutout_trim.png"
      : guitarProfile === "electric_4_knob_toggle"
        ? "assets/guitars/les_paul_cutout_trim.png"
        : "assets/guitars/strat_cutout_trim.png";

  const reachable = computeReachableChainFromGuitar();
  const pedalNodes = state.chain
    .map((pedalId) => {
      const pos = state.canvasPositions[pedalId] || [16, 16];
      const selected = runtime.selectedNodeId === pedalId;
      const connected = state.connectedChain.includes(pedalId);
      const statusLabel = connected ? "Connected" : (reachable.includes(pedalId) ? "Path Break" : "Unwired");
      return `
        <article class="board-pedal pedal-item ${selected ? "selected" : ""}" data-pedal-id="${pedalId}" style="left:${pos[0]}px;top:${pos[1]}px;">
          <button class="pedal-remove" type="button" data-remove-pedal="${pedalId}" title="Remove pedal">x</button>
          <button class="pedal-disconnect pedal-disconnect-out" type="button" data-pedal-id="${pedalId}" data-disconnect="output" title="Disconnect output">~</button>
          <button class="pedal-disconnect pedal-disconnect-in" type="button" data-pedal-id="${pedalId}" data-disconnect="input" title="Disconnect input">~</button>
          <span class="node-status ${connected ? "ok" : "warn"}">${statusLabel}</span>
          <div class="jack output" data-node-id="${pedalId}" title="Output"></div>
          <div class="jack input${inputClassFor(pedalId)}" data-node-id="${pedalId}" title="Input"></div>
          <div class="pedal-frame">
            ${renderPedalFace(pedalId, PEDAL_LIBRARY[pedalId], recommendation?.pedals?.[pedalId] || {})}
          </div>
        </article>
      `;
    })
    .join("");

  const ampBrand = ampBrandFromKey(recommendation?.ampModelKey);
  const ampSettings = recommendation?.amp || {};
  const ampLabel = recommendation?.ampLabel || ampSettings.modelLabel || "AMP";

  elements.boardNodes.innerHTML = `
    <article class="board-guitar ${runtime.selectedNodeId === GUITAR_NODE_ID ? "selected" : ""}" data-node-id="${GUITAR_NODE_ID}" style="left:${guitar.x}px;top:${guitar.y}px;width:${guitar.width}px;height:${guitar.height}px;">
      <h4>Guitar</h4>
      <img src="${guitarImage}" alt="Guitar" class="guitar-photo" />
      <div class="jack output" data-node-id="${GUITAR_NODE_ID}" title="Guitar Output"></div>
    </article>

    <article class="board-amp amp-rig amp-brand-${ampBrand} ${runtime.selectedNodeId === AMP_NODE_ID ? "selected" : ""}" data-node-id="${AMP_NODE_ID}" style="left:${amp.x}px;top:${amp.y}px;width:${amp.width}px;height:${amp.height}px;">
      <div class="amp-head">
        <div class="amp-head-top">
          <span class="amp-logo">${ampLabel}</span>
          <span class="amp-voice">${ampSettings.voicing || "Voice"}</span>
        </div>
        <div class="amp-control-row">
          ${[
            ["Gain", ampSettings.gain],
            ["Bass", ampSettings.bass],
            ["Mid", ampSettings.mid],
            ["Treble", ampSettings.treble],
            ["Presence", ampSettings.presence],
            ["Master", ampSettings.master],
          ]
            .map(
              ([label, value]) => `
                <div class="amp-control">
                  ${renderKnob(typeof value === "number" ? value : 50)}
                  <span>${label}</span>
                </div>
              `,
            )
            .join("")}
        </div>
      </div>
      <div class="amp-cabinet"><div class="amp-grill-cloth"></div></div>
      <div class="jack input${inputClassFor(AMP_NODE_ID)}" data-node-id="${AMP_NODE_ID}" title="Amp Input"></div>
    </article>

    ${pedalNodes}
  `;

  renderBoardCables();
}

function renderBoardCables() {
  if (!elements.boardCableLayer) {
    return;
  }

  const { width, height } = boardBounds();
  elements.boardCableLayer.setAttribute("viewBox", `0 0 ${width} ${height}`);
  elements.boardCableLayer.setAttribute("width", `${width}`);
  elements.boardCableLayer.setAttribute("height", `${height}`);

  const segments = [];
  (state.canvasConnections || []).forEach(([src, dst], edgeIndex) => {
    const start = src === GUITAR_NODE_ID ? guitarOutputPos() : pedalOutputPos(src);
    const end = dst === AMP_NODE_ID ? ampInputPos() : pedalInputPos(dst);
    const points = buildConnectionPath(start, end, src, dst);
    if (points.length >= 2) {
      segments.push(`
        <polyline
          points="${points.map((p) => `${p.x},${p.y}`).join(" ")}"
          class="cable-line ${runtime.selectedEdgeIndex === edgeIndex ? "selected" : ""}"
          data-edge-index="${edgeIndex}"
        />
      `);
    }
  });

  if (runtime.linkStart && runtime.linkPreview) {
    const start = runtime.linkStart === GUITAR_NODE_ID ? guitarOutputPos() : pedalOutputPos(runtime.linkStart);
    const end = runtime.linkPreview;
    const preview = [
      start,
      { x: start.x - 16, y: start.y },
      { x: end.x, y: start.y },
      end,
    ];
    segments.push(
      `<polyline points="${preview.map((p) => `${p.x},${p.y}`).join(" ")}" class="cable-line preview" />`,
    );
  }

  elements.boardCableLayer.innerHTML = segments.join("");
}

function snapshotConnections() {
  runtime.connectionHistory.push(deepClone(state.canvasConnections || []));
  if (runtime.connectionHistory.length > 40) {
    runtime.connectionHistory.shift();
  }
}

function undoConnectionMutation() {
  if (!runtime.connectionHistory.length) {
    showToast("No cable changes to undo.");
    return;
  }
  state.canvasConnections = runtime.connectionHistory.pop();
  runtime.selectedEdgeIndex = -1;
  renderAll();
  persistState();
  showToast("Undid last cable edit.");
}

function deleteSelectedConnection() {
  if (runtime.selectedEdgeIndex < 0 || runtime.selectedEdgeIndex >= state.canvasConnections.length) {
    return false;
  }
  snapshotConnections();
  state.canvasConnections.splice(runtime.selectedEdgeIndex, 1);
  runtime.selectedEdgeIndex = -1;
  renderAll();
  persistState();
  showToast("Cable removed.");
  return true;
}

function connectionObstacles(sourceNode = null, targetNode = null) {
  const obstacles = [];

  const addNodeObstacle = (nodeRect, sideGap = null, pad = 8) => {
    const expanded = expandRect(nodeRect, pad);
    const gap = clamp(20, 12, Math.max(12, Math.round(expanded.width * 0.28)));
    if (sideGap === "left") {
      obstacles.push({
        x: expanded.x + gap,
        y: expanded.y,
        width: Math.max(1, expanded.width - gap),
        height: expanded.height,
      });
      return;
    }
    if (sideGap === "right") {
      obstacles.push({
        x: expanded.x,
        y: expanded.y,
        width: Math.max(1, expanded.width - gap),
        height: expanded.height,
      });
      return;
    }
    obstacles.push(expanded);
  };

  addNodeObstacle(guitarRect(), sourceNode === GUITAR_NODE_ID || targetNode === GUITAR_NODE_ID ? "left" : null, 8);
  addNodeObstacle(ampRect(), sourceNode === AMP_NODE_ID || targetNode === AMP_NODE_ID ? "right" : null, 8);

  state.chain.forEach((pedalId) => {
    const base = pedalRect(pedalId);
    if (pedalId === sourceNode) {
      const leftSafe = Math.round(base.width * 0.32);
      obstacles.push({
        x: base.x + leftSafe,
        y: base.y + 1,
        width: Math.max(1, base.width - leftSafe - 1),
        height: Math.max(1, base.height - 2),
      });
      return;
    }
    if (pedalId === targetNode) {
      const rightSafe = Math.round(base.width * 0.32);
      obstacles.push({
        x: base.x + 1,
        y: base.y + 1,
        width: Math.max(1, base.width - rightSafe - 1),
        height: Math.max(1, base.height - 2),
      });
      return;
    }
    obstacles.push(expandRect(base, PEDAL_ROUTE_PADDING));
  });

  return obstacles;
}

function segmentIntersectsRect(p1, p2, rect) {
  if (p1.x === p2.x) {
    const x = p1.x;
    const y1 = Math.min(p1.y, p2.y);
    const y2 = Math.max(p1.y, p2.y);
    return x >= rect.x && x <= rect.x + rect.width && y1 <= rect.y + rect.height && y2 >= rect.y;
  }
  if (p1.y === p2.y) {
    const y = p1.y;
    const x1 = Math.min(p1.x, p2.x);
    const x2 = Math.max(p1.x, p2.x);
    return y >= rect.y && y <= rect.y + rect.height && x1 <= rect.x + rect.width && x2 >= rect.x;
  }
  return false;
}

function polylineHitsObstacles(points, obstacles) {
  for (let i = 0; i < points.length - 1; i += 1) {
    const p1 = points[i];
    const p2 = points[i + 1];
    for (const rect of obstacles) {
      if (segmentIntersectsRect(p1, p2, rect)) {
        return true;
      }
    }
  }
  return false;
}

function routeGridPath(startStub, endStub, obstacles, minX, maxX, minY, maxY) {
  const step = 6;
  const snap = (value, lo, hi) => clamp(Math.round(value / step) * step, lo, hi);

  const isBlocked = (x, y) => obstacles.some((rect) => pointInRect({ x, y }, rect));

  const nearestFree = (x, y) => {
    if (!isBlocked(x, y)) {
      return { x, y };
    }
    const seen = new Set([`${x}:${y}`]);
    const queue = [{ x, y }];
    while (queue.length) {
      const curr = queue.shift();
      const neighbors = [
        { x: clamp(curr.x + step, minX, maxX), y: curr.y },
        { x: clamp(curr.x - step, minX, maxX), y: curr.y },
        { x: curr.x, y: clamp(curr.y + step, minY, maxY) },
        { x: curr.x, y: clamp(curr.y - step, minY, maxY) },
      ];
      for (const next of neighbors) {
        const key = `${next.x}:${next.y}`;
        if (seen.has(key)) {
          continue;
        }
        seen.add(key);
        if (!isBlocked(next.x, next.y)) {
          return next;
        }
        queue.push(next);
      }
    }
    return { x, y };
  };

  const start = nearestFree(snap(startStub.x, minX, maxX), snap(startStub.y, minY, maxY));
  const goal = nearestFree(snap(endStub.x, minX, maxX), snap(endStub.y, minY, maxY));

  const heuristic = (node) => Math.abs(node.x - goal.x) + Math.abs(node.y - goal.y);
  const open = [{ node: start, g: 0, f: heuristic(start) }];
  const cameFrom = new Map();
  const gScore = new Map([[`${start.x}:${start.y}`, 0]]);
  const closed = new Set();

  while (open.length) {
    open.sort((a, b) => a.f - b.f || a.g - b.g);
    const current = open.shift();
    const ck = `${current.node.x}:${current.node.y}`;
    if (closed.has(ck)) {
      continue;
    }
    if (current.node.x === goal.x && current.node.y === goal.y) {
      const out = [current.node];
      let key = ck;
      while (cameFrom.has(key)) {
        const prev = cameFrom.get(key);
        out.push(prev);
        key = `${prev.x}:${prev.y}`;
      }
      out.reverse();
      return out;
    }
    closed.add(ck);

    const neighbors = [
      { x: clamp(current.node.x + step, minX, maxX), y: current.node.y },
      { x: clamp(current.node.x - step, minX, maxX), y: current.node.y },
      { x: current.node.x, y: clamp(current.node.y + step, minY, maxY) },
      { x: current.node.x, y: clamp(current.node.y - step, minY, maxY) },
    ];

    neighbors.forEach((neighbor) => {
      const nk = `${neighbor.x}:${neighbor.y}`;
      if (closed.has(nk) || isBlocked(neighbor.x, neighbor.y)) {
        return;
      }
      const tentative = current.g + step;
      const best = gScore.get(nk);
      if (best == null || tentative < best) {
        cameFrom.set(nk, current.node);
        gScore.set(nk, tentative);
        open.push({ node: neighbor, g: tentative, f: tentative + heuristic(neighbor) });
      }
    });
  }

  return [];
}

function buildConnectionPath(start, end, sourceNode = null, targetNode = null) {
  const stub = 14;
  const startStub = { x: start.x - stub, y: start.y };
  const endStub = { x: end.x + stub, y: end.y };
  const obstacles = connectionObstacles(sourceNode, targetNode);

  const minX = 8;
  const maxX = Math.max(minX, boardBounds().width - 8);
  const minY = 8;
  const maxY = Math.max(minY, boardBounds().height - 8);

  const dedupePoints = (points) => {
    const out = [];
    points.forEach((point) => {
      if (!out.length || out[out.length - 1].x !== point.x || out[out.length - 1].y !== point.y) {
        out.push({ x: Math.round(point.x), y: Math.round(point.y) });
      }
    });
    return out;
  };

  const pathLength = (points) => {
    let total = 0;
    for (let i = 0; i < points.length - 1; i += 1) {
      total += Math.abs(points[i + 1].x - points[i].x) + Math.abs(points[i + 1].y - points[i].y);
    }
    return total;
  };

  const candidates = [
    [start, startStub, { x: endStub.x, y: startStub.y }, endStub, end],
  ];

  const yCandidates = new Set([
    clamp(startStub.y, minY, maxY),
    clamp(endStub.y, minY, maxY),
  ]);

  if (obstacles.length) {
    const top = Math.min(...obstacles.map((rect) => rect.y));
    const bottom = Math.max(...obstacles.map((rect) => rect.y + rect.height));
    yCandidates.add(clamp(top - 18, minY, maxY));
    yCandidates.add(clamp(bottom + 18, minY, maxY));
    obstacles.forEach((rect) => {
      yCandidates.add(clamp(rect.y - 14, minY, maxY));
      yCandidates.add(clamp(rect.y + rect.height + 14, minY, maxY));
    });
  } else {
    [
      startStub.y - 32,
      startStub.y + 32,
      endStub.y - 32,
      endStub.y + 32,
    ].forEach((y) => yCandidates.add(clamp(y, minY, maxY)));
  }

  Array.from(yCandidates)
    .sort((a, b) => a - b)
    .forEach((y) => {
      candidates.push([
        start,
        startStub,
        { x: startStub.x, y },
        { x: endStub.x, y },
        endStub,
        end,
      ]);
    });

  const xCandidates = new Set([
    clamp(Math.min(startStub.x, endStub.x) - 20, minX, maxX),
    clamp(Math.max(startStub.x, endStub.x) + 20, minX, maxX),
  ]);
  obstacles.forEach((rect) => {
    xCandidates.add(clamp(rect.x - 16, minX, maxX));
    xCandidates.add(clamp(rect.x + rect.width + 16, minX, maxX));
  });

  Array.from(xCandidates)
    .sort((a, b) => a - b)
    .forEach((x) => {
      candidates.push([
        start,
        startStub,
        { x, y: startStub.y },
        { x, y: endStub.y },
        endStub,
        end,
      ]);
    });

  const valid = [];
  candidates.forEach((candidate) => {
    const points = dedupePoints(candidate);
    if (points.length < 2) {
      return;
    }
    if (!polylineHitsObstacles(points, obstacles)) {
      valid.push({ len: pathLength(points), points });
    }
  });

  const gridPath = routeGridPath(startStub, endStub, obstacles, minX, maxX, minY, maxY);
  if (gridPath.length) {
    const routed = dedupePoints([start, ...gridPath, end]);
    if (!polylineHitsObstacles(routed, obstacles)) {
      valid.push({ len: pathLength(routed), points: routed });
    }
  }

  if (valid.length) {
    valid.sort((a, b) => a.len - b.len);
    return valid[0].points;
  }

  return dedupePoints([start, startStub, { x: endStub.x, y: startStub.y }, endStub, end]);
}

function renderPedalsTab(recommendation) {
  renderPedalSelector();
  const pedalId = state.pedalReference || BANK_ORDER[0];
  const settings = recommendation?.pedals?.[pedalId] || {};
  const pedal = PEDAL_LIBRARY[pedalId];
  const pedalImagePath = `assets/pedals/${pedalId}.png`;

  elements.pedalShowcase.innerHTML = pedal
    ? `
      <div class="pedal-showcase-inner">
        <div class="pedal-image-wrap">
          <img src="${pedalImagePath}" alt="${pedal.model} reference image" class="pedal-ref-image" onerror="this.style.display='none'" />
        </div>
      </div>
    `
    : "";

  const info = PEDAL_REFERENCE[pedalId] || {
    name: pedal?.model || pedalId,
    summary: "No reference loaded.",
    controls: [],
    configure: [],
    possibilities: [],
    placement: [],
  };

  const lines = [info.name, "", "What It Does", `- ${info.summary}`];

  if (info.controls?.length) {
    lines.push("", "Controls");
    info.controls.forEach((entry) => lines.push(`- ${entry}`));
  }
  if (info.configure?.length) {
    lines.push("", "How To Configure");
    info.configure.forEach((entry) => lines.push(`- ${entry}`));
  }
  if (info.possibilities?.length) {
    lines.push("", "Possibilities");
    info.possibilities.forEach((entry) => lines.push(`- ${entry}`));
  }
  if (info.placement?.length) {
    lines.push("", "Placement Options");
    info.placement.forEach((entry) => lines.push(`- ${entry}`));
  }
  if (info.advanced?.length) {
    lines.push("", "Advanced Workflow");
    info.advanced.forEach((entry) => lines.push(`- ${entry}`));
  }

  lines.push("", "Current Suggested Settings");
  const settingBlock = formatPedalBlock(pedalId, settings).split("\n");
  if (settingBlock.length > 1) {
    settingBlock.slice(1).forEach((row) => lines.push(row));
  } else {
    lines.push("- Add this pedal to your connected chain to get active values.");
  }

  if (state.connectedChain.includes(pedalId)) {
    lines.push(
      "",
      `Connected Position: ${state.connectedChain.indexOf(pedalId) + 1} / ${state.connectedChain.length} in active signal path.`,
    );
  } else {
    lines.push("", "Connected Position: Not currently in the active guitar-to-amp path.");
  }

  elements.pedalDetails.textContent = lines.join("\n");
}

function briefSettingsLine(pedalId, settings = {}) {
  if (!settings || typeof settings !== "object") {
    return "Drag to builder canvas";
  }
  if (pedalId === "eq10" || pedalId === "ge7") {
    const mode = settings.mode || "Contour";
    return `${mode} EQ`;
  }
  if (pedalId === "rc30") {
    const rhythm = settings.rhythmType || "Rhythm";
    return `Looper ${rhythm}`;
  }

  const preferred = ["drive", "gain", "dist", "tone", "level", "effectLevel", "depth", "rate", "dTime"];
  const first = preferred.find((key) => typeof settings[key] === "number");
  if (first) {
    return `${capitalize(first)} ${quickKnob(settings[first])}`;
  }
  return "Drag to builder canvas";
}

function renderRigSetupTab(recommendation) {
  const connected = state.connectedChain;
  const reachable = computeReachableChainFromGuitar();
  const displayChain = connected.length ? connected : (reachable.length ? reachable : state.chain);

  if (displayChain.length) {
    elements.rigPedalEmpty.hidden = true;
    elements.rigPedalCards.innerHTML = displayChain
      .map((pedalId) => {
        const settings = recommendation.pedals[pedalId] || {};
        return `
          <section class="rig-pedal-card">${renderSettingsCard(pedalId, settings)}</section>
        `;
      })
      .join("");
  } else {
    elements.rigPedalEmpty.hidden = false;
    elements.rigPedalCards.innerHTML = "";
  }

  if (!connected.length && displayChain.length) {
    elements.rigPedalEmpty.hidden = false;
    elements.rigPedalEmpty.textContent =
      "Signal is not fully wired to the amp yet. Showing placed/reachable pedals with current recommendations.";
  } else {
    elements.rigPedalEmpty.textContent =
      "No connected signal chain yet. Add pedals and cable them from guitar to amp.";
  }

  const guitar = recommendation.guitar;
  const guitarLines = [];
  if (guitar) {
    guitarLines.push(guitar.label);
    Object.entries(guitar.settings || {}).forEach(([key, value]) => {
      if (key === "note") {
        return;
      }
      guitarLines.push(`- ${key}: ${value}`);
    });
    if (guitar.volumeAdvice) {
      guitarLines.push(`- Volume: ${guitar.volumeAdvice}`);
    }
  } else {
    guitarLines.push("No guitar settings.");
  }
  elements.rigGuitarPreview.textContent = guitarLines.join("\n");

  const amp = recommendation.amp || {};
  const ampLines = [
    `${recommendation.ampLabel || amp.modelLabel || "Amp"} (${amp.voicing || "Custom"})`,
    `Gain: ${quickKnob(amp.gain)}`,
    `Bass: ${quickKnob(amp.bass)}`,
    `Mid: ${quickKnob(amp.mid)}`,
    `Treble: ${quickKnob(amp.treble)}`,
    `Presence: ${quickKnob(amp.presence)}`,
    `Master: ${quickKnob(amp.master)}`,
  ];
  elements.rigAmpPreview.textContent = ampLines.join("\n");

  elements.guitarSettingsOutput.innerHTML = guitar
    ? renderGuitarSettingsCard(guitar)
    : `<p class="empty-setting">No guitar settings available.</p>`;
  elements.ampSettingsOutput.innerHTML = renderAmpSettingsCard(amp);
  elements.guidanceList.innerHTML = `<ul>${recommendation.notes.map((note) => `<li>${note}</li>`).join("")}</ul>`;

  renderRigSummary(recommendation);
}

function renderRigSummary(recommendation) {
  const amp = recommendation.amp || {};
  const connected = state.connectedChain;
  const reachable = computeReachableChainFromGuitar();
  const activeSignal = connected.length ? connected : (reachable.length ? reachable : state.chain);
  const unpatched = state.chain.filter((pedalId) => !activeSignal.includes(pedalId));
  const styleChords = extractConcertChordsForGenre(state.genre);
  const bestKey = determineBestNashvilleKey(styleChords);
  const chainLine = connected.length
    ? `Guitar -> ${activeSignal.map((id) => PEDAL_LIBRARY[id].model).join(" -> ")} -> AMP`
    : activeSignal.length
      ? `Guitar -> ${activeSignal.map((id) => PEDAL_LIBRARY[id].model).join(" -> ")} (continue wiring to AMP)`
      : "Guitar -> (none) -> AMP";
  const bullets = [
    `Style: ${recommendation.label}`,
    `Guitar: ${state.guitarType === "acoustic" ? "Acoustic" : "Electric"} | Profile: ${recommendation.guitar?.label || "Default"}`,
    `Amp: ${recommendation.ampLabel} (${amp.voicing || "Custom"})`,
    `Amp Dial: Gain ${quickKnob(amp.gain)}, Bass ${quickKnob(amp.bass)}, Mid ${quickKnob(amp.mid)}, Treble ${quickKnob(amp.treble)}, Presence ${quickKnob(amp.presence)}, Master ${quickKnob(amp.master)}`,
    `Signal Chain: ${chainLine}`,
    `Suggested Key Center: ${bestKey}`,
    ...activeSignal.map((pedalId) => `${PEDAL_LIBRARY[pedalId].model} active in chain`),
  ];
  if (unpatched.length) {
    bullets.push(`Not currently chained to amp: ${unpatched.map((id) => PEDAL_LIBRARY[id].model).join(", ")}`);
  }

  elements.summaryOutput.innerHTML = `<ul>${bullets.map((line) => `<li>${line}</li>`).join("")}</ul>`;
}

function renderNashvilleTableSkeleton() {
  elements.nashvilleTableBody.innerHTML = NASHVILLE_MAJOR_CHART.map(
    ([key, degrees]) => `
      <tr data-nashville-key="${key}">
        <td>${key}</td>
        ${degrees.map((deg) => `<td>${deg}</td>`).join("")}
      </tr>
    `,
  ).join("");
}

function bindTheoryEvents() {
  elements.nashvilleTableBody.addEventListener("click", (event) => {
    const row = event.target.closest("tr[data-nashville-key]");
    if (!row) {
      return;
    }
    state.selectedTheoryKey = row.dataset.nashvilleKey;
    renderTheoryTab(runtime.lastRecommendation);
    persistState();
  });

  elements.scaleTypeSelect.addEventListener("change", () => {
    state.theoryScale = SCALE_LIBRARY[elements.scaleTypeSelect.value]
      ? elements.scaleTypeSelect.value
      : "minor_pentatonic";
    renderTheoryTab(runtime.lastRecommendation);
    persistState();
  });

  elements.cagedShapeSelect.addEventListener("change", () => {
    state.theoryShape = CAGED_SHAPES[elements.cagedShapeSelect.value]
      ? elements.cagedShapeSelect.value
      : "g";
    renderTheoryTab(runtime.lastRecommendation);
    persistState();
  });

  elements.crazyBtn.addEventListener("click", () => {
    runtime.crazyPayloadCache.set(state.genre, makeCrazyPayload(state.genre));
    renderTheoryTab(runtime.lastRecommendation);
  });

  elements.circleOfFifths.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target.closest(".fifths-node[data-key]") : null;
    if (!target) {
      return;
    }
    const nextKey = target.dataset.key;
    if (!nextKey || tableRowForKey(nextKey) < 0) {
      return;
    }
    state.selectedTheoryKey = nextKey;
    renderTheoryTab(runtime.lastRecommendation);
    persistState();
  });
}

function renderTheoryTab(recommendation) {
  const styleChords = extractConcertChordsForGenre(state.genre);
  const bestKey = determineBestNashvilleKey(styleChords);
  const selectedKey = tableRowForKey(state.selectedTheoryKey) >= 0 ? state.selectedTheoryKey : bestKey;
  state.selectedTheoryKey = selectedKey;

  const usualKeys = usualKeysForGenre(state.genre);
  const usualMajorKeys = majorUsualKeysForGenre(state.genre);

  elements.usualKeys.textContent = usualKeys.length ? `Usual Keys: ${usualKeys.join("  •  ")}` : "Usual Keys: (none)";
  elements.nashvilleHint.textContent =
    selectedKey === bestKey
      ? `Selected key: ${selectedKey} (matches suggested key)`
      : `Suggested key: ${bestKey} | Selected key: ${selectedKey}`;

  highlightNashvilleRows(selectedKey, usualMajorKeys);

  const selectedChords = nashvilleDegreesForKey(selectedKey);
  const highlight = selectedChords.length ? selectedChords : styleChords;
  renderCircleOfFifths(highlight, selectedKey);
  const sevenChordLine = selectedChords.length
    ? `${selectedKey} diatonic 7: ${selectedChords.join(" - ")}`
    : `${selectedKey} diatonic 7: (not found)`;
  const highlightedLine = highlight.length
    ? `Highlighted chord family: ${highlight.join(", ")}`
    : "Highlighted from selected Nashville key or suggested style center.";
  elements.circleHint.textContent = `${sevenChordLine} | ${highlightedLine}`;

  renderScaleChart(selectedKey, state.theoryShape, state.theoryScale);
  const scale = SCALE_LIBRARY[state.theoryScale] || SCALE_LIBRARY.minor_pentatonic;
  elements.scaleHint.textContent = `${selectedKey} ${scale.label} • ${CAGED_SHAPES[state.theoryShape].label} • ${scale.formula}`;
  elements.keyToolkit.textContent = buildKeyToolkitLines(selectedKey, state.theoryScale).join("\n");

  renderTheoryPlaybook();
  renderCrazyPayload();
}

function highlightNashvilleRows(selectedKey, usualMajorKeys) {
  const usualSet = new Set(usualMajorKeys || []);
  Array.from(elements.nashvilleTableBody.querySelectorAll("tr[data-nashville-key]")).forEach((row) => {
    const key = row.dataset.nashvilleKey;
    row.classList.toggle("selected", key === selectedKey);
    row.classList.toggle("usual", key !== selectedKey && usualSet.has(key));
  });
}

function renderCircleOfFifths(highlightChords, selectedKey = "") {
  const highlighted = new Set(
    (highlightChords || [])
      .map((token) => majorKeyForSelection(token))
      .filter(Boolean),
  );

  const size = 360;
  const center = size / 2;
  const outerRadius = 136;
  const innerRadius = 92;

  const nodes = CIRCLE_FIFTHS_MAJOR.map((major, index) => {
    const angle = (Math.PI * 2 * index) / CIRCLE_FIFTHS_MAJOR.length - Math.PI / 2;
    const x = center + Math.cos(angle) * outerRadius;
    const y = center + Math.sin(angle) * outerRadius;
    const minor = CIRCLE_FIFTHS_MINOR[index];
    const majorLabel = CIRCLE_FIFTHS_MAJOR_DISPLAY[major] || major;
    const minorLabel = CIRCLE_FIFTHS_MINOR_DISPLAY[minor] || minor;
    const active = highlighted.has(major);
    const selected = major === selectedKey;
    const family = nashvilleDegreesForKey(major);
    return `
      <g class="fifths-node ${active ? "active" : ""} ${selected ? "selected" : ""}" data-key="${major}" title="${family.join(" - ")}">
        <circle cx="${x}" cy="${y}" r="20"></circle>
        <text class="major" x="${x}" y="${y - 3}" text-anchor="middle">${majorLabel}</text>
        <text class="minor" x="${x}" y="${y + 11}" text-anchor="middle">${minorLabel}</text>
      </g>
    `;
  }).join("");

  elements.circleOfFifths.innerHTML = `
    <svg class="fifths-svg" viewBox="0 0 ${size} ${size}" role="img" aria-label="Circle of fifths">
      <circle class="outer-ring" cx="${center}" cy="${center}" r="${outerRadius + 23}"></circle>
      <circle class="inner-ring" cx="${center}" cy="${center}" r="${innerRadius - 26}"></circle>
      ${nodes}
    </svg>
  `;
}

function renderScaleChart(keyName, shapeKey, scaleKey) {
  const scale = SCALE_LIBRARY[scaleKey] || SCALE_LIBRARY.minor_pentatonic;
  const rootPc = pitchClassForKeyName(keyName);
  const rootFret = preferredRootFret(rootPc);
  const [startFret, windowSize] = cagedWindowStart(rootFret, shapeKey, scale.family);
  const endFret = startFret + windowSize;

  const stringCount = 6;
  const width = 860;
  const height = 280;
  const leftPad = 52;
  const rightPad = 24;
  const topPad = 36;
  const bottomPad = 36;
  const fretCount = endFret - startFret;
  const fretSpacing = (width - leftPad - rightPad) / Math.max(1, fretCount);
  const stringSpacing = (height - topPad - bottomPad) / (stringCount - 1);

  const intervals = scale.intervals || [];
  const circles = [];

  for (let stringIndex = 0; stringIndex < stringCount; stringIndex += 1) {
    const openPc = STANDARD_TUNING_PCS_LOW_TO_HIGH[stringIndex];
    for (let fret = startFret; fret <= endFret; fret += 1) {
      const pc = (openPc + fret) % 12;
      const interval = (pc - rootPc + 12) % 12;
      if (!intervals.includes(interval)) {
        continue;
      }
      const x = leftPad + (fret - startFret) * fretSpacing;
      const y = topPad + (stringCount - 1 - stringIndex) * stringSpacing;
      const root = interval === 0;
      circles.push({
        x,
        y,
        root,
        note: displayNoteForPitchClass(pc, keyName),
        radius: root ? 14 : 12,
      });
    }
  }

  const strings = Array.from({ length: stringCount }, (_, i) => {
    const y = topPad + i * stringSpacing;
    return `<line class="neck-string" x1="${leftPad}" y1="${y}" x2="${width - rightPad}" y2="${y}" />`;
  }).join("");

  const frets = Array.from({ length: fretCount + 1 }, (_, idx) => {
    const x = leftPad + idx * fretSpacing;
    const fretNum = startFret + idx;
    return `
      <line class="neck-fret" x1="${x}" y1="${topPad}" x2="${x}" y2="${height - bottomPad}"></line>
      <text class="neck-fret-num" x="${x}" y="${height - 10}" text-anchor="middle">${fretNum}</text>
    `;
  }).join("");

  const dots = circles
    .map(
      (item) => `
      <g class="neck-note ${item.root ? "root" : "scale"}">
        <circle cx="${item.x}" cy="${item.y}" r="${item.radius}"></circle>
        <text x="${item.x}" y="${item.y + 4}" text-anchor="middle">${item.note}</text>
      </g>
    `,
    )
    .join("");

  elements.neckChart.innerHTML = `
    <svg class="neck-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Scale chart on guitar neck">
      <rect class="neck-bg" x="${leftPad}" y="${topPad}" width="${width - leftPad - rightPad}" height="${height - topPad - bottomPad}"></rect>
      ${strings}
      ${frets}
      ${dots}
    </svg>
  `;
}

function stylePlaybookFor(genreKey) {
  const fallback = STYLE_PLAYBOOK_FALLBACK[genreKey] || STYLE_PLAYBOOK_FALLBACK.rock || {};
  const fromConfig = STYLE_PLAYBOOK[genreKey] || {};
  return deepMerge(fallback, fromConfig);
}

function bootstrapBoardLayout() {
  ensureCanvasState();

  if (needsBoardAutoLayout()) {
    cleanUpLayout();
  }

  renderBoard(runtime.lastRecommendation);
}

function needsBoardAutoLayout() {
  const chain = sanitizeChain(state.chain);
  if (!chain.length) {
    return false;
  }

  const points = chain
    .map((pedalId) => state.canvasPositions[pedalId])
    .filter((value) => Array.isArray(value) && value.length === 2)
    .map((value) => [Number(value[0]) || 0, Number(value[1]) || 0]);

  if (points.length !== chain.length) {
    return true;
  }

  const uniquePoints = new Set(points.map(([x, y]) => `${x}:${y}`));
  if (uniquePoints.size <= 1 && chain.length > 1) {
    return true;
  }

  const bounds = pedalPositionBounds();
  const tightX = bounds.maxX - bounds.minX < PEDAL_SIZE.width + 40;
  const tightY = bounds.maxY - bounds.minY < PEDAL_SIZE.height + 40;
  return tightX || tightY;
}

function renderTheoryPlaybook() {
  const genre = state.genre;
  const playbook = stylePlaybookFor(genre);
  const picks = currentStyleProgressions(genre);
  const randomSet = picks.random_set || [];
  const popularPick = picks.popular_pick || "";

  const lines = [
    "Random Progressions (refreshes when style changes):",
    ...(randomSet.length ? randomSet.slice(0, 2).map((line, idx) => `- ${idx + 1}. ${line}`) : ["- (no progression data)"]),
    "",
    "Popular Progression (top-3 list):",
    `- ${popularPick || "(no popular progression configured)"}`,
    "",
    "Capo 5 Shapes:",
    ...(playbook.capo5Shapes || []).map((line) => `- ${line}`),
    "",
    `Open Shapes: ${(playbook.openShapes || []).join(", ")}`,
    `Capo Mapping: ${playbook.capoGuide || ""}`,
    `G-Shape Pentatonic Fret: ${playbook.pentatonicFret || ""}`,
    `Solo Guide: ${playbook.soloGuide || ""}`,
  ];

  elements.stylePlaybook.textContent = lines.join("\n");
}

function currentStyleProgressions(genreKey) {
  if (runtime.styleProgressionCache.has(genreKey)) {
    return runtime.styleProgressionCache.get(genreKey);
  }
  const payload = {
    random_set: sampleStyleProgressions(genreKey, 2),
    popular_pick: samplePopularProgression(genreKey),
  };
  runtime.styleProgressionCache.set(genreKey, payload);
  return payload;
}

function sampleStyleProgressions(genreKey, count = 2) {
  const playbook = stylePlaybookFor(genreKey);
  const pool = uniqueList((playbook.progressionPool || []).filter((entry) => typeof entry === "string" && entry.trim()));
  const fallback = uniqueList((playbook.concertProgression || []).filter((entry) => typeof entry === "string" && entry.trim()));
  const source = pool.length ? pool : fallback;
  if (!source.length) {
    return [];
  }
  if (source.length <= count) {
    return source;
  }
  return shuffle([...source]).slice(0, count);
}

function samplePopularProgression(genreKey) {
  const playbook = stylePlaybookFor(genreKey);
  const top = (playbook.popularTop3 || []).filter((entry) => typeof entry === "string" && entry.trim());
  if (top.length) {
    return top[Math.floor(Math.random() * top.length)];
  }
  const fallback = (playbook.concertProgression || []).find((entry) => typeof entry === "string" && entry.trim());
  return fallback || "";
}

function renderCrazyPayload() {
  const genre = state.genre;
  const payload = currentCrazyPayload(genre);

  const left = [
    "Under-utilized Progression:",
    `- ${payload.progression || ""}`,
    "",
    "Capo 5 Shape Mapping:",
    `- ${payload.capo_shapes || ""}`,
    "",
    `Key Center Guess: ${payload.key_center || "C"}`,
  ];

  const right = [
    "Unusual But Correct Scale:",
    `- ${payload.scale_name || ""}`,
    `- Formula: ${payload.scale_formula || ""}`,
    `- Notes: ${(payload.scale_notes || []).join(", ")}`,
    "",
    payload.scale_why || "",
  ];

  elements.crazyProgression.textContent = left.join("\n");
  elements.crazyScale.textContent = right.join("\n");
}

function currentCrazyPayload(genreKey) {
  if (runtime.crazyPayloadCache.has(genreKey)) {
    return runtime.crazyPayloadCache.get(genreKey);
  }
  const payload = makeCrazyPayload(genreKey);
  runtime.crazyPayloadCache.set(genreKey, payload);
  return payload;
}

function makeCrazyPayload(genreKey) {
  const playbook = stylePlaybookFor(genreKey);
  const pool = (playbook.progressionPool || []).filter((entry) => typeof entry === "string" && entry.trim());
  const popular = (playbook.popularTop3 || []).filter((entry) => typeof entry === "string" && entry.trim());
  const underUsed = pool.filter((entry) => !popular.includes(entry));
  const candidates = underUsed.length ? underUsed : (pool.length ? pool : [samplePopularProgression(genreKey)]);
  const progression = candidates[Math.floor(Math.random() * candidates.length)] || "C - Am - F - G";

  const capoShapes = splitProgressionTokens(progression)
    .map((token) => transposeChordRootForCapo(token, 5))
    .join(" - ");

  const keyCenter = progressionKeyCenter(progression);
  const scaleKeys = CRAZY_SCALE_BY_GENRE[genreKey] || Object.keys(CRAZY_SCALE_LIBRARY);
  const scaleKey = scaleKeys[Math.floor(Math.random() * scaleKeys.length)] || "harmonic_minor";
  const scale = CRAZY_SCALE_LIBRARY[scaleKey] || CRAZY_SCALE_LIBRARY.harmonic_minor;
  const rootPc = NOTE_TO_PITCH_CLASS[keyCenter] ?? NOTE_TO_PITCH_CLASS.C;
  const scaleNotes = (scale.intervals || []).map((interval) => displayNoteForPitchClass((rootPc + interval) % 12, keyCenter));

  return {
    progression,
    capo_shapes: capoShapes,
    key_center: keyCenter,
    scale_name: scale.name,
    scale_formula: scale.formula,
    scale_notes: scaleNotes,
    scale_why: scale.why,
  };
}

function bindFeedbackEvents() {
  elements.feedbackForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitFeedback();
  });

  elements.donateBtn.addEventListener("click", handleDonate);
}

function renderFeedbackTab() {
  const donate = APP_CONFIG.donate || {};
  elements.donateDetails.textContent = [
    `PayPal: ${donate.paypal_url ? "Configured" : "Not configured"}`,
    `Venmo: ${donate.venmo_url ? "Configured" : "Not configured"}`,
    `Zelle: ${donate.zelle_handle ? "Configured" : "Not configured"}`,
  ].join("\n");

  updateFeedbackLimitInfo();
}

function feedbackLimits() {
  const limiter = APP_CONFIG.feedback?.limiter || {};
  return {
    maxPerDay: Math.max(0, Number(limiter.max_per_day) || 0),
    maxPerUserPerDay: Math.max(0, Number(limiter.max_per_user_per_day) || 0),
    maxPerUserTotal: Math.max(0, Number(limiter.max_per_user_total) || 0),
    hardLimitTotal: Math.max(0, Number(limiter.hard_limit_total) || 0),
  };
}

function feedbackDayKey() {
  const now = new Date();
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const dd = String(now.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function loadFeedbackLimiterState() {
  try {
    const raw = localStorage.getItem(FEEDBACK_LIMITER_KEY);
    if (!raw) {
      return { total: 0, daily: {}, users: {} };
    }
    const parsed = JSON.parse(raw);
    return {
      total: Number(parsed.total) || 0,
      daily: typeof parsed.daily === "object" && parsed.daily ? parsed.daily : {},
      users: typeof parsed.users === "object" && parsed.users ? parsed.users : {},
    };
  } catch {
    return { total: 0, daily: {}, users: {} };
  }
}

function persistFeedbackLimiterState() {
  localStorage.setItem(FEEDBACK_LIMITER_KEY, JSON.stringify(runtime.feedbackLimitsState));
}

function userFeedbackCounters(userId) {
  const users = runtime.feedbackLimitsState.users || (runtime.feedbackLimitsState.users = {});
  if (!users[userId]) {
    users[userId] = { total: 0, daily: {} };
  }
  if (typeof users[userId].daily !== "object" || !users[userId].daily) {
    users[userId].daily = {};
  }
  return users[userId];
}

function checkFeedbackLimit(userId) {
  const limits = feedbackLimits();
  const day = feedbackDayKey();
  const total = Number(runtime.feedbackLimitsState.total) || 0;
  const dailyTotal = Number(runtime.feedbackLimitsState.daily?.[day]) || 0;
  const userState = userFeedbackCounters(userId);
  const userTotal = Number(userState.total) || 0;
  const userDaily = Number(userState.daily?.[day]) || 0;

  if (limits.hardLimitTotal && total >= limits.hardLimitTotal) {
    return [false, "Global feedback cap reached."];
  }
  if (limits.maxPerDay && dailyTotal >= limits.maxPerDay) {
    return [false, "Daily feedback limit reached."];
  }
  if (limits.maxPerUserPerDay && userDaily >= limits.maxPerUserPerDay) {
    return [false, "You reached your daily submission limit."];
  }
  if (limits.maxPerUserTotal && userTotal >= limits.maxPerUserTotal) {
    return [false, "You reached your total submission limit."];
  }
  return [true, ""];
}

function incrementFeedbackLimit(userId) {
  const day = feedbackDayKey();
  runtime.feedbackLimitsState.total = (Number(runtime.feedbackLimitsState.total) || 0) + 1;
  runtime.feedbackLimitsState.daily = runtime.feedbackLimitsState.daily || {};
  runtime.feedbackLimitsState.daily[day] = (Number(runtime.feedbackLimitsState.daily[day]) || 0) + 1;

  const userState = userFeedbackCounters(userId);
  userState.total = (Number(userState.total) || 0) + 1;
  userState.daily[day] = (Number(userState.daily[day]) || 0) + 1;
  persistFeedbackLimiterState();
}

function updateFeedbackLimitInfo() {
  const feedbackCfg = APP_CONFIG.feedback || {};
  const webhook = String(feedbackCfg.webhook_url || "").trim();
  const enabled = Boolean(feedbackCfg.enabled) && Boolean(webhook);
  const limits = feedbackLimits();

  const day = feedbackDayKey();
  const dayTotal = Number(runtime.feedbackLimitsState.daily?.[day]) || 0;
  const userState = userFeedbackCounters(runtime.feedbackUserId);
  const userDayTotal = Number(userState.daily?.[day]) || 0;
  const userTotal = Number(userState.total) || 0;

  const remaining = (limit, used) => (limit ? Math.max(0, limit - used) : "∞");

  elements.feedbackLimitInfo.textContent = [
    `Webhook: ${webhook ? "Configured" : "Not configured"}`,
    `Feedback Enabled: ${enabled ? "Yes" : "No"}`,
    `Limits - Day Remaining: ${remaining(limits.maxPerDay, dayTotal)} | Your Day Remaining: ${remaining(limits.maxPerUserPerDay, userDayTotal)} | Your Total Remaining: ${remaining(limits.maxPerUserTotal, userTotal)}`,
  ].join("\n");
}

function setFeedbackStatus(message, success = false) {
  elements.feedbackStatus.textContent = message;
  elements.feedbackStatus.classList.toggle("success", success);
  elements.feedbackStatus.classList.toggle("error", !success);
}

async function submitFeedback() {
  const message = String(elements.feedbackMessage.value || "").trim();
  if (message.length < 8) {
    setFeedbackStatus("Please enter at least a short message before submitting.", false);
    return;
  }

  const feedbackCfg = APP_CONFIG.feedback || {};
  const webhook = String(feedbackCfg.webhook_url || "").trim();
  if (!feedbackCfg.enabled || !webhook) {
    setFeedbackStatus("Feedback webhook is not configured for this build.", false);
    return;
  }

  const [allowed, reason] = checkFeedbackLimit(runtime.feedbackUserId);
  if (!allowed) {
    setFeedbackStatus(reason, false);
    return;
  }

  const payload = {
    timestamp: new Date().toISOString(),
    user: runtime.feedbackUserId,
    rating: Number(elements.feedbackRating.value) || 0,
    type: String(elements.feedbackType.value || "general"),
    name: String(elements.feedbackName.value || "").trim(),
    email: String(elements.feedbackEmail.value || "").trim(),
    message,
    context: {
      genre: state.genre,
      guitarType: state.guitarType,
      guitarProfile: state.guitarProfile,
      ampModel: state.ampModel,
      theme: state.theme,
      connectedChain: [...state.connectedChain],
    },
  };

  const timeoutSec = Math.max(2, Number(feedbackCfg.timeout_sec) || 8);
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutSec * 1000);

  try {
    const response = await fetch(webhook, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    if (!response.ok) {
      setFeedbackStatus(`Submit failed: HTTP ${response.status}`, false);
      return;
    }

    incrementFeedbackLimit(runtime.feedbackUserId);
    elements.feedbackMessage.value = "";
    setFeedbackStatus("Feedback sent. Thank you.", true);
    updateFeedbackLimitInfo();
  } catch (error) {
    setFeedbackStatus(`Submit failed: ${error?.message || "unknown error"}`, false);
  } finally {
    window.clearTimeout(timer);
  }
}

function handleDonate() {
  const method = String(elements.donateMethod.value || "paypal");
  const donate = APP_CONFIG.donate || {};
  const targetMap = {
    paypal: String(donate.paypal_url || "").trim(),
    venmo: String(donate.venmo_url || "").trim(),
    zelle: String(donate.zelle_handle || "").trim(),
  };

  const target = targetMap[method] || "";
  if (!target) {
    setFeedbackStatus(`${capitalize(method)} is not configured yet.`, false);
    return;
  }

  if (method === "paypal" || method === "venmo") {
    window.open(target, "_blank", "noopener,noreferrer");
    setFeedbackStatus(`Opened ${capitalize(method)}.`, true);
    return;
  }

  navigator.clipboard?.writeText(target).then(
    () => setFeedbackStatus("Zelle destination copied to clipboard.", true),
    () => setFeedbackStatus("Copy failed. Please copy manually from details.", false),
  );
}

function buildFeedbackUserId() {
  const host = String(window.location.hostname || "local");
  const ua = String(window.navigator.userAgent || "ua");
  return hashString(`${host}|${ua}`).slice(0, 16);
}

function applyTheme() {
  const theme = THEMES[state.theme] || THEMES.dark;
  const [, , fontPx] = FONT_PRESET_SPECS.find(([key]) => key === state.fontPreset) || FONT_PRESET_SPECS[1];

  const root = document.documentElement;
  root.style.setProperty("--bg-main", theme.bg);
  root.style.setProperty("--text-main", theme.text);
  root.style.setProperty("--panel-border", theme.frame);
  root.style.setProperty("--bg-panel", theme.panel);
  root.style.setProperty("--tab-bg", theme.tab);
  root.style.setProperty("--tab-active-bg", theme.tabSelectedBg);
  root.style.setProperty("--tab-active-fg", theme.tabSelectedFg);
  root.style.setProperty("--group-title", theme.groupTitle);
  root.style.setProperty("--canvas-bg", theme.canvasBg);
  root.style.setProperty("--canvas-grid", theme.canvasGrid);
  root.style.setProperty("--canvas-edge", theme.canvasEdge);
  root.style.setProperty("--canvas-edge-preview", theme.canvasPreview);
  root.style.setProperty("--positive", theme.positive);
  root.style.setProperty("--root-note", theme.rootNote);
  root.style.setProperty("--scale-note", theme.scaleNote);
  root.style.setProperty("--app-font-size", `${fontPx}px`);
}

function renderNashvilleKeyData(keyName) {
  const row = NASHVILLE_MAJOR_CHART.find(([name]) => name === keyName);
  return row ? row[1] : [];
}

function tableRowForKey(keyName) {
  return NASHVILLE_MAJOR_CHART.findIndex(([name]) => name === keyName);
}

function nashvilleDegreesForKey(keyName) {
  return renderNashvilleKeyData(keyName);
}

function normalizeNoteName(note) {
  if (!note) {
    return "";
  }
  const key = String(note).trim().toUpperCase();
  if (NOTE_ALIAS_MAP[key]) {
    return NOTE_ALIAS_MAP[key];
  }
  if (key.length === 2 && key[1] === "B") {
    return `${key[0]}b`;
  }
  return key;
}

function parseChordToken(token) {
  if (typeof token !== "string") {
    return null;
  }
  const clean = token.trim();
  if (!clean) {
    return null;
  }
  const match = CHORD_ROOT_RE.exec(clean);
  if (!match) {
    return null;
  }
  const root = normalizeNoteName(`${match[1]}${match[2]}`);
  const suffix = clean.slice(match[0].length).trim().toLowerCase();

  let quality = "major";
  if (suffix.includes("dim")) {
    quality = "dim";
  } else if (suffix.startsWith("m") && !suffix.startsWith("maj")) {
    quality = "minor";
  }

  let shorthand = root;
  if (quality === "minor") {
    shorthand = `${root}m`;
  } else if (quality === "dim") {
    shorthand = `${root}dim`;
  }

  return { token: clean, root, quality, shorthand };
}

function splitProgressionTokens(progression) {
  if (typeof progression !== "string") {
    return [];
  }
  return progression.split("-").map((part) => part.trim()).filter(Boolean);
}

function transposeChordRootForCapo(chordToken, capoFret = 5) {
  if (typeof chordToken !== "string") {
    return "";
  }
  const match = CHORD_ROOT_RE.exec(chordToken.trim());
  if (!match) {
    return chordToken.trim();
  }
  const root = normalizeNoteName(`${match[1]}${match[2]}`);
  if (!(root in NOTE_TO_PITCH_CLASS)) {
    return chordToken.trim();
  }
  const suffix = chordToken.trim().slice(match[0].length);
  const targetPc = (NOTE_TO_PITCH_CLASS[root] - Number(capoFret)) % 12;
  const wrapped = (targetPc + 12) % 12;
  return `${PITCH_CLASS_CANONICAL[wrapped]}${suffix}`;
}

function extractConcertChordsForGenre(genreKey) {
  const playbook = stylePlaybookFor(genreKey);
  let progressions = playbook.popularTop3 || playbook.concertProgression || [];
  if (!progressions.length) {
    progressions = playbook.progressionPool || [];
  }
  const out = [];
  progressions.forEach((progression) => {
    splitProgressionTokens(progression).forEach((token) => out.push(token));
  });
  return uniqueList(out);
}

function determineBestNashvilleKey(chordTokens) {
  const parsed = chordTokens.map(parseChordToken).filter(Boolean);
  if (!parsed.length) {
    return "C";
  }
  let bestKey = "C";
  let bestScore = -1;
  NASHVILLE_MAJOR_CHART.forEach(([key, degrees]) => {
    const set = new Set(degrees);
    let score = 0;
    parsed.forEach((chord) => {
      if (set.has(chord.shorthand)) {
        score += 2;
      } else if (set.has(chord.root)) {
        score += 1;
      }
    });
    if (score > bestScore) {
      bestScore = score;
      bestKey = key;
    }
  });
  return bestKey;
}

function majorKeyForSelection(token) {
  const parsed = parseChordToken(token);
  if (!parsed) {
    return "";
  }
  if (parsed.quality === "minor") {
    const minorToken = `${parsed.root}m`;
    const idx = CIRCLE_FIFTHS_MINOR.indexOf(minorToken);
    if (idx >= 0) {
      return CIRCLE_FIFTHS_MAJOR[idx];
    }
  }
  return parsed.root;
}

function usualKeysForGenre(genreKey) {
  return uniqueList((USUAL_KEYS_BY_GENRE[genreKey] || USUAL_KEYS_BY_GENRE.rock || []).filter(Boolean));
}

function majorUsualKeysForGenre(genreKey) {
  return uniqueList(usualKeysForGenre(genreKey).map((key) => majorKeyForSelection(key)).filter(Boolean));
}

function pitchClassForKeyName(keyName) {
  if (!keyName) {
    return NOTE_TO_PITCH_CLASS.C;
  }
  const major = majorKeyForSelection(keyName) || parseChordToken(String(keyName))?.root || normalizeNoteName(String(keyName));
  return NOTE_TO_PITCH_CLASS[major] ?? NOTE_TO_PITCH_CLASS.C;
}

function preferredRootFret(rootPitchClass) {
  const candidates = [];
  for (let fret = 0; fret <= 24; fret += 1) {
    if ((STANDARD_TUNING_PCS_LOW_TO_HIGH[0] + fret) % 12 === rootPitchClass) {
      candidates.push(fret);
    }
  }
  for (const fret of candidates) {
    if (fret >= 4 && fret <= 10) {
      return fret;
    }
  }
  for (const fret of candidates) {
    if (fret >= 1 && fret <= 15) {
      return fret;
    }
  }
  return candidates[0] ?? 0;
}

function cagedWindowStart(rootFret, shapeKey, scaleFamily) {
  const shape = CAGED_SHAPES[shapeKey] || CAGED_SHAPES.g;
  const offsetKey = scaleFamily === "major" ? "major_start_offset" : "minor_start_offset";
  let start = Number(rootFret) + Number(shape[offsetKey] || 0);
  while (start < 0) {
    start += 12;
  }
  while (start > 11) {
    start -= 12;
  }
  const size = Math.max(4, Number(shape.window_size) || 5);
  return [start, size];
}

function displayNoteForPitchClass(pitchClass, keyName) {
  const major = majorKeyForSelection(keyName) || "C";
  const names = SHARP_KEY_SIGNATURES.has(major) ? PITCH_CLASS_SHARP : PITCH_CLASS_CANONICAL;
  return names[((Number(pitchClass) % 12) + 12) % 12];
}

function progressionKeyCenter(progression) {
  const tokens = splitProgressionTokens(progression);
  if (!tokens.length) {
    return "C";
  }
  const first = parseChordToken(tokens[0]);
  if (first?.root && first.root in NOTE_TO_PITCH_CLASS) {
    return first.root;
  }
  return determineBestNashvilleKey(tokens);
}

function buildKeyToolkitLines(keyName, scaleKey = "minor_pentatonic") {
  const row = NASHVILLE_MAJOR_CHART.find(([name]) => name === keyName) || NASHVILLE_MAJOR_CHART[0];
  const degrees = row[1] || [];
  const scale = SCALE_LIBRARY[scaleKey] || SCALE_LIBRARY.minor_pentatonic;
  if (degrees.length < 7) {
    return [
      `Key Center: ${row[0]} major`,
      `Scale: ${scale.label} (${scale.formula})`,
    ];
  }
  const [one, two, three, four, five, six] = degrees;
  return [
    `Key Center: ${row[0]} major`,
    `Scale: ${scale.label} (${scale.formula})`,
    `Relative Minor: ${six}`,
    `Diatonic Triads: ${degrees.join(", ")}`,
    `Cadence (I-IV-V): ${one} - ${four} - ${five}`,
    `Cadence (ii-V-I): ${two} - ${five} - ${one}`,
    `Pop Turnaround (vi-IV-I-V): ${six} - ${four} - ${one} - ${five}`,
    `Solo Target: use ${six} or ${row[0]} pentatonic color over these chords.`,
  ];
}

function formatPedalBlock(pedalId, settings) {
  const safe = settings || {};
  const title = PEDAL_LIBRARY[pedalId]?.model || pedalId;
  const lines = [title];

  if (pedalId === "sd1") {
    lines.push(`- drive: ${quickKnob(safe.drive ?? 50)}`);
    lines.push(`- tone: ${quickKnob(safe.tone ?? 50)}`);
    lines.push(`- level: ${quickKnob(safe.level ?? 50)}`);
    return lines.join("\n");
  }
  if (pedalId === "bd2") {
    lines.push(`- gain: ${quickKnob(safe.gain ?? 50)}`);
    lines.push(`- tone: ${quickKnob(safe.tone ?? 50)}`);
    lines.push(`- level: ${quickKnob(safe.level ?? 50)}`);
    return lines.join("\n");
  }
  if (pedalId === "ds1") {
    lines.push(`- dist: ${quickKnob(safe.dist ?? 50)}`);
    lines.push(`- tone: ${quickKnob(safe.tone ?? 50)}`);
    lines.push(`- level: ${quickKnob(safe.level ?? 50)}`);
    return lines.join("\n");
  }
  if (pedalId === "cs3") {
    ["sustain", "attack", "tone", "level"].forEach((key) => {
      lines.push(`- ${key}: ${quickKnob(safe[key] ?? 50)}`);
    });
    return lines.join("\n");
  }
  if (pedalId === "ge7" || pedalId === "eq10") {
    lines.push(`- mode: ${safe.mode || "Contour"}`);
    if (typeof safe.level === "number") {
      lines.push(`- level: ${dbValue(safe.level)}`);
    }
    if (typeof safe.volume === "number") {
      lines.push(`- output: ${dbValue(safe.volume)}`);
    }
    if (typeof safe.gain === "number") {
      lines.push(`- gain: ${dbValue(safe.gain)}`);
    }
    Object.entries(safe.bands || {}).forEach(([band, value]) => {
      lines.push(`- ${band} Hz: ${dbValue(value)}`);
    });
    return lines.join("\n");
  }
  if (pedalId === "ch1") {
    ["effectLevel", "eq", "rate", "depth"].forEach((key) => {
      lines.push(`- ${key}: ${quickKnob(safe[key] ?? 50)}`);
    });
    return lines.join("\n");
  }
  if (pedalId === "dd3") {
    lines.push(`- mode: ${safe.mode || "320 ms"}`);
    ["eLevel", "fBack", "dTime"].forEach((key) => {
      lines.push(`- ${key}: ${quickKnob(safe[key] ?? 50)}`);
    });
    return lines.join("\n");
  }
  if (pedalId === "rc30") {
    ["rhythmType", "rhythmLevel", "track1", "track2", "quantize"].forEach((key) => {
      lines.push(`- ${key}: ${safe[key]}`);
    });
    return lines.join("\n");
  }

  Object.entries(safe).forEach(([key, value]) => {
    lines.push(`- ${key}: ${value}`);
  });
  return lines.join("\n");
}

function rectsIntersect(a, b) {
  return !(a.x + a.width < b.x || b.x + b.width < a.x || a.y + a.height < b.y || b.y + b.height < a.y);
}

function pointInRect(point, rect) {
  return point.x >= rect.x && point.x <= rect.x + rect.width && point.y >= rect.y && point.y <= rect.y + rect.height;
}

function expandRect(rect, pad) {
  return {
    x: rect.x - pad,
    y: rect.y - pad,
    width: rect.width + pad * 2,
    height: rect.height + pad * 2,
  };
}

function shuffle(list) {
  const out = [...list];
  for (let i = out.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

function deepMerge(base, overrides) {
  const output = deepClone(base);
  if (!overrides || typeof overrides !== "object") {
    return output;
  }
  Object.entries(overrides).forEach(([key, value]) => {
    if (value && typeof value === "object" && !Array.isArray(value) && output[key] && typeof output[key] === "object" && !Array.isArray(output[key])) {
      output[key] = deepMerge(output[key], value);
      return;
    }
    output[key] = value;
  });
  return output;
}

function hashString(value) {
  let hash = 2166136261;
  for (let i = 0; i < value.length; i += 1) {
    hash ^= value.charCodeAt(i);
    hash += (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
  }
  return (`00000000${(hash >>> 0).toString(16)}`).slice(-8).repeat(4);
}

function capitalize(value) {
  const text = String(value || "");
  return text ? text[0].toUpperCase() + text.slice(1) : text;
}

/* === Recommendation + Pedal Rendering Engine (ported from prior web build) === */
function renderPedalFace(pedalId, pedal, settings = {}) {
  if (pedal.type === "eq10") {
    return renderEq10Face(pedal, settings);
  }

  if (pedal.type === "eq7") {
    return renderGe7Face(pedal, settings);
  }

  if (pedal.type === "looper") {
    return renderRc30Face(pedal, settings);
  }

  if (pedal.type === "amp") {
    return renderAmpFace(pedal, settings);
  }

  return renderKnobPedalFace(pedalId, pedal, settings);
}

function renderKnobPedalFace(pedalId, pedal, settings = {}) {
  const knobs = pedal.controlKeys
    .map((key) => {
      const value = typeof settings[key] === "number" ? settings[key] : 50;
      return renderKnob(value);
    })
    .join("");

  return `
    <div class="pedal-face ${pedalId}">
      <div class="pedal-brand">${pedal.brand}</div>
      <div class="pedal-model">${pedal.model}</div>
      <div class="pedal-desc">${pedal.subtitle}</div>
      <div class="knob-strip">${knobs}</div>
      <div class="knob-labels">
        ${pedal.controlLabels.map((label) => `<span>${label}</span>`).join("")}
      </div>
      <div class="footswitch"></div>
      <div class="pedal-bottom">Analog Circuit</div>
    </div>
  `;
}

function renderEq10Face(pedal, settings = {}) {
  const bands = settings.bands || {};
  const sliders = EQ10_BANDS.map((band) => {
    const value = typeof bands[band] === "number" ? bands[band] : 0;
    return `<div class="eq-slider" title="${band} Hz: ${dbValue(value)}" style="--slider-pos:${sliderPercent(value, -12, 12)}%"></div>`;
  }).join("");
  const labels = EQ10_BANDS.map((band) => `<span>${shortBandLabel(band)}</span>`).join("");

  const output = typeof settings.volume === "number" ? settings.volume : 0;
  const gain = typeof settings.gain === "number" ? settings.gain : 0;

  return `
    <div class="pedal-face eq10">
      <div class="pedal-brand">${pedal.brand}</div>
      <div class="pedal-model">${pedal.model}</div>
      <div class="pedal-desc">${pedal.subtitle}</div>
      <div class="eq-master-row">
        <div class="eq-master-control">
          ${renderKnob(sliderPercent(output, -12, 12), "mini")}
          <span>Out ${dbValue(output)}</span>
        </div>
        <div class="eq-master-control">
          ${renderKnob(sliderPercent(gain, -12, 12), "mini")}
          <span>Gain ${dbValue(gain)}</span>
        </div>
      </div>
      <div class="eq-sliders">${sliders}</div>
      <div class="eq-band-labels eq10-band-labels">${labels}</div>
      <div class="pedal-bottom">31.25Hz - 16kHz</div>
    </div>
  `;
}

function renderGe7Face(pedal, settings = {}) {
  const bands = settings.bands || {};
  const level = typeof settings.level === "number" ? settings.level : 0;
  const sliders = [
    ...GE7_BANDS.map((band) => {
      const value = typeof bands[band] === "number" ? bands[band] : 0;
      return `<div class="eq-slider ge7-slider" title="${band} Hz: ${dbValue(value)}" style="--slider-pos:${sliderPercent(value, -15, 15)}%"></div>`;
    }),
    `<div class="eq-slider ge7-slider ge7-level" title="Level: ${dbValue(level)}" style="--slider-pos:${sliderPercent(level, -15, 15)}%"></div>`,
  ].join("");
  const labels = [...GE7_BANDS.map((band) => `<span>${shortBandLabel(band)}</span>`), "<span>Lvl</span>"].join("");

  return `
    <div class="pedal-face ge7">
      <div class="pedal-brand">${pedal.brand}</div>
      <div class="pedal-model">${pedal.model}</div>
      <div class="pedal-desc">${pedal.subtitle}</div>
      <div class="eq-side-labels">
        <span>${settings.mode || "Contour"}</span>
        <span>Level ${dbValue(level)}</span>
      </div>
      <div class="eq-sliders ge7-track">${sliders}</div>
      <div class="eq-band-labels ge7-band-labels">${labels}</div>
      <div class="pedal-bottom">100Hz - 6.4kHz</div>
    </div>
  `;
}

function renderRc30Face(pedal, settings = {}) {
  const track1 = typeof settings.track1 === "number" ? settings.track1 : 60;
  const track2 = typeof settings.track2 === "number" ? settings.track2 : 60;
  const rhythm = typeof settings.rhythmLevel === "number" ? settings.rhythmLevel : 15;

  return `
    <div class="pedal-face rc30">
      <div class="pedal-brand">${pedal.brand}</div>
      <div class="pedal-model">${pedal.model}</div>
      <div class="pedal-desc">${pedal.subtitle}</div>
      <div class="rc-panels">
        <div class="rc-panel">
          <span>Track 1</span>
          <div class="rc-meter"><div class="rc-fill" style="height:${clamp(track1, 0, 100)}%"></div></div>
        </div>
        <div class="rc-panel">
          <span>Track 2</span>
          <div class="rc-meter"><div class="rc-fill" style="height:${clamp(track2, 0, 100)}%"></div></div>
        </div>
      </div>
      <div class="rc-meta">Rhythm ${rhythm}% | ${settings.rhythmType || "Rock 1"}</div>
      <div class="rc-switches">
        <div class="footswitch"></div>
        <div class="footswitch"></div>
      </div>
      <div class="pedal-bottom">Stereo Phrase Looper</div>
    </div>
  `;
}

function renderAmpFace(pedal, settings = {}) {
  const ampName = settings.modelLabel || pedal.model;
  const ampSubtitle = settings.voicing || pedal.subtitle;
  const knobs = pedal.controlKeys
    .map((key) => {
      const value = typeof settings[key] === "number" ? settings[key] : 50;
      return renderKnob(value);
    })
    .join("");

  return `
    <div class="pedal-face amp">
      <div class="pedal-brand">${pedal.brand}</div>
      <div class="pedal-model">${ampName}</div>
      <div class="pedal-desc">${ampSubtitle}</div>
      <div class="knob-strip amp-knobs">${knobs}</div>
      <div class="knob-labels">
        ${pedal.controlLabels.map((label) => `<span>${label}</span>`).join("")}
      </div>
      <div class="amp-grill"></div>
      <div class="pedal-bottom">Speaker Out</div>
    </div>
  `;
}

function buildRecommendation(
  genreKey,
  chain,
  guitarType = "electric",
  ampModel = "auto",
  guitarProfile = AUTO_GUITAR_PROFILE_BY_TYPE[guitarType] || "electric_2_knob_toggle",
) {
  const normalizedChain = sanitizeChain(chain);
  const preset = deepClone(GENRE_PRESETS[genreKey] || GENRE_PRESETS.metal);
  const orderAnalysis = runOrderLab(genreKey, normalizedChain.length ? normalizedChain : preset.optimizedChain, guitarType);
  const presetNotes = filterPresetNotesByChain(preset.notes, normalizedChain);
  const recommendation = {
    label: preset.label,
    optimizedChain: orderAnalysis.bestChain,
    orderAnalysis,
    pedals: preset.pedals,
    amp: preset.amp,
    notes: [...presetNotes],
    ampModelKey: null,
    ampLabel: "Amp",
  };

  const indexMap = Object.fromEntries(normalizedChain.map((pedalId, index) => [pedalId, index]));
  const hasPedal = (pedalId) => Number.isInteger(indexMap[pedalId]);

  const driveIds = ["sd1", "bd2", "ds1"];
  const driveIndices = driveIds.map((pedalId) => indexMap[pedalId]).filter(Number.isInteger);
  const firstDriveIndex = driveIndices.length ? Math.min(...driveIndices) : null;
  const lastDriveIndex = driveIndices.length ? Math.max(...driveIndices) : null;

  if (hasPedal("cs3")) {
    const cs3 = recommendation.pedals.cs3;
    if (driveIndices.length && indexMap.cs3 < firstDriveIndex) {
      const pre = ORDER_RULES.compression.preGain;
      cs3.attack = clamp(cs3.attack + pre.attackDelta, 0, 100);
      cs3.sustain = clamp(cs3.sustain + pre.sustainDelta, 0, 100);
      recommendation.notes.push(pre.note);
    } else {
      const post = ORDER_RULES.compression.postGain;
      cs3.level = clamp(cs3.level + post.levelDelta, 0, 100);
      cs3.sustain = clamp(cs3.sustain + post.sustainDelta, 0, 100);
      recommendation.notes.push(post.note);
    }
  }

  if (hasPedal("sd1") && hasPedal("ds1")) {
    const sd1 = recommendation.pedals.sd1;
    const ds1 = recommendation.pedals.ds1;

    if (indexMap.sd1 < indexMap.ds1) {
      const stack = ORDER_RULES.driveStack.sd1IntoDs1;
      sd1.drive = clamp(sd1.drive + stack.sd1.driveDelta, 0, 100);
      sd1.level = clamp(sd1.level + stack.sd1.levelDelta, 0, 100);
      recommendation.notes.push(stack.note);
    } else {
      const stack = ORDER_RULES.driveStack.ds1IntoSd1;
      ds1.dist = clamp(ds1.dist + stack.ds1.distDelta, 0, 100);
      sd1.drive = clamp(sd1.drive + stack.sd1.driveDelta, 0, 100);
      recommendation.notes.push(stack.note);
    }
  }

  if (hasPedal("bd2") && (hasPedal("sd1") || hasPedal("ds1"))) {
    const bd2 = recommendation.pedals.bd2;
    const stackTargets = [indexMap.sd1, indexMap.ds1].filter(Number.isInteger);

    if (stackTargets.length && indexMap.bd2 < Math.min(...stackTargets)) {
      const rule = ORDER_RULES.driveStack.bd2BeforeOtherDrive;
      bd2.gain = clamp(bd2.gain + rule.bd2.gainDelta, 0, 100);
      bd2.level = clamp(bd2.level + rule.bd2.levelDelta, 0, 100);
      recommendation.notes.push(rule.note);
    } else if (stackTargets.length && indexMap.bd2 > Math.max(...stackTargets)) {
      const rule = ORDER_RULES.driveStack.bd2AfterOtherDrive;
      bd2.gain = clamp(bd2.gain + rule.bd2.gainDelta, 0, 100);
      bd2.tone = clamp(bd2.tone + rule.bd2.toneDelta, 0, 100);
      recommendation.notes.push(rule.note);
    }
  }

  if (hasPedal("ge7")) {
    const ge7 = recommendation.pedals.ge7;
    if (driveIndices.length && indexMap.ge7 < firstDriveIndex) {
      const rule = ORDER_RULES.ge7Placement.preDrive;
      ge7.mode = rule.mode;
      ge7.level = clamp(ge7.level + rule.levelDelta, -15, 15);
      Object.entries(rule.bandDeltas).forEach(([band, delta]) => {
        ge7.bands[band] = clamp(ge7.bands[band] + delta, -15, 15);
      });
      recommendation.notes.push(rule.note);
    } else if (driveIndices.length && indexMap.ge7 > lastDriveIndex) {
      const rule = ORDER_RULES.ge7Placement.postDrive;
      ge7.mode = rule.mode;
      ge7.level = clamp(ge7.level + rule.levelDelta, -15, 15);
      Object.entries(rule.bandDeltas).forEach(([band, delta]) => {
        ge7.bands[band] = clamp(ge7.bands[band] + delta, -15, 15);
      });
      recommendation.notes.push(rule.note);
    } else {
      ge7.mode = ORDER_RULES.ge7Placement.betweenDrives.mode;
      recommendation.notes.push(ORDER_RULES.ge7Placement.betweenDrives.note);
    }
    clampBandMap(ge7.bands, -15, 15);
  }

  if (hasPedal("eq10")) {
    const eq10 = recommendation.pedals.eq10;
    if (driveIndices.length && indexMap.eq10 < firstDriveIndex) {
      const rule = ORDER_RULES.eq10Placement.preDrive;
      eq10.mode = rule.mode;
      eq10.volume = clamp(eq10.volume + rule.volumeDelta, -12, 12);
      Object.entries(rule.bandDeltas).forEach(([band, delta]) => {
        eq10.bands[band] = clamp(eq10.bands[band] + delta, -12, 12);
      });
      recommendation.notes.push(rule.note);
    } else if (driveIndices.length && indexMap.eq10 > lastDriveIndex) {
      const rule = ORDER_RULES.eq10Placement.postDrive;
      eq10.mode = rule.mode;
      Object.entries(rule.bandDeltas).forEach(([band, delta]) => {
        eq10.bands[band] = clamp(eq10.bands[band] + delta, -12, 12);
      });
      recommendation.notes.push(rule.note);
    } else {
      eq10.mode = ORDER_RULES.eq10Placement.betweenDrives.mode;
      recommendation.notes.push(ORDER_RULES.eq10Placement.betweenDrives.note);
    }
    clampBandMap(eq10.bands, -12, 12);
  }

  if (hasPedal("ch1")) {
    const ch1 = recommendation.pedals.ch1;
    if (driveIndices.length && indexMap.ch1 < firstDriveIndex) {
      const rule = ORDER_RULES.chorus.preGain;
      ch1.depth = clamp(ch1.depth + rule.depthDelta, 0, 100);
      ch1.effectLevel = clamp(ch1.effectLevel + rule.levelDelta, 0, 100);
      recommendation.notes.push(rule.note);
    } else {
      const rule = ORDER_RULES.chorus.postGain;
      ch1.depth = clamp(ch1.depth + rule.depthDelta, 0, 100);
      recommendation.notes.push(rule.note);
    }

    if (hasPedal("dd3") && indexMap.ch1 > indexMap.dd3) {
      recommendation.notes.push(ORDER_RULES.chorus.afterDelayNote);
    }
  }

  if (hasPedal("dd3")) {
    const dd3 = recommendation.pedals.dd3;
    if (driveIndices.some((index) => index > indexMap.dd3)) {
      const rule = ORDER_RULES.delay.preGain;
      dd3.eLevel = clamp(dd3.eLevel + rule.levelDelta, 0, 100);
      dd3.fBack = clamp(dd3.fBack + rule.feedbackDelta, 0, 100);
      recommendation.notes.push(rule.note);
    } else {
      const rule = ORDER_RULES.delay.postGain;
      dd3.eLevel = clamp(dd3.eLevel + rule.levelDelta, 0, 100);
      recommendation.notes.push(rule.note);
    }

    if (hasPedal("rc30") && indexMap.dd3 < indexMap.rc30) {
      recommendation.notes.push(ORDER_RULES.delay.beforeLooperNote);
    }
    if (hasPedal("rc30") && indexMap.dd3 > indexMap.rc30) {
      recommendation.notes.push(ORDER_RULES.delay.afterLooperNote);
    }
  }

  if (hasPedal("rc30")) {
    const rc30 = recommendation.pedals.rc30;
    if (driveIndices.some((index) => index > indexMap.rc30)) {
      const rule = ORDER_RULES.looper.beforeGain;
      rc30.track1 = Math.min(rc30.track1, rule.track1Max);
      rc30.track2 = Math.min(rc30.track2, rule.track2Max);
      rc30.rhythmLevel = Math.min(rc30.rhythmLevel, rule.rhythmMax);
      recommendation.notes.push(rule.note);
    } else {
      const rule = ORDER_RULES.looper.afterGain;
      rc30.track1 = Math.max(rc30.track1, rule.track1Min);
      rc30.track2 = Math.max(rc30.track2, rule.track2Min);
      recommendation.notes.push(rule.note);
    }
  }

  const driveCount = driveIndices.length;
  const ampCountRules = ORDER_RULES.ampGainByDriveCount;
  if (driveCount === 0) {
    recommendation.amp.gain = clamp(recommendation.amp.gain + ampCountRules.none, 0, 100);
    recommendation.notes.push(ampCountRules.notes.none);
  } else if (driveCount >= 3) {
    recommendation.amp.gain = clamp(recommendation.amp.gain + ampCountRules.threeOrMore, 0, 100);
    recommendation.notes.push(ampCountRules.notes.threeOrMore);
  } else if (driveCount === 2) {
    recommendation.amp.gain = clamp(recommendation.amp.gain + ampCountRules.two, 0, 100);
    recommendation.notes.push(ampCountRules.notes.two);
  }

  if (!normalizedChain.length) {
    recommendation.notes.push("Add pedals to the chain to get full per-pedal settings.");
  }

  recommendation.notes.push(
    `Order Lab checked ${formatNumber(orderAnalysis.permutationsChecked)} possible layouts for this pedal set.`,
  );

  if (normalizedChain.length && !sameChain(normalizedChain, orderAnalysis.bestChain)) {
    recommendation.notes.push(`Best order for your current pedals: ${chainToText(orderAnalysis.bestChain)}`);
  }

  if (normalizedChain.length) {
    const chainAnalysis = evaluateChainOrder(
      normalizedChain,
      genreKey,
      guitarType,
      orderAnalysis.bestChain,
      true,
    );
    if (chainAnalysis.highlights.length) {
      recommendation.notes.push(...chainAnalysis.highlights);
    }
    if (chainAnalysis.eqJustification) {
      recommendation.notes.push(chainAnalysis.eqJustification);
    }
  }

  applyGuitarTypeProfile(recommendation, guitarType);
  applyAmpModelProfile(recommendation, resolveAmpModel(genreKey, guitarType, ampModel), genreKey, guitarType);
  applyGuitarProfile(recommendation, genreKey, guitarProfile, guitarType);

  recommendation.notes = uniqueList(recommendation.notes);
  return recommendation;
}

function renderGuitarSettingsCard(guitar) {
  if (!guitar) {
    return "";
  }

  const settings = guitar.settings || {};
  const asKnob = (value, fallback = 50) => knobValue(typeof value === "number" ? value : fallback);
  const rows = [];

  if (guitar.controls === "bass_treble") {
    rows.push(["Bass", asKnob(settings.bass)]);
    rows.push(["Treble", asKnob(settings.treble)]);
    rows.push(["Volume", "Set by ear (just below feedback)"]);
  } else if (guitar.controls === "master_volume_tone_toggle") {
    rows.push(["Master Volume", asKnob(settings.volume)]);
    rows.push(["Master Tone", asKnob(settings.tone)]);
    rows.push(["Toggle", settings.toggle || "Middle"]);
  } else if (guitar.controls === "dual_volume_tone_toggle") {
    rows.push(["Neck Volume", asKnob(settings.neckVolume)]);
    rows.push(["Neck Tone", asKnob(settings.neckTone)]);
    rows.push(["Bridge Volume", asKnob(settings.bridgeVolume)]);
    rows.push(["Bridge Tone", asKnob(settings.bridgeTone)]);
    rows.push(["Toggle", settings.toggle || "Middle"]);
  }

  if (guitar.volumeAdvice) {
    rows.push(["Volume Note", guitar.volumeAdvice]);
  }

  return cardTemplate(guitar.label, rows);
}

function renderSettingsCard(pedalId, settings) {
  const pedal = PEDAL_LIBRARY[pedalId];

  if (pedalId === "sd1") {
    return cardTemplate(pedal.model, [
      ["Drive", knobValue(settings.drive)],
      ["Tone", knobValue(settings.tone)],
      ["Level", knobValue(settings.level)],
    ]);
  }

  if (pedalId === "ds1") {
    return cardTemplate(pedal.model, [
      ["Dist", knobValue(settings.dist)],
      ["Tone", knobValue(settings.tone)],
      ["Level", knobValue(settings.level)],
    ]);
  }

  if (pedalId === "bd2") {
    return cardTemplate(pedal.model, [
      ["Gain", knobValue(settings.gain)],
      ["Tone", knobValue(settings.tone)],
      ["Level", knobValue(settings.level)],
    ]);
  }

  if (pedalId === "cs3") {
    return cardTemplate(pedal.model, [
      ["Sustain", knobValue(settings.sustain)],
      ["Attack", knobValue(settings.attack)],
      ["Tone", knobValue(settings.tone)],
      ["Level", knobValue(settings.level)],
    ]);
  }

  if (pedalId === "ch1") {
    return cardTemplate(pedal.model, [
      ["Effect Level", knobValue(settings.effectLevel)],
      ["EQ", knobValue(settings.eq)],
      ["Rate", knobValue(settings.rate)],
      ["Depth", knobValue(settings.depth)],
    ]);
  }

  if (pedalId === "dd3") {
    return cardTemplate(pedal.model, [
      ["Mode", settings.mode],
      ["E.Level", knobValue(settings.eLevel)],
      ["F.Back", knobValue(settings.fBack)],
      ["D.Time", knobValue(settings.dTime)],
    ]);
  }

  if (pedalId === "ge7") {
    const rows = [["Mode", settings.mode], ["Level", dbValue(settings.level)], ...GE7_BANDS.map((band) => [`${band} Hz`, dbValue(settings.bands[band])])];
    return cardTemplate(pedal.model, rows);
  }

  if (pedalId === "eq10") {
    const rows = [
      ["Mode", settings.mode],
      ["Output", dbValue(settings.volume)],
      ["Gain", dbValue(settings.gain)],
      ...EQ10_BANDS.map((band) => [`${band} Hz`, dbValue(settings.bands[band])]),
    ];
    return cardTemplate("10-Band EQ", rows);
  }

  if (pedalId === "rc30") {
    return cardTemplate("RC-30", [
      ["Rhythm Type", settings.rhythmType],
      ["Rhythm Lvl", `${settings.rhythmLevel}%`],
      ["Track 1", `${settings.track1}%`],
      ["Track 2", `${settings.track2}%`],
      ["Quantize", settings.quantize],
    ]);
  }

  return "";
}

function renderAmpSettingsCard(settings) {
  return cardTemplate(settings.modelLabel || "Amp", [
    ["Voice", settings.voicing || "Custom"],
    ["Gain", knobValue(settings.gain)],
    ["Bass", knobValue(settings.bass)],
    ["Mid", knobValue(settings.mid)],
    ["Treble", knobValue(settings.treble)],
    ["Presence", knobValue(settings.presence)],
    ["Master", knobValue(settings.master)],
  ]);
}

function cardTemplate(title, rows) {
  return `
    <section class="setting-card">
      <h3>${title}</h3>
      <ul class="setting-list">
        ${rows
          .map(
            ([label, value]) => `
              <li>
                <span class="label">${label}</span>
                <span>${value}</span>
              </li>
            `,
          )
          .join("")}
      </ul>
    </section>
  `;
}

function knobValue(value) {
  return `${toClock(value)} on clock (${value}%)`;
}

function dbValue(value) {
  if (value > 0) {
    return `+${value} dB`;
  }
  return `${value} dB`;
}

function shortBandLabel(label) {
  const normalized = String(label || "").toLowerCase();
  if (normalized === "31.25") {
    return "31";
  }
  if (normalized === "62.5") {
    return "62";
  }
  return String(label);
}

function toClock(percent) {
  const clamped = clamp(percent, 0, 100);
  const startMinutes = 7 * 60;
  const sweepMinutes = 10 * 60;
  const absolute = Math.round(startMinutes + (clamped / 100) * sweepMinutes);
  let hours = Math.floor(absolute / 60);
  const minutes = absolute % 60;
  if (hours > 12) {
    hours -= 12;
  }
  return `${hours}:${String(minutes).padStart(2, "0")}`;
}

function angleFromPercent(percent) {
  const clamped = clamp(percent, 0, 100);
  return Math.round(-135 + (clamped / 100) * 270);
}

function renderKnob(percent, variant = "") {
  const className = variant ? `knob ${variant}` : "knob";
  return `
    <div class="${className}">
      <span class="knob-pointer" style="transform:translateX(-50%) rotate(${angleFromPercent(percent)}deg)"></span>
    </div>
  `;
}

function sliderPercent(value, min, max) {
  if (max <= min) {
    return 50;
  }
  return clamp(((value - min) / (max - min)) * 100, 0, 100);
}

function chainToText(chain) {
  if (!chain.length) {
    return "(empty) -> AMP";
  }
  return `${chain.map((pedalId) => PEDAL_LIBRARY[pedalId].model).join(" -> ")} -> AMP`;
}

function renderSummary(recommendation) {
  if (!elements.summaryOutput) {
    return;
  }

  const amp = recommendation.amp || {};
  const guitarTypeLabel = state.guitarType === "acoustic" ? "Acoustic" : "Electric";
  const bullets = [
    `Style: ${recommendation.label}`,
    `Guitar: ${guitarTypeLabel} | Profile: ${recommendation.guitar?.label || "Default"}`,
    guitarSummaryLine(recommendation.guitar),
    `Amp: ${recommendation.ampLabel || amp.modelLabel || "Amp"} (${amp.voicing || "Custom"})`,
    `Amp Dial: Gain ${quickKnob(amp.gain)}, Bass ${quickKnob(amp.bass)}, Mid ${quickKnob(amp.mid)}, Treble ${quickKnob(amp.treble)}, Presence ${quickKnob(amp.presence)}, Master ${quickKnob(amp.master)}`,
    `Signal Chain: ${chainToText(state.chain)}`,
    ...state.chain
      .map((pedalId) => pedalSummaryLine(pedalId, recommendation.pedals[pedalId]))
      .filter(Boolean),
  ].filter(Boolean);

  elements.summaryOutput.innerHTML = `
    <ul>${bullets.map((line) => `<li>${line}</li>`).join("")}</ul>
  `;
}

function guitarSummaryLine(guitar) {
  if (!guitar || !guitar.settings) {
    return "";
  }

  const settings = guitar.settings;
  if (guitar.controls === "bass_treble") {
    return `Guitar Dial: Bass ${quickKnob(settings.bass)}, Treble ${quickKnob(settings.treble)}, Volume set by ear below feedback.`;
  }
  if (guitar.controls === "master_volume_tone_toggle") {
    return `Guitar Dial: Volume ${quickKnob(settings.volume)}, Tone ${quickKnob(settings.tone)}, Toggle ${settings.toggle || "Middle"}.`;
  }
  if (guitar.controls === "dual_volume_tone_toggle") {
    return `Guitar Dial: Neck Vol ${quickKnob(settings.neckVolume)}, Neck Tone ${quickKnob(settings.neckTone)}, Bridge Vol ${quickKnob(settings.bridgeVolume)}, Bridge Tone ${quickKnob(settings.bridgeTone)}, Toggle ${settings.toggle || "Middle"}.`;
  }
  return "";
}

function pedalSummaryLine(pedalId, settings = {}) {
  const pedal = PEDAL_LIBRARY[pedalId];
  if (!pedal || !settings) {
    return "";
  }

  if (pedalId === "sd1") {
    return `SD-1: Drive ${quickKnob(settings.drive)}, Tone ${quickKnob(settings.tone)}, Level ${quickKnob(settings.level)}.`;
  }
  if (pedalId === "ds1") {
    return `DS-1: Dist ${quickKnob(settings.dist)}, Tone ${quickKnob(settings.tone)}, Level ${quickKnob(settings.level)}.`;
  }
  if (pedalId === "bd2") {
    return `BD-2: Gain ${quickKnob(settings.gain)}, Tone ${quickKnob(settings.tone)}, Level ${quickKnob(settings.level)}.`;
  }
  if (pedalId === "cs3") {
    return `CS-3: Sustain ${quickKnob(settings.sustain)}, Attack ${quickKnob(settings.attack)}, Tone ${quickKnob(settings.tone)}, Level ${quickKnob(settings.level)}.`;
  }
  if (pedalId === "ch1") {
    return `CH-1: E.Level ${quickKnob(settings.effectLevel)}, EQ ${quickKnob(settings.eq)}, Rate ${quickKnob(settings.rate)}, Depth ${quickKnob(settings.depth)}.`;
  }
  if (pedalId === "dd3") {
    return `DD-3: Mode ${settings.mode || "320 ms"}, E.Level ${quickKnob(settings.eLevel)}, F.Back ${quickKnob(settings.fBack)}, D.Time ${quickKnob(settings.dTime)}.`;
  }
  if (pedalId === "ge7") {
    return `GE-7 (${settings.mode || "Contour"}): Level ${dbValue(settings.level || 0)}, 800Hz ${dbValue(settings.bands?.["800"] || 0)}, 1.6kHz ${dbValue(settings.bands?.["1.6k"] || 0)}, 3.2kHz ${dbValue(settings.bands?.["3.2k"] || 0)}.`;
  }
  if (pedalId === "eq10") {
    return `10-BAND EQ (${settings.mode || "Shape"}): Output ${dbValue(settings.volume || 0)}, Gain ${dbValue(settings.gain || 0)}, 125Hz ${dbValue(settings.bands?.["125"] || 0)}, 1kHz ${dbValue(settings.bands?.["1k"] || 0)}, 2kHz ${dbValue(settings.bands?.["2k"] || 0)}.`;
  }
  if (pedalId === "rc30") {
    return `RC-30: Rhythm ${settings.rhythmType || "Rock 1"} at ${settings.rhythmLevel || 0}%, Track 1 ${settings.track1 || 0}%, Track 2 ${settings.track2 || 0}%, Quantize ${settings.quantize || "On"}.`;
  }
  return `${pedal.model}: settings loaded.`;
}

function quickKnob(value) {
  const safe = clamp(Math.round(typeof value === "number" ? value : 50), 0, 100);
  return `${toClock(safe)} (${safe}%)`;
}

function formatNumber(value) {
  const safe = Number.isFinite(Number(value)) ? Number(value) : 0;
  return safe.toLocaleString("en-US");
}

function calculateChainScore(chain, optimizedChain) {
  if (!chain.length) {
    return 0;
  }

  const target = optimizedChain;
  const common = chain.filter((pedalId) => target.includes(pedalId));
  if (!common.length) {
    return 0;
  }

  let pairTotal = 0;
  let pairCorrect = 0;

  for (let i = 0; i < common.length; i += 1) {
    for (let j = i + 1; j < common.length; j += 1) {
      pairTotal += 1;
      if (target.indexOf(common[i]) < target.indexOf(common[j])) {
        pairCorrect += 1;
      }
    }
  }

  const orderScore = pairTotal === 0 ? 100 : (pairCorrect / pairTotal) * 100;
  const missing = Math.max(0, target.length - common.length);
  const missingPenalty = (missing / target.length) * 34;

  return Math.max(0, Math.round(orderScore - missingPenalty));
}

function sanitizeChain(chain) {
  const seen = new Set();
  return chain.filter((pedalId) => {
    if (!PEDAL_LIBRARY[pedalId] || pedalId === "amp") {
      return false;
    }
    if (seen.has(pedalId)) {
      return false;
    }
    seen.add(pedalId);
    return true;
  });
}

function runOrderLab(genreKey, chain, guitarType = "electric") {
  const stylePreset = GENRE_PRESETS[genreKey] || GENRE_PRESETS.metal;
  const pedalPool = sanitizeChain(chain);
  const fallbackPool = sanitizeChain(stylePreset.optimizedChain || []);
  const workingPool = pedalPool.length ? pedalPool : fallbackPool;

  if (!workingPool.length) {
    return {
      bestChain: [],
      score: 0,
      permutationsChecked: 0,
      highlights: [],
      eqJustification: "",
    };
  }

  const cacheKey = `${genreKey}|${guitarType}|${[...workingPool].sort().join(",")}`;
  const cached = orderLabCache.get(cacheKey);
  if (cached) {
    return deepClone(cached);
  }

  const styleTarget = sanitizeChain(stylePreset.optimizedChain || []);
  const n = workingPool.length;
  const used = new Array(n).fill(false);
  const candidate = new Array(n);
  let permutationsChecked = 0;
  let best = {
    chain: [...workingPool],
    score: Number.NEGATIVE_INFINITY,
    mismatch: Number.POSITIVE_INFINITY,
    lexical: "",
  };

  function visit(depth) {
    if (depth === n) {
      permutationsChecked += 1;
      const chainCandidate = [...candidate];
      const evaluation = evaluateChainOrder(chainCandidate, genreKey, guitarType, styleTarget);
      const mismatch = pairMismatchCount(chainCandidate, styleTarget);
      const lexical = chainCandidate.join("|");
      if (
        evaluation.score > best.score ||
        (evaluation.score === best.score &&
          (mismatch < best.mismatch || (mismatch === best.mismatch && lexical < best.lexical)))
      ) {
        best = {
          chain: chainCandidate,
          score: evaluation.score,
          mismatch,
          lexical,
        };
      }
      return;
    }

    for (let i = 0; i < n; i += 1) {
      if (used[i]) {
        continue;
      }
      used[i] = true;
      candidate[depth] = workingPool[i];
      visit(depth + 1);
      used[i] = false;
    }
  }

  visit(0);

  const bestEvaluation = evaluateChainOrder(best.chain, genreKey, guitarType, styleTarget, true);
  const result = {
    bestChain: best.chain,
    score: best.score,
    permutationsChecked,
    highlights: uniqueList(bestEvaluation.highlights || []).slice(0, 5),
    eqJustification: bestEvaluation.eqJustification || "",
  };
  orderLabCache.set(cacheKey, deepClone(result));
  return result;
}

function evaluateChainOrder(chain, genreKey, guitarType, styleTarget = [], includeNotes = false) {
  const indexMap = Object.fromEntries(chain.map((pedalId, index) => [pedalId, index]));
  const has = (pedalId) => Number.isInteger(indexMap[pedalId]);
  const notes = [];
  const driveIds = ["sd1", "bd2", "ds1"].filter(has);
  const driveIndices = driveIds.map((pedalId) => indexMap[pedalId]).sort((a, b) => a - b);
  const firstDrive = driveIndices.length ? driveIndices[0] : -1;
  const lastDrive = driveIndices.length ? driveIndices[driveIndices.length - 1] : -1;
  let score = 0;

  const modernGenres = new Set(["metal", "rock", "pop", "country", "hip-hop"]);
  const vintageGenres = new Set(["classic-rock", "blues"]);
  const targetIndices = Object.fromEntries(styleTarget.map((pedalId, index) => [pedalId, index]));

  const addRule = (condition, weight, passNote) => {
    if (condition) {
      score += weight;
      if (includeNotes && passNote) {
        notes.push(passNote);
      }
      return;
    }
    score -= Math.round(weight * 0.72);
  };

  let pairTotal = 0;
  let pairCorrect = 0;
  for (let i = 0; i < chain.length; i += 1) {
    for (let j = i + 1; j < chain.length; j += 1) {
      const left = chain[i];
      const right = chain[j];
      if (!Number.isInteger(targetIndices[left]) || !Number.isInteger(targetIndices[right])) {
        continue;
      }
      pairTotal += 1;
      if (targetIndices[left] < targetIndices[right]) {
        pairCorrect += 1;
      }
    }
  }
  if (pairTotal) {
    const pairRatio = pairCorrect / pairTotal;
    score += Math.round(pairRatio * 34);
    if (includeNotes) {
      notes.push(`Style-order alignment scored ${Math.round(pairRatio * 100)}% against ${genreKey} best-practice ordering.`);
    }
  }

  if (has("cs3") && driveIndices.length) {
    addRule(
      indexMap.cs3 < firstDrive,
      14,
      "CS-3 is ahead of gain stages for tighter pick response and cleaner sustain.",
    );
  }

  if (has("sd1") && has("ds1")) {
    const preferSd1First = modernGenres.has(genreKey) || guitarType === "electric";
    addRule(
      preferSd1First ? indexMap.sd1 < indexMap.ds1 : indexMap.ds1 < indexMap.sd1,
      preferSd1First ? 12 : 8,
      preferSd1First
        ? "SD-1 is before DS-1 so it acts as a focused boost into distortion."
        : "DS-1 is before SD-1 to soften clipping and keep a vintage-style response.",
    );
  }

  if (driveIndices.length > 1) {
    const driveSpread = driveIndices[driveIndices.length - 1] - driveIndices[0] + 1;
    const driveGaps = driveSpread - driveIndices.length;
    addRule(
      driveGaps <= 1,
      8,
      "Drive pedals are grouped tightly for predictable stacking behavior.",
    );
  }

  if (has("ge7") && driveIndices.length) {
    const wantsPost = modernGenres.has(genreKey) && guitarType === "electric";
    const placementOk = wantsPost ? indexMap.ge7 > lastDrive : indexMap.ge7 < firstDrive;
    addRule(
      placementOk,
      10,
      wantsPost
        ? "GE-7 is post-drive for final contour and mix cut."
        : "GE-7 is pre-drive for focused mid push into clipping.",
    );
  }

  if (has("eq10") && driveIndices.length) {
    const wantsPost = modernGenres.has(genreKey) && guitarType === "electric";
    const placementOk = wantsPost ? indexMap.eq10 > lastDrive : indexMap.eq10 < firstDrive;
    addRule(
      placementOk,
      11,
      wantsPost
        ? "10-band EQ is post-drive for broad final sculpting."
        : "10-band EQ is pre-drive for broader pre-clipping tone shaping.",
    );
  }

  if (has("ch1") && driveIndices.length) {
    addRule(
      indexMap.ch1 > lastDrive,
      11,
      "CH-1 is after gain for cleaner modulation and width.",
    );
  }

  if (has("dd3") && driveIndices.length) {
    addRule(
      indexMap.dd3 > lastDrive,
      13,
      "DD-3 is after gain for clearer repeat definition.",
    );
  }

  if (has("ch1") && has("dd3")) {
    addRule(
      indexMap.ch1 < indexMap.dd3,
      7,
      "CH-1 before DD-3 keeps modulation natural before repeats.",
    );
  }

  if (has("rc30")) {
    const rcIndex = indexMap.rc30;
    const lastIndex = chain.length - 1;
    addRule(
      rcIndex === lastIndex,
      18,
      "RC-30 is at chain end for stable loop playback while toggling other pedals.",
    );

    if (has("dd3")) {
      addRule(
        indexMap.dd3 < rcIndex,
        10,
        "Delay is before RC-30 so repeats are captured into loops naturally.",
      );
    }
    if (has("ch1")) {
      addRule(
        indexMap.ch1 < rcIndex,
        6,
        "Chorus is before RC-30 for consistent modulated loop capture.",
      );
    }
  }

  let eqJustification = "";
  if (has("ge7") && has("eq10")) {
    const eqGap = Math.abs(indexMap.ge7 - indexMap.eq10);
    const bothPost = driveIndices.length && indexMap.ge7 > lastDrive && indexMap.eq10 > lastDrive;
    const bothPre = driveIndices.length && indexMap.ge7 < firstDrive && indexMap.eq10 < firstDrive;
    const unavoidableAdjacency = chain.length <= 2;

    if (eqGap === 1 && !unavoidableAdjacency) {
      score -= 9;
    } else if (eqGap > 1) {
      score += 6;
    }

    if (bothPost && has("ge7") && has("eq10")) {
      addRule(
        indexMap.ge7 < indexMap.eq10,
        4,
        "GE-7 sits before 10-band in post-drive stage for surgical-mid first, broad-sculpt second.",
      );
    }

    if (bothPre && has("ge7") && has("eq10")) {
      addRule(
        indexMap.eq10 < indexMap.ge7,
        4,
        "10-band sits before GE-7 pre-drive for broad prep first, focused mid-shaping second.",
      );
    }

    if (eqGap === 1) {
      if (bothPost) {
        eqJustification =
          "GE-7 and 10-band are adjacent by design here: GE-7 handles narrow mid surgery, then EQ10 does broad final contour.";
      } else if (bothPre) {
        eqJustification =
          "GE-7 and 10-band are adjacent here for staged pre-drive shaping: broad EQ10 prep followed by focused GE-7 push.";
      } else {
        eqJustification =
          "GE-7 and 10-band ended up adjacent only because separating them cost more overall chain quality in this pedal set.";
      }
    } else {
      eqJustification =
        "GE-7 and 10-band are intentionally separated to keep each EQ stage distinct and avoid stacked over-filtering.";
    }
  }

  if (vintageGenres.has(genreKey) && has("bd2") && has("sd1")) {
    addRule(
      indexMap.bd2 < indexMap.sd1,
      7,
      "BD-2 before SD-1 keeps the stack touch-sensitive for vintage and blues dynamics.",
    );
  }

  return {
    score,
    highlights: notes,
    eqJustification,
  };
}

function pairMismatchCount(chain, target) {
  if (!chain.length || !target.length) {
    return 0;
  }

  const indexMap = Object.fromEntries(target.map((pedalId, index) => [pedalId, index]));
  const common = chain.filter((pedalId) => Number.isInteger(indexMap[pedalId]));
  let mismatch = 0;

  for (let i = 0; i < common.length; i += 1) {
    for (let j = i + 1; j < common.length; j += 1) {
      if (indexMap[common[i]] > indexMap[common[j]]) {
        mismatch += 1;
      }
    }
  }

  return mismatch;
}

function sameChain(left, right) {
  if (!Array.isArray(left) || !Array.isArray(right) || left.length !== right.length) {
    return false;
  }
  for (let i = 0; i < left.length; i += 1) {
    if (left[i] !== right[i]) {
      return false;
    }
  }
  return true;
}

function persistState() {
  const snapshot = {
    genre: state.genre,
    guitarType: state.guitarType,
    guitarProfile: state.guitarProfile,
    ampModel: state.ampModel,
    chain: state.chain,
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
}

function loadSavedState() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return;
  }

  try {
    const parsed = JSON.parse(raw);
    if (parsed.genre && GENRE_PRESETS[parsed.genre]) {
      state.genre = parsed.genre;
    }
    if (parsed.guitarType === "acoustic" || parsed.guitarType === "electric") {
      state.guitarType = parsed.guitarType;
    }
    if (parsed.guitarProfile && GUITAR_PROFILES[parsed.guitarProfile]) {
      state.guitarProfile = parsed.guitarProfile;
    }
    if (parsed.ampModel === "auto" || AMP_MODELS[parsed.ampModel]) {
      state.ampModel = parsed.ampModel;
    }
    if (Array.isArray(parsed.chain)) {
      state.chain = sanitizeChain(parsed.chain);
    }
  } catch {
    state.genre = "metal";
    state.guitarType = "electric";
    state.guitarProfile = AUTO_GUITAR_PROFILE_BY_TYPE.electric || "electric_2_knob_toggle";
    state.ampModel = "auto";
    state.chain = [...DEFAULT_CHAIN];
  }
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("show");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 1900);
}

function clampBandMap(map, min, max) {
  Object.keys(map).forEach((key) => {
    map[key] = clamp(map[key], min, max);
  });
}

function uniqueList(list) {
  return [...new Set(list)];
}

function filterPresetNotesByChain(notes, chain) {
  const noteList = Array.isArray(notes) ? notes : [];
  if (!noteList.length) {
    return [];
  }
  const chainSet = new Set(sanitizeChain(Array.isArray(chain) ? chain : []));
  if (!chainSet.size) {
    return [];
  }
  return noteList.filter((note) => presetNoteApplies(note, chainSet));
}

function presetNoteApplies(note, chainSet) {
  const text = String(note || "").toLowerCase().trim();
  if (!text) {
    return false;
  }

  const matchedPedals = Object.entries(PEDAL_NOTE_PATTERNS)
    .filter(([, patterns]) => patterns.some((pattern) => text.includes(pattern)))
    .map(([pedalId]) => pedalId);

  if (!matchedPedals.length) {
    return true;
  }

  const requiresAll =
    (text.includes(" and ") || text.includes(" plus ") || text.includes(" into ")) && !text.includes(" or ");

  if (requiresAll) {
    return matchedPedals.every((pedalId) => chainSet.has(pedalId));
  }
  return matchedPedals.some((pedalId) => chainSet.has(pedalId));
}

function applyGuitarTypeProfile(recommendation, guitarType) {
  if (guitarType !== "acoustic") {
    recommendation.notes.push("Electric mode keeps standard gain staging and pedal drive behavior.");
    return;
  }

  recommendation.amp.gain = clamp(recommendation.amp.gain - 18, 0, 100);
  recommendation.amp.bass = clamp(recommendation.amp.bass - 6, 0, 100);
  recommendation.amp.mid = clamp(recommendation.amp.mid + 4, 0, 100);
  recommendation.amp.treble = clamp(recommendation.amp.treble + 5, 0, 100);
  recommendation.amp.presence = clamp(recommendation.amp.presence + 5, 0, 100);

  if (recommendation.pedals.cs3) {
    recommendation.pedals.cs3.sustain = clamp(recommendation.pedals.cs3.sustain - 10, 0, 100);
    recommendation.pedals.cs3.attack = clamp(recommendation.pedals.cs3.attack + 6, 0, 100);
    recommendation.pedals.cs3.tone = clamp(recommendation.pedals.cs3.tone + 4, 0, 100);
  }

  if (recommendation.pedals.sd1) {
    recommendation.pedals.sd1.drive = clamp(recommendation.pedals.sd1.drive - 18, 0, 100);
    recommendation.pedals.sd1.level = clamp(recommendation.pedals.sd1.level - 8, 0, 100);
  }

  if (recommendation.pedals.bd2) {
    recommendation.pedals.bd2.gain = clamp(recommendation.pedals.bd2.gain - 20, 0, 100);
    recommendation.pedals.bd2.level = clamp(recommendation.pedals.bd2.level - 8, 0, 100);
  }

  if (recommendation.pedals.ds1) {
    recommendation.pedals.ds1.dist = clamp(recommendation.pedals.ds1.dist - 30, 0, 100);
    recommendation.pedals.ds1.level = clamp(recommendation.pedals.ds1.level - 10, 0, 100);
    recommendation.pedals.ds1.tone = clamp(recommendation.pedals.ds1.tone - 6, 0, 100);
  }

  if (recommendation.pedals.ge7) {
    const ge7 = recommendation.pedals.ge7;
    ge7.mode = "Acoustic contour";
    ge7.level = clamp(ge7.level, -15, 15);
    ge7.bands["100"] = clamp(ge7.bands["100"] - 3, -15, 15);
    ge7.bands["200"] = clamp(ge7.bands["200"] - 2, -15, 15);
    ge7.bands["1.6k"] = clamp(ge7.bands["1.6k"] + 2, -15, 15);
    ge7.bands["3.2k"] = clamp(ge7.bands["3.2k"] + 2, -15, 15);
    clampBandMap(ge7.bands, -15, 15);
  }

  if (recommendation.pedals.eq10) {
    const eq10 = recommendation.pedals.eq10;
    eq10.mode = "Acoustic contour";
    eq10.bands["31.25"] = clamp(eq10.bands["31.25"] - 4, -12, 12);
    eq10.bands["62.5"] = clamp(eq10.bands["62.5"] - 3, -12, 12);
    eq10.bands["1k"] = clamp(eq10.bands["1k"] + 2, -12, 12);
    eq10.bands["2k"] = clamp(eq10.bands["2k"] + 2, -12, 12);
    eq10.bands["4k"] = clamp(eq10.bands["4k"] + 1, -12, 12);
    clampBandMap(eq10.bands, -12, 12);
  }

  if (recommendation.pedals.ch1) {
    recommendation.pedals.ch1.depth = clamp(recommendation.pedals.ch1.depth - 10, 0, 100);
    recommendation.pedals.ch1.rate = clamp(recommendation.pedals.ch1.rate - 8, 0, 100);
    recommendation.pedals.ch1.effectLevel = clamp(recommendation.pedals.ch1.effectLevel - 5, 0, 100);
  }

  if (recommendation.pedals.dd3) {
    recommendation.pedals.dd3.eLevel = clamp(recommendation.pedals.dd3.eLevel - 6, 0, 100);
    recommendation.pedals.dd3.fBack = clamp(recommendation.pedals.dd3.fBack - 8, 0, 100);
  }

  recommendation.notes.push("Acoustic mode softens gain stages and shapes EQ for clarity, body control, and reduced boom.");
}

function resolveGuitarProfile(guitarProfile, guitarType) {
  if (guitarProfile && GUITAR_PROFILES[guitarProfile]) {
    return guitarProfile;
  }
  return AUTO_GUITAR_PROFILE_BY_TYPE[guitarType] || Object.keys(GUITAR_PROFILES)[0];
}

function applyGuitarProfile(recommendation, genreKey, guitarProfile, guitarType) {
  const profileKey = resolveGuitarProfile(guitarProfile, guitarType);
  const profile = GUITAR_PROFILES[profileKey];
  if (!profile) {
    return;
  }

  const genreSettings = deepClone(profile.genres?.[genreKey] || profile.genres?.rock || {});
  recommendation.guitar = {
    profileKey,
    label: profile.label,
    type: profile.type,
    controls: profile.controls,
    volumeAdvice: profile.volumeAdvice || "",
    settings: genreSettings,
  };

  if (profile.note) {
    recommendation.notes.push(profile.note);
  }
  if (genreSettings.note) {
    recommendation.notes.push(genreSettings.note);
  }

  if (profileKey === "taylor_acoustic") {
    recommendation.amp.bass = clamp(recommendation.amp.bass - 2, 0, 100);
    recommendation.amp.treble = clamp(recommendation.amp.treble + 2, 0, 100);
    if (recommendation.pedals.ge7) {
      recommendation.pedals.ge7.bands["100"] = clamp(recommendation.pedals.ge7.bands["100"] - 1, -15, 15);
      recommendation.pedals.ge7.bands["3.2k"] = clamp(recommendation.pedals.ge7.bands["3.2k"] + 1, -15, 15);
    }
    recommendation.notes.push("Taylor profile trims low boom and adds top-end presence for live clarity.");
  }

  if (profileKey === "electric_2_knob_toggle" && recommendation.pedals.ds1) {
    const toggle = String(genreSettings.toggle || "").toLowerCase();
    if (toggle.includes("bridge")) {
      recommendation.pedals.ds1.tone = clamp(recommendation.pedals.ds1.tone - 2, 0, 100);
      recommendation.notes.push("2-knob bridge setting slightly softens DS-1 tone to avoid harsh highs.");
    }
  }

  if (profileKey === "electric_4_knob_toggle" && recommendation.pedals.bd2) {
    const toggle = String(genreSettings.toggle || "").toLowerCase();
    if (toggle.includes("neck")) {
      recommendation.pedals.bd2.tone = clamp(recommendation.pedals.bd2.tone + 3, 0, 100);
      recommendation.notes.push("4-knob neck setting brightens BD-2 tone slightly to keep definition.");
    }
  }
}

function resolveAmpModel(genreKey, guitarType, ampModel) {
  if (ampModel && ampModel !== "auto" && AMP_MODELS[ampModel]) {
    return ampModel;
  }
  const typeMap = AUTO_AMP_BY_GENRE[guitarType] || AUTO_AMP_BY_GENRE.electric || {};
  return typeMap[genreKey] || "orange_rockerverb_mk3";
}

function applyAmpModelProfile(recommendation, ampModelKey, genreKey, guitarType) {
  const profile = AMP_MODELS[ampModelKey];
  if (!profile) {
    recommendation.ampLabel = "Amp";
    recommendation.amp.modelLabel = "Amp";
    recommendation.amp.voicing = "Custom";
    return;
  }

  const base = profile.base || {};
  const genreOffsets = profile.genreOffsets?.[genreKey] || {};
  const typeOffsets = guitarType === "acoustic" ? profile.acousticOffset || {} : {};

  const keys = ["gain", "bass", "mid", "treble", "presence", "master"];
  const merged = {};

  keys.forEach((key) => {
    const existing = typeof recommendation.amp[key] === "number" ? recommendation.amp[key] : 50;
    const profileTarget = clamp((base[key] ?? existing) + (genreOffsets[key] ?? 0) + (typeOffsets[key] ?? 0), 0, 100);
    merged[key] = clamp(Math.round(existing * 0.42 + profileTarget * 0.58), 0, 100);
  });

  recommendation.amp = {
    ...recommendation.amp,
    ...merged,
    modelLabel: profile.shortLabel || profile.label,
    voicing: profile.type === "acoustic" ? "Acoustic Voice" : "Guitar Voice",
  };
  recommendation.ampModelKey = ampModelKey;
  recommendation.ampLabel = profile.label;
  recommendation.notes.push(profile.note);

  if (guitarType === "acoustic" && profile.type !== "acoustic") {
    recommendation.notes.push("Acoustic guitar into an electric amp profile may need extra high-cut and feedback control live.");
  }
  if (guitarType === "electric" && profile.type === "acoustic") {
    recommendation.notes.push("Electric guitar into Acoustic 100 profile is cleaner and less saturated by design.");
  }
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function deepClone(value) {
  return JSON.parse(JSON.stringify(value));
}

/* === Runtime overrides for state persistence and toast === */

function persistState() {
  const snapshot = {
    genre: state.genre,
    guitarType: state.guitarType,
    guitarProfile: state.guitarProfile,
    ampModel: state.ampModel,
    chain: state.chain,
    canvasPositions: state.canvasPositions,
    canvasConnections: state.canvasConnections,
    theme: state.theme,
    fontPreset: state.fontPreset,
    theoryScale: state.theoryScale,
    theoryShape: state.theoryShape,
    selectedTheoryKey: state.selectedTheoryKey,
    pedalReference: state.pedalReference,
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
}

function loadSavedState() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return;
  }

  try {
    const parsed = JSON.parse(raw);

    if (parsed.genre && GENRE_PRESETS[parsed.genre]) {
      state.genre = parsed.genre;
    }
    if (parsed.guitarType === "acoustic" || parsed.guitarType === "electric") {
      state.guitarType = parsed.guitarType;
    }
    if (parsed.guitarProfile && GUITAR_PROFILES[parsed.guitarProfile]) {
      state.guitarProfile = parsed.guitarProfile;
    }
    if (parsed.ampModel === "auto" || AMP_MODELS[parsed.ampModel]) {
      state.ampModel = parsed.ampModel;
    }
    if (Array.isArray(parsed.chain)) {
      state.chain = sanitizeChain(parsed.chain);
    }

    if (parsed.theme && THEMES[parsed.theme]) {
      state.theme = parsed.theme;
    }
    if (FONT_PRESET_SPECS.find(([key]) => key === parsed.fontPreset)) {
      state.fontPreset = parsed.fontPreset;
    }
    if (parsed.theoryScale && SCALE_LIBRARY[parsed.theoryScale]) {
      state.theoryScale = parsed.theoryScale;
    }
    if (parsed.theoryShape && CAGED_SHAPES[parsed.theoryShape]) {
      state.theoryShape = parsed.theoryShape;
    }
    if (parsed.selectedTheoryKey && tableRowForKey(parsed.selectedTheoryKey) >= 0) {
      state.selectedTheoryKey = parsed.selectedTheoryKey;
    }
    if (parsed.pedalReference && PEDAL_LIBRARY[parsed.pedalReference]) {
      state.pedalReference = parsed.pedalReference;
    }

    if (parsed.canvasPositions && typeof parsed.canvasPositions === "object") {
      const cleanPositions = {};
      Object.entries(parsed.canvasPositions).forEach(([pedalId, value]) => {
        if (!PEDAL_LIBRARY[pedalId] || !Array.isArray(value) || value.length !== 2) {
          return;
        }
        cleanPositions[pedalId] = [Number(value[0]) || 16, Number(value[1]) || 16];
      });
      state.canvasPositions = cleanPositions;
    }

    if (Array.isArray(parsed.canvasConnections)) {
      state.canvasConnections = parsed.canvasConnections
        .filter((entry) => Array.isArray(entry) && entry.length === 2)
        .map((entry) => [String(entry[0]), String(entry[1])]);
    }
  } catch {
    state.genre = "metal";
    state.guitarType = "electric";
    state.guitarProfile = AUTO_GUITAR_PROFILE_BY_TYPE.electric || "electric_2_knob_toggle";
    state.ampModel = "auto";
    state.chain = [...DEFAULT_CHAIN];
    state.canvasPositions = {};
    state.canvasConnections = [];
    state.theme = "dark";
    state.fontPreset = "medium";
    state.theoryScale = "minor_pentatonic";
    state.theoryShape = "g";
    state.selectedTheoryKey = "";
    state.pedalReference = BANK_ORDER[0];
  }
}

function showToast(message, options = {}) {
  if (!elements.toast) {
    return;
  }
  const chain = options.chain || [];
  const preview = chain.length
    ? `<span class="toast-preview">${[
        "GTR",
        ...chain.map((pedalId) => PEDAL_LIBRARY[pedalId]?.model || pedalId),
        "AMP",
      ].join(" → ")}</span>`
    : "";

  elements.toast.innerHTML = `<span>${message}</span>${preview}`;
  elements.toast.classList.add("show");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 2200);
}
