# 长图生产流程

本流程的唯一生产真源是：`1080px 连续 HTML → 自包含 poster.html → 同一 Chromium 导出 final.png`。阅读区不是固定比例帧；高度由已确认内容决定。

预确认阶段不是“素材盘点”或“建立生产工程”。它只分析当前对话输入并准备确认稿。

## 1. 锁定输入与两层文案

先保存完整 `source_copy`，再建立 `current_input_allowlist`：只包括用户在当前对话中明确提供或指定路径的素材。不得扫描工作目录、上级目录、历史案例、参考图库或旧输出。Skill 的批准基线只能阅读以校准质量，绝不属于可用素材。

再盘点 `fact_locks`。`fact_locks` 覆盖原文中所有事实性信息：人名、机构、品牌、产品、日期、时间、地点、价格、数量、课程次数、权益、CTA、二维码动作、经历、成果和任何可验证主张。它们默认冻结，不是等待用户挑选的可选信息。

在不改变 `fact_locks` 的前提下，分析并生成 `display_copy`：主标题、副标题、核心卖点、证据、利益点和行动信息。`display_copy` 可以压缩重复句、调整阅读顺序和提炼营销重点；它不能静默篡改事实，也不能覆盖原文来源。

## 2. 先确认，再生产

若用户明确指定输出根目录，可用 `create_case_plan.py` 在 `cases/<语义化名称>/plan.md` 创建唯一预确认文件；若未指定目录，先在对话准备确认稿。不得建立 `assets/`、`frames/`、`render.html`、`poster.html` 或 `final.png`。

完成输入、内容分析和营销分析后，先输出一份用户确认稿：

```text
展示主标题 / 副标题：
重点内容：
报名 / 行动信息：
请确认以上展示文案；如需修改，请直接指出要改的内容。
```

- 用户在这一步只确认展示文案是否准确、营销重点是否正确；不展示或确认事实锁定项、原文映射、R/L、阅读区、长图结构、视觉方向、资产预算或技术路线。
- 展示文案尚未确认：`awaiting-copy-confirmation`。
- 素材、事实或规则有缺口：`input-blocked` 或 `preflight-blocked`。

用户要求修改时，只更新展示文案，再发送同样简洁的确认稿；不得开始首帧判断或任何生产动作。

展示文案确认后，才进行首帧人像判断：没有人像输入时，问用户是否有希望放在首帧展示的人像可提供；用户回答没有后，内部直接走主题主视觉。已有导师/嘉宾人像时，只问是否放在首帧作为主视觉；回答是则走人像首帧，回答否则走主题主视觉。不得向用户使用 “ImageGen 方案” 等技术表述。

上述状态下不得调用 ImageGen、处理人像、复制素材、创建资产/诊断目录、开始排版或完整导出。展示文案确认且首帧路线确定后才写 `approved-for-production`。

## 3. 阅读区与版式

按 `content-planning.md` 和 `layout-recipes.md` 选择一个 `Rxx`，再为每个阅读区选择能解释真实关系的 `Lxx`。每区记录读者问题、结论、依据、视觉关系、契约、变体和下一段衔接。

阅读区可使用推荐最小/最大高度作预算，但最终高度由正式字体、实际换行和内容决定。文字过多时，优先扩高、重组或拆出新阅读区；不按 9:16 分页，不缩小字号下限，不为了填空添加装饰。

## 4. 首帧与资产策略

首帧必须建立唯一视觉中心。

- `mentor-portrait`：导师/嘉宾身份或阵容是传播重点，且已提供可用真实人像。首帧使用确认的导师人像，不启动 ImageGen 主视觉。
- `imagegen`：主题、方法、成果、活动体验或抽象概念是传播重点，或导师并非首帧重点。默认生成 1 项语义主视觉；若局部验收出现客观失败，允许 1 次替换。

真实人物绝不由 ImageGen 改脸或重生。人物先选 `transparent / masked / source-crop`；多人场景以合适裁切和基本图文归属为止，不在 Skill 内解决像素级精修。

中段仅保留承担真实内容任务的来源资产、程序化解释图或关键词一一对应的 icon。准确文字、数字、二维码、Logo、真人身份和严格图表不走 ImageGen。

## 5. 连续 HTML 与正式交付

1. 用 `render.html` 建立连续 1080px 宽的 HTML/CSS/SVG 编辑源；背景、网格、轨道、资产和文字都在一张画布中定位。
2. 在 `poster.html` 中按 `text-rendering-rules.md` 标注可测元素，再运行 `export_layout_manifest.py`。它从浏览器实际布局树取得文字行、容器、阅读区、主视觉和高风险元素坐标，生成 `layout-manifest.json`；不得手填坐标。
3. 执行 `package_poster_html.py`。它把本地图片、CSS 资源和内置字体嵌入单个 `poster.html`。
4. 用 Playwright Chromium 渲染这份 `poster.html` 为 `final.png`。不能用第二套排版或字体渲染器。
5. 对非常高的连续画布，允许同一 Chromium 从同一 DOM 分段截图；拼接只复制像素，不重新布局、重采样 SVG 或计算字体。

```bash
.venv/bin/python scripts/package_poster_html.py --input <case>/render.html --output <case>/poster.html --proof <case>/poster-proof.json
.venv/bin/python scripts/export_layout_manifest.py --input <case>/poster.html --output <case>/layout-manifest.json
.venv/bin/python scripts/render_longform.py --input <case>/poster.html --output <case>/final.png --render-proof <case>/render-proof.json
.venv/bin/python scripts/verify-case-layout.py <case>/layout-manifest.json --poster-html <case>/poster.html --png <case>/final.png --render-proof <case>/render-proof.json
```

`poster.html` 是可编辑的正式母版；`final.png` 是直接发布图。不得把 data URL 或 base64 内容写进 Plan、日志或对话。

## 6. 验收与预算

- 默认完整导出 1 次；只有已命名的客观问题允许 1 次修复性导出。
- 默认查看完整 PNG、首帧诊断裁片及最多两张命中风险区的裁片，并做浏览器 Mobile View Check；不生成独立 360px 输出。
- 验收使用 `daily-self-check.md`。客观错误必须修复；主视觉材质、透视和气质不能自动判断时标记 `human-review-needed`。
- 用户明确要求比较、替换或多方案时，可超过默认 ImageGen 预算；在 Plan 记录范围、目标和成本即可。
