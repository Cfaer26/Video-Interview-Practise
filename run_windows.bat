@echo off
REM Download and install Python 3 if not installed: https://www.python.org/downloads/
REM Download and extract ffmpeg: https://ffmpeg.org/download.html
REM Add ffmpeg/bin to your PATH variable!

IF NOT EXIST venv (
    python -m venv venv
)
call venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

where ffmpeg >nul 2>nul
IF %errorlevel% NEQ 0 (
    echo.
    echo "ERROR: ffmpeg not found! Please install ffmpeg and add it to your PATH."
    echo See https://ffmpeg.org/download.html
    pause
    exit /b
)

set FLASK_APP=app.py
python app.py
pause