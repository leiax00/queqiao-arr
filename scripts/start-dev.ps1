# Queqiao-arr 开发环境启动脚本 (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Queqiao-arr 开发环境启动" -ForegroundColor Cyan
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
    Write-Host "[警告] 未找到 .env 文件" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Write-Host "[信息] 正在从 .env.example 复制配置..." -ForegroundColor Cyan
        Copy-Item ".env.example" ".env"
        Write-Host "[完成] .env 文件已创建" -ForegroundColor Green
        Write-Host "[提示] 请编辑 .env 文件配置您的环境变量" -ForegroundColor Yellow
    } else {
        Write-Host "[错误] .env.example 文件也不存在" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

# 创建必要的目录
Write-Host "[信息] 创建必要的目录..." -ForegroundColor Cyan
if (-not (Test-Path "runtime")) { New-Item -ItemType Directory -Path "runtime" | Out-Null }
if (-not (Test-Path "runtime/data")) { New-Item -ItemType Directory -Path "runtime/data" | Out-Null }
if (-not (Test-Path "runtime/logs")) { New-Item -ItemType Directory -Path "runtime/logs" | Out-Null }
Write-Host "[完成] 目录创建完成" -ForegroundColor Green
Write-Host ""

# 启动服务
Write-Host "[信息] 启动开发环境..." -ForegroundColor Cyan
Write-Host ""

# 判断是否需要前端服务
if ($args -contains "--with-frontend" -or $args -contains "-f") {
    Write-Host "启动模式: 后端 + 前端开发服务器" -ForegroundColor Green
    docker-compose -f docker-compose.dev.yml --profile frontend up --build
} else {
    Write-Host "启动模式: 仅后端服务" -ForegroundColor Green
    Write-Host "[提示] 使用 --with-frontend 或 -f 参数同时启动前端开发服务器" -ForegroundColor Yellow
    docker-compose -f docker-compose.dev.yml up --build
}

