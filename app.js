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

const state = {
  genre: "metal",
  guitarType: "electric",
  guitarProfile: AUTO_GUITAR_PROFILE_BY_TYPE.electric || "electric_2_knob_toggle",
  ampModel: "auto",
  chain: [...DEFAULT_CHAIN],
};

const elements = {
  tabButtons: Array.from(document.querySelectorAll("[data-tab-target]")),
  tabBuilder: document.getElementById("tabBuilder"),
  tabSettings: document.getElementById("tabSettings"),
  tabSummary: document.getElementById("tabSummary"),
  genreSelect: document.getElementById("genreSelect"),
  guitarTypeSelect: document.getElementById("guitarTypeSelect"),
  guitarProfileSelect: document.getElementById("guitarProfileSelect"),
  ampSelect: document.getElementById("ampSelect"),
  optimizeBtn: document.getElementById("optimizeBtn"),
  resetBtn: document.getElementById("resetBtn"),
  saveBtn: document.getElementById("saveBtn"),
  pedalBank: document.getElementById("pedalBank"),
  chainList: document.getElementById("chainList"),
  chainDropZone: document.getElementById("chainDropZone"),
  ampNode: document.getElementById("ampNode"),
  emptyHint: document.getElementById("emptyHint"),
  chainScore: document.getElementById("chainScore"),
  chainSummary: document.getElementById("chainSummary"),
  ampMusicGuide: document.getElementById("ampMusicGuide"),
  recommendationMeta: document.getElementById("recommendationMeta"),
  settingsOutput: document.getElementById("settingsOutput"),
  guitarVisual: document.getElementById("guitarVisual"),
  guitarSettingsOutput: document.getElementById("guitarSettingsOutput"),
  pedalSettingsOutput: document.getElementById("pedalSettingsOutput"),
  ampSettingsOutput: document.getElementById("ampSettingsOutput"),
  summaryOutput: document.getElementById("summaryOutput"),
  guidanceList: document.getElementById("guidanceList"),
  toast: document.getElementById("toast"),
};

const orderLabCache = new Map();
const PEDAL_NOTE_PATTERNS = {
  cs3: ["cs-3", "cs3", "compression sustainer", "compressor"],
  sd1: ["sd-1", "sd1", "super overdrive"],
  bd2: ["bd-2", "bd2", "blues driver"],
  ds1: ["ds-1", "ds1", "distortion"],
  ge7: ["ge-7", "ge7"],
  eq10: ["10-band", "10 band", "10-band eq", "eq10", "10 channel"],
  ch1: ["ch-1", "ch1", "chorus"],
  dd3: ["dd-3", "dd3", "delay"],
  rc30: ["rc-30", "rc30", "loop station", "looper"],
};

loadSavedState();
init();

function init() {
  normalizeStateSelections();
  populateGenreSelect();
  populateGuitarTypeSelect();
  populateGuitarProfileSelect();
  populateAmpSelect();
  bindEvents();
  setActiveTab("builder");
  renderAll();
}

function normalizeStateSelections() {
  state.guitarType = state.guitarType === "acoustic" ? "acoustic" : "electric";
  if (!GUITAR_PROFILES[state.guitarProfile]) {
    state.guitarProfile = AUTO_GUITAR_PROFILE_BY_TYPE[state.guitarType] || Object.keys(GUITAR_PROFILES)[0];
  }
  const profile = GUITAR_PROFILES[state.guitarProfile];
  if (profile && profile.type !== state.guitarType) {
    state.guitarType = profile.type;
  }
  if (state.ampModel !== "auto" && !AMP_MODELS[state.ampModel]) {
    state.ampModel = "auto";
  }
}

function populateGenreSelect() {
  const options = Object.entries(GENRE_PRESETS)
    .map(([value, preset]) => `<option value="${value}">${preset.label}</option>`)
    .join("");
  elements.genreSelect.innerHTML = options;
  elements.genreSelect.value = state.genre;
}

function populateGuitarTypeSelect() {
  elements.guitarTypeSelect.value = state.guitarType;
}

function populateGuitarProfileSelect() {
  const options = Object.entries(GUITAR_PROFILES).map(([value, profile]) => {
    const typeLabel = profile.type === "acoustic" ? "Acoustic" : "Electric";
    return `<option value="${value}">${profile.label} (${typeLabel})</option>`;
  });
  elements.guitarProfileSelect.innerHTML = options.join("");

  if (!GUITAR_PROFILES[state.guitarProfile]) {
    state.guitarProfile = AUTO_GUITAR_PROFILE_BY_TYPE[state.guitarType] || Object.keys(GUITAR_PROFILES)[0];
  }
  elements.guitarProfileSelect.value = state.guitarProfile;
}

function populateAmpSelect() {
  if (state.ampModel !== "auto" && !AMP_MODELS[state.ampModel]) {
    state.ampModel = "auto";
  }
  const options = [
    `<option value="auto">Auto (Best Match)</option>`,
    ...Object.entries(AMP_MODELS).map(
      ([value, amp]) => `<option value="${value}">${amp.label}</option>`,
    ),
  ];
  elements.ampSelect.innerHTML = options.join("");
  elements.ampSelect.value = state.ampModel;
}

function bindEvents() {
  elements.tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      setActiveTab(button.dataset.tabTarget || "builder");
    });
  });

  elements.genreSelect.addEventListener("change", (event) => {
    state.genre = event.target.value;
    renderAll();
    persistState();
  });

  elements.guitarTypeSelect.addEventListener("change", (event) => {
    state.guitarType = event.target.value === "acoustic" ? "acoustic" : "electric";
    const profile = GUITAR_PROFILES[state.guitarProfile];
    if (!profile || profile.type !== state.guitarType) {
      state.guitarProfile = AUTO_GUITAR_PROFILE_BY_TYPE[state.guitarType] || state.guitarProfile;
      populateGuitarProfileSelect();
    }
    renderAll();
    persistState();
  });

  elements.guitarProfileSelect.addEventListener("change", (event) => {
    const selected = GUITAR_PROFILES[event.target.value] ? event.target.value : state.guitarProfile;
    state.guitarProfile = selected;
    const profile = GUITAR_PROFILES[state.guitarProfile];
    if (profile && profile.type !== state.guitarType) {
      state.guitarType = profile.type;
      populateGuitarTypeSelect();
    }
    renderAll();
    persistState();
  });

  elements.ampSelect.addEventListener("change", (event) => {
    state.ampModel = AMP_MODELS[event.target.value] ? event.target.value : "auto";
    renderAll();
    persistState();
  });

  elements.optimizeBtn.addEventListener("click", () => {
    const preset = GENRE_PRESETS[state.genre] || GENRE_PRESETS.metal;
    const seedChain = state.chain.length ? state.chain : preset.optimizedChain;
    const orderAnalysis = runOrderLab(state.genre, seedChain, state.guitarType);
    state.chain = sanitizeChain([...orderAnalysis.bestChain]);
    renderAll();
    persistState();
    showToast(
      `${preset.label} optimized (${formatNumber(orderAnalysis.permutationsChecked)} layouts checked).`,
    );
  });

  elements.resetBtn.addEventListener("click", () => {
    state.chain = [...DEFAULT_CHAIN];
    renderAll();
    persistState();
    showToast("Chain reset to your full pedalboard.");
  });

  elements.saveBtn.addEventListener("click", () => {
    persistState();
    showToast("Saved locally on this device.");
  });

  elements.pedalBank.addEventListener("dragstart", onDragStart);
  elements.chainList.addEventListener("dragstart", onDragStart);

  elements.chainList.addEventListener("dragover", onChainDragOver);
  elements.chainList.addEventListener("drop", onChainDrop);
  elements.chainList.addEventListener("dragleave", onChainDragLeave);

  elements.chainDropZone.addEventListener("dragover", (event) => {
    event.preventDefault();
  });

  document.addEventListener("dragend", () => {
    clearActiveDropTargets();
    document.querySelectorAll(".pedal-item.dragging").forEach((item) => item.classList.remove("dragging"));
  });

  elements.chainList.addEventListener("click", (event) => {
    const removeButton = event.target.closest("[data-remove-index]");
    if (!removeButton) {
      return;
    }

    const index = Number(removeButton.dataset.removeIndex);
    if (!Number.isInteger(index) || index < 0 || index >= state.chain.length) {
      return;
    }

    const [removed] = state.chain.splice(index, 1);
    renderAll();
    persistState();
    showToast(`${PEDAL_LIBRARY[removed].model} removed from chain.`);
  });
}

function setActiveTab(tabKey) {
  const safeTab = ["builder", "settings", "summary"].includes(tabKey) ? tabKey : "builder";
  const paneMap = {
    builder: elements.tabBuilder,
    settings: elements.tabSettings,
    summary: elements.tabSummary,
  };

  elements.tabButtons.forEach((button) => {
    const isActive = button.dataset.tabTarget === safeTab;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-selected", isActive ? "true" : "false");
  });

  Object.entries(paneMap).forEach(([key, pane]) => {
    if (!pane) {
      return;
    }
    const isActive = key === safeTab;
    pane.classList.toggle("active", isActive);
    pane.hidden = !isActive;
  });
}

function onDragStart(event) {
  const item = event.target.closest(".pedal-item[draggable='true']");
  if (!item) {
    return;
  }

  const origin = item.dataset.origin;
  const payload = {
    origin,
    pedalId: item.dataset.pedalId,
  };

  if (origin === "chain") {
    payload.index = Number(item.dataset.index);
  }

  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/plain", JSON.stringify(payload));
  item.classList.add("dragging");
}

function onChainDragOver(event) {
  event.preventDefault();
  const target = event.target.closest("[data-drop-index]") || getClosestDropTargetByPoint(event.clientX, event.clientY);
  if (target) {
    clearActiveDropTargets();
    target.classList.add("active-target");
  }
}

function onChainDragLeave(event) {
  const leftChain = !event.currentTarget.contains(event.relatedTarget);
  if (leftChain) {
    clearActiveDropTargets();
  }
}

function onChainDrop(event) {
  event.preventDefault();

  let payload;
  try {
    payload = JSON.parse(event.dataTransfer.getData("text/plain"));
  } catch {
    return;
  }

  const activeTarget = elements.chainList.querySelector(".active-target");
  const target =
    event.target.closest("[data-drop-index]") ||
    activeTarget ||
    getClosestDropTargetByPoint(event.clientX, event.clientY);
  const targetIndex = target ? Number(target.dataset.dropIndex) : state.chain.length;

  if (!Number.isInteger(targetIndex)) {
    clearActiveDropTargets();
    return;
  }

  if (payload.origin === "bank") {
    if (state.chain.includes(payload.pedalId)) {
      showToast(`${PEDAL_LIBRARY[payload.pedalId].model} is already in the chain.`);
      clearActiveDropTargets();
      return;
    }

    state.chain.splice(targetIndex, 0, payload.pedalId);
    renderAll();
    persistState();
    showToast(`${PEDAL_LIBRARY[payload.pedalId].model} added to chain.`);
    return;
  }

  if (payload.origin === "chain") {
    const fromIndex = Number(payload.index);
    if (!Number.isInteger(fromIndex) || fromIndex < 0 || fromIndex >= state.chain.length) {
      clearActiveDropTargets();
      return;
    }

    const [moved] = state.chain.splice(fromIndex, 1);
    const adjustedTarget = fromIndex < targetIndex ? targetIndex - 1 : targetIndex;
    state.chain.splice(adjustedTarget, 0, moved);

    renderAll();
    persistState();
    return;
  }

  clearActiveDropTargets();
}

function getClosestDropTargetByPoint(clientX, clientY) {
  const targets = Array.from(elements.chainList.querySelectorAll("[data-drop-index]"));
  if (!targets.length) {
    return null;
  }

  return targets.reduce((closest, target) => {
    const rect = target.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const distance = Math.hypot(clientX - centerX, clientY - centerY);

    if (!closest || distance < closest.distance) {
      return { target, distance };
    }
    return closest;
  }, null).target;
}

function clearActiveDropTargets() {
  elements.chainList
    .querySelectorAll(".chain-cell.active-target, .chain-end-slot.active-target")
    .forEach((target) => target.classList.remove("active-target"));
}

function renderAll() {
  state.chain = sanitizeChain(state.chain);
  const recommendation = buildRecommendation(
    state.genre,
    state.chain,
    state.guitarType,
    state.ampModel,
    state.guitarProfile,
  );
  renderPedalBank(recommendation);
  renderChain(recommendation);
  renderAmpNode(recommendation.amp, recommendation.ampModelKey, recommendation.ampLabel);
  renderAmpMusicGuide(state.genre);
  renderGuitarVisual(recommendation.guitar);
  renderRecommendations(recommendation);
}

function renderPedalBank(recommendation) {
  elements.pedalBank.innerHTML = BANK_ORDER.map((pedalId) => {
    const disabled = state.chain.includes(pedalId);
    return renderPedalNode({
      pedalId,
      origin: "bank",
      draggable: !disabled,
      disabled,
      visualSettings: recommendation.pedals[pedalId],
    });
  }).join("");
}

function renderChain(recommendation) {
  const html = state.chain
    .map(
      (pedalId, index) => `
        <div class="chain-cell" data-drop-index="${index}" title="Drop pedal here">
          <div class="chain-index">${index + 1}</div>
          ${renderPedalNode({
            pedalId,
            origin: "chain",
            index,
            draggable: true,
            visualSettings: recommendation.pedals[pedalId],
          })}
        </div>
      `,
    )
    .join("");

  elements.chainList.innerHTML = `
    ${html}
    <div class="chain-end-slot" data-drop-index="${state.chain.length}" title="Drop pedal at end">
      Drop New Pedal
    </div>
  `;

  if (state.chain.length === 0) {
    elements.emptyHint.classList.remove("hidden");
  } else {
    elements.emptyHint.classList.add("hidden");
  }

  elements.chainSummary.textContent = chainToText(state.chain);
}

function renderAmpNode(ampSettings, ampModelKey = null, ampLabel = "Amp") {
  const brandClass = `amp-brand-${ampBrandFromKey(ampModelKey)}`;
  const controls = [
    ["Gain", ampSettings.gain],
    ["Bass", ampSettings.bass],
    ["Mid", ampSettings.mid],
    ["Treble", ampSettings.treble],
    ["Presence", ampSettings.presence],
    ["Master", ampSettings.master],
  ]
    .map(([label, value]) => renderAmpControl(label, value))
    .join("");

  const modelLabel = ampSettings.modelLabel || ampLabel || "Amp";
  const voicing = ampSettings.voicing || "Custom";
  elements.ampNode.innerHTML = `
    <section class="amp-rig ${brandClass}" aria-label="${modelLabel} amp settings">
      <div class="amp-head">
        <div class="amp-head-top">
          <span class="amp-logo">${modelLabel}</span>
          <span class="amp-voice">${voicing}</span>
        </div>
        <div class="amp-control-row">${controls}</div>
      </div>
      <div class="amp-cabinet">
        <div class="amp-grill-cloth"></div>
      </div>
    </section>
  `;
}

function renderAmpMusicGuide(genreKey) {
  if (!elements.ampMusicGuide) {
    return;
  }

  const guide = STYLE_PLAYBOOK[genreKey] || STYLE_PLAYBOOK.rock;
  if (!guide) {
    elements.ampMusicGuide.innerHTML = "";
    return;
  }

  const heardProgressions = Array.isArray(guide.concertProgression)
    ? guide.concertProgression
    : Array.isArray(guide.progression)
      ? guide.progression
      : [];
  const capoShapeProgressions = Array.isArray(guide.capo5Shapes) ? guide.capo5Shapes : [];
  const shapes = Array.isArray(guide.openShapes) ? guide.openShapes : [];
  const heardLines = heardProgressions.map((line) => `<li>${line}</li>`).join("");
  const shapeProgressionLines = (capoShapeProgressions.length ? capoShapeProgressions : heardProgressions)
    .map((line) => `<li>${line}</li>`)
    .join("");
  const shapeText = shapes.length ? shapes.join(", ") : "N/A";
  const pentatonicFret = guide.pentatonicFret || "G-shape pentatonic around the 8th fret.";

  elements.ampMusicGuide.innerHTML = `
    <section class="amp-music-guide-card">
      <h4>Style Progressions</h4>
      <p><strong>Heard Chords:</strong></p>
      <ul class="amp-guide-list">${heardLines}</ul>
      <p><strong>Play These Shapes (Capo 5):</strong></p>
      <ul class="amp-guide-list">${shapeProgressionLines}</ul>
      <p><strong>Open Shapes Used:</strong> ${shapeText}</p>
      <p><strong>Capo Mapping:</strong> ${guide.capoGuide || "Capo 5 recommended for tighter range."}</p>
      <p><strong>G-Shape Pentatonic Fret:</strong> ${pentatonicFret}</p>
      <p><strong>Solo Guide:</strong> ${guide.soloGuide || "Solo around G-shape pentatonic phrasing."}</p>
    </section>
  `;
}

function renderAmpControl(label, value) {
  const knobPercent = typeof value === "number" ? value : 50;
  return `
    <div class="amp-control">
      ${renderKnob(knobPercent)}
      <span>${label}</span>
    </div>
  `;
}

function ampBrandFromKey(ampModelKey) {
  const key = String(ampModelKey || "").toLowerCase();
  if (key.startsWith("orange_")) {
    return "orange";
  }
  if (key.startsWith("marshall_")) {
    return "marshall";
  }
  if (key.startsWith("fender_")) {
    return "fender";
  }
  if (key.startsWith("vox_")) {
    return "vox";
  }
  if (key.startsWith("mesa_")) {
    return "mesa";
  }
  return "generic";
}

function renderGuitarVisual(guitar) {
  if (!elements.guitarVisual) {
    return;
  }

  if (!guitar) {
    elements.guitarVisual.innerHTML = `<p class="empty-setting">Choose a guitar profile to preview the guitar controls.</p>`;
    return;
  }

  const settings = guitar.settings || {};
  if (guitar.controls === "bass_treble") {
    elements.guitarVisual.innerHTML = renderAcousticGuitarVisual(guitar, settings);
    return;
  }
  if (guitar.controls === "dual_volume_tone_toggle") {
    elements.guitarVisual.innerHTML = renderLesPaulVisual(guitar, settings);
    return;
  }
  elements.guitarVisual.innerHTML = renderStratVisual(guitar, settings);
}

function renderAcousticGuitarVisual(guitar, settings) {
  return `
    <section class="guitar-card acoustic-view">
      <h3>${guitar.label}</h3>
      <div class="guitar-stage">
        <div class="guitar-svg-wrap" aria-hidden="true">
          <img class="guitar-photo" src="assets/guitars/taylor_cutout_trim.png" alt="Taylor acoustic guitar" />
        </div>
        <div class="guitar-controls-cluster es2-cluster">
          <p>ES2 Controls</p>
          <div class="guitar-knob-row">
            ${renderGuitarControlKnob("Bass", settings.bass, 50)}
            ${renderGuitarControlKnob("Treble", settings.treble, 50)}
            ${renderGuitarControlKnob("Vol", 52, 52, "User")}
          </div>
        </div>
      </div>
    </section>
  `;
}

function renderLesPaulVisual(guitar, settings) {
  return `
    <section class="guitar-card les-paul-view">
      <h3>${guitar.label}</h3>
      <div class="guitar-stage">
        <div class="guitar-svg-wrap" aria-hidden="true">
          <img class="guitar-photo" src="assets/guitars/les_paul_cutout_trim.png" alt="Les Paul style electric guitar" />
        </div>
        <div class="guitar-controls-cluster electric-cluster">
          <p>2V / 2T + Toggle</p>
          <div class="guitar-knob-grid four-knobs">
            ${renderGuitarControlKnob("N Vol", settings.neckVolume, 75)}
            ${renderGuitarControlKnob("N Tone", settings.neckTone, 50)}
            ${renderGuitarControlKnob("B Vol", settings.bridgeVolume, 85)}
            ${renderGuitarControlKnob("B Tone", settings.bridgeTone, 55)}
          </div>
          <div class="toggle-pill">Toggle: ${settings.toggle || "Middle"}</div>
        </div>
      </div>
    </section>
  `;
}

function renderStratVisual(guitar, settings) {
  return `
    <section class="guitar-card strat-view">
      <h3>${guitar.label}</h3>
      <div class="guitar-stage">
        <div class="guitar-svg-wrap" aria-hidden="true">
          <img class="guitar-photo" src="assets/guitars/strat_cutout_trim.png" alt="Strat style electric guitar" />
        </div>
        <div class="guitar-controls-cluster electric-cluster">
          <p>Master Controls</p>
          <div class="guitar-knob-row">
            ${renderGuitarControlKnob("Volume", settings.volume, 85)}
            ${renderGuitarControlKnob("Tone", settings.tone, 55)}
          </div>
          <div class="toggle-pill">Toggle: ${settings.toggle || "Middle"}</div>
        </div>
      </div>
    </section>
  `;
}

function renderGuitarControlKnob(label, value, fallback = 50, suffix = "") {
  const safeValue = typeof value === "number" ? clamp(value, 0, 100) : fallback;
  const suffixText = suffix ? ` ${suffix}` : "";
  return `
    <div class="guitar-knob-item">
      ${renderKnob(safeValue)}
      <span class="guitar-knob-label">${label}</span>
      <span class="guitar-knob-read">${toClock(safeValue)}${suffixText}</span>
    </div>
  `;
}

function renderRecommendations(recommendation) {
  const score = calculateChainScore(state.chain, recommendation.optimizedChain);
  elements.chainScore.textContent = `Tone Match: ${score}%`;

  const optimized = chainToText(recommendation.optimizedChain);
  const guitarLabel = state.guitarType === "acoustic" ? "Acoustic" : "Electric";
  const guitarProfileLabel = recommendation.guitar?.label || "Guitar";
  const ampLabel = recommendation.ampLabel || "Amp";
  const orderLabLine = recommendation.orderAnalysis
    ? `<br><span class="order-lab-meta">Order Lab: ${formatNumber(
        recommendation.orderAnalysis.permutationsChecked,
      )} layouts scored (exhaustive search across every pedal position).</span>`
    : "";
  elements.recommendationMeta.innerHTML = `
    <p><strong>${recommendation.label}</strong> | ${guitarLabel} guitar | Controls: ${guitarProfileLabel} | Amp: ${ampLabel}<br>${optimized}${orderLabLine}</p>
  `;

  if (elements.guitarSettingsOutput && elements.pedalSettingsOutput && elements.ampSettingsOutput) {
    elements.guitarSettingsOutput.innerHTML = recommendation.guitar
      ? renderGuitarSettingsCard(recommendation.guitar)
      : `<p class="empty-setting">Select a guitar profile to view guitar controls.</p>`;

    const pedalCards = state.chain
      .map((pedalId) => {
        const settings = recommendation.pedals[pedalId];
        if (!settings) {
          return "";
        }
        return renderSettingsCard(pedalId, settings);
      })
      .filter(Boolean)
      .join("");

    elements.pedalSettingsOutput.innerHTML =
      pedalCards || `<p class="empty-setting">Add pedals to your chain to generate pedal settings.</p>`;
    elements.ampSettingsOutput.innerHTML = renderAmpSettingsCard(recommendation.amp);
  } else {
    const fallbackCards = [];
    if (recommendation.guitar) {
      fallbackCards.push(renderGuitarSettingsCard(recommendation.guitar));
    }
    state.chain.forEach((pedalId) => {
      const settings = recommendation.pedals[pedalId];
      if (!settings) {
        return;
      }
      fallbackCards.push(renderSettingsCard(pedalId, settings));
    });
    fallbackCards.push(renderAmpSettingsCard(recommendation.amp));
    elements.settingsOutput.innerHTML = fallbackCards.join("");
  }

  elements.guidanceList.innerHTML = `
    <ul>${recommendation.notes.map((note) => `<li>${note}</li>`).join("")}</ul>
  `;
  renderSummary(recommendation);
}

function renderPedalNode({
  pedalId,
  origin,
  index = -1,
  draggable = false,
  disabled = false,
  fixed = false,
  visualSettings = null,
}) {
  const pedal = PEDAL_LIBRARY[pedalId];
  const classes = ["pedal-item"];

  if (origin === "chain") {
    classes.push("chain");
  }
  if (disabled) {
    classes.push("disabled");
  }

  return `
    <article
      class="${classes.join(" ")}" 
      data-origin="${origin}"
      data-index="${index}"
      data-pedal-id="${pedalId}"
      draggable="${draggable ? "true" : "false"}"
      aria-label="${pedal.model} pedal"
    >
      <div class="pedal-frame">
        ${renderPedalFace(pedalId, pedal, visualSettings)}
      </div>
      ${origin === "chain" && !fixed ? `<button class="remove-btn" data-remove-index="${index}">Remove</button>` : ""}
    </article>
  `;
}

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
