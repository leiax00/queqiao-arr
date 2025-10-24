# Queqiao-arr 生产环境启动脚本 (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Queqiao-arr 生产环境启动" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否安装
Write-Host "检查 Docker 环境..." -ForegroundColor Yellow
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[错误] 未检测到 Docker，请先安装 Docker" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "[错误] 未检测到 Docker Compose，请先安装 Docker Compose" -ForegroundColor Red
    exit 1
}

Write-Host "[完成] Docker 环境检查通过" -ForegroundColor Green
Write-Host ""

# 检查是否存在 .env 文件
if (-not (Test-Path ".env")) {
    Write-Host "[错误] 未找到 .env 文件" -ForegroundColor Red
    Write-Host "[提示] 请从 .env.example 复制并配置您的环境变量" -ForegroundColor Yellow
    Write-Host "命令: Copy-Item .env.example .env" -ForegroundColor Cyan
    exit 1
}

# 检查 SECRET_KEY 是否配置
$envContent = Get-Content ".env" -Raw
if ($envContent -match "please-change-this-secret-key-in-production") {
    Write-Host "[警告] 检测到默认的 SECRET_KEY" -ForegroundColor Yellow
    Write-Host "[错误] 生产环境必须配置安全的 SECRET_KEY" -ForegroundColor Red
    Write-Host "[提示] 请修改 .env 文件中的 SECRET_KEY" -ForegroundColor Yellow
    exit 1
}

Write-Host "[完成] 环境变量配置检查通过" -ForegroundColor Green
Write-Host ""

# 创建必要的目录
Write-Host "[信息] 创建必要的目录..." -ForegroundColor Cyan
if (-not (Test-Path "runtime")) { New-Item -ItemType Directory -Path "runtime" | Out-Null }
if (-not (Test-Path "runtime/data")) { New-Item -ItemType Directory -Path "runtime/data" | Out-Null }
if (-not (Test-Path "runtime/logs")) { New-Item -ItemType Directory -Path "runtime/logs" | Out-Null }
Write-Host "[完成] 目录创建完成" -ForegroundColor Green
Write-Host ""

# 启动服务
Write-Host "[信息] 启动生产环境..." -ForegroundColor Cyan
Write-Host ""

if ($args -contains "--build" -or $args -contains "-b") {
    Write-Host "启动模式: 重新构建并启动" -ForegroundColor Green
    docker-compose -f docker-compose.prod.yml up -d --build
} else {
    Write-Host "启动模式: 使用现有镜像启动" -ForegroundColor Green
    Write-Host "[提示] 使用 --build 或 -b 参数重新构建镜像" -ForegroundColor Yellow
    docker-compose -f docker-compose.prod.yml up -d
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "[成功] 服务启动成功！" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "查看服务状态:" -ForegroundColor Yellow
Write-Host "   docker-compose -f docker-compose.prod.yml ps" -ForegroundColor White
Write-Host ""
Write-Host "查看服务日志:" -ForegroundColor Yellow
Write-Host "   docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor White
Write-Host ""
Write-Host "停止服务:" -ForegroundColor Yellow
Write-Host "   docker-compose -f docker-compose.prod.yml down" -ForegroundColor White
Write-Host ""
Write-Host "访问地址:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

