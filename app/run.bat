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

:check_database
"%FARM_PYTHON%" check_database.py
if errorlevel 2 goto start_local_demo
if errorlevel 1 goto database_unavailable
goto launch_app

:start_local_demo
if not exist "%~dp0..\.local\start-demo.ps1" goto database_unavailable
echo Starting this PC's isolated demo database...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\.local\start-demo.ps1"
timeout /t 5 /nobreak >nul
"%FARM_PYTHON%" check_database.py
if errorlevel 1 goto database_unavailable
goto launch_app

:database_unavailable
echo.
echo Fix the issue reported above, then choose Retry.
echo For a connection failure, start MySQL and check DB_HOST and DB_PORT in app\.env.
choice /c RQ /n /m "R = retry database check, Q = quit: "
if errorlevel 2 exit /b 1
goto check_database

:launch_app

start "" "%FARM_PYTHONW%" app.py
