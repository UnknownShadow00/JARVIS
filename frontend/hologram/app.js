import * as THREE from "three";

const DEFAULT_COLOR = "#00d4ff";
const EMOTION_COLORS = {
  success: "#00ff88",
  concern: "#ff4444",
  thinking: "#ffaa00",
  neutral: DEFAULT_COLOR
};
const WS_URL = "ws://localhost:8000/ws";
const RECONNECT_DELAY_MS = 3000;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x000000);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 4;

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setPixelRatio(window.devicePixelRatio || 1);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.domElement.style.width = "100vw";
renderer.domElement.style.height = "100vh";
document.body.appendChild(renderer.domElement);

const overlay = document.createElement("div");
overlay.style.position = "absolute";
overlay.style.bottom = "0";
overlay.style.left = "0";
overlay.style.width = "100%";
overlay.style.minHeight = "20vh";
overlay.style.padding = "20px";
overlay.style.boxSizing = "border-box";
overlay.style.fontSize = "2rem";
overlay.style.color = "#ffffff";
overlay.style.background = "rgba(0,0,200,0.15)";
overlay.style.fontFamily = "monospace";
overlay.style.display = "none";
overlay.style.alignItems = "center";
document.body.appendChild(overlay);

const group = new THREE.Group();
scene.add(group);

const ringMaterial = new THREE.MeshBasicMaterial({ color: DEFAULT_COLOR, wireframe: true });
const coreMaterial = new THREE.MeshBasicMaterial({ color: DEFAULT_COLOR, wireframe: true });

const ring = new THREE.Mesh(new THREE.TorusGeometry(1.6, 0.12, 16, 96), ringMaterial);
const core = new THREE.Mesh(new THREE.IcosahedronGeometry(0.65, 0), coreMaterial);

group.add(ring);
group.add(core);

const ambientLight = new THREE.AmbientLight(0xffffff, 1);
scene.add(ambientLight);

function setOverlayText(text) {
  const nextText = typeof text === "string" ? text.trim() : "";
  overlay.textContent = nextText;
  overlay.style.display = nextText ? "flex" : "none";
}

function setEmotionColor(emotion) {
  const normalizedEmotion = typeof emotion === "string" ? emotion.toLowerCase() : "neutral";
  coreMaterial.color.set(EMOTION_COLORS[normalizedEmotion] || DEFAULT_COLOR);
}

function handleMessage(rawData) {
  let payload;

  try {
    payload = JSON.parse(rawData);
  } catch (error) {
    console.warn("Ignoring invalid websocket payload.", error);
    return;
  }

  if (!payload || typeof payload !== "object") {
    return;
  }

  if (payload.type === "reply") {
    setOverlayText(payload.reply || payload.text || "");
    return;
  }

  if (payload.type === "emotion") {
    setEmotionColor(payload.emotion);
  }
}

let socket = null;
let reconnectTimer = null;

function scheduleReconnect() {
  if (reconnectTimer !== null) {
    return;
  }

  reconnectTimer = window.setTimeout(() => {
    reconnectTimer = null;
    connectWebSocket();
  }, RECONNECT_DELAY_MS);
}

function connectWebSocket() {
  if (socket) {
    socket.onopen = null;
    socket.onmessage = null;
    socket.onclose = null;
    socket.onerror = null;
    try {
      socket.close();
    } catch (error) {
      console.warn("Failed to close stale websocket.", error);
    }
  }

  try {
    socket = new WebSocket(WS_URL);
  } catch (error) {
    console.warn("WebSocket connection failed.", error);
    scheduleReconnect();
    return;
  }

  socket.onmessage = (event) => {
    handleMessage(event.data);
  };

  socket.onerror = () => {
    console.warn("WebSocket error on hologram display.");
  };

  socket.onclose = () => {
    scheduleReconnect();
  };
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

window.addEventListener("resize", onWindowResize);

function animate() {
  window.requestAnimationFrame(animate);
  core.rotation.x += 0.005;
  core.rotation.y += 0.01;
  ring.rotation.z += 0.003;
  group.rotation.y += 0.002;
  renderer.render(scene, camera);
}

setEmotionColor("neutral");
connectWebSocket();
animate();
