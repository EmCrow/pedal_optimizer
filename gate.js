(function () {
  const ACCESS_CACHE_KEY = "pedal_architect_last_host";
  const ACCESS_PASSKEY_KEY = "pedal_architect_saved_passkey";
  const ACCESS_REMEMBER_KEY = "pedal_architect_remember_passkey";
  const gate = document.getElementById("accessGate");
  const appShell = document.getElementById("appShell");
  const form = document.getElementById("accessForm");
  const hostnameInput = document.getElementById("hostnameInput");
  const passkeyInput = document.getElementById("passkeyInput");
  const rememberPasskey = document.getElementById("rememberPasskey");
  const unlockBtn = document.getElementById("unlockBtn");
  const status = document.getElementById("accessStatus");
  const policy = window.ACCESS_POLICY;

  if (
    !gate ||
    !appShell ||
    !form ||
    !hostnameInput ||
    !passkeyInput ||
    !rememberPasskey ||
    !unlockBtn ||
    !status
  ) {
    return;
  }

  if (!window.crypto || !window.crypto.subtle) {
    setStatus("This browser does not support Web Crypto unlock checks.", true);
    return;
  }

  if (!policy || !Array.isArray(policy.entries)) {
    setStatus("Access policy missing. Check data/access.js.", true);
    return;
  }

  const rememberedHost = localStorage.getItem(ACCESS_CACHE_KEY) || "";
  const rememberedPasskey = normalizePasskey(localStorage.getItem(ACCESS_PASSKEY_KEY) || "");
  const rememberEnabled = localStorage.getItem(ACCESS_REMEMBER_KEY) === "1";
  const locationHost = normalizeHostname(window.location.hostname || "");
  if (locationHost && locationHost !== "localhost" && locationHost !== "127.0.0.1") {
    hostnameInput.value = locationHost;
  } else if (rememberedHost) {
    hostnameInput.value = rememberedHost;
  }
  if (rememberEnabled) {
    rememberPasskey.checked = true;
    passkeyInput.value = rememberedPasskey;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setStatus("");

    const hostname = normalizeHostname(hostnameInput.value);
    const passkey = normalizePasskey(passkeyInput.value);

    if (!hostname) {
      setStatus("Enter the hostname used for key generation.", true);
      hostnameInput.focus();
      return;
    }
    if (!passkey) {
      setStatus("Enter a valid passkey.", true);
      passkeyInput.focus();
      return;
    }

    const entry = policy.entries.find((item) => normalizeHostname(item.hostname || "") === hostname);
    if (!entry) {
      setStatus(
        "No access entry found for that hostname. Generate one with .secrets/device_keygen.py.",
        true,
      );
      return;
    }

    unlockBtn.disabled = true;
    unlockBtn.textContent = "Checking...";
    try {
      const isValid = await verifyPasskey(passkey, entry, policy.kdf || {});
      if (!isValid) {
        setStatus("Passkey rejected for this hostname.", true);
        return;
      }

      localStorage.setItem(ACCESS_CACHE_KEY, hostname);
      if (rememberPasskey.checked) {
        localStorage.setItem(ACCESS_REMEMBER_KEY, "1");
        localStorage.setItem(ACCESS_PASSKEY_KEY, passkey);
      } else {
        localStorage.removeItem(ACCESS_REMEMBER_KEY);
        localStorage.removeItem(ACCESS_PASSKEY_KEY);
      }
      setStatus(`Unlocked for ${entry.label || hostname}.`, false, true);
      await loadApp();
    } catch (error) {
      setStatus(`Unlock failed: ${error.message}`, true);
    } finally {
      unlockBtn.disabled = false;
      unlockBtn.textContent = "Unlock Pedal Architect";
    }
  });

  rememberPasskey.addEventListener("change", () => {
    if (rememberPasskey.checked) {
      localStorage.setItem(ACCESS_REMEMBER_KEY, "1");
      const passkey = normalizePasskey(passkeyInput.value);
      if (passkey) {
        localStorage.setItem(ACCESS_PASSKEY_KEY, passkey);
      }
      return;
    }
    localStorage.removeItem(ACCESS_REMEMBER_KEY);
    localStorage.removeItem(ACCESS_PASSKEY_KEY);
  });

  passkeyInput.addEventListener("input", () => {
    if (!rememberPasskey.checked) {
      return;
    }
    const passkey = normalizePasskey(passkeyInput.value);
    if (!passkey) {
      localStorage.removeItem(ACCESS_PASSKEY_KEY);
      return;
    }
    localStorage.setItem(ACCESS_PASSKEY_KEY, passkey);
  });

  async function loadApp() {
    await loadScript("app.js?v=21");
    gate.hidden = true;
    appShell.hidden = false;
  }

  function normalizeHostname(value) {
    return (value || "")
      .trim()
      .toLowerCase()
      .normalize("NFKC")
      .replace(/[^a-z0-9._-]+/g, "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "");
  }

  function normalizePasskey(value) {
    const compact = (value || "").toUpperCase().replace(/[^A-Z2-7]/g, "");
    if (!compact) {
      return "";
    }
    const groups = compact.match(/.{1,5}/g) || [];
    return groups.join("-");
  }

  async function verifyPasskey(passkey, entry, defaultKdf) {
    const iterations = clampInt(entry.iterations || defaultKdf.iterations || 210000, 50000, 600000);
    const dklen = clampInt(entry.dklen || defaultKdf.dklen || 32, 16, 64);
    const salt = base64ToBytes(entry.salt_b64 || "");
    const expected = base64ToBytes(entry.hash_b64 || "");
    if (!salt.length || !expected.length) {
      throw new Error("Invalid access policy entry.");
    }

    const passBytes = new TextEncoder().encode(passkey);
    const keyMaterial = await crypto.subtle.importKey("raw", passBytes, { name: "PBKDF2" }, false, [
      "deriveBits",
    ]);
    const bits = await crypto.subtle.deriveBits(
      {
        name: "PBKDF2",
        hash: "SHA-256",
        salt,
        iterations,
      },
      keyMaterial,
      dklen * 8,
    );
    const candidate = new Uint8Array(bits);
    return timingSafeEqual(candidate, expected);
  }

  function base64ToBytes(value) {
    try {
      const binary = atob(value);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i += 1) {
        bytes[i] = binary.charCodeAt(i);
      }
      return bytes;
    } catch (_error) {
      return new Uint8Array();
    }
  }

  function timingSafeEqual(left, right) {
    if (left.length !== right.length) {
      return false;
    }
    let mismatch = 0;
    for (let i = 0; i < left.length; i += 1) {
      mismatch |= left[i] ^ right[i];
    }
    return mismatch === 0;
  }

  function clampInt(value, min, max) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) {
      return min;
    }
    const rounded = Math.round(parsed);
    return Math.max(min, Math.min(max, rounded));
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = src;
      script.async = false;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Failed to load ${src}`));
      document.body.appendChild(script);
    });
  }

  function setStatus(message, isError = false, isSuccess = false) {
    status.textContent = message;
    status.classList.toggle("error", Boolean(isError));
    status.classList.toggle("success", Boolean(isSuccess));
  }
})();
