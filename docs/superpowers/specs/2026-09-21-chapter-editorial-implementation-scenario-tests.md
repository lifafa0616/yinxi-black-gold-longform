# Chapter Editorial v1 · 实现门槛情景测试

## 目的与执行方式

本文件是 `chapter-editorial-production-contract-design.md` 的实现前验收集。它验证规格在真实操作情景中是否给出唯一、可执行且不绕过发布门槛的状态路径；不是尚不存在的 Python 实现的测试报告。

每个情景必须以当前规格独立推演。通过条件是：每步均有合法 writer、所需证据和唯一的后续状态；任何绕过、矛盾或未定义状态都记为 P0。所有案例使用逻辑占位素材，不修改真实案例或输出文件。

## S01 · 正常直接视觉通过并发布

一份已确认的课程长图，使用已启用的 `L12-6`，所有资产获准。候选图通过确定性检查；同一 Agent 已打开完整候选、风险裁片和移动查看图，七项 rubric 均为 `pass`。

检查：从 copy/hero 确认到 preflight、candidate、prepare、直接视觉收据、finalize 和 promotion 的完整状态链；`final.png` 只能在最后一步写入；session、制品打开记录与收据必须使用同一 host-issued Agent run ID，换一个 Agent run ID 的收据必须被拒绝。

## S02 · 视觉失败后的版式修复

S01 的候选在移动查看中出现正文和金色结论重叠。Agent 写入包含一个 `fail`、具体修复说明和全部证据的合法视觉收据。随后只调整该段的版式与间距，未改 source、事实、资产、组件或 profile。

检查：合法 `fail` 是否写入 `evaluation-failed`；旧 session/receipt 是否被标为历史；是否经过重新 preflight 后回到 production 并产生新的 candidate；旧收据是否不能绑定新 candidate。

## S03 · 不确定视觉结论与人审

候选图的 hero 裁切权利无法由可用证据判断，七项中有一个 `uncertain`，其余 `pass`。先在原候选的 `human-review-needed` 状态提交一次 hash 不匹配的人审批准，再对精确 bundle/spec/session hash 提交批准。

检查：有效不确定收据是否写入 `human-review-needed`；精确匹配的人审批准是否进入 `evaluation-passed`；不匹配批准是否被拒绝且不改变状态。

## S04 · minor-copy 继承与安全回退

一张已 direct-pass 的候选仅修正一处非事实正文错字；文字角色、事实绑定 ID、行数、bbox、样式、Token、组件、资产、结构和信号均不变，图片差异仅位于旧/新文字 bbox 并集各扩 8px 内。随后再将同一段正文改长到发生换行。

检查：第一处修改是否由 `reopen_case.py` 识别并记录为 `minor-copy`，重新 preflight/render 后由 `prepare_evaluation.py --review-mode inherited` 生成 `review-inheritance.json`；不要求原生重新看图且仍经过 fresh deterministic checks。第二处是否拒绝继承并进入 `awaiting-visual-review`。

## S05 · 事实、素材与主视觉变更

从一个 `evaluation-passed` 案例开始，依次发生：(a) 日期/价格事实修正；(b) 普通证据图片替换；(c) hero 人像或 hero 策略替换。

检查：每一种是否由 `reopen_case.py` 作废旧评估；(a)/(b) 是否返回 `awaiting-copy-confirmation`；(c) 是否以 hero 分支优先返回 `awaiting-hero-confirmation`；是否都不能直接渲染或发布。

## S06 · 收据篡改与合法非通过收据

构造一份字段和哈希完整、但 top-level `verdict: pass`，七项中包含一个 `uncertain` 的收据；再构造一份 top-level `fail` 且有一个 rubric `fail` 的收据。

检查：前者是否因结论与七项推导结果不符而判 malformed；后者是否是合法收据并写入 `evaluation-failed`，而非被当作“non-pass receipt”一概拒绝。

## S07 · 路由、注册组件与 disabled variant

分别输入六项等权短信息、没有注册组件的 L14 权益清单，以及声称为 `L12-6`、实际却使用单列列表 DOM 的候选。

检查：第一项是否解析为 `L12-6` 的具体 registry entry；第二项是否返回 `unsupported-in-v1` 且不进入 renderer；第三项是否因 registry template/topology 不匹配而失败。

## S08 · 默认正文轴与组件例外

一个已注册的 L09 组件把标题/图片 root 合法置于 `x=80–1000`，普通正文置于 `x=112–968`；另一个候选把未获 schema 例外的正文放到 `x=80`。

检查：前者是否按 `allowed_content_rect` 通过；后者是否被 design-system check 拒绝；Evaluator 是否没有把默认正文轴误当成所有组件的全局裁切边界。

## 总体验收

- S01–S08 全部给出无歧义、不可绕过的状态/拒绝结果。
- 每项失败必须指向一条最小规格修订；P1 不阻断实现。
- 通过后才开始实现 profile、registry、renderer 和 Evaluator 脚本。
