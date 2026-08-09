---
name: novel-writer
description: NovelForge 自动化小说写作工作流。读取进度→生成下一章→质检→提交推送。用于逐章创作、全书生成、断点续跑。
agent_created: true
---

# novel-writer · 自动化小说写作工作流

NovelForge 的编排技能。按状态机执行「大纲 → 逐章创作 → 质检 → Git 提交推送」,支持断点续跑与错误重试。

## 前置条件

- 仓库根目录为工作区,包含 `novel-config.json`、`outline/chapter-plan.json`、`state/progress.json`。
- 辅助脚本:`scripts/nf.py`(进度读写、台账原子更新、L1 质检)。
- Python:使用 `/Users/mac/.workbuddy/binaries/python/versions/3.13.12/bin/python3`(或任意 python3)。

## 执行流程(严格顺序)

### Step 0 · 读进度(断点续跑)

```bash
python3 scripts/nf.py progress
```

- `phase=OUTLINE` 且 `outlineDone=false` → 先执行大纲生成(见 §A)。
- `phase=WRITING` → 取 `nextChapter`,执行单章创作(见 §B)。

### §A 大纲生成(仅在 outlineDone=false 时)

1. 读 `novel-config.json`。
2. 三段式生成:
   - 世界观 → `outline/worldbuilding.md`
   - 人物 → `outline/characters.md`
   - 章节骨架 → `outline/chapter-plan.json` + `outline/story-outline.md`
   - 文风基准 → `outline/style-guide.md`
3. 初始化台账:`memory/timeline.json`、`character-state.json`、`foreshadowing.json`、`plot-threads.json`。
4. 更新进度:`python3 scripts/nf.py progress-set phase=WRITING outlineDone=true nextChapter=1`。
5. 提交:`git commit -m "outline: 生成大纲 v1.0.0"`。

### §B 单章创作(核心循环)

**每章严格 6 步:**

1. **读上下文**:本章计划(`chapter-plan.json` 中 `chapters[index-1]`)+ 四个台账 + 上一章末尾 200 字。
2. **生成正文**到 `chapters/chapter-{编号}.md`,头部 YAML 元信息(chapter/title/arc/pov/date/words/status/qc_score),正文后注释块记结构备忘与伏笔操作。
3. **L1 质检**:
   ```bash
   python3 scripts/nf.py qc-l1 chapters/chapter-001.md
   ```
   不通过 → 修复后重跑,最多 2 次。
4. **L2 质检**(LLM 评审):按 5 维度评分卡(角色一致性 0.25 / 情节逻辑 0.25 / 文风贴合 0.20 / 悬念钩子 0.15 / 伏笔执行 0.15),阈值 7.5。生成 `reports/qc-chapter-{编号}.md`。FAIL → 携带评审意见重写(≤2 次),仍 FAIL → 标记 `needs-human`,跳过本章并记录 `logs/errors.log`。
5. **原子更新台账**:
   - 伏笔:本章播种的 `status: planned → planted`,回收的 → `paidoff` + `payoffAt`。
   - 角色状态:更新位置 / 心理状态 / 新增认知 / 关系。
   - 时间线:追加本章事件与时间锚点。
   - 情节线:更新各线状态。
   - 更新正文 YAML:`status: passed`、`qc_score`。
6. **提交**:`git add -A && git commit -m "chapter-{编号}: {标题}"`;更新进度 `progress-set nextChapter={编号+1}`。推送见 §C。

### §C 版本管理与推送

- 每章一个 commit,格式 `chapter-{编号}: {标题}`。
- 全部章节完成后:更新 README 版本历史,打 tag `v1.0.0` 并推送。
- 推送方式(任选其一,已实测):
  - **方式 A(推荐)**:GitHub 集成(connector)的 push_files API 推送单个 commit 内容到远程。
  - **方式 B**:Contents API + PAT —— 用 `PUT /repos/{owner}/{repo}/contents/{path}` 逐文件上传,message 即 commit 说明。实测可用(网络环境下 github.com 主站可能不可达,但 api.github.com 可达,故 git CLI push 可能失败,API 方式更稳)。
  - **方式 C**:git CLI push(需 github.com 主站网络可达 + 凭据)。
- 推送失败重试 3 次;仍失败则保留本地 commit,记录 `logs/errors.log`,下次运行增量补推。

## 错误重试与容错

| 失败类型 | 重试 | 兜底 |
|---|---|---|
| 生成异常/超时 | 3 次(指数退避 10s/30s/90s) | 记录日志,标记 retry-pending |
| JSON 解析失败 | 3 次 | 回滚上次合法版本 |
| 质检 FAIL | 重写 ≤2 次 | needs-human 跳过本章 |
| git push 失败 | 3 次 | 本地保留,下次补推 |

## 质量红线

- 禁止:角色 OOC、时间线矛盾、伏笔悬空不登记。
- 字数:目标 ±40%(脚本区间),尽量贴近目标。
- 每章结尾必须有钩子(末章除外)。
- 永不丢失已写正文(先写文件、台账原子写、git 保护)。

## 输出规范

- Markdown 按章分文件:`chapters/chapter-{编号}.md`。
- 头目录:`README.md`(简介 + 卷章导航 + 世界观人物链接 + 版本历史)。
- 头部 YAML 元信息 + 尾部结构注释块。
