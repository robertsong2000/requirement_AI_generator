#!/bin/bash

# 需求生成测试用例系统启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 启动需求生成测试用例系统..."
echo "📁 项目目录: $SCRIPT_DIR"

# 检查Python和Node.js
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装Node.js和npm"
    exit 1
fi




# 启动后端
echo "📦 启动后端服务..."
cd backend

# 启动后端服务
echo "🌐 后端服务启动在 http://localhost:8005"
python app.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "🎨 启动前端服务..."
cd ../frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 启动前端服务
echo "🌐 前端服务启动在 http://localhost:5174"
npm run dev &
FRONTEND_PID=$!

# 等待前端启动
sleep 5

# 等待用户中断
echo ""
echo "✅ 系统启动完成！"
echo "📱 前端地址: http://localhost:5174"
echo "🔧 后端API: http://localhost:8005"
echo "📚 API文档: http://localhost:8005/docs"
echo "🧪 API测试: python test_api.py"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获中断信号
cleanup() {
    echo ""
    echo "🛑 正在停止服务..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ 后端服务已停止"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ 前端服务已停止"
    fi
    exit 0
}

trap cleanup INT TERM

# 等待
wait