@echo off
setlocal enabledelayedexpansion

:: 1. Find the Current Local IP (IPv4)
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set "IP=%%a"
    set "IP=!IP: =!"
    goto :found
)
:found

echo ----------------------------------------------------
echo [INFO] Detected Local IP: !IP!
echo ----------------------------------------------------

:: 2. Start Django on 0.0.0.0:8000
echo [STATUS] Starting Backend on http://!IP!:8000
echo [WEB] Link for Browser: http://localhost:8000
echo [MOBILE] Link for Phone: http://!IP!:8000
echo ----------------------------------------------------

python manage.py runserver 0.0.0.0:8000
