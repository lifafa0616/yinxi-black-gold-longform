# 长图生产流程

本流程的唯一生产真源是：`1080px 连续 HTML → 自包含 poster.html → 同一 Chromium 导出 final.png`。阅读区不是固定比例帧；高度由已确认内容决定。

## 1. 锁定输入与两层文案

先保存完整 `source_copy`，再盘点 `fact_locks`：人名、机构、品牌、产品、日期、时间、地点、价格、数量、课程次数、权益、CTA、二维码动作，以及用户要求逐字保留的内容。

在不改变 `fact_locks` 的前提下，分析并生成 `display_copy`：主标题、副标题、核心卖点、证据、利益点和行动信息。`display_copy` 可以压缩重复句、调整阅读顺序和提炼营销重点；它不能静默篡改事实，也不能覆盖原文来源。

## 2. 先确认，再生产

复制 `daily-plan-template.md` 为案例 `plan.md`，完成输入、内容分析、营销分析、R 配方、阅读区、资产和主题判断后，输出一份用户确认稿：

```text
展示主标题 / 副标题：
核心卖点与阅读顺序：
必须逐字保留的事实：
首帧策略：mentor-portrait / imagegen
若为 imagegen：主实体、辅助关系、文字安静区与默认生成预算：
阅读区序列及 Lxx：
```

- 展示文案或事实锁定项尚未确认：`awaiting-copy-confirmation`。
- 首帧策略尚未确认：`awaiting-hero-confirmation`。
- 素材、事实或规则有缺口：`input-blocked` 或 `preflight-blocked`。

上述状态下不得调用 ImageGen、处理人像、开始排版或完整导出。用户确认后才写 `approved-for-production`。

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
2. 从浏览器实际布局树取得文字行、容器、阅读区、主视觉和高风险元素坐标，生成 `layout-manifest.json`。
3. 执行 `package_poster_html.py`。它把本地图片、CSS 资源和内置字体嵌入单个 `poster.html`。
4. 用 Playwright Chromium 渲染这份 `poster.html` 为 `final.png`。不能用第二套排版或字体渲染器。
5. 对非常高的连续画布，允许同一 Chromium 从同一 DOM 分段截图；拼接只复制像素，不重新布局、重采样 SVG 或计算字体。

```bash
.venv/bin/python scripts/package_poster_html.py --input <case>/render.html --output <case>/poster.html --proof <case>/poster-proof.json
.venv/bin/python scripts/render_longform.py --input <case>/poster.html --output <case>/final.png --render-proof <case>/render-proof.json
.venv/bin/python scripts/verify-case-layout.py <case>/layout-manifest.json --poster-html <case>/poster.html --png <case>/final.png --render-proof <case>/render-proof.json
```

`poster.html` 是可编辑的正式母版；`final.png` 是直接发布图。不得把 data URL 或 base64 内容写进 Plan、日志或对话。

## 6. 验收与预算

- 默认完整导出 1 次；只有已命名的客观问题允许 1 次修复性导出。
- 默认查看完整 PNG、首帧诊断裁片及最多两张命中风险区的裁片，并做浏览器 Mobile View Check；不生成独立 360px 输出。
- 验收使用 `daily-self-check.md`。客观错误必须修复；主视觉材质、透视和气质不能自动判断时标记 `human-review-needed`。
- 用户明确要求比较、替换或多方案时，可超过默认 ImageGen 预算；在 Plan 记录范围、目标和成本即可。
