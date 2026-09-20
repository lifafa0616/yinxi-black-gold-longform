---
name: yinxi-black-gold-longform
description: 从中文长文案、真实素材和行动信息制作可编辑的黑金手机长图 HTML，并由同一浏览器导出 1080px PNG；适用于课程、活动、研究、权益与专业内容海报。
---

# Yinxi Black Gold Longform

制作一张 1080px 宽、连续阅读的黑金手机长图。正式母版是可编辑且自包含的 `poster.html`：图片和正式字体均嵌入文件；同一份 HTML 由固定浏览器渲染为可发布的 `final.png`。

## 适用边界

- 仅使用 `minimal-editorial-tech + black-gold-editorial`，不改为蓝色、霓虹、金箔、蒸汽朋克或奢侈品广告风。
- 新任务建立语义化案例目录，不覆盖已有输出、参考或历史案例。
- 原始文案是事实来源，不能覆盖或丢失。长文案可提炼为海报展示文案，但人名、品牌、日期、地点、价格、数量、权益、CTA 与用户要求逐字保留的内容必须锁定。
- 正式交付是 `plan.md`、自包含 `poster.html` 与由该 HTML 导出的 `final.png`。`frames/` 如出现，只能存放最终 PNG 的诊断裁片，绝不参与生产或拼接。

## 日常读取路由

先读并填写以下最小链路：

1. [daily-plan-template.md](references/daily-plan-template.md)
2. [content-planning.md](references/content-planning.md) 的“内容与营销两层分析”
3. [layout-recipes.md](references/layout-recipes.md) 的“配方选择索引”
4. [black-gold-system.md](references/black-gold-system.md) 的主题、首帧策略、人物与信息模块
5. `assets/baseline/baseline-notes.md` 与批准首帧正例
6. [text-rendering-rules.md](references/text-rendering-rules.md) 与 [daily-self-check.md](references/daily-self-check.md)

只在命中时再读：所选 `Lxx` 的 [layout-contracts.md](references/layout-contracts.md)、卡片/网格/人物/章节号的 [layout-rules.md](references/layout-rules.md)，以及异常输入或规则维护时的 [production-workflow.md](references/production-workflow.md)。

## 固定生产关口

1. 创建并填写 `plan.md`：输入可用性 → 内容分析 → 营销提炼 → R 配方与阅读区 → 资产与主题 → 放行。
2. 输出“确认稿”，包含展示文案、事实锁定项、阅读区顺序、首帧策略与 ImageGen 预算。状态记为 `awaiting-copy-confirmation` 或 `awaiting-hero-confirmation`。
3. 用户确认前，不得调用 ImageGen、处理人像、排版或完整渲染。任何阻塞项标为 `input-blocked` 或 `preflight-blocked`。
4. 首帧必须有一个视觉中心：若传播重点是导师/嘉宾身份，使用确认的真实人像作为 `mentor-portrait` 主视觉；否则使用 1 项解释标题对象、关系或变化的 `imagegen` 主视觉。中段不因留白生图。
5. 先局部验收主视觉或人像，再合成整图。主视觉检查语义、材质、透视、文字安静区与边界；人物检查对应展示模式、头脸完整和边缘。
6. 在一张连续 HTML/CSS/SVG 母版上合成背景、资产与精确文字。阅读区高度由内容决定，不能按 9:16 分页、缩字或添加无意义装饰。
7. 先把可编辑 `render.html` 打包为自包含 `poster.html`，再从该 HTML 导出和验证 PNG。HTML 与 PNG 不得来自两份版式源。

## 固定渲染命令

首次使用，在 Skill 根目录执行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/playwright install chromium
```

案例的编辑源必须含唯一 `#longform-canvas`，并使用 `assets/template/render.html` 的 `.longform-serif` / `.longform-sans` 字体类。正式打包、导出与检查固定为：

```bash
.venv/bin/python scripts/package_poster_html.py \
  --input <case>/render.html \
  --output <case>/poster.html \
  --proof <case>/poster-proof.json

.venv/bin/python scripts/render_longform.py \
  --input <case>/poster.html \
  --output <case>/final.png \
  --render-proof <case>/render-proof.json

.venv/bin/python scripts/verify-case-layout.py <case>/layout-manifest.json \
  --poster-html <case>/poster.html \
  --png <case>/final.png \
  --render-proof <case>/render-proof.json
```

打包器会把本地图片、CSS 图片资源和两套正式字体嵌入 `poster.html`。渲染器只接受这种自包含 HTML，并固定使用 Playwright Chromium；字体、图片、画布宽度或 Chromium 不符合要求时必须失败，不得回退到系统字体、外部图片、`sips`、ImageMagick 或另一套排版引擎。超长图如需分段，只能从同一浏览器 DOM 取像素条带后逐像素拼合。

## 生产预算与停止条件

- `mentor-portrait` 首帧默认不调用 ImageGen；`imagegen` 首帧默认 1 项，局部验收有客观失败才允许 1 次替换。用户明确要求多方案或替换时，在 Plan 记录其范围后执行。
- 真人不得由 ImageGen 改脸或重生。根据 `transparent / masked / source-crop` 选择展示模式；复杂多人像不在 Skill 内做像素级精修。
- 默认完整导出 1 次；仅对检查中已命名的客观错误允许 1 次修复性完整导出。主视觉问题停在资产阶段解决。
- 正式验收查看完整最终 PNG、首帧与命中风险区的诊断裁片，并在浏览器以约三分之一视觉比例完成 Mobile View Check；不交付独立 360px 缩略图。

## 状态与维护边界

日常出图完成后可写 `agent-checked / human-review-needed`；只有人类确认后才能写 `human-approved`。跨案例复盘、规则升格与基线更新属于维护流程，不属于同事每次调用的日常生产路径。
