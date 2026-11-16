@echo off
cd /d "%~dp0"
set "FARM_PYTHON=python"
set "FARM_PYTHONW=pythonw"
if exist "%~dp0..\.venv\Scripts\python.exe" (
  set "FARM_PYTHON=%~dp0..\.venv\Scripts\python.exe"
  set "FARM_PYTHONW=%~dp0..\.venv\Scripts\pythonw.exe"
)
"%FARM_PYTHON%" -c "import pymysql, PIL, dotenv, langchain_google_genai" 2>nul
if errorlevel 1 (
  echo Packages are missing. Please double-click setup.bat first.
  pause
  exit /b 1
)
start "" "%FARM_PYTHONW%" app.py
