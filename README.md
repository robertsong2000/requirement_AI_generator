# 需求生成测试用例系统

这是一个基于大语言模型的需求生成测试用例系统，可以将自然语言需求描述转换为结构化的测试用例。

## 功能特性

- 📝 **需求输入**: 支持Markdown和纯文本格式的需求描述
- 📋 **需求模板**: 提供多种预设的需求模板（雨刷器测试、CAN通信测试、性能测试等）
- 🔍 **智能解析**: 使用LLM自动解析需求，提取测试步骤和预期结果
- 🚀 **测试用例生成**: 基于解析结果自动生成完整的测试用例
- 📊 **多格式导出**: 支持JSON、Markdown、Excel格式的测试用例导出
- 🌐 **多语言支持**: 支持中文和英文界面切换
- 💬 **实时编辑**: 支持解析结果的实时编辑和调整

## 系统架构

```
requirement_generator/
├── frontend/          # Vue.js前端应用
│   ├── src/
│   │   ├── components/
│   │   │   └── RequirementGenerator.vue
│   │   ├── stores/
│   │   │   └── language.ts
│   │   └── router/
│   │       └── index.ts
│   └── package.json
└── backend/           # FastAPI后端服务
    ├── app.py
    └── requirements.txt
```

## 快速开始

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端服务将在 `http://localhost:5174` 启动

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python app.py
```

后端API服务将在 `http://localhost:8005` 启动

### 使用Docker启动

```bash
# 仅启动后端服务
docker-compose up -d

# 启动后端 + 前端开发环境
docker-compose --profile dev up -d

# 启动后端 + 前端生产环境
docker-compose --profile prod up -d
```

**服务访问地址：**
- 后端API: `http://localhost:8005`
- 前端开发环境: `http://localhost:5174`
- 前端生产环境: `http://localhost:80`

## API文档

启动后端服务后，可以访问以下地址查看API文档：

- Swagger UI: `http://localhost:8005/docs`
- ReDoc: `http://localhost:8005/redoc`

## 主要API端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 获取服务信息 |
| `/health` | GET | 健康检查 |
| `/parse-requirement` | POST | 解析需求 |
| `/generate-testcase` | POST | 生成测试用例 |
| `/testcases/{session_id}` | GET | 获取测试用例列表 |
| `/parsed-requirements/{session_id}` | GET | 获取解析需求列表 |
| `/session/{session_id}` | DELETE | 清除会话数据 |

## 使用说明

### 1. 输入需求

在左侧面板中：
- 选择需求模板（可选）
- 输入需求标题
- 编写需求描述（支持Markdown格式）
- 选择测试类型、优先级和复杂度

### 2. 解析需求

点击"解析需求"按钮，系统将：
- 使用LLM分析需求描述
- 提取测试目标
- 生成测试步骤和预期结果
- 创建前置条件

### 3. 编辑和确认

在右侧面板中：
- 查看解析结果
- 编辑测试用例名称、目标、前置条件
- 调整测试步骤
- 添加或删除步骤

### 4. 生成测试用例

点击"生成测试用例"按钮：
- 基于解析结果创建最终测试用例
- 在左侧列表中显示生成的测试用例
- 支持多选和批量操作

### 5. 导出结果

选择测试用例后可以：
- 导出为JSON格式
- 导出为Markdown文档
- 导出到Excel表格（开发中）
- 复制到剪贴板

## 配置说明

### 环境变量

在backend目录下创建`.env`文件：

```env
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 其他LLM服务配置
# OPENAI_BASE_URL=https://api.deepseek.com/v1
# OPENAI_API_KEY=your_deepseek_api_key_here
```

### 支持的LLM服务

- OpenAI GPT系列
- DeepSeek
- 其他兼容OpenAI API的服务

## 开发指南

### 前端开发

前端基于Vue 3 + TypeScript + Element Plus开发：

```bash
cd frontend
npm install
npm run dev      # 开发模式
npm run build    # 生产构建
npm run preview  # 预览构建结果
```

### 后端开发

后端基于FastAPI + Python开发：

```bash
cd backend
pip install -r requirements.txt
python app.py  # 开发模式
```

### 添加新的需求模板

在`frontend/src/components/RequirementGenerator.vue`中的`requirementTemplates`数组中添加新模板：

```typescript
{
  id: 'new_template',
  name: t('新模板名称'),
  description: t('模板描述'),
  template: `# 模板内容`,
  testType: 'functional',
  priority: 'medium',
  complexity: 'simple'
}
```

## 故障排除

### 常见问题

1. **服务连接失败**
   - 检查后端服务是否在8005端口运行
   - 确认防火墙设置

2. **LLM服务错误**
   - **未配置API密钥**: 检查`.env`文件中的`OPENAI_API_KEY`配置
   - **API密钥无效**: 确认API密钥正确且有效
   - **网络连接问题**: 检查网络连接或使用代理服务
   - **API配额超限**: 检查API服务配额或更换密钥
   - **服务不可用**: 确认LLM服务状态正常

   ⚠️ **注意**: 本系统已移除Fallback机制，必须配置有效的LLM服务才能正常工作

3. **前端无法启动**
   - 检查Node.js版本（需要16+）
   - 删除node_modules重新安装

4. **端口冲突**
   - 修改`vite.config.ts`中的前端端口（默认5174）
   - 修改`app.py`中的后端端口（默认8005）

### 日志查看

- 前端日志：浏览器开发者工具控制台
- 后端日志：终端输出或日志文件

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请创建Issue或联系开发团队。