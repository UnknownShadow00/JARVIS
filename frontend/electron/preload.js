const { contextBridge, ipcRenderer } = require("electron");

const messageCallbacks = new Set();

function emitMessage(payload) {
  for (const callback of messageCallbacks) {
    callback(payload);
  }
}

contextBridge.exposeInMainWorld("jarvis", {
  onMessage(callback) {
    if (typeof callback !== "function") {
      return () => {};
    }

    messageCallbacks.add(callback);

    const ipcListener = (_event, payload) => {
      callback(payload);
    };

    ipcRenderer.on("jarvis-message", ipcListener);

    return () => {
      messageCallbacks.delete(callback);
      ipcRenderer.removeListener("jarvis-message", ipcListener);
    };
  },
  send(channel, data) {
    ipcRenderer.send(channel, data);
  },
  connectWS() {
    const socket = new WebSocket("ws://localhost:8000/ws");

    socket.addEventListener("message", (event) => {
      try {
        const parsed = JSON.parse(event.data);
        emitMessage(parsed);
      } catch (_error) {
        emitMessage({
          type: "reply",
          reply: "Invalid message received from JARVIS server.",
        });
      }
    });

    socket.addEventListener("error", () => {
      emitMessage({
        type: "reply",
        reply: "Unable to connect to ws://localhost:8000/ws",
      });
    });

    return socket;
  },
});
