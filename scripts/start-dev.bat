@echo off
REM Queqiao-arr Development Environment Startup Script (Windows)
REM This script calls PowerShell version for better Chinese support

powershell -ExecutionPolicy Bypass -File "%~dp0start-dev.ps1" %*

