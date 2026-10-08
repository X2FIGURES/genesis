@echo off
REM Double-click on Windows to install (first run) and open Atelier Studio locally.
cd /d "%~dp0"
where py >nul 2>&1 && set PY=py -3 || set PY=python
%PY% -m pip install -e . 
if errorlevel 1 (
  echo Failed to install. Need Python 3.11+ from https://www.python.org/downloads/
  pause
  exit /b 1
)
%PY% -m atelier.desktop.app
if errorlevel 1 (
  echo.
  echo If Blender is missing: https://www.blender.org/download/
  echo Or set ATELIER_BLENDER to blender.exe
  pause
)
