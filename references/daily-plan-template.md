# 黑金长图日常 Plan 模板

复制为案例目录内的 `plan.md`。这是一份生产记录；它先记录待确认的文案与首帧策略，确认后才记录资产和导出。

## 1. 身份、原文与事实锁定

```text
项目名称：
案例目录：
状态：planning / awaiting-copy-confirmation / awaiting-hero-confirmation / input-blocked / preflight-blocked / approved-for-production / rendered / checked
审阅：not-reviewed / agent-checked / human-review-needed / human-approved
source_copy 来源：
current_input_allowlist（当前对话明确提供的附件、链接、路径；不含历史案例或基线）：
fact_locks（原文中所有事实性信息：身份、时间、价格、权益、经历、成果、数字、CTA 等；默认冻结）：
待确认或缺失项：
```

| 源模块 ID | 原文角色 | 原文摘要 | 事实 / 表达 | 最终阅读区 |
|---|---|---|---|---|
|  | `claim/context/explain/proof/benefit/action` |  | 冻结事实 / 可提炼表达 | `Vx / Lxx` |

## 2. 内容与营销确认稿

```text
Hero Message：
Supporting Message：
Proof：
Benefits：
CTA：
display_copy（按阅读区）：
display_copy 来源模块 ID 映射：
用户确认展示文案：待确认 / 已确认 / 要求修改；日期：
用户修改意见与本轮修订：
```

## 3. 首帧策略确认

```text
本次输入是否含导师 / 嘉宾人像：是 / 否
若无：是否询问用户可补充首帧人像；用户答复：
若有：是否询问用户将其用于首帧；用户答复：
内部首帧策略：mentor-portrait / imagegen
选择理由：
若 mentor-portrait：人物、身份与首帧传播重点：
若 imagegen：唯一主实体、辅助关系、文字安静区、禁止文字：
首帧判断状态：待确认 / 已确定；日期：
默认 ImageGen 预算 / 用户授权的额外范围：
```

## 4. 放行

| 顺序 | 结论 | 结果 |
|---|---|---|
| 输入可用性 |  | 通过 / 阻塞 |
| 内容分析与事实锁定 |  | 通过 / 阻塞 |
| 营销确认稿 |  | 已确认 / 待确认 |
| 首帧人像判断 |  | 已确定 / 待确认 |
| R 配方、阅读区与 L 契约 |  | 通过 / 阻塞 |
| 资产与黑金系统 |  | 通过 / 阻塞 |
| 放行 |  | `approved-for-production` / 其他状态 |

阻塞项与下一步：

```text
预确认文件边界：只存在 plan.md / 是否合规：是 / 否
未确认前未创建 assets、frames、render.html、poster.html、final.png：是 / 否
```

## 5. 连续阅读区

```text
Rxx：
选择原因：
连续画布：宽 1080px；高度由渲染器实测；不使用固定帧数或比例。
```

| 区域 | 读者问题 | 核心结论 | 真实关系 | 最终 Lxx / variant | 预计 / 实际高度 | 视觉关系 | 下一段衔接 |
|---|---|---|---|---|---|---|---|
| V1 |  |  |  |  |  |  |  |

相邻 `Lxx` 不重复：是 / 否；任一 `Lxx` ≤ 2 或已走合法降级：是 / 否。

## 6. 资产与人物

| 资产 | 服务区域 | 路径 | 删除后失去的理解 | 主实体 / 关系映射 | 文字安全区 | 融入 / 拒绝条件 |
|---|---|---|---|---|---|---|
|  | `Vx/Lxx` | `approved-source/imagegen/procedural/text-render` |  |  |  |  |

```text
V1 几何：copy_anchor_bottom；copy_group_height；hero_visible_bbox；实际顶部间距；实际可见高度；hero.strategy。
```

| 人物 | 原图路径 | `portrait_mode` | 介绍锚点 | 原图/透明边缘检查 | 关联文字区 | 备注 |
|---|---|---|---|---|---|---|
|  |  | `transparent/masked/source-crop` | `intro_text_top` |  |  |  |

```text
transparent：可见头顶 ↔ intro_text_top ≤ 8px；在 #10100F 上确认透明边缘。
masked / source-crop：图片矩形顶部 ↔ intro_text_top ≤ 8px；完整保留头顶、脸和下巴。
多导师：选择 M01 单导师 / M02 双导师 / M03 三导师 / M04 人物墙；精细抠图与像素级多人关系交由后续编辑器。
```

## 7. 输出与验收

```text
编辑源：render.html
正式可编辑母版：poster.html
打包证明：poster-proof.json
发布 PNG：final.png
渲染证明：render-proof.json
Layout Manifest：layout-manifest.json
浏览器测量：`export_layout_manifest.py` 已执行 / 未执行；poster SHA256：
诊断裁片（来自 final.png）：
Mobile View Check（浏览器约 1/3 比例）：
完整导出次数：
ImageGen 次数与理由：
验收状态：
```
