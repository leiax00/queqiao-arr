@echo off
REM Queqiao-arr Development Environment Startup Script (Windows)

setlocal enabledelayedexpansion

echo =========================================
echo   Queqiao-arr Development Environment
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
    echo [WARNING] .env file not found
    if exist ".env.example" (
        echo [INFO] Copying .env.example to .env...
        copy .env.example .env >nul
        echo [OK] .env file created
        echo [TIP] Please edit .env file to configure your environment variables
    ) else (
        echo [ERROR] .env.example file not found
        exit /b 1
    )
    echo.
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
echo [OK] Directories created
echo.

REM Start services
echo [INFO] Starting development environment...
echo.

REM Check if frontend service is needed
if "%1"=="--with-frontend" goto WITH_FRONTEND
if "%1"=="-f" goto WITH_FRONTEND

echo Mode: Backend service only
echo [TIP] Use --with-frontend or -f to start frontend dev server too
docker-compose -f docker-compose.dev.yml up --build
goto END

:WITH_FRONTEND
echo Mode: Backend + Frontend development server
docker-compose -f docker-compose.dev.yml --profile frontend up --build

:END
endlocal

