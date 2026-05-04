Run `npm install` in `frontend/electron`.
Start the HUD with `npm start`.
The Electron app loads `renderer/index.html`.
The preload script connects to `ws://localhost:8000/ws`.
Requires the JARVIS server running on port 8000.
