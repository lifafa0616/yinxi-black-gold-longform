# 黑金长图日常 Plan 模板

复制为案例目录内的 `plan.md`。这是一页生产记录；真人、二维码、ImageGen、复杂容器只在命中时追加对应附录。

## 1. 身份与输入

```text
项目名称：
案例目录：
状态：planning / input-blocked / preflight-blocked / approved-for-production / rendered / checked
审阅：not-reviewed / agent-checked / human-review-needed / human-approved
冻结文案来源：
必须保留的事实、数字、时间、价格、行动：
缺失或待确认项（无则写“无”）：
```

| 源模块 ID | 原文角色 | 必须保留 | 最终阅读区 |
|---|---|---|---|
|  | `claim/context/explain/proof/benefit/action` | 是 | `Vx / Lxx` |

## 2. 生产前放行

| 顺序 | 结论 | 结果 |
|---|---|---|
| 输入可用性：信息有去处，素材与限制明确 |  | 通过 / 阻塞 |
| 整图叙事：`Rxx`、比例、阅读区数量成立 |  | 通过 / 阻塞 |
| 信息关系：每段完成候选与最终 `Lxx` |  | 通过 / 阻塞 |
| 资产可用性：真实素材、主视觉与文字安全区可用 |  | 通过 / 阻塞 |
| 黑金系统：主题、组件与文字层级无冲突 |  | 通过 / 阻塞 |
| 放行 |  | `approved-for-production` / `preflight-blocked` |

阻塞项与下一步：

## 3. 内容关系与配方选择

```text
比例：N × 9:16 / N × 3:4
主叙事：Rxx
选择原因：
```

| 区域 | 读者问题 | 核心结论 | 真实关系 | 主候选 / 备选 | 最终 Lxx | 未选原因 | 下一段衔接 |
|---|---|---|---|---|---|---|---|
| V1 |  |  |  |  |  |  |  |

相邻 `Lxx` 不重复：是 / 否；任一 `Lxx` ≤ 2：是 / 否。

## 4. 黑金与母版

```text
连续母版：#10100F；总高度；阅读区裁切策略
渲染真源：连续 SVG / HTML 内部源；固定引擎 Playwright Chromium；正式字体加载结果；最终 PNG 是否由该引擎直接导出（是 / 否）
孤行预检：实际 `rendered_lines` 来源；是否出现单字 / 单字符孤行；若出现，字号调整、扩宽或重排的处理记录
批准视觉基线：已读路径；借用的质量目标；明确不复用项
面板：#181816；启用容器 id
章节号：启用 / 未启用；启用区 title-top / chapter-top
轨道与内网格：启用项 / 删除的冗余线
主标题 signal：原文“____”
每区额外 signal：无 / Vx 原文“____”及职责
```

## 5. 资产路由

| 资产 | 服务区域 | 删除后失去的理解 | 路径 | 主实体 / 辅助关系映射 | 文字安全区 | `edge_mode` / 融入 | 拒绝条件 |
|---|---|---|---|---|---|---|---|
|  | `Vx/Lxx` |  | `approved-source/imagegen/procedural/text-render` |  |  |  |  |

- 首帧主视觉（必填）：`imagegen`；填写唯一主实体、每项辅助关系的“图元 → 冻结文案”映射、安静区、`edge_mode: native-alpha / dark-scene-canvas-mask`、禁止文字及局部验收拒绝条件。真实来源资产或程序化结构不得取代首帧主视觉。
- 首帧几何（必填）：`copy_anchor_bottom`、`copy_group_height`、`hero_visible_bbox`、实际顶部间距、实际可见高度；按黑金系统的 `64–144px` / `max(560px, 1.2 × copy_group_height)` 关口填写。此处记录可见主体，不记录含大面积透明留白的图片画布。
- 中段 ImageGen：默认无；仅 icon 组在图标库无法表达且有明确区分收益时可填写 1 项无文字透明同组资产。

### 条件附录：人物

| 人物 | 原图路径 | `portrait_mode` | 去背景尝试结果 / 降级原因 | `intro_text_top` | `visible_head_top / image_rect_top` | `visible_bbox / image_rect` 与文字区 | 母版色边缘检查 |
|---|---|---|---|---:|---:|---|---|

```text
transparent：visible_head_top ↔ intro_text_top ≤ 8px；visible_bbox 不得超过 related_text_region；必须在 #10100F 上确认真实透明边缘。
source-crop：image_rect_top ↔ intro_text_top ≤ 8px；image_rect 不得超过 related_text_region；不使用透明人物的渐隐模板。
intro_text_top 取姓名或身份信息的第一个关联文本，不能取“导师”等章节标签。
多导师 / 人像密集：默认 source-crop；记录每位人物的关联文字块，不强制透明抠图。
```

### 条件附录：二维码与复杂布局

```text
二维码：approved-source 路径 / 正方形与扫描检查；未提供则“待提供”占位。存在价格时：CTA 数据组 id / QR 与价格的垂直对齐关系 / 不与日期时间行重叠；即使位于相邻容器也必须共用同一组 id。
容器或高风险布局：layout-manifest.json 路径 / render-proof.json 路径 / final.png 路径 / `background_samples` 与每个阅读区连接 `seams[].sample_points` / 验证脚本结果。
```

## 6. 输出与日常验收

```text
最终图：
360px 预览：
内部 SVG / HTML 源：
渲染引擎与正式字体加载记录：
render-proof.json：
诊断裁片（从最终 PNG 裁出：V1 必填；命中多行卡片 / 人像 / CTA 时追加）：
完整渲染次数：1 / 2（仅命名失败修复）
ImageGen 次数：0 / 1 / 2（第二次必须写客观失败原因）
验收状态：
```
