const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { interpreter } = require('node-calls-python');

// Load the Python module once and reuse it for insert/lookup.
const py = interpreter;
const bloomModule = py.importSync(path.join(__dirname, 'python', 'bloom'));

function createWindow() {
  const win = new BrowserWindow({
    width: 420,
    height: 420,
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

ipcMain.handle('bloom:insert', (_event, value) => {
  if (!value) return { ok: false, message: 'Please enter a value.' };
  try {
    py.callSync(bloomModule, 'insert', value);
    return { ok: true, message: `"${value}" inserted.` };
  } catch (err) {
    return { ok: false, message: err.message || 'Insert failed.' };
  }
});

ipcMain.handle('bloom:lookup', (_event, value) => {
  if (!value) return { ok: false, message: 'Please enter a value.' };
  try {
    const exists = py.callSync(bloomModule, 'lookup', value);
    const message = exists
      ? `"${value}" is probably in the set.`
      : `"${value}" is probably not in the set.`;
    return { ok: true, exists, message };
  } catch (err) {
    return { ok: false, message: err.message || 'Lookup failed.' };
  }
});
