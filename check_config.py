#!/usr/bin/env python3
"""
配置检查脚本
用于验证需求生成测试用例系统的配置是否正确
"""

import os
import sys
from pathlib import Path
import requests

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro} (需要 >= 3.8)")
        return False

def check_env_file():
    """检查环境变量文件"""
    print("\n📁 检查环境变量文件...")

    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env 文件存在")

        # 读取环境变量
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查必需的环境变量
        api_key_configured = False
        base_url_configured = False

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('OPENAI_API_KEY='):
                api_key = line.split('=', 1)[1].strip()
                if api_key and api_key != 'your_openai_api_key_here':
                    api_key_configured = True
                    print("✅ OPENAI_API_KEY 已配置")
                else:
                    print("❌ OPENAI_API_KEY 未配置或使用默认值")
            elif line.startswith('OPENAI_BASE_URL='):
                base_url = line.split('=', 1)[1].strip()
                if base_url:
                    base_url_configured = True
                    print(f"✅ OPENAI_BASE_URL 已配置: {base_url}")

        if not api_key_configured:
            print("❌ 缺少有效的 OPENAI_API_KEY 配置")
            return False

        if not base_url_configured:
            print("⚠️  未配置 OPENAI_BASE_URL，将使用默认值")

        return True
    else:
        print("❌ .env 文件不存在")
        print("💡 请复制 .env.example 为 .env 并配置API密钥")
        return False

def check_dependencies():
    """检查Python依赖"""
    print("\n📦 检查Python依赖...")

    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'openai',
        'python-dotenv',
        'requests'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")

    if missing_packages:
        print(f"\n💡 安装缺失的依赖: pip install {' '.join(missing_packages)}")
        return False

    return True

def check_api_connection():
    """检查API连接"""
    print("\n🌐 检查API连接...")

    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')

    if not api_key:
        print("❌ OPENAI_API_KEY 未配置")
        return False

    try:
        import openai

        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        # 发送一个简单的测试请求
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )

        print("✅ API连接正常")
        return True

    except openai.AuthenticationError:
        print("❌ API密钥无效或已过期")
        return False
    except openai.RateLimitError:
        print("❌ API配额已用完或频率超限")
        return False
    except openai.APIConnectionError:
        print("❌ 无法连接到API服务，请检查网络或API地址")
        return False
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def check_ports():
    """检查端口占用"""
    print("\n🔌 检查端口占用...")

    import socket

    ports = [
        (8005, "后端API"),
        (5174, "前端开发服务器")
    ]

    for port, service in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        try:
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                print(f"⚠️  端口 {port} ({service}) 已被占用")
            else:
                print(f"✅ 端口 {port} ({service}) 可用")
        except Exception:
            print(f"❌ 检查端口 {port} 失败")
        finally:
            sock.close()

def main():
    """主检查函数"""
    print("🔍 需求生成测试用例系统 - 配置检查")
    print("=" * 50)

    checks = [
        ("Python版本", check_python_version),
        ("环境变量文件", check_env_file),
        ("Python依赖", check_dependencies),
        ("API连接", check_api_connection),
        ("端口占用", check_ports)
    ]

    results = []

    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 检查失败: {e}")
            results.append((name, False))

    # 总结
    print("\n" + "=" * 50)
    print("📊 检查结果总结:")

    passed = 0
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
        if result:
            passed += 1

    print(f"\n总计: {passed}/{total} 项检查通过")

    if passed == total:
        print("🎉 所有检查通过，系统配置正常！")
        print("\n🚀 可以运行以下命令启动系统:")
        print("  ./start.sh")
        return True
    else:
        print("⚠️  存在配置问题，请根据上述提示修复后重新检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)