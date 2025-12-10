const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  insert: (value) => ipcRenderer.invoke('bloom:insert', value),
  lookup: (value) => ipcRenderer.invoke('bloom:lookup', value),
});
