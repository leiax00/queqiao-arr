@echo off
REM Queqiao-arr Stop Script (Windows)
REM This script calls PowerShell version for better Chinese support

powershell -ExecutionPolicy Bypass -File "%~dp0stop.ps1" %*

