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
确认稿素材询问：是否有希望使用的导师/嘉宾人像，以及报名二维码可一并上传？如有，请现在一并提供。
本轮人像上传/明确无：
本轮二维码上传/明确无：
```

## 3. 素材与首帧决定

```text
portrait_hero_decision：theme-imagegen / mentor-portrait-by-request
用户明确的人像首帧要求（无则写“无”）：
默认首帧：主题主视觉；导师/嘉宾人像用途：中段讲师信息 / 明确要求的首帧
二维码状态：provided / explicitly-none / pending
二维码 CTA：已直接使用 / 待提供占位；发布状态：可发布 / 不可发布待补输入
首帧唯一主实体、辅助关系与文字安静区：
edge_mode、顶部融合、底部融合、低亮度/低饱和度/低暖黄检查：
首帧 `data-hero-cover`：是；首帧章节号：无；首个内容模块章节号：01
首帧 `data-hero-surface` 满幅范围与标题—视觉间距：
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
```

| 区域 | 读者问题 | 核心结论 | Lxx | 关键产出（金色，如有） | 章节导航号/眉题（V1 无号） | rhythm_change | 预计/实际高度 |
|---|---|---|---|---|---|---|---|
| V1 |  |  |  |  |  |  |  |

相邻 `Lxx` 不重复且相邻模块有结构节奏变化：是 / 否。

## 5. 输出与验收

```text
编辑源：render.html
正式母版：poster.html
打包证明：poster-proof.json
发布 PNG：final.png
渲染证明：render-proof.json
Layout Manifest：layout-manifest.json；poster SHA256：
三套嵌入字体：Serif Bold / Sans Regular / Sans Medium
完整导出次数：
ImageGen 次数与理由：
验收状态：
```
