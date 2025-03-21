@echo off
title Ultimate PDF Tools

:: Start the application
python main.py
if %errorlevel% neq 0 (
    echo Error: Ultimate PDF Tools failed to start.
    echo Check if all files are present and try again.
    pause
    exit /b 1
) 