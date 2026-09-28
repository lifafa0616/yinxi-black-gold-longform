---
name: yinxi-black-gold-longform
description: 从中文长文案、真实素材和行动信息制作可编辑的黑金手机长图 HTML，并由同一浏览器导出 1080px PNG；适用于课程、活动、研究、权益与专业内容海报。
---

# Yinxi Black Gold Longform

制作一张宽 1080px、连续阅读的黑金手机长图。正式母版是可编辑、自包含的 `poster.html`：图片和三套正式字体均嵌入文件，并由同一 Chromium 导出 `final.png`。

## 边界

- 仅使用 `minimal-editorial-tech + black-gold-editorial`，不改为蓝色、霓虹、金箔、蒸汽朋克或奢侈品广告风。
- 新任务建立语义化案例目录，不覆盖已有输出、参考或历史案例。
- 原始文案是事实来源。人名、品牌、日期、地点、价格、数量、权益、CTA 与可验证主张默认冻结；只能提炼表达、重排顺序和压缩重复句。
- 本次可用素材仅限用户在**当前对话**上传、粘贴、链接或明确指定路径的文案、图片、二维码、Logo 和文件；不得扫描历史目录寻找素材。`assets/baseline/` 仅用于质量校准。

## 日常读取路由

先读并填写 [daily-plan-template.md](references/daily-plan-template.md)、[content-planning.md](references/content-planning.md) 的内容与营销两层分析、[layout-recipes.md](references/layout-recipes.md) 的配方选择索引、[black-gold-system.md](references/black-gold-system.md) 的主题与首帧规则、[text-rendering-rules.md](references/text-rendering-rules.md) 和 [daily-self-check.md](references/daily-self-check.md)。

只在命中时再读所选 `Lxx` 的 [layout-contracts.md](references/layout-contracts.md)、卡片/网格/人物/章节号的 [layout-rules.md](references/layout-rules.md)，或异常输入时的 [production-workflow.md](references/production-workflow.md)。

## 固定生产关口

1. 仅根据本次对话的输入创建并填写 `plan.md`：输入可用性 → 内容分析 → 营销提炼 → R 配方与阅读区 → 资产与主题 → 放行。未确认前不得创建生产文件、处理人像、调用 ImageGen 或排版。
2. 先只输出展示文案确认稿：项目、主标题、副标题、重点内容、报名/行动信息；末尾同时询问：“是否有希望使用的导师/嘉宾人像，以及报名二维码可一并上传？如有，请现在一并提供。”不得展示 R/L、视觉方向或技术名词。
3. 用户要求修改时，只修订展示文案并重新确认。用户确认并上传的素材登记到 `current_input_allowlist` 和 Plan；不再为人像或二维码单独开启确认轮次。
4. 保留 `portrait_hero_decision`。当前默认首帧为 `imagegen` 主题主视觉；导师/嘉宾人像用于中段讲师信息。只有用户主动明确要求“人像作为首帧主视觉”时，才使用 `mentor-portrait`。已上传二维码直接用于 CTA；用户明确没有二维码时使用“待提供二维码”占位，并标记不可发布/待补输入。
5. 首帧是无章节号的封面：只保留一个承担项目/活动语境的眉题，主标题承担核心主张，副标题只补充新信息。主题主视觉以 `[data-hero-surface]` 从中下部满幅延展至两侧，并包含唯一 `[data-hero]`；标题先读、主视觉后读，二者之间不得留下无意义大空场。后续第一个内容大模块才从 `01` 连续编号。
6. 选择一个 R 配方，再按真实信息关系选择 L 契约。相邻模块必须在结构骨架、图文关系或导航节奏上有明确变化；不可只重复“左标签 + 左标题 + 列表”。
7. 先局部验收主视觉或人像，再合成整图。局部检查首帧的顶部/底部融合、标题优先级、低亮度/低饱和度/低暖黄、单一视觉中心、语义相关性与无生成式文字；再用浏览器实测检查满幅主视觉表面、通栏文字轴、字号、换行、溢出、碰撞和章节号位置。视觉融入、封面语义去重和金色词语的语义准确性须标 `human-review-needed`，不能自动判定通过。
8. 在一张连续 HTML/CSS/SVG 母版上合成背景、资产与精确文字。阅读区高度由内容决定，不能按 9:16 分页、缩字或添加无意义装饰。
9. 先将 `render.html` 打包为自包含 `poster.html`，再从同一 HTML 导出并验证 `final.png`。HTML 和 PNG 不得来自两份版式源。

## 固定渲染命令

首次使用，在 Skill 根目录执行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/playwright install chromium
```

确认前如已由用户指定输出根目录，仅可运行：

```bash
.venv/bin/python scripts/create_case_plan.py --output-root <用户指定的目录> --case <语义化案例名称>
```

案例编辑源含唯一 `#longform-canvas`，使用 `.longform-serif`、解释正文 `.longform-sans`（Regular）和信息强调 `.longform-sans-medium`（Medium）。正式生产固定为：

```bash
.venv/bin/python scripts/package_poster_html.py --input <case>/render.html --output <case>/poster.html --proof <case>/poster-proof.json
.venv/bin/python scripts/export_layout_manifest.py --input <case>/poster.html --output <case>/layout-manifest.json
.venv/bin/python scripts/render_longform.py --input <case>/poster.html --output <case>/final.png --render-proof <case>/render-proof.json
.venv/bin/python scripts/verify-case-layout.py <case>/layout-manifest.json --poster-html <case>/poster.html --png <case>/final.png --render-proof <case>/render-proof.json --plan <case>/plan.md
```

打包器会嵌入本地图片、CSS 图片资源与 Bold Serif、Regular Sans、Medium Sans 三套正式字体。任何字体、图片、画布宽度或 Playwright Chromium 不符合要求时必须失败，绝不回退系统字体、外部图片或另一套排版引擎。

## 预算与验收

- 默认仅生成 1 项 `imagegen` 首帧；局部验收发生命名的客观失败时可替换 1 次。用户明确要求人像首帧时使用确认原图，不调用 ImageGen 改脸或重生。
- 默认完整导出 1 次；只有已命名的客观错误可进行 1 次修复性导出。
- 最终验收看完整 PNG 和命中风险区裁片。文字可读性由最小字号、实际换行、溢出及碰撞规则保障，不增加主观的手机比例检查。
- 日常出图可写 `agent-checked / human-review-needed`；只有人类确认后可写 `human-approved`。跨案例规则维护不属于日常出图路径。
