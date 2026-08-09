# 雾海孤灯

> 悬疑科幻 · 6 章 · 状态:✅ 已完结(v1.0.0)

## 简介

2087 年,被永久海雾隔离的孤岛城市「雾港」。记忆维修师林澈发现自己的记忆出现一天空白,在追查真相中,他揭开了一个由城市守护者"灯塔"维持了三十年的记忆篡改体系。记忆,到底该被抹去,还是被找回?

## 卷章导航

- **第一幕 引子**(第 1–2 章)
  - [第 1 章 雾中来客](chapters/chapter-001.md) — 已发布
  - [第 2 章 校准](chapters/chapter-002.md) — 已发布
- **第二幕 逼近**(第 3–4 章)
  - [第 3 章 删除层](chapters/chapter-003.md) — 已发布
  - [第 4 章 雾祭](chapters/chapter-004.md) — 已发布
- **第三幕 抉择与收束**(第 5–6 章)
  - [第 5 章 守灯人](chapters/chapter-005.md) — 已发布
  - [第 6 章 雾散](chapters/chapter-006.md) — 已发布

## 世界观与人物

- [世界观设定](outline/worldbuilding.md)
- [人物设定](outline/characters.md)
- [文风手册](outline/style-guide.md)
- [总纲与伏笔台账](outline/story-outline.md)

## 创作配置

- [创作配置](novel-config.json)(题材 / 风格 / 目标字数)
- [章节计划](outline/chapter-plan.json)(机读)

## 工程信息

- 工作流辅助脚本:`scripts/nf.py`(进度 / 台账 / L1 质检)
- 质检报告:`reports/`
- 断点续跑状态:`state/progress.json`

## 构建与运行

本仓库由 NovelForge 自动化工作流驱动。重新触发创作:

```bash
# 查看进度
python3 scripts/nf.py progress

# 生成下一章(由编排器执行完整流水线:创作 → 质检 → 提交)
# 详见 .workbuddy/skills/novel-writer/SKILL.md
```

## 版本历史

| 版本 | 说明 |
|---|---|
| v0.1.0 | 大纲生成完成 |
| v0.2.0 | 第 1 章发布 |
| v0.3.0 | 第 2 章发布 |
| v0.4.0 | 第 3 章发布 |
| v0.5.0 | 第 4 章发布 |
| v0.6.0 | 第 5 章发布 |
| **v1.0.0** | **全书完结(6 章)** |
