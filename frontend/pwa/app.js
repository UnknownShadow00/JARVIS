(function () {
  var STORAGE_KEY = "jarvis_server";
  var GLASSES_MODE_KEY = "jarvis_glasses_mode";
  var AUDIO_OUTPUT_KEY = "jarvis_audio_output";
  var DEFAULT_WS_URL = "ws://localhost:8000/ws";
  var MAX_RETRY_DELAY = 30000;
  var LONG_PRESS_MS = 700;
  var GLASSES_RESTART_DELAY_MS = 800;
  var GLASSES_SILENCE_MS = 8000;
  var GLASSES_NOISE_WORDS = {
    hmm: true,
    uh: true,
    um: true,
    hmmm: true,
    uhh: true,
    umm: true
  };

  var state = {
    socket: null,
    reconnectTimer: null,
    retryDelay: 1000,
    isConnected: false,
    recognition: null,
    isListening: false,
    longPressTimer: null,
    silenceTimer: null,
    restartTimer: null,
    recognitionResultReceived: false,
    awaitingReply: false,
    restartOnEnd: false,
    glassesMode: localStorage.getItem(GLASSES_MODE_KEY) === "true",
    audioOutput: localStorage.getItem(AUDIO_OUTPUT_KEY) || "default",
    audioOutputProbe: new Audio()
  };

  var elements = {
    title: document.getElementById("title"),
    connectionDot: document.getElementById("connectionDot"),
    connectionLabel: document.getElementById("connectionLabel"),
    statusLine: document.getElementById("statusLine"),
    transcript: document.getElementById("transcript"),
    arcReactor: document.getElementById("arcReactor"),
    composer: document.getElementById("composer"),
    input: document.getElementById("messageInput"),
    micButton: document.getElementById("micButton"),
    glassesToggle: document.getElementById("glasses-toggle"),
    audioOutput: document.getElementById("audio-output")
  };

  function getIdleStatus() {
    if (state.isListening && state.glassesMode) {
      return "Listening (Glasses Mode)...";
    }
    if (state.isListening) {
      return "Listening...";
    }
    return state.isConnected ? "Connected" : "Disconnected";
  }

  function getServerUrl() {
    var saved = localStorage.getItem(STORAGE_KEY) || DEFAULT_WS_URL;
    return saved.trim() || DEFAULT_WS_URL;
  }

  function setServerUrl(url) {
    var next = (url || "").trim();
    if (!next) {
      return;
    }
    localStorage.setItem(STORAGE_KEY, next);
  }

  function normalizeWsUrl(rawUrl) {
    if (!rawUrl) {
      return DEFAULT_WS_URL;
    }

    if (rawUrl.indexOf("http://") === 0) {
      rawUrl = "ws://" + rawUrl.slice("http://".length);
    } else if (rawUrl.indexOf("https://") === 0) {
      rawUrl = "wss://" + rawUrl.slice("https://".length);
    }

    if (rawUrl.indexOf("ws://") !== 0 && rawUrl.indexOf("wss://") !== 0) {
      rawUrl = "ws://" + rawUrl.replace(/^\/+/, "");
    }

    if (!/\/ws(?:\/)?$/i.test(rawUrl)) {
      rawUrl = rawUrl.replace(/\/+$/, "") + "/ws";
    }

    return rawUrl;
  }

  function getRestUrl(wsUrl) {
    return normalizeWsUrl(wsUrl)
      .replace(/^ws:\/\//i, "http://")
      .replace(/^wss:\/\//i, "https://")
      .replace(/\/ws\/?$/i, "/chat");
  }

  function setConnection(isConnected) {
    state.isConnected = isConnected;
    elements.connectionDot.classList.toggle("connected", isConnected);
    elements.connectionLabel.textContent = isConnected ? "Connected" : "Disconnected";
    if (!isConnected && !state.isListening) {
      setStatus("Disconnected");
    }
  }

  function setStatus(label) {
    elements.statusLine.textContent = label;
    elements.arcReactor.classList.toggle("active", /Listening|Processing|Speaking/i.test(label));
  }

  function updateGlassesToggle() {
    elements.glassesToggle.textContent = state.glassesMode ? "Glasses ON" : "Glasses OFF";
    elements.glassesToggle.setAttribute("aria-pressed", state.glassesMode ? "true" : "false");
  }

  function updateAudioOutputSelection() {
    elements.audioOutput.value = state.audioOutput;
  }

  function clearSilenceTimer() {
    if (state.silenceTimer) {
      window.clearTimeout(state.silenceTimer);
      state.silenceTimer = null;
    }
  }

  function clearRestartTimer() {
    if (state.restartTimer) {
      window.clearTimeout(state.restartTimer);
      state.restartTimer = null;
    }
  }

  function isMeaningfulTranscript(text) {
    var trimmed = (text || "").trim();
    var compact = trimmed.toLowerCase().replace(/[^\w\s]/g, "");
    var words = compact.split(/\s+/).filter(Boolean);

    if (!trimmed) {
      return false;
    }

    if (!state.glassesMode) {
      return true;
    }

    if (words.length >= 2 || trimmed.length >= 8) {
      return true;
    }

    if (words.length === 1) {
      if (GLASSES_NOISE_WORDS[words[0]]) {
        return false;
      }
      if (words[0].length < 3) {
        return false;
      }
    }

    return false;
  }

  function scheduleRecognitionRestart(delay) {
    if (!state.glassesMode || !state.recognition || state.awaitingReply) {
      return;
    }

    clearRestartTimer();
    state.restartTimer = window.setTimeout(function () {
      state.restartTimer = null;
      if (state.glassesMode) {
        startRecognition("Listening (Glasses Mode)...");
      }
    }, delay);
  }

  function startSilenceTimer() {
    clearSilenceTimer();
    if (!state.glassesMode || !state.recognition) {
      return;
    }

    state.silenceTimer = window.setTimeout(function () {
      state.silenceTimer = null;
      if (!state.glassesMode || !state.recognition || !state.isListening || state.recognitionResultReceived) {
        return;
      }

      state.restartOnEnd = true;
      try {
        state.recognition.stop();
      } catch (error) {
        scheduleRecognitionRestart(0);
      }
    }, GLASSES_SILENCE_MS);
  }

  function startRecognition(statusText) {
    if (!state.recognition) {
      return;
    }

    clearRestartTimer();
    if (state.isListening) {
      return;
    }

    state.recognitionResultReceived = false;
    state.restartOnEnd = false;

    try {
      state.recognition.start();
      setStatus(statusText || (state.glassesMode ? "Listening (Glasses Mode)..." : "Listening..."));
    } catch (error) {
      setStatus(statusText || getIdleStatus());
    }
  }

  function setGlassesMode(enabled) {
    state.glassesMode = !!enabled;
    localStorage.setItem(GLASSES_MODE_KEY, state.glassesMode ? "true" : "false");
    updateGlassesToggle();
    clearSilenceTimer();
    clearRestartTimer();
    state.awaitingReply = false;
    state.restartOnEnd = false;

    if (state.glassesMode) {
      setStatus("Glasses Mode enabled");
    } else if (state.isListening) {
      try {
        state.recognition.stop();
      } catch (error) {
      }
      setStatus(getIdleStatus());
    } else {
      setStatus(getIdleStatus());
    }
  }

  async function applyAudioOutputSelection(selectedValue) {
    state.audioOutput = selectedValue === "glasses" ? "glasses" : "default";
    localStorage.setItem(AUDIO_OUTPUT_KEY, state.audioOutput);
    updateAudioOutputSelection();

    if (state.audioOutput !== "glasses") {
      setStatus(getIdleStatus());
      return;
    }

    if (typeof state.audioOutputProbe.setSinkId !== "function") {
      setStatus("Manual audio routing required for glasses output");
      return;
    }

    try {
      await state.audioOutputProbe.setSinkId("default");
      setStatus("Audio output routed to selected device");
    } catch (error) {
      setStatus("Manual audio routing required for glasses output");
    }
  }

  function addMessage(role, text) {
    var bubble = document.createElement("div");
    bubble.className = "message " + role;
    bubble.textContent = text;
    elements.transcript.appendChild(bubble);
    elements.transcript.scrollTop = elements.transcript.scrollHeight;
  }

  function speakReply(text) {
    if (!("speechSynthesis" in window) || !text) {
      if (state.glassesMode) {
        state.awaitingReply = false;
        scheduleRecognitionRestart(GLASSES_RESTART_DELAY_MS);
      }
      setStatus(getIdleStatus());
      return;
    }

    window.speechSynthesis.cancel();
    var utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.onstart = function () {
      setStatus("Speaking...");
    };
    utterance.onend = function () {
      state.awaitingReply = false;
      if (state.glassesMode) {
        scheduleRecognitionRestart(GLASSES_RESTART_DELAY_MS);
        return;
      }
      setStatus(getIdleStatus());
    };
    utterance.onerror = function () {
      state.awaitingReply = false;
      if (state.glassesMode) {
        scheduleRecognitionRestart(GLASSES_RESTART_DELAY_MS);
        return;
      }
      setStatus(getIdleStatus());
    };
    window.speechSynthesis.speak(utterance);
  }

  function handleReply(payload) {
    if (!payload || !payload.reply) {
      return;
    }
    addMessage("jarvis", payload.reply);
    speakReply(payload.reply);
  }

  function handleSocketMessage(event) {
    var payload;

    try {
      payload = JSON.parse(event.data);
    } catch (error) {
      return;
    }

    if (payload.type === "listening") {
      setStatus(payload.active ? (state.glassesMode ? "Listening (Glasses Mode)..." : "Listening...") : getIdleStatus());
      return;
    }

    if (payload.type === "reply") {
      setStatus("Processing...");
      handleReply(payload);
    }
  }

  function scheduleReconnect() {
    if (state.reconnectTimer) {
      return;
    }

    var delay = state.retryDelay;
    state.reconnectTimer = window.setTimeout(function () {
      state.reconnectTimer = null;
      connectSocket();
    }, delay);
    state.retryDelay = Math.min(state.retryDelay * 2, MAX_RETRY_DELAY);
  }

  function connectSocket() {
    var url = normalizeWsUrl(getServerUrl());

    if (state.socket) {
      state.socket.onopen = null;
      state.socket.onclose = null;
      state.socket.onerror = null;
      state.socket.onmessage = null;
      try {
        state.socket.close();
      } catch (error) {
      }
    }

    setStatus("Connecting...");

    try {
      state.socket = new WebSocket(url);
    } catch (error) {
      setConnection(false);
      scheduleReconnect();
      return;
    }

    state.socket.onopen = function () {
      state.retryDelay = 1000;
      setConnection(true);
      setStatus("Connected");
    };

    state.socket.onmessage = handleSocketMessage;

    state.socket.onerror = function () {
      setConnection(false);
    };

    state.socket.onclose = function () {
      setConnection(false);
      scheduleReconnect();
    };
  }

  async function sendRestFallback(text) {
    var response = await fetch(getRestUrl(getServerUrl()), {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: text })
    });

    if (!response.ok) {
      throw new Error("Fallback request failed");
    }

    return response.json();
  }

  async function sendMessage(text) {
    var trimmed = (text || "").trim();
    if (!trimmed) {
      return;
    }

    addMessage("user", trimmed);
    elements.input.value = "";
    setStatus("Processing...");

    if (state.socket && state.socket.readyState === WebSocket.OPEN) {
      state.socket.send(JSON.stringify({ message: trimmed }));
      return;
    }

    try {
      var fallbackPayload = await sendRestFallback(trimmed);
      handleReply(fallbackPayload);
    } catch (error) {
      addMessage("jarvis", "Connection unavailable. Check the server URL and try again.");
      setStatus("Disconnected");
    }
  }

  function setupRecognition() {
    var SpeechRecognitionCtor = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognitionCtor) {
      elements.micButton.disabled = true;
      elements.micButton.textContent = "N/A";
      return;
    }

    var recognition = new SpeechRecognitionCtor();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.continuous = false;

    recognition.onstart = function () {
      state.isListening = true;
      state.recognitionResultReceived = false;
      elements.micButton.classList.add("listening");
      setStatus(state.glassesMode ? "Listening (Glasses Mode)..." : "Listening...");
      startSilenceTimer();
    };

    recognition.onresult = function (event) {
      var transcript = "";
      if (event.results && event.results[0] && event.results[0][0]) {
        transcript = event.results[0][0].transcript || "";
      }
      state.recognitionResultReceived = true;
      clearSilenceTimer();

      if (!isMeaningfulTranscript(transcript)) {
        state.awaitingReply = false;
        return;
      }

      state.awaitingReply = state.glassesMode;
      sendMessage(transcript);
    };

    recognition.onerror = function () {
      state.isListening = false;
      clearSilenceTimer();
      elements.micButton.classList.remove("listening");
      if (state.glassesMode && !state.awaitingReply) {
        scheduleRecognitionRestart(GLASSES_RESTART_DELAY_MS);
        return;
      }
      setStatus(getIdleStatus());
    };

    recognition.onend = function () {
      state.isListening = false;
      clearSilenceTimer();
      elements.micButton.classList.remove("listening");
      if (state.glassesMode) {
        if (state.restartOnEnd) {
          state.restartOnEnd = false;
          scheduleRecognitionRestart(0);
          return;
        }
        if (!state.awaitingReply) {
          scheduleRecognitionRestart(GLASSES_RESTART_DELAY_MS);
          return;
        }
      }
      if (/^Listening/.test(elements.statusLine.textContent)) {
        setStatus(getIdleStatus());
      }
    };

    state.recognition = recognition;
  }

  function promptForServerUrl() {
    var current = normalizeWsUrl(getServerUrl());
    var next = window.prompt("Enter JARVIS WebSocket URL", current);
    if (!next) {
      return;
    }
    setServerUrl(normalizeWsUrl(next));
    connectSocket();
  }

  function setupLongPress() {
    function startPress() {
      clearTimeout(state.longPressTimer);
      state.longPressTimer = window.setTimeout(promptForServerUrl, LONG_PRESS_MS);
    }

    function cancelPress() {
      clearTimeout(state.longPressTimer);
    }

    elements.title.addEventListener("touchstart", startPress, { passive: true });
    elements.title.addEventListener("touchend", cancelPress);
    elements.title.addEventListener("touchcancel", cancelPress);
    elements.title.addEventListener("mousedown", startPress);
    elements.title.addEventListener("mouseup", cancelPress);
    elements.title.addEventListener("mouseleave", cancelPress);
  }

  function registerServiceWorker() {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("./sw.js").catch(function () {
      });
    }
  }

  function bindEvents() {
    elements.composer.addEventListener("submit", function (event) {
      event.preventDefault();
      sendMessage(elements.input.value);
    });

    elements.glassesToggle.addEventListener("click", function () {
      setGlassesMode(!state.glassesMode);
    });

    elements.audioOutput.addEventListener("change", function (event) {
      applyAudioOutputSelection(event.target.value);
    });

    elements.micButton.addEventListener("click", function () {
      if (state.recognition) {
        startRecognition(state.glassesMode ? "Listening (Glasses Mode)..." : "Listening...");
      }
    });
  }

  addMessage("jarvis", "JARVIS mobile link ready.");
  updateGlassesToggle();
  updateAudioOutputSelection();
  setupRecognition();
  setupLongPress();
  bindEvents();
  registerServiceWorker();
  connectSocket();
  applyAudioOutputSelection(state.audioOutput);
})();
