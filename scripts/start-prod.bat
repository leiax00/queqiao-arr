@echo off
REM Queqiao-arr Production Environment Startup Script (Windows)
REM This script calls PowerShell version for better Chinese support

powershell -ExecutionPolicy Bypass -File "%~dp0start-prod.ps1" %*

