# AI-English-Coach 比赛现场演示脚本

## 使用场景

本脚本用于比赛项目展示、评委现场讲解或项目说明录屏。目标是在 5 分钟左右讲清楚：

- 这个项目解决什么问题；
- 页面如何让用户顺利完成英语口语练习；
- 为什么无 API Key 也能稳定演示；
- 视觉设计、交互设计和信息架构分别体现在哪里；
- 当前有哪些可验证的运行证据。

## 演示准备

启动项目：

```bash
cd "/Users/ferdavismuyassar/Documents/qiniu project/AI-English-Coach"
streamlit run app.py
```

打开页面：

```text
http://localhost:8501
```

建议预先准备的展示材料：

| 用途 | 文件 |
| --- | --- |
| 练习中心首页 | `outputs/screenshot_competition_v1.png` |
| 历史记录 | `outputs/screenshot_competition_history.png` |
| 学习统计 | `outputs/screenshot_competition_stats.png` |
| 报告导出 | `outputs/screenshot_competition_export.png` |
| 设置说明 | `outputs/screenshot_competition_settings.png` |
| 产品展示海报 | `outputs/canva_showcase.png` |
| Figma 设计稿 | <https://www.figma.com/design/p7RyLn8dlM23u6Ica8ehsY> |

## 5 分钟讲解流程

### 1. 开场定位

建议话术：

> 我们的项目是 AI-English-Coach，一款面向英语口语场景训练的本地可运行工具。它支持面试、点餐和会议三类场景，用户输入英文回答后，系统会给出 AI 角色回复、纠错反馈、表达优化、五维评分和课后总结。

要点：

- 这是一个能运行的产品原型，不只是静态页面。
- 项目重点是稳定演示和完整闭环。
- 无 `OPENAI_API_KEY` 时会自动进入本地演示模式。

建议展示：

- `outputs/screenshot_competition_v1.png`

### 2. 核心练习流程

现场操作顺序：

1. 在左侧选择 `面试 Interview`。
2. 难度选择 `中等`。
3. 在练习中心查看当前练习任务。
4. 点击 `填入示例回答`。
5. 点击 `提交练习`。
6. 观察 AI 回复、纠错反馈和评分结果。
7. 点击 `生成课后总结`。

建议话术：

> 用户不需要先学习复杂规则。页面会先告诉用户当前练习任务，再提供建议问题和目标表达。提交后，AI 回复、纠错反馈和评分集中显示在右侧，用户可以马上知道自己哪里说得好、哪里需要改。

设计说明：

- 好用：快捷填入降低比赛现场演示风险。
- 清楚：输入区、AI 回复、纠错反馈、评分区分层展示。
- 稳定：无 Key 时 fallback 流程仍能完整跑通。

### 3. 视觉设计说明

建议话术：

> 页面采用深色学习工具风格，避免默认表单感。顶部 Hero 展示当前模式、场景、难度和进度，评分卡使用高对比深色卡片，解决了之前深色主题下分数看不清的问题。

对应证据：

- `docs/ui_design_spec.md`
- `docs/product_design_qa.md`
- `outputs/canva_showcase.png`

重点说明：

- 视觉设计：深色背景、统一色彩、清晰状态卡。
- 评分区域：白色分数、浅灰说明、蓝绿进度条。
- 展示图：可直接放入比赛项目说明或展示 PPT。

### 4. 信息架构说明

建议话术：

> 我们没有把所有功能堆在一个长页面，而是拆成五个标签页：练习中心、历史记录、学习统计、报告导出和设置说明。练习中心负责高频操作，历史和统计负责复盘，报告导出负责提交材料，设置说明负责运行和测试。

建议展示顺序：

1. `outputs/screenshot_competition_v1.png`
2. `outputs/screenshot_competition_history.png`
3. `outputs/screenshot_competition_stats.png`
4. `outputs/screenshot_competition_export.png`
5. `outputs/screenshot_competition_settings.png`

对应说明：

- 练习中心：完成当前对话练习。
- 历史记录：证明 JSON 保存和记录管理。
- 学习统计：证明数据复盘能力。
- 报告导出：证明 Markdown / HTML 输出能力。
- 设置说明：证明项目可测试、可配置、可扩展。

### 5. 双模式与工程稳定性

建议话术：

> 比赛现场最重要的是稳定运行。这个项目支持 API 模式和本地演示模式。如果存在 `OPENAI_API_KEY`，系统可以调用 API；如果没有 Key 或 API 失败，系统会自动使用模板回复、规则纠错、启发式评分和模板总结，不会因为外部服务不可用而中断。

可讲模块：

- `api_client.py`：API 配置和降级。
- `feedback.py`：AI 回复和纠错反馈。
- `evaluator.py`：五维评分。
- `storage.py`：JSON 历史保存。
- `report_exporter.py`：HTML 报告导出。

### 6. 测试与验收结果

建议话术：

> 当前版本已经通过核心测试和 smoke test。本地页面返回 200 OK，核心测试覆盖场景回复、纠错、评分、总结、历史保存和音频降级。

验证命令：

```bash
pytest -q
python scripts/smoke_test.py
python scripts/check_api.py
python scripts/render_canva_showcase.py
```

当前结果：

| 验证项 | 结果 |
| --- | --- |
| `pytest -q` | `11 passed` |
| `python scripts/smoke_test.py` | 通过 |
| `python scripts/check_api.py` | 无 Key dry run 正常 |
| `http://localhost:8501` | `200 OK` |
| Figma Slides | 已生成比赛项目展示稿预览 |

### 7. 收尾总结

建议话术：

> AI-English-Coach 的核心价值是低成本、可本地运行、完整闭环。它把场景练习、AI 追问、纠错反馈、五维评分、课后总结、历史保存和报告导出串成一个稳定流程。当前版本适合比赛现场演示，后续可以继续增强真实发音评分、更多场景和更细的练习计划。

## 评委可能会问的问题

### 1. 没有 API Key 时是不是只是空页面？

不是。没有 API Key 时系统自动进入本地演示模式，仍然可以完成 AI 回复、纠错、评分、总结和历史保存。

### 2. 发音评分是否是真实评测？

当前 Pronunciation 是模拟评分，页面和文档中已经说明。第一版重点是完整流程和稳定演示，后续可以接入真实发音评测或本地语音特征分析。

### 3. 音频模型不可用怎么办？

音频转写是可选能力。如果 `faster-whisper` 或 `whisper` 不可用，系统会提示使用文本输入，不影响主流程。

### 4. 数据保存在哪里？

练习历史保存到 `outputs/` 目录下的 JSON 文件。课后总结可以导出 Markdown，学习报告可以生成 HTML。

### 5. 页面设计如何证明不是临时堆出来的？

项目提供了三类证据：

- 运行页面截图；
- Figma 可编辑设计稿和 Figma Slides 展示稿；
- `docs/ui_design_spec.md` 与 `docs/product_design_qa.md` 中的设计说明和 QA 结论。

## 演示检查清单

- [ ] 本地页面可以打开：`http://localhost:8501`
- [ ] 当前模式显示为本地演示模式或 API 模式。
- [ ] 练习中心能填入示例回答并提交。
- [ ] 页面能显示 AI 回复、纠错反馈和五维评分。
- [ ] 能生成课后总结。
- [ ] 历史记录页能看到保存记录。
- [ ] 学习统计页能显示指标和趋势。
- [ ] 报告导出页能说明 Markdown / HTML 导出能力。
- [ ] 设置说明页能展示测试命令。
- [ ] 展示图 `outputs/canva_showcase.png` 可正常打开。
