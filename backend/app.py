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
    user_prompt: Optional[str] = None
    session_id: str

class GenerateTestCaseRequest(BaseModel):
    parsed_requirement: Dict[str, Any]
    user_prompt: Optional[str] = None
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
    test_type: str
    coverage_aspect: Optional[str] = None
    steps: List[Dict[str, str]]
    created_at: str
    requirement_id: Optional[str] = None
    user_prompt: Optional[str] = None

class MultipleTestCases(BaseModel):
    test_cases: List[TestCase]
    requirement_id: str
    coverage_note: str

def generate_test_case_id() -> str:
    """生成测试用例ID"""
    return f"TC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

def parse_requirement_with_llm(title: str, description: str, test_type: str, priority: str, complexity: str, user_prompt: Optional[str] = None) -> Dict[str, Any]:
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

    # 读取系统提示词
    try:
        with open('system_prompt.txt', 'r', encoding='utf-8') as f:
            system_prompt = f.read().strip()
    except FileNotFoundError:
        # 如果文件不存在，使用默认提示词
        system_prompt = """你是一个专业的测试用例设计专家。请将需求描述转换为结构化的测试用例格式。

返回要求：
1. 直接返回JSON格式，不要包含任何其他文字
2. JSON结构必须包含：name, objective, preconditions, steps
3. steps数组必须包含3-8个测试步骤
4. 每个步骤必须包含：test_step, description, expected_result
5. 测试步骤要逻辑清晰，可执行
6. 预期结果要明确具体"""
    except Exception as e:
        # 如果读取失败，使用简化提示词
        print(f"警告：无法读取系统提示词文件，使用默认提示词。错误：{str(e)}")
        system_prompt = "你是测试用例设计专家，请将需求转换为测试用例JSON格式。"

      # 构建基础提示词
    base_prompt = f"""
请分析以下需求并生成测试用例：

需求标题: {title}
需求描述: {description}
测试类型: {test_type}
优先级: {priority}
预估复杂度: {complexity}

根据需求的复杂程度，请选择合适的格式返回：

对于简单或中等复杂度需求，返回单个测试用例：
{{
    "name": "基于需求标题的测试用例名称",
    "objective": "明确具体的测试目标",
    "preconditions": "测试环境准备要求和前置条件（必须是字符串格式）",
    "test_type": "{test_type}",
    "priority": "{priority}",
    "steps": [
        {{
            "test_step": "测试步骤名称",
            "description": "详细的操作描述",
            "expected_result": "明确的预期结果"
        }}
    ]
}}

对于复杂需求，返回多个相关测试用例：
{{
    "test_cases": [
        {{
            "name": "具体测试用例名称1",
            "objective": "该测试用例的具体目标",
            "preconditions": "前置条件",
            "test_type": "{test_type}",
            "priority": "{priority}",
            "coverage_aspect": "覆盖方面描述",
            "steps": [步骤数组]
        }},
        {{
            "name": "具体测试用例名称2",
            "objective": "该测试用例的具体目标",
            "preconditions": "前置条件",
            "test_type": "{test_type}",
            "priority": "medium",
            "coverage_aspect": "覆盖方面描述",
            "steps": [步骤数组]
        }}
    ],
    "requirement_id": "REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "coverage_note": "这些测试用例如何覆盖需求的说明"
}}

需求内容：
{description}
"""

    # 如果有用户提示词，将其整合到提示词中
    if user_prompt and user_prompt.strip():
        final_user_prompt = f"""{base_prompt}

特别注意，用户提供了以下额外要求，请在生成测试用例时严格遵守：
{user_prompt.strip()}

请根据上述所有要求生成测试用例。"""
    else:
        final_user_prompt = base_prompt

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
                {"role": "user", "content": final_user_prompt}
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

        # 验证返回格式 - 支持单个和多个测试用例
        if 'test_cases' in result:
            # 多测试用例格式验证
            multi_required_fields = ['test_cases', 'requirement_id', 'coverage_note']
            for field in multi_required_fields:
                if field not in result:
                    raise Exception(f"LLM返回结果缺少必需字段: {field}")

            if not isinstance(result['test_cases'], list) or len(result['test_cases']) == 0:
                raise Exception("LLM返回的test_cases字段为空或格式错误")

            # 验证每个测试用例
            for i, test_case in enumerate(result['test_cases']):
                single_required_fields = ['name', 'objective', 'preconditions', 'steps', 'test_type', 'priority']
                for field in single_required_fields:
                    if field not in test_case:
                        raise Exception(f"测试用例{i+1}缺少必需字段: {field}")

                # 验证步骤
                if not isinstance(test_case['steps'], list) or len(test_case['steps']) == 0:
                    raise Exception(f"测试用例{i+1}的steps字段为空或格式错误")

                for j, step in enumerate(test_case['steps']):
                    step_fields = ['test_step', 'description', 'expected_result']
                    for field in step_fields:
                        if field not in step:
                            raise Exception(f"测试用例{i+1}步骤{j+1}缺少必需字段: {field}")

                # 确保preconditions是字符串类型
                if isinstance(test_case['preconditions'], list):
                    test_case['preconditions'] = "; ".join(str(item) for item in test_case['preconditions'])
                elif not isinstance(test_case['preconditions'], str):
                    test_case['preconditions'] = str(test_case['preconditions'])

        else:
            # 单个测试用例格式验证
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
    model_name = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')
    return {
        "status": "healthy",
        "service": "requirement_generator",
        "model_name": model_name
    }

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
            request.complexity,
            request.user_prompt
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
    """生成测试用例（支持单个和多个测试用例）"""
    try:
        # 获取会话
        if request.session_id not in store:
            raise HTTPException(status_code=404, detail="会话不存在")

        session_data = store[request.session_id]

        # 从解析的需求生成测试用例
        parsed_requirement = request.parsed_requirement

        # 检查是否是多测试用例格式
        if "test_cases" in parsed_requirement:
            # 处理多个测试用例
            return await generate_multiple_testcases(parsed_requirement, session_data, request.user_prompt)
        else:
            # 处理单个测试用例
            return await generate_single_testcase(parsed_requirement, session_data, request.user_prompt)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试用例生成失败: {str(e)}")

async def generate_single_testcase(parsed_requirement: Dict[str, Any], session_data: SessionData, user_prompt: Optional[str] = None):
    """生成单个测试用例"""
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
        test_type=parsed_requirement.get("test_type", "functional"),
        coverage_aspect=parsed_requirement.get("coverage_aspect"),
        steps=parsed_requirement.get("steps", []),
        created_at=datetime.now().isoformat(),
        user_prompt=user_prompt
    )

    # 存储测试用例
    session_data.generated_testcases[testcase.id] = testcase.dict()

    return {
        "test_case": testcase.dict(),
        "message": "测试用例生成成功",
        "type": "single"
    }

async def generate_multiple_testcases(parsed_requirement: Dict[str, Any], session_data: SessionData, user_prompt: Optional[str] = None):
    """生成多个测试用例"""
    test_cases_data = []
    requirement_id = parsed_requirement.get("requirement_id", generate_test_case_id())

    for i, tc_data in enumerate(parsed_requirement.get("test_cases", [])):
        # 确保preconditions是字符串类型
        preconditions_value = tc_data.get("preconditions", "")
        if isinstance(preconditions_value, list):
            preconditions_value = "; ".join(str(item) for item in preconditions_value)
        elif not isinstance(preconditions_value, str):
            preconditions_value = str(preconditions_value)

        # 创建测试用例
        testcase = TestCase(
            id=generate_test_case_id(),
            name=tc_data.get("name", f"测试用例{i+1}"),
            objective=tc_data.get("objective", ""),
            preconditions=preconditions_value,
            priority=tc_data.get("priority", "medium"),
            test_type=tc_data.get("test_type", "functional"),
            coverage_aspect=tc_data.get("coverage_aspect"),
            steps=tc_data.get("steps", []),
            created_at=datetime.now().isoformat(),
            requirement_id=requirement_id,
            user_prompt=user_prompt
        )

        # 存储测试用例
        session_data.generated_testcases[testcase.id] = testcase.dict()
        test_cases_data.append(testcase.dict())

    return {
        "test_cases": test_cases_data,
        "requirement_id": requirement_id,
        "coverage_note": parsed_requirement.get("coverage_note", ""),
        "message": f"成功生成{len(test_cases_data)}个测试用例",
        "type": "multiple"
    }

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