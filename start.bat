@echo off
echo ============================================
echo    AutoAgent AI - Starting...
echo ============================================
echo.
echo [1/3] Installing dependencies...
pip install flask flask-cors psutil send2trash winshell ollama
echo.
echo [2/3] Making sure Ollama is running...
start /B ollama serve
timeout /t 2 /nobreak > nul
echo.
echo [3/3] Starting AutoAgent AI Dashboard...
echo.
echo    Open your browser at: http://localhost:5000
echo.
python app.py
pause