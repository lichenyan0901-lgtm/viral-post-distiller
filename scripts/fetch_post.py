#!/usr/bin/env python3
"""
fetch_post.py — viral-post-distiller 的数据采集主入口

功能：
1. 接收一个抖音链接（短链或完整链接）
2. 调 TikHub API 拿原始数据
3. 用 adapter 归一化成内部标准结构
4. 推导 viral 信号
5. 把归一化数据存到 data/ 目录，stdout 也打印一份

使用：
    python3 scripts/fetch_post.py "https://v.douyin.com/xxxxx/"

退出码：
    0 = 成功
    1 = 链接格式错误
    2 = TikHub API 调用失败
    3 = 其他错误
"""

import sys
import json
import re
from pathlib import Path

# 让 utils 可以被 import
sys.path.insert(0, str(Path(__file__).parent))

from utils.tikhub_client import (  # noqa: E402
    fetch_douyin_post_by_share_url,
    TikHubAuthError,
    TikHubInsufficientFundsError,
    TikHubError,
)
from utils.adapter import adapt_douyin_post, derive_signals  # noqa: E402


# 颜色
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def normalize_share_url(raw_input: str) -> str:
    """
    用户可能粘贴抖音 App 完整分享文案，里面有一堆乱码。
    我们只提取里面的 v.douyin.com 短链或 douyin.com 完整链接。

    例如输入：
        "8.96 复制打开抖音... https://v.douyin.com/0s3YL9cCAjY/ tEu:/ ..."
    返回：
        "https://v.douyin.com/0s3YL9cCAjY/"
    """
    # 优先匹配短链
    short_link_pattern = r'https?://v\.douyin\.com/[A-Za-z0-9]+/?'
    match = re.search(short_link_pattern, raw_input)
    if match:
        return match.group(0)

    # 其次匹配完整链接
    full_link_pattern = r'https?://(?:www\.)?douyin\.com/video/\d+'
    match = re.search(full_link_pattern, raw_input)
    if match:
        return match.group(0)

    return raw_input.strip()


def is_valid_douyin_url(url: str) -> bool:
    """简单校验是不是抖音链接"""
    return bool(
        re.match(r'^https?://v\.douyin\.com/', url) or
        re.match(r'^https?://(www\.)?douyin\.com/video/', url) or
        re.match(r'^https?://(www\.)?iesdouyin\.com/', url)
    )


def main() -> int:
    if len(sys.argv) < 2:
        print(f"{RED}用法: python3 fetch_post.py <抖音链接>{RESET}", file=sys.stderr)
        return 1

    raw_input_url = sys.argv[1]
    share_url = normalize_share_url(raw_input_url)

    if not is_valid_douyin_url(share_url):
        print(
            f"{RED}❌ 链接无效：{share_url}{RESET}\n"
            f"{YELLOW}应为抖音分享链接，如 https://v.douyin.com/xxxxx/{RESET}",
            file=sys.stderr,
        )
        return 1

    print(f"📥 调用 TikHub 拉取作品数据...", file=sys.stderr)
    print(f"   链接: {share_url}", file=sys.stderr)

    # 调 API
    try:
        raw = fetch_douyin_post_by_share_url(share_url)
    except TikHubAuthError as e:
        print(f"{RED}❌ 鉴权失败{RESET}: {e}", file=sys.stderr)
        return 2
    except TikHubInsufficientFundsError as e:
        print(f"{RED}❌ 余额不足{RESET}: {e}", file=sys.stderr)
        return 2
    except TikHubError as e:
        print(f"{RED}❌ TikHub 调用失败{RESET}: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"{RED}❌ 未知错误{RESET}: {e}", file=sys.stderr)
        return 3

    # 归一化
    print(f"🔧 归一化数据...", file=sys.stderr)
    adapted = adapt_douyin_post(raw)
    signals = derive_signals(adapted)
    adapted['signals'] = signals

    # 存盘
    aweme_id = adapted['post']['aweme_id'] or 'unknown'
    skill_root = Path(__file__).parent.parent
    data_dir = skill_root / 'data'
    data_dir.mkdir(exist_ok=True)
    output_path = data_dir / f"{aweme_id}.json"
    output_path.write_text(
        json.dumps(adapted, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f"{GREEN}✅ 数据已保存到{RESET}: {output_path}", file=sys.stderr)

    # 打印简要摘要
    print("", file=sys.stderr)
    print(f"📌 摘要", file=sys.stderr)
    print(f"   作者: {adapted['author']['nickname']} (粉丝 {adapted['author']['follower_count']:,})", file=sys.stderr)
    print(f"   文案: {adapted['post']['desc'][:60]}{'...' if len(adapted['post']['desc']) > 60 else ''}", file=sys.stderr)
    print(f"   数据: 👍 {adapted['stats']['digg_count']:,} | 💬 {adapted['stats']['comment_count']:,} | "
          f"🔁 {adapted['stats']['share_count']:,} | ⭐ {adapted['stats']['collect_count']:,}", file=sys.stderr)

    if signals['comment_over_digg']:
        print(f"{YELLOW}   ⚡ 关键信号: 评论 > 点赞（讨论/求助型爆款）{RESET}", file=sys.stderr)
    if signals['is_low_follower_viral']:
        print(f"{YELLOW}   ⚡ 关键信号: 低粉爆款{RESET}", file=sys.stderr)
    if signals['collect_rate'] and signals['collect_rate'] > 0.5:
        print(f"{YELLOW}   ⚡ 关键信号: 高收藏率（工具/教程型，收藏/点赞 = {signals['collect_rate']}）{RESET}", file=sys.stderr)

    # 把归一化数据打到 stdout，方便上层直接读
    print(json.dumps(adapted, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
