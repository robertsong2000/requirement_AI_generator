from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
import json
import uuid
import sys
from pathlib import Path
from datetime import datetime
import re
from dotenv import load_dotenv

# 添加父级目录到sys.path以导入现有模块
sys.path.insert(0, str(Path(__file__).parent.parent))

# 加载环境变量
load_dotenv()

app = FastAPI(title="需求生成测试用例系统 - API", version="1.0.0")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储会话数据
class SessionData:
    def __init__(self):
        self.parsed_requirements = {}  # id -> parsed_requirement
        self.generated_testcases = {}  # id -> testcase

# 全局存储
store = {}

# Pydantic模型
class ParseRequirementRequest(BaseModel):
    title: str
    description: str
    test_type: str
    priority: str
    complexity: str
    session_id: str

class GenerateTestCaseRequest(BaseModel):
    parsed_requirement: Dict[str, Any]
    session_id: str

class ParsedRequirement(BaseModel):
    id: str
    name: str
    objective: str
    preconditions: str
    steps: List[Dict[str, str]]

class TestCase(BaseModel):
    id: str
    name: str
    objective: str
    preconditions: str
    priority: str
    steps: List[Dict[str, str]]
    created_at: str

def generate_test_case_id() -> str:
    """生成测试用例ID"""
    return f"TC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

def parse_requirement_with_llm(title: str, description: str, test_type: str, priority: str, complexity: str) -> Dict[str, Any]:
    """使用OpenAI兼容API解析需求"""

    # 检查环境变量
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise Exception("未配置OPENAI_API_KEY环境变量，请在.env文件中设置API密钥")

    base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    model_name = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')
    temperature = float(os.getenv('TEMPERATURE', '0.3'))
    top_p = float(os.getenv('TOP_P', '1.0'))
    max_tokens = int(os.getenv('MAX_TOKENS', '2000'))

    # 构建提示词
    system_prompt = """你是一个资深的软件测试工程师和测试用例设计专家，拥有10年以上的测试经验。你需要将用户提供的需求描述转换为专业、标准化的测试用例格式。

## 你的专业能力包括：
- 深度理解软件需求规格说明书
- 设计覆盖功能、性能、安全、易用性等多维度的测试用例
- 确保测试用例的可执行性和可复现性
- 遵循业界最佳实践和测试标准

## 测试用例设计原则：
1. **完整性**：覆盖需求的核心功能和边界条件
2. **独立性**：每个测试步骤相互独立，不依赖其他测试的状态
3. **可重复性**：测试结果应可重复验证
4. **清晰性**：描述准确无歧义，任何人都能理解并执行
5. **实用性**：步骤实际可操作，预期结果可验证

## 返回格式要求：
1. 严格按照JSON格式返回，不包含任何额外的说明文字、代码块或markdown格式
2. JSON结构必须包含以下字段：
   - name: 测试用例名称（简洁明确，体现测试目标）
   - objective: 测试目标（具体说明要验证什么功能或特性）
   - preconditions: 前置条件（字符串格式，测试环境、数据、用户状态等准备要求，不要返回数组）
   - steps: 测试步骤数组（3-8个步骤，逻辑清晰）

3. 每个测试步骤必须包含：
   - test_step: 步骤编号和简短描述（如："步骤1：打开登录页面"）
   - description: 详细的操作说明（具体点击什么、输入什么、选择什么）
   - expected_result: 明确的预期结果（界面显示、系统响应、数据变化等）

## 输出质量标准：
- 测试步骤按执行顺序排列，逻辑递进
- 每个步骤都是具体的、可观察的操作
- 预期结果必须是可验证的、明确的
- 避免模糊表述（如"正常"、"正确"），要具体说明
- 包含必要的正常流程和异常场景验证

## 测试类型处理指南：
根据测试类型调整测试用例的设计重点：
- **功能测试**: 聚焦于功能正确性、业务流程、输入验证、边界值测试
- **性能测试**: 关注响应时间、吞吐量、并发用户、资源利用率
- **安全测试**: 强调身份验证、权限控制、数据加密、SQL注入、XSS防护
- **兼容性测试**: 考虑不同浏览器、操作系统、设备、网络环境
- **用户体验测试**: 注重界面交互、易用性、视觉设计、导航流程

## 复杂度处理指南：
- **简单复杂度**: 生成3-4个核心测试步骤，覆盖主要功能点
- **中等复杂度**: 生成5-6个测试步骤，包含正常流程和基本异常场景
- **复杂复杂度**: 生成7-8个测试步骤，涵盖边界条件、异常处理和多种测试场景

## 特别注意：
- 不要添加任何解释性文字或注释
- 确保JSON格式完全正确，可以直接解析
- 根据复杂度和测试类型调整步骤数量和详细程度
- 考虑用户体验和业务流程的完整性
- 针对特定测试类型设计相应的验证点和预期结果
- 测试用例名称应体现测试类型特征"""

    user_prompt = f"""
请分析以下需求并生成测试用例：

需求标题: {title}
需求描述: {description}
测试类型: {test_type}
优先级: {priority}
预估复杂度: {complexity}

请按照以下JSON格式返回：
{{
    "name": "基于需求标题的测试用例名称",
    "objective": "明确具体的测试目标",
    "preconditions": "测试环境准备要求和前置条件（注意：必须是字符串格式，不要返回数组）",
    "steps": [
        {{
            "test_step": "测试步骤名称",
            "description": "详细的操作描述",
            "expected_result": "明确的预期结果"
        }}
    ]
}}

需求内容：
{description}
"""

    try:
        import openai

        # 创建OpenAI客户端
        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        # 调用API
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )

        # 获取响应内容
        content = response.choices[0].message.content.strip()

        # 尝试解析JSON
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # 清理可能的markdown格式
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            elif content.startswith('```'):
                content = content.replace('```', '').strip()

            # 再次尝试解析
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                raise Exception(f"LLM返回的不是有效的JSON格式: {content}")

        # 验证必需字段
        required_fields = ['name', 'objective', 'preconditions', 'steps']
        for field in required_fields:
            if field not in result:
                raise Exception(f"LLM返回结果缺少必需字段: {field}")

        # 确保preconditions是字符串类型
        if isinstance(result['preconditions'], list):
            result['preconditions'] = "; ".join(str(item) for item in result['preconditions'])
        elif not isinstance(result['preconditions'], str):
            result['preconditions'] = str(result['preconditions'])

        if not isinstance(result['steps'], list) or len(result['steps']) == 0:
            raise Exception("LLM返回的steps字段为空或格式错误")

        # 确保每个步骤都有必需字段
        for i, step in enumerate(result['steps']):
            step_fields = ['test_step', 'description', 'expected_result']
            for field in step_fields:
                if field not in step:
                    raise Exception(f"步骤{i+1}缺少必需字段: {field}")

        return result

    except openai.APIConnectionError as e:
        raise Exception(f"无法连接到OpenAI服务: {str(e)}")
    except openai.AuthenticationError as e:
        raise Exception(f"OpenAI API密钥无效或已过期: {str(e)}")
    except openai.RateLimitError as e:
        raise Exception(f"OpenAI API调用频率超限: {str(e)}")
    except openai.APIError as e:
        raise Exception(f"OpenAI API错误: {str(e)}")
    except Exception as e:
        raise Exception(f"LLM解析失败: {str(e)}")


# API端点
@app.get("/")
async def root():
    return {"message": "需求生成测试用例系统API服务运行中", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "requirement_generator"}

@app.post("/parse-requirement")
async def parse_requirement(request: ParseRequirementRequest):
    """解析需求"""
    try:
        # 获取或创建会话
        if request.session_id not in store:
            store[request.session_id] = SessionData()

        session_data = store[request.session_id]

        # 解析需求
        parsed_data = parse_requirement_with_llm(
            request.title,
            request.description,
            request.test_type,
            request.priority,
            request.complexity
        )

        # 生成ID
        requirement_id = generate_test_case_id()
        parsed_data["id"] = requirement_id

        
        # 存储解析结果
        session_data.parsed_requirements[requirement_id] = parsed_data

        return {
            "parsed_requirement": parsed_data,
            "message": "需求解析成功"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"需求解析失败: {str(e)}")

@app.post("/generate-testcase")
async def generate_testcase(request: GenerateTestCaseRequest):
    """生成测试用例"""
    try:
        # 获取会话
        if request.session_id not in store:
            raise HTTPException(status_code=404, detail="会话不存在")

        session_data = store[request.session_id]

        # 从解析的需求生成测试用例
        parsed_requirement = request.parsed_requirement

        # 确保preconditions是字符串类型
        preconditions_value = parsed_requirement.get("preconditions", "")
        if isinstance(preconditions_value, list):
            preconditions_value = "; ".join(str(item) for item in preconditions_value)
        elif not isinstance(preconditions_value, str):
            preconditions_value = str(preconditions_value)

        # 创建测试用例
        testcase = TestCase(
            id=parsed_requirement.get("id", generate_test_case_id()),
            name=parsed_requirement.get("name", "未命名测试用例"),
            objective=parsed_requirement.get("objective", ""),
            preconditions=preconditions_value,
            priority=parsed_requirement.get("priority", "medium"),
            steps=parsed_requirement.get("steps", []),
            created_at=datetime.now().isoformat()
        )

        # 存储测试用例
        session_data.generated_testcases[testcase.id] = testcase.dict()

        return {
            "test_case": testcase.dict(),
            "message": "测试用例生成成功"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试用例生成失败: {str(e)}")

@app.get("/testcases/{session_id}")
async def get_testcases(session_id: str):
    """获取会话的所有测试用例"""
    try:
        if session_id not in store:
            return {"test_cases": []}

        session_data = store[session_id]
        test_cases = list(session_data.generated_testcases.values())

        return {"test_cases": test_cases}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取测试用例失败: {str(e)}")

@app.get("/parsed-requirements/{session_id}")
async def get_parsed_requirements(session_id: str):
    """获取会话的所有解析需求"""
    try:
        if session_id not in store:
            return {"parsed_requirements": []}

        session_data = store[session_id]
        parsed_requirements = list(session_data.parsed_requirements.values())

        return {"parsed_requirements": parsed_requirements}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取解析需求失败: {str(e)}")

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """清除会话数据"""
    try:
        if session_id in store:
            del store[session_id]

        return {"message": "会话已清除"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除会话失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)