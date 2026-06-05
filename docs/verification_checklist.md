# AI-English-Coach 交付核对清单

## 功能分支

- 场景选择：已实现面试、点餐、会议三类场景，数据在 `scenarios.py`。
- 文本对话：已通过 Streamlit 文本框和提交按钮完成，逻辑在 `app.py`。
- fallback AI 回复：无 API Key 时使用场景模板和关键词变化，逻辑在 `feedback.py`。
- 语法纠错：覆盖 `I am agree`、`discuss about`、`He go`、`want to + noun`、大小写、标点和短句提示。
- 长文本反馈：无明显语法错误时展示摘要、口语优化建议和建议口语版本，避免重复整篇文章。
- 五维评分：覆盖 Pronunciation、Fluency、Grammar、Expression、Completeness，逻辑在 `evaluator.py`。
- 课后总结：支持 Markdown 总结生成和下载，逻辑在 `report_generator.py`。
- 历史记录：每次练习保存 JSON，侧边栏可查看最近记录详情，逻辑在 `storage.py` 和 `app.py`。
- 音频上传：支持 wav、mp3、m4a；可选 `faster-whisper` / `whisper`，不可用时降级。
- API 模式：支持 `OPENAI_API_KEY`、`OPENAI_MODEL`、`OPENAI_BASE_URL`，失败时回退本地演示模式。
- 文档交付：README、比赛项目说明、示例对话、音频说明和测试脚本已提供。
- UI 设计：顶部状态总览、练习任务卡、快捷填入、空状态、高对比评分卡和五标签信息架构已完成。

## 验证命令

```bash
pytest -q
python scripts/smoke_test.py
python scripts/check_api.py
python scripts/render_canva_showcase.py
WHISPER_MODEL_SIZE=tiny.en python scripts/test_transcription.py
streamlit run app.py
```

## 当前验证结果

- `pytest -q`：通过，覆盖 11 个核心测试。
- `python scripts/smoke_test.py`：通过。
- `python scripts/check_api.py`：dry run 通过，不发送真实 API 请求。
- `python scripts/render_canva_showcase.py`：通过，生成 `outputs/canva_showcase.png`。
- `WHISPER_MODEL_SIZE=tiny.en python scripts/test_transcription.py`：样例音频成功转写。
- 浏览器页面：`http://localhost:8501` 可打开并展示聊天式练习页面。

## 仍属于演示级的部分

- Pronunciation 发音评分仍为模拟评分，不是真实发音评测。
- API 模式未做 live 请求，避免产生额外花销。
- Whisper 模型是可选依赖，首次使用需要下载模型。

## V1.0 完整版新增分支

- 结构化练习：`course_plan.py` 提供四阶段练习任务、当前步骤和完成度。
- 学习统计：`analytics.py` 提供总次数、平均分、最高分、场景分布、趋势、维度均分和高频错误。
- 历史管理：页面支持筛选、详情查看、JSON 下载和删除记录。
- 报告导出：`report_exporter.py` 支持把课后总结导出为 HTML 报告。
- UI 分区：主页面升级为练习中心、历史记录、学习统计、报告导出、设置说明五个标签页。
- 视觉说明：`docs/ui_design_spec.md` 记录视觉设计、交互设计、信息架构和 Figma/Canva 复刻建议。
- 产品设计 QA：`docs/product_design_qa.md` 按页面好看、好用、清楚三项目标给出验收结论。
- 非 Canva 完成状态：`docs/non_canva_completion_status.md` 记录当前本地、Figma、Product Design 和测试验证结果。
- 外部工具状态：`docs/external_design_tool_status.md` 记录 Figma Starter 调用额度限制和 Canva 在线生成工具未暴露的情况。
- Figma 设计稿：<https://www.figma.com/design/p7RyLn8dlM23u6Ica8ehsY>
- Figma 画板验证：已生成 `AI-English-Coach Desktop UI - Practice Screen`、`AI-English-Coach Design Handoff - Tokens and UX Flow` 和 `AI-English-Coach Canva Showcase Poster` 三个可编辑画板。
- 暂停项：Canva 在线设计链接先不作为当前完成条件；本地已保留 Canva 风格 HTML、PNG、生成脚本和 Magic Design 提示，后续可恢复。
