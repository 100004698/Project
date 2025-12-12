@echo off
REM Launch the library backend and GUI in separate windows
pushd "%~dp0"








exit /b 0popdstart "Library GUI" cmd /k "python -u ""%~dp0frontend\gui.py"""
nREM Start GUI in a new cmd window (keeps window open)start "Library Backend" cmd /k "python -u ""%~dp0backend\app.py"""nREM Start backend in a new cmd window (keeps window open for logs)