# 黑金长图日常 Plan 模板

复制为案例目录的 `plan.md`。预确认阶段只写本文件，不创建生产资产或输出。

## 1. 输入与事实锁定

```text
项目名称：
案例目录：
状态：planning / awaiting-copy-confirmation / input-blocked / preflight-blocked / approved-for-production / rendered / checked
审阅：not-reviewed / agent-checked / human-review-needed / human-approved
source_copy 来源：
current_input_allowlist（仅当前对话提供的附件、链接、路径）：
fact_locks：
待确认或缺失项：
```

| 源模块 ID | 原文角色 | 原文摘要 | 事实/表达 | 最终阅读区 |
|---|---|---|---|---|
|  | `claim/context/explain/proof/benefit/action` |  | 冻结事实 / 可提炼表达 | `Vx / Lxx` |

## 2. 内容与营销确认稿

```text
Hero Message：
Supporting Message：
封面眉题（唯一活动/项目语境）：
主标题的核心主张：
副标题的新信息（不得复述眉题/主标题）：
Proof：
Benefits：
CTA：
display_copy（按阅读区）：
display_copy 来源模块 ID 映射：
用户确认展示文案：待确认 / 已确认 / 要求修改；日期：
第一屏选择提问：这张长图的开头第一屏，你希望读者第一眼先记住什么？
用户选择：1 先记住内容主题 / 2 先记住导师或嘉宾 / 3 由我根据内容判断 / 未选择
选择 3 时的 Agent 判断与依据：
本轮人像上传/明确无：
本轮二维码上传/明确无：
```

## 3. 素材与首帧决定

```text
portrait_hero_decision：theme-imagegen / mentor-portrait-by-request
决定来源：用户选项 1 / 用户选项 2 / Agent 根据选项 3 判断 / 未选择默认选项 1
第一屏方案：内容主题画面 / 导师或嘉宾人像
导师/嘉宾人像用途：中段讲师信息 / 第一屏主要画面 / 未提供
portrait_recipe：P01 / P02 / P03 / P04 / 不适用
人物关系与人数：单人焦点 / 双人等权 / 三人中心在前 / 四人两层分组；人数：
透明资产与 QA：source_sha256｜alpha_sha256｜模型/版本｜双底色边缘检查｜状态
人物映射：subject id｜depth｜head/face/shoulder/body bbox｜caption 对齐/方向｜保护 token
人物组边界、中心误差、头部尺度差、身体交叠与下缘渐隐：
二维码状态：provided / explicitly-none / pending
二维码 CTA：已直接使用 / 待提供占位；发布状态：可发布 / 不可发布待补输入
首帧唯一主实体、辅助关系与文字安静区：
edge_mode、顶部融合、底部融合、低亮度/低饱和度/低暖黄检查：
首帧 `data-hero-cover`：是；首帧章节号：无；首个内容模块章节号：01
首帧 `data-hero-surface` 满幅范围｜表面上缘相对主标题底部偏移｜副标题叠图时的半透明渐变与人工可读性复核：
通栏文本轴 ID｜左边界｜右边界｜成员（标题/副标/说明）：

## 首帧语义与金色关键词

封面信息去重、主视觉融入与关键词语义准确性：`human-review-needed / human-approved`

| 金色关键词 | 原文依据 |
|---|---|
|  | `source module ID：原文准确片段` |
```

## 4. 放行与连续阅读区

| 顺序 | 结论 | 结果 |
|---|---|---|
| 输入与事实锁定 |  | 通过 / 阻塞 |
| 展示文案与同轮素材收集 |  | 已确认 / 待确认 |
| `portrait_hero_decision` 与二维码状态 |  | 已记录 / 待补 |
| R 配方、阅读区、L 契约 |  | 通过 / 阻塞 |
| 资产、主题与结构节奏 |  | 通过 / 阻塞 |
| 生产放行 / 发布放行 |  | `approved-for-production` / 不可发布 |

```text
Rxx：
选择原因：
连续画布：宽 1080px；高度由正式字体和浏览器实测决定。
生产起点：assets/template/render.html（确认放行后复制，不覆盖历史案例）
```

| 区域 | 读者问题 | 核心结论 | Lxx | 代码来源／必要调整 | 关键产出（金色，如有） | 章节导航号/眉题（V1 无号） | rhythm_change | 预计/实际高度 |
|---|---|---|---|---|---|---|---|---|
| V1 |  |  |  |  |  |  |  |  |

代码来源填种子内模块或 `assets/recipes/…` 路径；无匹配代码则填“按契约实现”。必要调整简记内容适配与保留的结构特征，不另写审批表；代码缺失不构成生产阻塞。按 [代码索引](recipe-code-index.md) 替换示意内容、素材、ID 与绑定，P 仅首帧、IP 仅正文。

正文模块在“代码来源／必要调整”中简记短标题、可选说明与主内容事实映射；命中 L02 受众变体时写明年限、身份、已有基础和目标的原文依据，缺项不补造。

相邻 `Lxx` 不重复且相邻模块有结构节奏变化：是 / 否。

正文人物（命中 L13 时）：

```text
inner_portrait_recipe：IP01 / IP02 / IP03 / IP04 / M04-3C / 单人通用 / 不适用
人物数与逐人文案密度：
逐人 unit_id 与姓名/身份/说明归属：
统一头部尺度、露出比例、文字对齐与内容轴：
透明资产 QA、完整部位与下缘融合：
```

## 5. 输出与验收

```text
编辑源：render.html
中间渲染文档：poster.html（需要 Google Fonts 网络访问）
打包证明：poster-proof.json
发布 PNG：final.png
渲染证明：render-proof.json
Layout Manifest：layout-manifest.json；poster SHA256：
Google Fonts：Noto Serif SC 700 / Noto Sans SC 400 / 500；加载证明：
完整导出次数：
ImageGen 次数与理由：
验收状态：
```
