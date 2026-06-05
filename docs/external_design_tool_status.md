# 外部设计工具状态记录

## 记录目的

本文件记录 Figma、Canva 与 Product Design 插件在当前项目中的实际使用状态，避免比赛项目说明或后续交付中混淆“已完成交付”和“受外部工具限制的交付”。

## Figma 状态

已完成：

- 已创建 Figma 可编辑设计文件：<https://www.figma.com/design/p7RyLn8dlM23u6Ica8ehsY>
- 已创建并验证 3 张可编辑画板：
  - `AI-English-Coach Desktop UI - Practice Screen`
  - `AI-English-Coach Design Handoff - Tokens and UX Flow`
  - `AI-English-Coach Canva Showcase Poster`

受限项：

- 后续尝试通过 Figma MCP 导出截图时，触发 Starter 计划 MCP tool call limit。
- 该限制不影响 Figma 文件本身存在，也不影响手动打开 Figma 链接截图。

建议操作：

1. 打开 Figma 链接。
2. 截图 3 张画板。
3. 放入比赛项目说明的“界面设计与展示”章节。

## Canva 状态

最近复查：2026-06-05 10:14（Asia/Shanghai）。结果仍未暴露 Canva 在线创建/编辑 MCP 工具；当前可调用的外部设计工具仍以 Figma 为主。

已完成：

- Canva 插件安装请求已经确认成功。
- 本地已提供 Canva 风格展示页：`docs/canva_showcase.html`
- 本地已生成 Canva 风格展示 PNG：`outputs/canva_showcase.png`
- 已提供可复现生成脚本：`scripts/render_canva_showcase.py`
- 已提供 Canva 在线生成提示：`docs/canva_generation_prompt.md`
- Figma 文件中已提供 Canva 风格展示海报画板：`AI-English-Coach Canva Showcase Poster`
- `docs/figma_canva_handoff.md` 已提供 Canva 手动复刻步骤。

受限项：

- 插件确认安装后，当前 Codex 会话仍未暴露可创建或编辑 Canva 在线设计稿的 MCP 工具。
- 本地可见 Canva 技能包括：
  - `canva-branded-presentation`
  - `canva-resize-for-all-social-media`
  - `canva-translate-design`
- 这些技能需要对应 Canva 搜索、生成或编辑工具配合；当前会话未暴露这些工具，因此无法直接返回 Canva 在线设计链接。

建议操作：

1. 打开 `docs/canva_showcase.html` 并截图，作为 Canva 风格展示图。
2. 直接使用 `outputs/canva_showcase.png` 放入比赛项目说明或展示 PPT。
3. 或打开 Figma 文件中的 `AI-English-Coach Canva Showcase Poster`，手动复制到 Canva。
4. 如果后续 Canva MCP 工具可用，再生成在线 Canva 设计稿。

## Product Design 状态

已完成：

- 产品设计目标已明确：
  - 让页面好看：视觉设计
  - 让页面好用：交互设计
  - 让页面清楚：信息架构
- 已生成产品设计 QA 报告：`docs/product_design_qa.md`
- 已生成 UI 设计规范：`docs/ui_design_spec.md`
- 已生成 Figma / Canva 交付说明：`docs/figma_canva_handoff.md`

## 当前可交付证据

| 类别 | 证据 |
| --- | --- |
| 本地页面 | `http://localhost:8501` |
| Streamlit 源码 | `app.py` |
| Figma 设计稿 | <https://www.figma.com/design/p7RyLn8dlM23u6Ica8ehsY> |
| Canva 风格本地页 | `docs/canva_showcase.html` |
| Canva 风格 PNG | `outputs/canva_showcase.png` |
| Canva PNG 生成脚本 | `scripts/render_canva_showcase.py` |
| Canva 生成提示 | `docs/canva_generation_prompt.md` |
| 产品设计 QA | `docs/product_design_qa.md` |
| UI 设计规范 | `docs/ui_design_spec.md` |
| 验收清单 | `docs/verification_checklist.md` |

## 结论

当前项目在本地页面、Figma 设计稿、Canva 风格展示替代物和 Product Design 文档方面已经具备比赛项目交付能力。按照当前安排，Canva 在线设计链接先暂停，不再作为本轮完成条件；原因仍记录为当前会话没有暴露对应 Canva 创建/编辑工具。
