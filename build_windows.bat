@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo [1/3] Checking Python...
where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher ^(py^) was not found. Install Python 3.11 or newer from python.org and enable Add Python to PATH.
    exit /b 1
)
py -3 --version
if errorlevel 1 exit /b 1

echo [2/3] Installing dependencies...
py -3 -m pip install --upgrade pip
py -3 -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b %errorlevel%

echo [3/3] Building Wisely.exe...
py -3 -m PyInstaller --noconfirm --clean Wisely.spec
if errorlevel 1 exit /b %errorlevel%

rem Ship the AI key with the build so Wisely.exe works out of the box.
rem This does NOT bake the key into the compiled program: it copies your
rem local .env (never committed to git — see .gitignore) into dist\ as a
rem plain sibling file next to Wisely.exe, exactly what ai_engine.py
rem already looks for at startup. Anyone who has the .exe can also read
rem this .env in plain text, so only ship it in builds you control the
rem distribution of; it is not a substitute for a real backend if you
rem need the key to stay secret from end users.
if exist ".env" (
    copy /y ".env" "dist\.env" >nul
    echo Copied .env next to Wisely.exe - AI works immediately.
) else (
    echo No .env found in project root - Wisely.exe will show "AI unavailable"
    echo until a .env with GEMINI_API_KEY is placed next to it.
)

echo.
echo Build complete: %CD%\dist\Wisely.exe
endlocal
