#!/usr/bin/env python3
"""
测试API接口的简单脚本
"""

import requests
import json
import time

BASE_URL = "http://localhost:8005"

def test_health():
    """测试健康检查接口"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_parse_requirement():
    """测试需求解析接口"""
    try:
        data = {
            "title": "雨刷器功能测试",
            "description": "验证车辆雨刷器在不同档位和工况下的正常工作状态",
            "test_type": "functional",
            "priority": "high",
            "complexity": "medium",
            "session_id": "test_session_" + str(int(time.time()))
        }

        response = requests.post(f"{BASE_URL}/parse-requirement", json=data)
        print(f"✅ Parse requirement: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            parsed = result.get("parsed_requirement", {})
            print(f"   - 名称: {parsed.get('name', 'N/A')}")
            print(f"   - 目标: {parsed.get('objective', 'N/A')}")
            print(f"   - 步骤数: {len(parsed.get('steps', []))}")
            return result
        else:
            print(f"❌ Parse requirement failed: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Parse requirement failed: {e}")
        return None

def test_generate_testcase(parsed_requirement):
    """测试测试用例生成接口"""
    try:
        data = {
            "parsed_requirement": parsed_requirement,
            "session_id": "test_session_" + str(int(time.time()))
        }

        response = requests.post(f"{BASE_URL}/generate-testcase", json=data)
        print(f"✅ Generate testcase: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            testcase = result.get("test_case", {})
            print(f"   - 用例ID: {testcase.get('id', 'N/A')}")
            print(f"   - 名称: {testcase.get('name', 'N/A')}")
            print(f"   - 步骤数: {len(testcase.get('steps', []))}")
            return True
        else:
            print(f"❌ Generate testcase failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Generate testcase failed: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试需求生成测试用例系统API...")
    print(f"📡 测试地址: {BASE_URL}")
    print()

    # 测试健康检查
    if not test_health():
        print("❌ 服务未启动或不可用，请先启动后端服务")
        return

    print()

    # 测试需求解析
    parsed_result = test_parse_requirement()
    if not parsed_result:
        print("❌ 需求解析失败")
        return

    print()

    # 测试测试用例生成
    if test_generate_testcase(parsed_result):
        print("✅ 所有测试通过！")
    else:
        print("❌ 测试用例生成失败")

if __name__ == "__main__":
    main()