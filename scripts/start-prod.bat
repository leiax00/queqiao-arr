@echo off
REM Queqiao-arr Production Environment Startup Script (Windows)

setlocal enabledelayedexpansion

echo =========================================
echo   Queqiao-arr Production Environment
echo =========================================
echo.

REM Check if Docker is installed
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker not found. Please install Docker first.
    exit /b 1
)

where docker-compose >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose not found. Please install Docker Compose first.
    exit /b 1
)

echo [OK] Docker environment check passed
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [ERROR] .env file not found
    echo [TIP] Please copy .env.example and configure your environment variables
    echo Command: copy .env.example .env
    exit /b 1
)

REM Check if SECRET_KEY is configured
findstr /C:"please-change-this-secret-key-in-production" .env >nul
if %errorlevel% equ 0 (
    echo [WARNING] Default SECRET_KEY detected
    echo [ERROR] Production environment requires a secure SECRET_KEY
    echo [TIP] Please modify SECRET_KEY in .env file
    exit /b 1
)

echo [OK] Environment variable check passed
echo.

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
echo [OK] Directories created
echo.

REM Start services
echo [INFO] Starting production environment...
echo.

if "%1"=="--build" goto BUILD
if "%1"=="-b" goto BUILD

echo Mode: Starting with existing images
echo [TIP] Use --build or -b to rebuild images
docker-compose -f docker-compose.prod.yml up -d
goto SUCCESS

:BUILD
echo Mode: Rebuilding and starting
docker-compose -f docker-compose.prod.yml up -d --build

:SUCCESS
echo.
echo =========================================
echo [SUCCESS] Service started!
echo =========================================
echo.
echo View service status:
echo    docker-compose -f docker-compose.prod.yml ps
echo.
echo View service logs:
echo    docker-compose -f docker-compose.prod.yml logs -f
echo.
echo Stop service:
echo    docker-compose -f docker-compose.prod.yml down
echo.
echo Access URL:
echo    http://localhost:8000
echo.

endlocal

