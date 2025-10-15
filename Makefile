.PHONY: help build dev prod clean logs stop

# 默认目标
help:
	@echo "可用命令:"
	@echo "  build     - 构建所有服务"
	@echo "  dev       - 启动开发环境 (前端+后端)"
	@echo "  prod      - 启动生产环境 (后端+Nginx)"
	@echo "  backend   - 仅启动后端服务"
	@echo "  redis     - 启动 Redis (可选)"
	@echo "  logs      - 查看日志"
	@echo "  stop      - 停止所有服务"
	@echo "  clean     - 清理 Docker 资源"
	@echo "  setup     - 初始化项目环境"

# 构建所有服务
build:
	@echo "构建所有服务..."
	docker-compose build

# 开发环境
dev:
	@echo "启动开发环境..."
	cp .env.example .env 2>/dev/null || true
	docker-compose --profile dev up -d
	@echo "前端地址: http://localhost:5173"
	@echo "后端地址: http://localhost:8000"

# 生产环境
prod:
	@echo "启动生产环境..."
	docker-compose --profile prod up -d
	@echo "应用地址: http://localhost:80"

# 仅后端
backend:
	@echo "启动后端服务..."
	docker-compose up -d backend
	@echo "后端地址: http://localhost:8000"

# 包含 Redis 的开发环境
dev-redis:
	@echo "启动开发环境 (包含 Redis)..."
	cp .env.example .env 2>/dev/null || true
	docker-compose --profile dev --profile redis up -d
	@echo "前端地址: http://localhost:5173"
	@echo "后端地址: http://localhost:8000"
	@echo "Redis: localhost:6379"

# 查看日志
logs:
	docker-compose logs -f

# 查看特定服务日志
logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend-dev

# 停止服务
stop:
	@echo "停止所有服务..."
	docker-compose down

# 强制停止并清理
clean:
	@echo "停止并清理所有资源..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# 重新构建并启动
rebuild: clean build

# 初始化项目环境
setup:
	@echo "初始化项目环境..."
	@if [ ! -f .env ]; then \
		echo "创建 .env 文件..."; \
		cp .env.example .env; \
		echo "请编辑 .env 文件，设置您的 API 密钥"; \
	else \
		echo ".env 文件已存在"; \
	fi
	@mkdir -p logs
	@echo "环境初始化完成！"

# 健康检查
health:
	@echo "检查服务健康状态..."
	@curl -s http://localhost:8000/health > /dev/null && echo "✅ 后端服务正常" || echo "❌ 后端服务异常"
	@curl -s http://localhost:5173 > /dev/null && echo "✅ 前端服务正常" || echo "❌ 前端服务异常"

# 进入后端容器
shell-backend:
	docker-compose exec backend /bin/bash

# 进入前端容器
shell-frontend:
	docker-compose exec frontend-dev /bin/sh