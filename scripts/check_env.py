#!/usr/bin/env python3
"""
环境自检脚本：验证 viral-post-distiller skill 运行所需的环境是否就绪。

依赖检查：
1. Python 版本 ≥ 3.10
2. requests 库已安装
3. TIKHUB_API_KEY 已配置（环境变量或 config.json）

使用：
    python3 scripts/check_env.py

退出码：
    0 = 全部通过
    1 = 有项失败（终端会打印详情）
"""

import sys
import os
import json
from typing import Tuple
from pathlib import Path


# 颜色码（让输出更直观）
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def check_python_version() -> Tuple[bool, str]:
    """Check Python >= 3.9"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, (
        f"Python {version.major}.{version.minor}.{version.micro} "
        f"(需要 3.9+，请升级)"
    )


def check_requests() -> Tuple[bool, str]:
    """Check requests installed"""
    try:
        import requests
        return True, f"requests {requests.__version__}"
    except ImportError:
        return False, "requests 未安装。运行: pip3 install requests"


def find_api_key() -> Tuple[bool, str]:
    """
    Try 2 places for API key:
    1. env var TIKHUB_API_KEY
    2. <skill_root>/config.json
    """
    # 1. env var
    key = os.environ.get('TIKHUB_API_KEY')
    if key:
        masked = key[:8] + '***' if len(key) > 8 else '***'
        return True, f"TIKHUB_API_KEY (env var) = {masked}"

    # 2. config.json
    skill_root = Path(__file__).parent.parent
    config_path = skill_root / 'config.json'
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
            key = config.get('tikhub_api_key')
            if key:
                masked = key[:8] + '***' if len(key) > 8 else '***'
                return True, f"TIKHUB_API_KEY (config.json) = {masked}"
        except json.JSONDecodeError:
            return False, f"config.json 格式错误：{config_path}"

    return False, (
        "未找到 TIKHUB_API_KEY。请用以下任一方式配置：\n"
        "    方式 1（推荐）: echo 'export TIKHUB_API_KEY=\"你的key\"' >> ~/.zshrc && source ~/.zshrc\n"
        f"    方式 2: 在 {skill_root}/ 下创建 config.json，内容: {{\"tikhub_api_key\": \"你的key\"}}"
    )


def main() -> int:
    print("=" * 50)
    print("viral-post-distiller 环境自检")
    print("=" * 50)

    checks = [
        ("Python 版本", check_python_version),
        ("requests 库", check_requests),
        ("TikHub API Key", find_api_key),
    ]

    all_passed = True
    for label, check_fn in checks:
        ok, msg = check_fn()
        if ok:
            print(f"{GREEN}✅ {label}{RESET}: {msg}")
        else:
            print(f"{RED}❌ {label}{RESET}: {msg}")
            all_passed = False

    print("=" * 50)
    if all_passed:
        print(f"{GREEN}全部通过，可以使用 skill。{RESET}")
        return 0
    else:
        print(f"{RED}有项失败，请按上面的提示修复后重试。{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
