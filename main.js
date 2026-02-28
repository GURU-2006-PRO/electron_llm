const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let pythonProcess = null;
let mainWindow = null;
let backendReady = false;

// Determine if running in development or production
const isDev = !app.isPackaged;

function getBackendPath() {
    if (isDev) {
        // Development: use Python script
        return {
            command: 'python',
            args: [path.join(__dirname, 'backend', 'api_server.py')],
            cwd: path.join(__dirname, 'backend')
        };
    } else {
        // Production: use bundled executable
        const exePath = path.join(process.resourcesPath, 'backend', 'api_server.exe');
        return {
            command: exePath,
            args: [],
            cwd: path.join(process.resourcesPath, 'backend')
        };
    }
}

function startPythonBackend() {
    const backend = getBackendPath();
    
    console.log('[BACKEND] Starting Python backend...');
    console.log('[BACKEND] Command:', backend.command);
    console.log('[BACKEND] Args:', backend.args);
    console.log('[BACKEND] CWD:', backend.cwd);
    
    try {
        pythonProcess = spawn(backend.command, backend.args, {
            cwd: backend.cwd,
            env: { ...process.env }
        });
        
        pythonProcess.stdout.on('data', (data) => {
            const output = data.toString();
            console.log(`[BACKEND] ${output}`);
            
            // Check if backend is ready
            if (output.includes('Running on')) {
                backendReady = true;
                console.log('[BACKEND] Backend is ready!');
            }
        });
        
        pythonProcess.stderr.on('data', (data) => {
            console.error(`[BACKEND ERROR] ${data}`);
        });
        
        pythonProcess.on('close', (code) => {
            console.log(`[BACKEND] Process exited with code ${code}`);
            backendReady = false;
        });
        
        pythonProcess.on('error', (err) => {
            console.error('[BACKEND] Failed to start:', err);
        });
        
    } catch (error) {
        console.error('[BACKEND] Error starting backend:', error);
    }
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1200,
        minHeight: 700,
        icon: path.join(__dirname, 'assets', 'icon.png'),
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true
        },
        backgroundColor: '#1a1a2e',
        show: false,
        frame: true,
        titleBarStyle: 'default'
    });
    
    // Load the app
    mainWindow.loadFile('index_simple.html');
    
    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        
        // Open DevTools in development
        if (isDev) {
            mainWindow.webContents.openDevTools();
        }
    });
    
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// Wait for backend to be ready, then create window
function waitForBackendAndCreateWindow() {
    let attempts = 0;
    const maxAttempts = 30; // 30 seconds timeout
    
    const checkBackend = setInterval(() => {
        attempts++;
        
        if (backendReady) {
            clearInterval(checkBackend);
            console.log('[APP] Backend ready, creating window...');
            createWindow();
        } else if (attempts >= maxAttempts) {
            clearInterval(checkBackend);
            console.error('[APP] Backend failed to start in time');
            // Create window anyway, user will see connection error
            createWindow();
        } else {
            console.log(`[APP] Waiting for backend... (${attempts}/${maxAttempts})`);
        }
    }, 1000);
}

// App lifecycle
app.on('ready', () => {
    console.log('[APP] Electron app ready');
    console.log('[APP] Is packaged:', app.isPackaged);
    console.log('[APP] Resources path:', process.resourcesPath);
    
    // Start backend first
    startPythonBackend();
    
    // Wait for backend, then create window
    waitForBackendAndCreateWindow();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('quit', () => {
    console.log('[APP] Quitting, killing backend...');
    if (pythonProcess) {
        pythonProcess.kill();
    }
});

// Handle backend restart request
ipcMain.on('restart-backend', () => {
    console.log('[APP] Restarting backend...');
    if (pythonProcess) {
        pythonProcess.kill();
    }
    setTimeout(() => {
        startPythonBackend();
    }, 2000);
});
