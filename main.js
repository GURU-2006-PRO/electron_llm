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
        // Production: backend is in extraResources
        let backendPath;
        let backendCwd;
        
        // Primary location: extraResources (recommended by electron-builder)
        const extraResourcesPath = path.join(process.resourcesPath, 'backend', 'dist', 'api_server.exe');
        
        // Fallback locations
        const possiblePaths = [
            extraResourcesPath,
            path.join(process.resourcesPath, 'app.asar.unpacked', 'backend', 'dist', 'api_server.exe'),
            path.join(__dirname, 'backend', 'dist', 'api_server.exe'),
            path.join(__dirname, '..', 'backend', 'dist', 'api_server.exe'),
        ];
        
        console.log('[BACKEND] ========================================');
        console.log('[BACKEND] Searching for backend executable...');
        console.log('[BACKEND] __dirname:', __dirname);
        console.log('[BACKEND] process.resourcesPath:', process.resourcesPath);
        console.log('[BACKEND] ========================================');
        
        for (const testPath of possiblePaths) {
            console.log('[BACKEND] Trying:', testPath);
            if (fs.existsSync(testPath)) {
                backendPath = testPath;
                backendCwd = path.dirname(testPath);
                console.log('[BACKEND] ✓ Found at:', backendPath);
                console.log('[BACKEND] Working directory:', backendCwd);
                break;
            } else {
                console.log('[BACKEND] ✗ Not found');
            }
        }
        
        if (!backendPath) {
            console.error('[BACKEND] ========================================');
            console.error('[BACKEND] ERROR: Backend executable not found!');
            console.error('[BACKEND] ========================================');
            console.error('[BACKEND] Searched in:');
            possiblePaths.forEach(p => console.error('[BACKEND]   -', p));
            
            // List what's actually in resources
            try {
                console.log('[BACKEND] ========================================');
                console.log('[BACKEND] Listing actual directory contents:');
                console.log('[BACKEND] Resources folder:', fs.readdirSync(process.resourcesPath));
                
                const backendDir = path.join(process.resourcesPath, 'backend');
                if (fs.existsSync(backendDir)) {
                    console.log('[BACKEND] Backend folder:', fs.readdirSync(backendDir));
                    
                    const distDir = path.join(backendDir, 'dist');
                    if (fs.existsSync(distDir)) {
                        console.log('[BACKEND] Dist folder:', fs.readdirSync(distDir));
                    }
                }
                console.log('[BACKEND] ========================================');
            } catch (e) {
                console.error('[BACKEND] Could not list directories:', e.message);
            }
        }
        
        return {
            command: backendPath,
            args: [],
            cwd: backendCwd
        };
    }
}

function startPythonBackend() {
    const backend = getBackendPath();
    
    console.log('[BACKEND] ========================================');
    console.log('[BACKEND] Starting Python backend...');
    console.log('[BACKEND] Command:', backend.command);
    console.log('[BACKEND] Args:', backend.args);
    console.log('[BACKEND] CWD:', backend.cwd);
    console.log('[BACKEND] ========================================');
    
    // Check if backend file exists
    if (!isDev && !fs.existsSync(backend.command)) {
        console.error('[BACKEND] ERROR: Backend executable not found!');
        console.error('[BACKEND] Expected location:', backend.command);
        console.error('[BACKEND] Please ensure api_server.exe is in the backend/dist folder');
        return;
    }
    
    try {
        pythonProcess = spawn(backend.command, backend.args, {
            cwd: backend.cwd,
            env: { ...process.env },
            stdio: ['ignore', 'pipe', 'pipe']
        });
        
        console.log('[BACKEND] Process spawned with PID:', pythonProcess.pid);
        
        pythonProcess.stdout.on('data', (data) => {
            const output = data.toString();
            console.log(`[BACKEND STDOUT] ${output}`);
            
            // Check if backend is ready
            if (output.includes('Running on')) {
                backendReady = true;
                console.log('[BACKEND] ✓ Backend is ready!');
            }
        });
        
        pythonProcess.stderr.on('data', (data) => {
            const error = data.toString();
            console.error(`[BACKEND STDERR] ${error}`);
        });
        
        pythonProcess.on('close', (code) => {
            console.log(`[BACKEND] Process exited with code ${code}`);
            backendReady = false;
            
            if (code !== 0) {
                console.error('[BACKEND] Backend crashed! Check logs above for errors.');
            }
        });
        
        pythonProcess.on('error', (err) => {
            console.error('[BACKEND] Failed to start backend process:');
            console.error('[BACKEND] Error:', err.message);
            console.error('[BACKEND] Code:', err.code);
            
            if (err.code === 'ENOENT') {
                console.error('[BACKEND] Backend executable not found at:', backend.command);
            }
        });
        
    } catch (error) {
        console.error('[BACKEND] Exception while starting backend:', error);
    }
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1200,
        minHeight: 700,
        icon: path.join(__dirname, 'assets', 'logo.png'),
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
