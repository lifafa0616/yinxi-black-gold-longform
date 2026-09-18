---
name: yinxi-black-gold-longform
description: 从冻结中文文案、真实素材和行动信息制作 1080px 宽黑金手机长图；适用于课程、活动、研究、权益与专业内容海报，不用于多主题探索或纯网页交付。
---

# Yinxi Black Gold Longform

制作一张连续阅读的中文黑金手机长图：先识别文案的信息关系，再选择 R/L 配方、准备必要资产、以精确文字合成，并输出 1080px PNG 与 360px 预览。HTML/CSS/SVG 仅可作内部渲染源，不是交付物。

## 适用边界

- 仅使用 `minimal-editorial-tech + black-gold-editorial`；不改为蓝色、霓虹、金箔、蒸汽朋克或奢侈品广告风。
- 新任务建立语义化案例目录，不覆盖已有输出、参考或历史案例。
- 不删减、改写或遗漏用户冻结文案；标题、正文、数字、日期、价格、行动、二维码说明均以后置精确文字完成。
- 日常交付仅包含 `plan.md`、1080px 宽最终 PNG 与 360px 宽预览。SVG / HTML 仅为内部连续母版源；`frames/` 仅存放从最终 PNG 裁出的诊断图，绝不参与拼接或独立铺背景。

## 日常读取路由（先少后多）

日常生产不得为“保险起见”全文重读所有规则。先读以下最小链路，并把选择结果写入一页 `plan.md`：

1. [daily-plan-template.md](references/daily-plan-template.md)
2. [layout-recipes.md](references/layout-recipes.md) 的“配方选择索引”
3. [black-gold-system.md](references/black-gold-system.md) 的“固定 Token / 首帧语义主视觉 / 人物呈现 / 编辑信息模块”
4. `assets/baseline/baseline-notes.md` 与批准首帧正例（首帧主视觉必选）
5. [text-rendering-rules.md](references/text-rendering-rules.md) 的字号底线
6. [daily-self-check.md](references/daily-self-check.md)

完成内容关系分析与候选配方选择后，按命中条件再完整阅读：

| 命中条件 | 必读材料 |
|---|---|
| 选中任意 `Lxx` | [layout-contracts.md](references/layout-contracts.md) 中该 `Lxx` 合同 |
| 卡片、多列、复杂网格、章节号或人物并列 | [layout-rules.md](references/layout-rules.md) 相应章节 |
| 高风险坐标布局 | `layout-rules.md` 内的 Layout Manifest 附录与验证脚本 |
| 输入关系难以归类、需要调整整图叙事 | [content-planning.md](references/content-planning.md) 的“阅读区签名 / 配方候选” |
| 规则维护、基线升格或案例复盘 | [production-workflow.md](references/production-workflow.md)；首帧生产前已读基线，无需重复读取 |

不得跳过“配方选择索引”而凭关键词或好排程度直接挑选 `Lxx`；也不必为未命中的条件规则支付阅读成本。`production-workflow.md` 与 `content-planning.md` 是异常输入和维护使用的扩展依据，不是每张常规海报的必读全文。

## 固定生产关口

1. 先创建并填写 `plan.md`：输入可用性 → 信息关系与 R 配方 → 阅读区候选/选择 L 契约 → 资产可用性 → 黑金系统 → 放行。
2. 任一阻塞项标为 `input-blocked` 或 `preflight-blocked`；未放行前不得生图、排字或试稿。
3. 每个阅读区记录一行结构签名：读者问题、结论、真实关系、候选、最终 `Lxx`、未选原因与下一段衔接。
4. 首帧必须有一个由 ImageGen 生成、解释冻结文案对象、关系或变化的语义主视觉；真实来源资产与程序化结构可进入后续阅读区，但不得取代首帧主视觉。中段不因留白生成装饰图；分条纯文字确有区分收益时，才使用与关键词一一对应的统一 icon 组。
5. **先验收资产，再合成整图。** 首帧主视觉先以局部资产检查语义、材质、透视、文字安静区和边界；人物先在 `#10100F` 底上检查透明边缘与可见头顶。资产不通过，不得进入整图渲染。
6. 在同一张连续 SVG / HTML 母版上一次合成背景、资产与精确文字；不得逐帧独立铺黑底再拼接。最终 PNG 必须由已加载正式字体的同一浏览器渲染引擎直接导出，不能把 SVG 交给其他栅格化工具二次转换。
7. 先完成静态预检；从最终 PNG 裁出 V1 首帧和所有多行卡片 / 人像 / CTA 等命中风险区的诊断图，再导出 360px 预览并执行日常验收。

## 生产预算与停止条件

- 首帧语义主视觉必选，且默认只生成 **1 项**局部 ImageGen 主视觉；不生成中段氛围图、额外版本或“先看看”的备选图。
- 若该资产在局部验收中出现可见的变形透视、破损对象、烘焙文字、红黄灰边、独立矩形边界、材质粗糙或与标题关系不成立，可生成 **1 次受限替换**；这是失败修复，不是视觉探索。第二次仍不通过则标 `preflight-blocked / human-review-needed`，不能低质入图。
- 真人不得调用 ImageGen。一次安全去背景尝试通过后用透明 PNG；失败时立即降级为原图合理裁切，并写明原因。不得为抠图反复生成或反复重试。
- 默认完整渲染 **1 次**；仅对最终检查中已经命名的客观错误允许 **1 次**修复性完整渲染。主视觉问题必须在局部资产阶段解决，不能带入整图后再反复渲染。
- 默认查看 360px 整图、V1 主视觉裁片，以及最多两张命中多行卡片 / 人像 / CTA 的诊断裁片；这些裁片均从最终 PNG 导出，不输出独立背景帧。`layout-manifest.json` 必须从正式浏览器渲染后导出，不能手工补写替代检查。
- HTML/CSS/SVG 如为渲染工具所需，只保留为案例内部源；不作为交付、报告或额外版本。交付仍只有 PNG、预览和 `plan.md`。

## 状态与维护边界

日常出图完成后可写 `agent-checked / human-review-needed`。只有人类确认后才能写 `human-approved`。

跨案例复盘、历史样张比对、规则沉淀、基线升级和新旧案例回归属于维护者流程，不属于同事每次调用 Skill 的日常生产路径。
