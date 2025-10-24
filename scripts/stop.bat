@echo off
REM Queqiao-arr Stop Script (Windows)

echo Stopping Queqiao-arr services...
echo.

REM Stop all possible running services
if exist "docker-compose.dev.yml" (
    echo Stopping development environment...
    docker-compose -f docker-compose.dev.yml --profile frontend down 2>nul
)

if exist "docker-compose.prod.yml" (
    echo Stopping production environment...
    docker-compose -f docker-compose.prod.yml down 2>nul
)

if exist "docker-compose.yml" (
    echo Stopping default environment...
    docker-compose down 2>nul
)

echo.
echo [OK] All services stopped

