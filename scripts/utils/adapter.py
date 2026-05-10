"""
TikHub 响应数据归一化适配器。

把 TikHub 的原始响应（字段繁杂、命名不统一、有 None 值）
归一化成本 skill 内部使用的标准结构。

设计原则：
- 只保留拆解爆款用得到的字段，丢掉冗余
- 给所有字段加合理的兜底值（None / 0 / 空字符串）
- 返回结构稳定，下游脚本和 prompt 都依赖它
"""

from typing import Any, Dict


def adapt_douyin_post(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    把 TikHub 抖音作品响应归一化成内部标准结构。

    Args:
        raw: TikHub 完整响应 dict（call_endpoint 的返回值）

    Returns:
        归一化后的 dict，结构详见 SCHEMA 注释
    """
    aweme = raw.get('data', {}).get('aweme_detail', {}) or {}
    author = aweme.get('author', {}) or {}
    stats = aweme.get('statistics', {}) or {}
    video = aweme.get('video', {}) or {}
    music = aweme.get('music', {}) or {}

    # 话题/标签
    text_extra = aweme.get('text_extra', []) or []
    hashtags = [
        item.get('hashtag_name', '')
        for item in text_extra
        if item.get('hashtag_name')
    ]

    # 视频时长（毫秒 → 秒）。注意：TikHub 偶尔会返回 0 或 None，下游要兜底
    duration_ms = video.get('duration') or aweme.get('duration') or 0
    duration_sec = duration_ms / 1000 if duration_ms else None

    # 封面 URL（取第一个）
    cover_urls = (video.get('cover') or {}).get('url_list', []) or []
    cover_url = cover_urls[0] if cover_urls else None

    # 视频播放 URL（取第一个）
    play_urls = (video.get('play_addr') or {}).get('url_list', []) or []
    play_url = play_urls[0] if play_urls else None

    # 是否图文
    is_image_post = bool(aweme.get('images') or aweme.get('image_list'))

    return {
        # === 作品本体 ===
        "post": {
            "aweme_id": aweme.get('aweme_id'),
            "share_url": aweme.get('share_url'),
            "desc": aweme.get('desc') or '',
            "create_time": aweme.get('create_time'),  # unix timestamp
            "duration_sec": duration_sec,
            "is_image_post": is_image_post,
            "cover_url": cover_url,
            "play_url": play_url,
            "hashtags": hashtags,
            "region": aweme.get('region'),
        },
        # === 互动数据 ===
        "stats": {
            "digg_count": stats.get('digg_count') or 0,        # 点赞
            "comment_count": stats.get('comment_count') or 0,  # 评论
            "share_count": stats.get('share_count') or 0,      # 分享
            "collect_count": stats.get('collect_count') or 0,  # 收藏
            "play_count": stats.get('play_count'),             # 播放（通常 None）
            "download_count": stats.get('download_count'),     # 下载
        },
        # === 作者画像 ===
        "author": {
            "nickname": author.get('nickname') or '',
            "short_id": author.get('short_id'),  # 抖音号
            "sec_uid": author.get('sec_uid'),
            "signature": author.get('signature') or '',
            "follower_count": author.get('follower_count') or 0,
            "following_count": author.get('following_count') or 0,
            "total_favorited": author.get('total_favorited') or author.get('favoriting_count') or 0,
            "aweme_count": author.get('aweme_count'),
            "verify_reason": author.get('custom_verify') or author.get('enterprise_verify_reason') or '',
        },
        # === BGM ===
        "music": {
            "title": music.get('title') or '',
            "author": music.get('author') or '',
            "is_original": music.get('is_original', False),
            "duration": music.get('duration'),
        },
    }


def derive_signals(adapted: Dict[str, Any]) -> Dict[str, Any]:
    """
    从归一化数据推导一些 viral 关键信号，给 AI 分析时用。

    这些信号是"算出来的事实"，不是 AI 猜的。
    """
    stats = adapted['stats']
    author = adapted['author']

    digg = stats['digg_count']
    comment = stats['comment_count']
    share = stats['share_count']
    collect = stats['collect_count']
    follower = author['follower_count']

    # 信号 1: 是否"评论 > 点赞"（讨论/求助型爆款的标志）
    comment_over_digg = comment > digg if digg > 0 else False

    # 信号 2: 收藏率（占点赞比例，高 = 工具/教程型）
    collect_rate = round(collect / digg, 2) if digg > 0 else None

    # 信号 3: 转发率（占点赞比例，高 = 社交货币型）
    share_rate = round(share / digg, 2) if digg > 0 else None

    # 信号 4: "低粉爆款"判断（粉丝少但互动高）
    interaction_total = digg + comment + share + collect
    interaction_per_follower = (
        round(interaction_total / follower, 2) if follower > 0 else None
    )
    is_low_follower_viral = (
        follower < 1000 and interaction_total > follower * 0.5
    )

    return {
        "comment_over_digg": comment_over_digg,
        "collect_rate": collect_rate,
        "share_rate": share_rate,
        "interaction_per_follower": interaction_per_follower,
        "is_low_follower_viral": is_low_follower_viral,
        "interaction_total": interaction_total,
    }
