---
name: yinxi-black-gold-longform
description: 从中文长文案、真实素材和行动信息制作可编辑的黑金手机长图 HTML，并由同一浏览器导出 1080px PNG；适用于课程、活动、研究、权益与专业内容海报。
---

# Yinxi Black Gold Longform

制作一张 1080px 宽、连续阅读的黑金手机长图。正式母版是可编辑且自包含的 `poster.html`：图片和正式字体均嵌入文件；同一份 HTML 由固定浏览器渲染为可发布的 `final.png`。

## 适用边界

- 仅使用 `minimal-editorial-tech + black-gold-editorial`，不改为蓝色、霓虹、金箔、蒸汽朋克或奢侈品广告风。
- 新任务建立语义化案例目录，不覆盖已有输出、参考或历史案例。
- 原始文案是事实来源，不能覆盖或丢失。原文中所有事实性信息都默认冻结：人名、品牌、日期、地点、价格、数量、权益、CTA 与任何可验证的主张均不得改写含义、补充或删成相反结论。长文案只可提炼表达、重排顺序和压缩重复句。
- 正式交付是 `plan.md`、自包含 `poster.html` 与由该 HTML 导出的 `final.png`。`frames/` 如出现，只能存放最终 PNG 的诊断裁片，绝不参与生产或拼接。

## 本次输入与预确认边界

- 本次可用素材只包括用户在**当前对话**中上传、粘贴、链接或明确指定路径的文案、图片、二维码、Logo 和其他文件。不得扫描工作目录、上级目录、历史案例、参考图库或旧输出以寻找素材。
- `assets/baseline/` 的批准样张仅用于理解黑金视觉质量、构图和排版节奏；它们不是本案素材候选，不能复用、盘点或因缺少“可用素材”而向用户汇报。
- 用户尚未确认展示文案与首帧策略时，唯一允许的案例写入是一个新的语义化案例目录中的 `plan.md`。使用 `create_case_plan.py` 创建它；不得创建或写入 `assets/`、`frames/`、`render.html`、`poster.html`、`final.png`，不得复制素材、调用 ImageGen、处理人像、排版或导出。
- 用户没有指定输出根目录时，先在对话中完成确认稿；不得以扫描当前项目目录的方式推断输入、素材或输出位置。

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

1. 仅根据本次对话的输入创建并填写 `plan.md`：输入可用性 → 内容分析 → 营销提炼 → R 配方与阅读区 → 资产与主题 → 放行。预确认阶段不盘点历史目录或创建生产文件。
2. 先只输出“海报展示文案确认稿”：项目、主标题、副标题、重点内容、报名/行动信息，并请用户确认或直接指出修改。不得展示 R 配方、L 契约、长图结构、阅读区顺序、视觉方向、资产预算或技术名词。事实冻结由原文自动执行。
3. 文案需要修改时，回到展示文案修订：保留全部冻结事实，只调整提炼表达与营销重点，再发精简确认稿；在文案确认前不得调用 ImageGen、处理人像、排版或完整渲染。
4. 文案确认后才判断首帧人像：未收到导师/嘉宾人像时，只问用户是否有希望在首帧展示的人像可提供；用户回答没有后，内部直接选择 `imagegen`。已收到人像时，只问该人像是否要放在首帧作为主视觉；回答是则内部选择 `mentor-portrait`，回答否则内部选择 `imagegen`。不得对用户使用“ImageGen 方案”表述。
5. 首帧必须有一个视觉中心：内部选择 `mentor-portrait` 时使用确认的真实人像；内部选择 `imagegen` 时使用 1 项解释标题对象、关系或变化的主题主视觉。中段不因留白生图。
6. 任何阻塞项标为 `input-blocked` 或 `preflight-blocked`；只有展示文案已确认且首帧路线已确定，才写 `approved-for-production`。
7. 先局部验收主视觉或人像，再合成整图。主视觉必须先通过可测的顶部间距、可见高度、文字安静区和单一视觉中心关口；再由人检查语义、材质、透视与边界。人物检查对应展示模式、头脸完整和边缘。
8. 在一张连续 HTML/CSS/SVG 母版上合成背景、资产与精确文字。阅读区高度由内容决定，不能按 9:16 分页、缩字或添加无意义装饰。
9. 先把可编辑 `render.html` 打包为自包含 `poster.html`，再从该 HTML 导出和验证 PNG。HTML 与 PNG 不得来自两份版式源。

## 固定渲染命令

首次使用，在 Skill 根目录执行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/playwright install chromium
```

确认前如已由用户指定输出根目录，仅可运行下列命令创建 Plan：

```bash
.venv/bin/python scripts/create_case_plan.py \
  --output-root <用户指定的目录> \
  --case <语义化案例名称>
```

该命令只创建 `cases/<语义化案例名称>/plan.md`；确认前不得以自定义 `mkdir` 命令创建资产或导出目录。

案例的编辑源必须含唯一 `#longform-canvas`，并使用 `assets/template/render.html` 的 `.longform-serif` / `.longform-sans` 字体类。正式打包、导出与检查固定为：

```bash
.venv/bin/python scripts/package_poster_html.py \
  --input <case>/render.html \
  --output <case>/poster.html \
  --proof <case>/poster-proof.json

.venv/bin/python scripts/export_layout_manifest.py \
  --input <case>/poster.html \
  --output <case>/layout-manifest.json

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

`export_layout_manifest.py` 也必须在打包完成后运行。它从同一份 `poster.html` 的 Chromium 实际布局树读取文字行、字号、文字框、卡片、二维码、CTA、首帧主体与背景采样点；校验器会重新测量该 HTML，拒绝手填、改写或来自另一份 HTML 的 Manifest。标记写法见 `text-rendering-rules.md`。

## 生产预算与停止条件

- `mentor-portrait` 首帧默认不调用 ImageGen；`imagegen` 首帧默认 1 项，局部验收有客观失败才允许 1 次替换。用户明确要求多方案或替换时，在 Plan 记录其范围后执行。
- 真人不得由 ImageGen 改脸或重生。根据 `transparent / masked / source-crop` 选择展示模式；复杂多人像不在 Skill 内做像素级精修。
- 默认完整导出 1 次；仅对检查中已命名的客观错误允许 1 次修复性完整导出。主视觉问题停在资产阶段解决。
- 正式验收查看完整最终 PNG、首帧与命中风险区的诊断裁片，并在浏览器以约三分之一视觉比例完成 Mobile View Check；不交付独立 360px 缩略图。

## 状态与维护边界

日常出图完成后可写 `agent-checked / human-review-needed`；只有人类确认后才能写 `human-approved`。跨案例复盘、规则升格与基线更新属于维护流程，不属于同事每次调用的日常生产路径。
