@echo off
REM Docker Configuration Verification Script (Windows)

setlocal enabledelayedexpansion

echo =========================================
echo   Docker Configuration Verification
echo =========================================
echo.

REM Check if Docker is installed
echo 1. Checking Docker environment...
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker not installed
    exit /b 1
)

where docker-compose >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose not installed
    exit /b 1
)

echo [OK] Docker environment is ready
echo.

REM Verify Dockerfile
echo 2. Verifying Dockerfile...
if not exist "Dockerfile" (
    echo [ERROR] Dockerfile not found
    exit /b 1
)
echo [OK] Dockerfile exists
echo.

REM Verify docker-compose configuration files
echo 3. Verifying docker-compose configuration...

if exist "docker-compose.dev.yml" (
    echo    Checking development environment config...
    docker-compose -f docker-compose.dev.yml config --quiet >nul 2>&1
    if %errorlevel% equ 0 (
        echo    [OK] Development environment config is valid
    ) else (
        echo    [ERROR] Development environment config is invalid
        exit /b 1
    )
) else (
    echo    [ERROR] docker-compose.dev.yml not found
    exit /b 1
)

REM Production environment needs .env file
if exist ".env" (
    echo    Checking production environment config...
    docker-compose -f docker-compose.prod.yml config --quiet >nul 2>&1
    if %errorlevel% equ 0 (
        echo    [OK] Production environment config is valid
    ) else (
        echo    [WARNING] Production environment config check failed (may need env vars)
    )
) else (
    echo    [WARNING] .env file not found, skipping production config check
)

echo.

REM Check necessary files
echo 4. Checking necessary files...
set all_exists=true

if exist ".dockerignore" (
    echo    [OK] .dockerignore
) else (
    echo    [ERROR] .dockerignore not found
    set all_exists=false
)

if exist ".env.example" (
    echo    [OK] .env.example
) else (
    echo    [ERROR] .env.example not found
    set all_exists=false
)

if exist "scripts\start-dev.bat" (
    echo    [OK] scripts\start-dev.bat
) else (
    echo    [ERROR] scripts\start-dev.bat not found
    set all_exists=false
)

if exist "scripts\start-prod.bat" (
    echo    [OK] scripts\start-prod.bat
) else (
    echo    [ERROR] scripts\start-prod.bat not found
    set all_exists=false
)

if exist "scripts\stop.bat" (
    echo    [OK] scripts\stop.bat
) else (
    echo    [ERROR] scripts\stop.bat not found
    set all_exists=false
)

if "%all_exists%"=="false" (
    exit /b 1
)

echo.
echo =========================================
echo [SUCCESS] All configuration verified!
echo =========================================
echo.
echo Next steps:
echo    1. Copy environment file: copy .env.example .env
echo    2. Edit .env file to configure necessary variables
echo    3. Run development: scripts\start-dev.bat
echo    4. Run production: scripts\start-prod.bat
echo.

endlocal

