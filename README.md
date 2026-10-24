# anything-to-doubao

多源内容智能处理器：把公众号文章、网页、PDF、Office 文档、图片、音频、抖音/B站/快手视频等任意内容，自动变成 **播客 / PPT / 思维导图 / 深度分析报告 / Quiz**。

> 面向国内使用场景设计：免代理、免境外服务，抖音生态原生友好。生成层完全基于豆包本地能力。

## 它能做什么

| 输入 | 输出 |
|---|---|
| 微信文章链接 | 中文播客（双主持对谈 MP3） |
| PDF / Word / PPT / Excel / EPUB | PPT、思维导图、报告 |
| 普通网页 / 付费文章 | 深度分析、Quiz |
| 抖音 / B站 / 快手视频 | 思维导图、内容总结 |
| 多篇资料（最多任意组合） | 多源综合报告、观点对比 |

## 核心能力

- **多源获取**：微信公众号直抓正文；网页三级回退抓取（直连 → 代理服务 → 存档）；本地文件全格式转换（markitdown）
- **豆包生成层**：TTS 播客、飞书幻灯片 PPT、ECharts 交互式思维导图、带来源引用的深度分析
- **深度分析模式**：三轮递进 12 问（概览框架 → 深度挖掘 → 综合反刍），每轮答案标注原文出处
- **基于来源引用**：生成内容严格基于资料原文，原文没有的信息明确标注，不编造
- **抖音适配**：本地视频 → 音频提取 → 转写 → 生成的完整通道

## 目录结构

```
anything-to-doubao/
├── SKILL.md                # 技能定义与工作流（豆包环境自动加载）
├── scripts/
│   ├── fetch_content.py    # 微信文章 / 本地文件统一获取 → TXT
│   ├── fetch_url.py        # 普通网页抓取（直连 → r.jina.ai → archive 回退）
│   └── extract_audio.py    # 视频提取音频（PyAV，无 ffmpeg 依赖）
```

## 安装

```bash
# 放到豆包用户技能目录（Windows 示例）
C:\Users\<你>\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills\

# 依赖
pip install httpx beautifulsoup4 "markitdown[all]" av
```

## 使用方式

在豆包环境中直接说：

```text
"把这篇微信文章做成播客 https://mp.weixin.qq.com/s/..."
"这个 PDF 生成 PPT D:\docs\report.pdf"
"这个抖音视频画个思维导图"（附视频文件或文案）
"把这篇文章和这个网页一起生成一份对比报告"
```

## 脚本用法（命令行）

```bash
# 获取内容
python scripts/fetch_content.py <微信链接或本地文件> <输出.txt>
python scripts/fetch_url.py <网页URL> <输出.txt>

# 视频转音频（抖音/B站/快手等本地文件）
python scripts/extract_audio.py <视频.mp4> <输出.wav>
```

## 致谢与许可

本项目为独立实现，设计思路受 [qiaomu-anything-to-notebooklm](https://github.com/joeseesun/qiaomu-anything-to-notebooklm)（MIT License, Copyright (c) 2026 Joe）启发：保留其多源内容获取思想，生成层完全改为豆包本地能力，并针对国内环境与抖音生态重新设计。

- 原项目：https://github.com/joeseesun/qiaomu-anything-to-notebooklm（MIT License）
- 本项目 License：MIT（见 [LICENSE](LICENSE)）

## 声明

- 仅供个人学习研究使用，请遵守目标网站的服务条款与内容版权
- 网页抓取通道（含代理服务与存档站）仅用于获取公开内容，不对付费墙内容做规避性分发
- 生成内容请核实后使用

## License

MIT
