"""
TikHub API HTTP client.

封装鉴权、错误处理、超时。所有对 TikHub 的请求都走这里。
"""

import os
import json
from pathlib import Path
from typing import Any, Dict

import requests


TIKHUB_BASE_URL = "https://api.tikhub.io"
DEFAULT_TIMEOUT = 30  # seconds


class TikHubError(Exception):
    """TikHub API 调用失败时抛出"""
    pass


class TikHubAuthError(TikHubError):
    """API Key 无效或鉴权失败"""
    pass


class TikHubInsufficientFundsError(TikHubError):
    """余额不足"""
    pass


def _load_api_key() -> str:
    """
    从两个可能的位置读取 API key:
    1. 环境变量 TIKHUB_API_KEY
    2. <skill_root>/config.json
    """
    key = os.environ.get('TIKHUB_API_KEY')
    if key:
        return key

    # config.json fallback
    skill_root = Path(__file__).parent.parent.parent
    config_path = skill_root / 'config.json'
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
            key = config.get('tikhub_api_key')
            if key:
                return key
        except json.JSONDecodeError:
            pass

    raise TikHubAuthError(
        "未找到 TIKHUB_API_KEY。请配置环境变量或 config.json，"
        "详见 README.md"
    )


def call_endpoint(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    调用一个 TikHub endpoint。

    Args:
        path: endpoint 路径，例如 "/api/v1/douyin/web/fetch_one_video_by_share_url"
        params: query string 参数

    Returns:
        TikHub 返回的完整 JSON（dict）

    Raises:
        TikHubAuthError: 鉴权失败
        TikHubInsufficientFundsError: 余额不足
        TikHubError: 其他失败
    """
    api_key = _load_api_key()

    url = f"{TIKHUB_BASE_URL}{path}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT
        )
    except requests.Timeout:
        raise TikHubError(f"请求超时 ({DEFAULT_TIMEOUT}s)")
    except requests.RequestException as e:
        raise TikHubError(f"网络错误: {e}")

    # 解析响应
    try:
        body = response.json()
    except ValueError:
        raise TikHubError(
            f"TikHub 返回非 JSON 内容（status={response.status_code}）: "
            f"{response.text[:200]}"
        )

    # HTTP 状态码
    if response.status_code == 401:
        raise TikHubAuthError(f"鉴权失败：API Key 无效或已过期。详情: {body}")
    if response.status_code == 402:
        raise TikHubInsufficientFundsError(
            f"TikHub 余额不足，请去 https://user.tikhub.io 充值。详情: {body}"
        )
    if response.status_code == 429:
        raise TikHubError(f"频率限制，请稍后重试。详情: {body}")
    if response.status_code >= 500:
        raise TikHubError(f"TikHub 服务端错误（{response.status_code}）: {body}")
    if response.status_code != 200:
        raise TikHubError(
            f"未知错误（status={response.status_code}）: {body}"
        )

    # TikHub 业务码
    if body.get('code') != 200:
        raise TikHubError(
            f"TikHub 业务错误（code={body.get('code')}）: "
            f"{body.get('message', body)}"
        )

    return body


def fetch_douyin_post_by_share_url(share_url: str) -> Dict[str, Any]:
    """
    根据分享链接拉取抖音作品详情。

    Args:
        share_url: 抖音分享短链，如 https://v.douyin.com/xxxxx/

    Returns:
        完整的 TikHub 响应 dict
    """
    return call_endpoint(
        path="/api/v1/douyin/web/fetch_one_video_by_share_url",
        params={"share_url": share_url},
    )
