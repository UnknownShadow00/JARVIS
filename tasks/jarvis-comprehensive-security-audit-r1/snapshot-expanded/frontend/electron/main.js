const path = require("path");
const { app, BrowserWindow, ipcMain } = require("electron");

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 300,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  mainWindow.loadFile(path.join(__dirname, "renderer", "index.html"));

  mainWindow.on("close", () => {
    app.quit();
  });
}

app.whenReady().then(() => {
  createWindow();

  ipcMain.on("hide", () => {
    if (mainWindow) {
      mainWindow.hide();
    }
  });

  ipcMain.on("show", () => {
    if (mainWindow) {
      mainWindow.show();
    }
  });
});

app.on("window-all-closed", () => {
  app.quit();
});
