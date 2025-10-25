# Queqiao-arr 停止脚本 (PowerShell)

Write-Host "停止 Queqiao-arr 服务..." -ForegroundColor Yellow
Write-Host ""

# 停止所有可能运行的服务
if (Test-Path "docker-compose.dev.yml") {
    Write-Host "停止开发环境..." -ForegroundColor Cyan
    docker-compose -f docker-compose.dev.yml --profile frontend down 2>$null
}

if (Test-Path "docker-compose.prod.yml") {
    Write-Host "停止生产环境..." -ForegroundColor Cyan
    docker-compose -f docker-compose.prod.yml down 2>$null
}

if (Test-Path "docker-compose.yml") {
    Write-Host "停止默认环境..." -ForegroundColor Cyan
    docker-compose down 2>$null
}

Write-Host ""
Write-Host "[完成] 所有服务已停止" -ForegroundColor Green

