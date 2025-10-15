# 需求生成测试用例系统 - Docker 部署指南

本文档介绍如何使用 Docker 部署需求生成测试用例系统。

## 快速开始

### 1. 环境准备

确保已安装以下软件：
- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- Make (可选，用于简化命令)

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置您的 API 密钥
nano .env
```

### 3. 启动服务

#### 开发环境 (包含前端开发服务器)
```bash
# 使用 Makefile
make dev

# 或直接使用 docker-compose
docker-compose --profile dev up -d
```

#### 生产环境 (仅后端 + Nginx)
```bash
# 使用 Makefile
make prod

# 或直接使用 docker-compose
docker-compose --profile prod up -d
```

## 服务配置

### 可用服务

| 服务 | 端口 | 描述 |
|------|------|------|
| backend | 8000 | Python FastAPI 后端服务 |
| frontend-dev | 5173 | Vue.js 开发服务器 |
| frontend-prod | 80 | Nginx 生产服务器 |
| redis | 6379 | Redis 缓存服务 (可选) |

### 环境变量

主要环境变量说明：

```bash
# 必需
OPENAI_API_KEY=your_api_key_here

# 可选
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7
TOP_P=1.0
MAX_TOKENS=4000
```

支持的 LLM 服务示例请参考 `.env.example` 文件。

## 常用命令

### 使用 Makefile (推荐)

```bash
# 查看所有可用命令
make help

# 初始化项目
make setup

# 启动开发环境
make dev

# 启动生产环境
make prod

# 查看日志
make logs

# 停止服务
make stop

# 清理资源
make clean

# 健康检查
make health
```

### 使用 Docker Compose

```bash
# 构建服务
docker-compose build

# 启动开发环境
docker-compose --profile dev up -d

# 启动生产环境
docker-compose --profile prod up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 进入容器
docker-compose exec backend /bin/bash
```

## 开发工作流

### 1. 本地开发

```bash
# 启动包含 Redis 的开发环境
make dev-redis

# 实时查看日志
make logs

# 进入后端容器调试
make shell-backend
```

### 2. 生产部署

```bash
# 构建生产镜像
make build

# 启动生产环境
make prod

# 检查服务状态
make health
```

### 3. 调试和故障排除

```bash
# 查看后端日志
make logs-backend

# 查看前端日志
make logs-frontend

# 进入后端容器
make shell-backend

# 重启特定服务
docker-compose restart backend
```

## 数据持久化

### 日志目录
- `./logs/` - 应用日志目录

### Redis 数据
- 使用 Docker volume `redis_data` 持久化

## 网络配置

所有服务运行在自定义网络 `requirement-generator-network` 中，确保服务间可以正常通信。

## 安全配置

### 生产环境建议

1. **HTTPS 配置**
   - 准备 SSL 证书文件
   - 取消注释 nginx.conf 中的 HTTPS 配置
   - 将证书文件放在 `frontend/ssl/` 目录

2. **环境变量安全**
   - 不要将 `.env` 文件提交到版本控制
   - 使用 Docker secrets 或环境变量管理工具

3. **网络隔离**
   - 在防火墙中只开放必要端口 (80, 443)
   - 内部服务端口不对外暴露

## 性能优化

### Nginx 配置
- 启用 Gzip 压缩
- 静态资源缓存
- API 代理优化

### 后端优化
- 健康检查配置
- 合理的超时设置
- 日志级别控制

## 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   lsof -i :8000
   lsof -i :5173
   lsof -i :80
   ```

2. **权限问题**
   ```bash
   # 确保 Docker 有足够权限
   sudo usermod -aG docker $USER
   ```

3. **环境变量问题**
   ```bash
   # 检查环境变量
   docker-compose exec backend env | grep OPENAI
   ```

4. **健康检查失败**
   ```bash
   # 手动检查健康状态
   curl http://localhost:8000/health
   ```

### 日志分析

```bash
# 查看容器状态
docker-compose ps

# 查看资源使用情况
docker stats

# 导出日志
docker-compose logs --no-color > docker.log
```

## 版本更新

```bash
# 拉取最新代码
git pull

# 重新构建镜像
make rebuild

# 重启服务
make stop && make dev
```

## 支持

如果遇到问题，请检查：
1. Docker 和 Docker Compose 版本是否符合要求
2. 环境变量是否正确配置
3. 防火墙和端口配置是否正确
4. 查看相关日志文件获取错误信息