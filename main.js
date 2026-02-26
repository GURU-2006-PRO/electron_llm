const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    title: 'InsightX - Leadership Analytics'
  });

  mainWindow.loadFile('index_simple.html');
  mainWindow.webContents.openDevTools();

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

function startPythonBackend() {
  // Start Python Flask server
  console.log('Starting Python backend...');
  pythonProcess = spawn('python', ['backend/app_simple.py']);
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python: ${data}`);
  });
  
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });
  
  pythonProcess.on('error', (error) => {
    console.error('Failed to start Python backend:', error);
    console.log('Please start backend manually: cd backend && python app.py');
  });
}

app.whenReady().then(() => {
  createWindow();
  startPythonBackend();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (pythonProcess) {
    pythonProcess.kill();
  }
  if (process.platform !== 'darwin') app.quit();
});
