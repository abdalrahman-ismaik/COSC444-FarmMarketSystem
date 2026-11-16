@echo off
title Farm-to-Market Setup
cd /d "%~dp0"
echo Installing Python packages...
set "FARM_PYTHON=python"
if exist "%~dp0..\.venv\Scripts\python.exe" set "FARM_PYTHON=%~dp0..\.venv\Scripts\python.exe"
"%FARM_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Python was not found or packages failed to install. Install Python 3.10+ from python.org and tick "Add python.exe to PATH".
  pause
  exit /b 1
)
echo.
"%FARM_PYTHON%" setup_database.py
echo.
pause
