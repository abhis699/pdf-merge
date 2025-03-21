@echo off
echo PDF Merger by Abhishek Shukla
echo =============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in your PATH.
    echo Please install Python 3.6+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import PyQt5, PyPDF2" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing required dependencies...
    echo This may take a moment...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Error installing dependencies. 
        echo Please run the following command manually:
        echo pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo Dependencies installed successfully!
) else (
    echo All dependencies are already installed.
)

echo.
echo Starting PDF Merger...
echo.
python pdf_merger.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error running PDF Merger.
    echo If this is your first time running the application, make sure all dependencies are installed.
    echo.
    pause
) 