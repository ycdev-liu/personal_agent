# 开发环境启动脚本 - 同时启动前后端
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动开发环境" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# 检查后端依赖服务
Write-Host "`n检查 Docker 服务..." -ForegroundColor Yellow
$milvus = docker ps --filter "name=milvus-standalone" --format "{{.Names}}"
$mongodb = docker ps --filter "name=personal-agent-mongodb" --format "{{.Names}}"

if (-not $milvus -or -not $mongodb) {
    Write-Host "启动数据库服务..." -ForegroundColor Yellow
    docker-compose up -d milvus etcd minio mongodb
    Write-Host "等待服务就绪..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

# 启动后端
Write-Host "`n启动后端服务 (http://localhost:8000)..." -ForegroundColor Green
$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; uv run python main.py" -PassThru

# 等待后端启动
Start-Sleep -Seconds 5

# 启动前端
Write-Host "启动前端服务 (http://localhost:3000)..." -ForegroundColor Green
$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev" -PassThru

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "开发环境已启动！" -ForegroundColor Green
Write-Host "前端: http://localhost:3000" -ForegroundColor Cyan
Write-Host "后端: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API 文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n按 Ctrl+C 停止所有服务" -ForegroundColor Yellow

# 等待用户中断
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "`n正在停止服务..." -ForegroundColor Yellow
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
    Write-Host "服务已停止" -ForegroundColor Green
}

