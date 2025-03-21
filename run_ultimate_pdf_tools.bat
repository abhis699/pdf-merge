@echo off
title Ultimate PDF Tools

echo Checking for Python installation...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Attempting to install using winget...
    winget install Python.Python.3.11
    if %errorlevel% neq 0 (
        echo Failed to install Python using winget.
        echo Please install Python manually from https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation
        pause
        exit /b 1
    )
    echo Python installed successfully!
)

echo Checking for required dependencies...

:: Check for PyQt5
python -c "import PyQt5" > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyQt5...
    pip install PyQt5==5.15.9
    if %errorlevel% neq 0 (
        echo Failed to install PyQt5. Please run: pip install PyQt5==5.15.9
        pause
        exit /b 1
    )
) else (
    echo PyQt5 is already installed.
)

:: Check for PyPDF2
python -c "import PyPDF2" > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyPDF2...
    pip install PyPDF2==3.0.1
    if %errorlevel% neq 0 (
        echo Failed to install PyPDF2. Please run: pip install PyPDF2==3.0.1
        pause
        exit /b 1
    )
) else (
    echo PyPDF2 is already installed.
)

:: Check for pikepdf
python -c "import pikepdf" > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pikepdf...
    pip install pikepdf==7.2.0
    
    :: Double-check if pikepdf was installed successfully
    python -c "import pikepdf" > nul 2>&1
    if %errorlevel% neq 0 (
        echo Failed to install pikepdf. Please run: pip install pikepdf==7.2.0
        pause
        exit /b 1
    ) else (
        echo pikepdf installed successfully.
    )
) else (
    echo pikepdf is already installed.
)

:: Check for PyMuPDF (fitz)
python -c "import fitz" > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyMuPDF...
    pip install PyMuPDF==1.22.5
    if %errorlevel% neq 0 (
        echo Failed to install PyMuPDF. Please run: pip install PyMuPDF==1.22.5
        pause
        exit /b 1
    )
) else (
    echo PyMuPDF is already installed.
)

echo All dependencies are installed.
echo Starting Ultimate PDF Tools...

python main.py

if %errorlevel% neq 0 (
    echo Error: Ultimate PDF Tools failed to start.
    echo Check if all files are present and try again.
    pause
    exit /b 1
)

exit /b 0 