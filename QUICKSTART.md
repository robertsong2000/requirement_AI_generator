# 快速启动指南

## 🚀 一键启动

```bash
cd requirement_generator
./start.sh
```

## 📋 手动启动

### 1. 启动后端

```bash
cd backend
python app.py
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

## 🌐 访问地址

- **前端界面**: http://localhost:5174
- **后端API**: http://localhost:8005
- **API文档**: http://localhost:8005/docs

## 🧪 测试API

```bash
python test_api.py
```

## ⚙️ 环境配置

⚠️ **重要**: 本系统必须配置LLM服务才能正常工作！

复制 `.env.example` 为 `.env` 并配置你的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
# OpenAI API (必需)
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 或使用其他兼容服务
# OPENAI_API_KEY=your_deepseek_key_here
# OPENAI_BASE_URL=https://api.deepseek.com/v1
```

## 🐳 Docker启动

```bash
docker-compose up -d
```

## 📱 使用流程

1. 在左侧输入需求描述
2. 选择需求模板（可选）
3. 点击"解析需求"
4. 编辑解析结果
5. 点击"生成测试用例"
6. 导出测试用例

## 🔧 故障排除

1. **端口冲突**: 修改 `vite.config.ts` 中的前端端口或 `app.py` 中的后端端口
2. **LLM服务错误**:
   - 检查 `.env` 文件中的API密钥配置
   - 确认网络连接正常
   - 验证API服务可用性
3. **依赖问题**: 删除 `node_modules` 重新安装
4. **环境变量问题**: 确保在项目根目录创建了 `.env` 文件

## 📞 支持

如遇问题，请查看 [README.md](README.md) 或提交Issue。