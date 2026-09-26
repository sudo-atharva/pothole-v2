@echo off
REM Installs Python dependencies for the road damage assessment apps.
REM Requires Python 3.8+ on PATH (tick "Add python.exe to PATH" in the Python installer).

where python >nul 2>nul || (
    echo Python not found on PATH. Install it from https://www.python.org/downloads/ and re-run.
    pause
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install ultralytics opencv-python pyserial pillow numpy || (
    echo Install failed, see errors above.
    pause
    exit /b 1
)

echo.
echo Done. Start the GUI with:  python gui_app.py
pause
