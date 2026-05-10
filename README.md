# Viral Post Distiller

> 拆解抖音爆款 + 帮你写同款的 Claude Code skill。
> 不只告诉你"为什么这条火"，更直接产出一篇可发布的同款笔记。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-orange)](https://docs.claude.com/en/docs/claude-code)
[![TikHub API](https://img.shields.io/badge/data-TikHub%20API-blueviolet)](https://tikhub.io)

---

## 这个 skill 在解决什么

绝大多数爆款分析工具都停在"现象层"——告诉你视频用了什么标题公式、什么钩子。但**模仿这些招式做不出爆款**——因为你不知道怎么把"同样的爆款基因"迁移到你自己的主题上。

本 skill 做两件事：

- 🔍 **拆解**：从「封面与标题」「内容结构」「情绪与需求」「爆款基因」四个模块严谨拆出"为什么这条火"
- ✍️ **迁移**：你给一个新主题，skill 直接帮你写一篇同款 —— 5 个不同公式的标题备选 + 完整正文 + 话题标签 + 封面建议

**核心差异化**：不只让你"理解爆款"，让你"立刻产出爆款"。

---

## 工作流

```
你扔抖音链接
    ↓
skill 自动通过 TikHub 取数 + 四模块拆解
    ↓
输出拆解报告（output/拆解_xxx.md）
    ↓
skill 主动询问：「要不要我用同款基因帮你写一篇？」
    ↓
你给新主题
    ↓
输出创作产出（output/创作_xxx.md）
```

两份产出物，**拆解能看懂、创作能直接发**。

---

## 安装

### 前置要求

- macOS / Linux
- Python 3.9+
- [Claude Code](https://docs.claude.com/en/docs/claude-code) 已安装并登录
- TikHub API Key — [免费注册](https://user.tikhub.io/) → 充值少量余额（每条视频成本约 $0.01）

### 步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/IreneYan/viral-post-distiller.git
cp -r viral-post-distiller ~/.claude/skills/
```

#### 2. 配置 TikHub API Key

推荐用环境变量：

```bash
echo 'export TIKHUB_API_KEY="你的key"' >> ~/.zshrc
source ~/.zshrc
```

或者在 skill 目录下创建 `config.json`：

```json
{
  "tikhub_api_key": "你的key"
}
```

> ⚠️ `config.json` 已在 `.gitignore` 里，不会被意外提交。

#### 3. 安装 Python 依赖

```bash
pip3 install requests
```

#### 4. 验证安装

```bash
cd ~/.claude/skills/viral-post-distiller
python3 scripts/check_env.py
```

期望看到三项全绿 ✅✅✅。

---

## 使用

启动 Claude Code（推荐加 `--dangerously-skip-permissions` 跳过每步确认）：

```bash
claude --dangerously-skip-permissions
```

然后扔链接：

```
拆解这条抖音 https://v.douyin.com/xxxxx/
```

skill 跑完拆解后会**主动询问**要不要写同款，回答即可。

---

## 产出示例

### 拆解报告（节选）

```markdown
# 抖音爆款拆解：0 粉新人发一个问题，靠评论区众包出福田大排档地图

## 🎯 模块 1：封面与标题

### 标题公式
- 主公式：提问型 + 身份代入（双钩叠加）
- 公式证据：「第一次来深圳」激活身份代入,「有没有热心网友」激活提问型

### SEO/搜索关键词
- 品类:大排档、深圳美食
- 地域:福田区
- 需求:推荐
- 组合策略:「地域 + 品类 + 求推荐」三段式

## 🧬 模块 4:爆款基因提炼

1. 反共识身份钩子(「第一次来」+「热心网友」)
2. 地域精准限定(仅限福田区)
3. UGC 触发器结构(问题 > 答案)
4. 评论区即产品(193 评论 vs 116 赞)
5. 0 信息密度文案(仅 50 字 + 3 标签)
```

### 创作产出（节选）

```markdown
# 同款创作:25 岁姐妹,有没有靠谱的 INFJ 抗内耗书单

## 🎯 标题备选(5 个,5 种公式)

【备选 1】(数字型)
> INFJ 必看的 3 本抗内耗书,救了我半年

【备选 2】(身份代入)
> 25 岁 INFJ 姐妹,你们都是怎么扛过内耗期的

【备选 3】(悬念型)
> 我以为是焦虑症,看完这本书才知道是 INFJ 通病

【备选 4】(利益承诺型)
> 看完这 5 本书,我半年没情绪内耗过一次

【备选 5】(提问型)
> 有没有 INFJ 姐妹,推荐几本真的抗内耗的书

## 📝 完整正文
[基于原爆款的 UGC 触发器结构产出的同款正文]

## 🏷️ 话题标签
#INFJ #抗内耗 #25 岁焦虑 #人格成长 #自我接纳

## 🖼️ 封面建议
- 视觉类型:文字密集型
- 主标题大字:「INFJ 抗内耗 救命书单」
- 配色情绪:莫兰迪冷淡治愈
```

---

## 当前版本：v0.2

### ✅ 已支持

- 抖音单条作品自动拆解
- 四模块拆解（封面标题 / 内容结构 / 情绪需求 / 爆款基因）
- 8 公式标题库（数字 / 痛点 / 身份代入 / 悬念 / 反差 / 利益承诺 / 对比 / 提问）
- 创作迁移：直接产出 5 个标题 + 完整正文 + 话题标签 + 封面建议
- 自动信号识别（评论 > 点赞 / 低粉爆款 / 高收藏率）
- 视频 / 图文笔记自动识别

### 🚧 路线图

- [ ] **v0.5** — 接入小红书
- [ ] **v0.5** — 评论区情绪分析
- [ ] **v1.0** — Sub-skill 知识资产化（积累多条同主题视频后自动蒸馏成专属创作助手）
- [ ] **v1.0** — 多视频对比模式（横向找规律）

---

## 项目结构

```
viral-post-distiller/
├── SKILL.md                          # Claude Code skill 元定义
├── scripts/                          # 执行层（确定性任务）
│   ├── check_env.py                  # 环境自检
│   ├── fetch_post.py                 # 主入口：链接 → 标准化 JSON
│   └── utils/
│       ├── tikhub_client.py          # TikHub HTTP 客户端
│       └── adapter.py                # 数据归一化 + 信号推导
├── references/                       # AI prompt 资产（创造性任务）
│   ├── post-anatomy-prompt.md        # 四模块拆解 prompt
│   ├── title-formulas.md             # 8 公式标题库
│   ├── creation-transfer-prompt.md   # 创作迁移 prompt（核心）
│   ├── output-template.md            # 拆解报告模板
│   └── creation-template.md          # 创作产出模板
├── data/                             # 缓存原始 JSON（git ignore）
└── output/                           # 输出报告（git ignore）
```

**设计哲学**：脚本干确定的事（取数 / IO / 信号计算），AI 干创造的事（拆解 / 信念挖掘 / 创作）。

---

## 贡献指南

欢迎以下贡献：

- 🐛 **Bug 反馈**：用了之后发现某个环节不对，开 [Issue](https://github.com/IreneYan/viral-post-distiller/issues)
- 💡 **prompt 优化**：你拆出来一份高质量报告，把它发我（脱敏后），帮我打磨 prompt
- 📝 **文档改进**：发现 README 哪里不清楚，PR welcome
- 🌐 **平台扩展**：想接小红书 / B 站 / YouTube？欢迎 PR
- 🎨 **新框架**：想加 SCQA、AIDA、五段式等其他分析框架？欢迎 PR

提 PR 前请简单说明改动思路，避免无效工作。

---

## 隐私与合规

- TikHub API Key 只存在用户本地（环境变量或 `config.json`），**永不上传任何地方**
- 本 skill 不收集任何使用数据
- TikHub 是商业 API 服务，请遵守其使用条款
- **本 skill 仅供学习和个人内容研究使用**，请勿用于大规模数据抓取或商业转售

---

## 鸣谢

- 项目灵感来自三个开源 skill：
  - [chenxiachan/xhs-claude-skills](https://github.com/chenxiachan/xhs-claude-skills) — 小红书数据获取思路
  - [ALBEDO-TABAI/video-copy-analyzer](https://github.com/ALBEDO-TABAI/video-copy-analyzer) — 字幕提取三级火箭设计
  - [otter1101/blogger-distiller](https://github.com/otter1101/blogger-distiller) — "脚本 30%、AI 70%" 架构哲学

- 数据来源：[TikHub.io](https://tikhub.io) — 抖音/小红书 API 服务

- 8 公式标题库参考了多份小红书/抖音运营方法论的总结

---

## License

[MIT](LICENSE) © 2026 Irene Yan
