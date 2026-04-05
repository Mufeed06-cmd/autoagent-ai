@echo off
title AutoAgent AI
echo.
echo  ================================
echo    AutoAgent AI - Starting...
echo  ================================
echo.

start "AutoAgent API" /min C:\Users\mufee\AppData\Local\Programs\Python\Python311\python.exe server/api.py

timeout /t 3 /nobreak > nul

start "" "%~dp0frontend\index.html"

echo  AutoAgent is running!
echo  Browser should open automatically.
echo  Close this window anytime.
pause