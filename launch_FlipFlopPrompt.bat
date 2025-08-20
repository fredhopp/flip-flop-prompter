@echo off
REM FlipFlopPrompt Launcher
REM This batch file activates the virtual environment and launches FlipFlopPrompt

echo Starting FlipFlopPrompt...

REM Change to the project directory
cd /d "Z:\Dev\FlipFlopPrompt"

REM Check if the project directory exists
if not exist "Z:\Dev\FlipFlopPrompt" (
    echo Error: Project directory not found at Z:\Dev\FlipFlopPrompt
    echo Please update the path in this batch file if the project has moved.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found at .venv\Scripts\activate.bat
    echo Please ensure the virtual environment is set up correctly.
    pause
    exit /b 1
)

REM Activate virtual environment and launch the application
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated. Launching FlipFlopPrompt GUI...
python main.py --gui

REM Pause to show any error messages
if errorlevel 1 (
    echo.
    echo FlipFlopPrompt exited with an error.
    pause
)
