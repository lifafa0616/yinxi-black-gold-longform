# 文字渲染与授权底线

本文件规定文字准确性、授权、字重和浏览器实测标记；主题文件决定具体视觉家族。

## 1. 真实文字与正式字体

- 正文、价格、行动、资源说明、日期和所有事实性文字必须以后置真实文字从冻结原文渲染；不得由图像模型猜写中文、数字、价格、时间或行动。
- 正式 `poster.html` 必须内嵌 `NotoSerifCJKsc-Bold.otf`、`NotoSansCJKsc-Regular.otf` 与 `NotoSansCJKsc-Medium.otf`。系统字体不是正式交付或回退方案；替换字体须有明确商业许可，并重新检查换行、行高、网格、容器内边距和浏览器实测几何。
- `render.html` 使用 `.longform-serif`（700）、`.longform-sans`（400）和 `.longform-sans-medium`（500）。

## 2. 1080px 文字契约

| 角色 | 最低规格 | 字重规则 |
|---|---|---|
| 主标题 | ≥110px | 展示 Bold |
| 模块小标题、章节标签 | ≥40px | Medium 或更高 |
| 解释性正文 | ≥36px | Regular：长解释、流程说明、讲师履历、准备事项、卡片说明 |
| 日期、价格、行动、关键数据 | ≥36px | Medium 或更高 |
| 说明/元信息 | ≥26px | 解释为 Regular；标签为 Medium |

- 容器过窄或文案过多时，依次换行、扩高、改结构或按 `M ∈ {80,72,64,56,48,40,32,28}px` 重布网；`M=28px` 后增加阅读区。不得缩小字号下限。
- 主标题、模块标题、章节标签、日期、价格、行动和关键数据不可降为 Regular；解释性正文不得伪加粗为 Medium。
- 正式浏览器换行中，主标题、模块标题与正文不得有单个汉字、单个英文字母或无意义符号独占一行。先按 4px 步进缩小到下限，再扩宽、重排或扩高；不得裁切或隐藏。
- 同一阅读区采用通栏标题、副标题和说明时，全部叶子文字标记同一个 `data-fullwidth-text-axis` 值，并以相同 CSS 宽度、左边界和右边界排版。不得为了章节号、装饰或“视觉留白”预先缩窄其中任一文本框；需要真实图文分栏或信息卡时，改用相应契约而非伪装为通栏。
- 首帧主标题的每个金色词用独立 `<span data-gold-keyword="hero-title">原文词语</span>` 标记。Plan 必须为每个标记单列原文依据；浏览器可检查标记与登记是否存在，不能判断语义是否准确，后者为 `human-review-needed`。

## 3. 验收底线

```text
□ 事实性文字逐字正确，且不是生成式伪文字
□ 三套嵌入字体可用且许可已记录；没有系统字体依赖
□ 主标题/模块标题/解释正文/说明分别达到 110px / 40px / 36px / 26px 下限
□ 解释正文为 Regular；模块/章节标签、日期、价格、行动和关键数据为 Medium 或更高
□ 金色只承担标题关键词、结论、行动、关键产出或关键事实
□ 通栏文字共享已声明的 `data-fullwidth-text-axis` 的左、右边界；章节号未迫使文字轴提前收窄
□ 主标题金色关键词已逐项登记原文依据；语义准确性标为人工复核
□ 实际 `rendered_lines` 无孤行；浏览器实测无溢出、容器越界或章节碰撞
```

## 4. 浏览器实测标记

```html
<main id="longform-canvas" data-canvas-color="#10100F">
  <section data-reading-zone="V1" data-contract="L01" data-hero-cover>
    <div data-hero-copy data-fullwidth-text-axis="V1-copy">
      <h1 data-layout-role="title" data-fullwidth-text-axis="V1-copy">从<span data-gold-keyword="hero-title">原文关键词</span>开始</h1>
      <p data-layout-role="body" data-fullwidth-text-axis="V1-copy">补充说明</p>
    </div>
    <div data-hero-surface><div data-hero="imagegen"></div></div>
  </section>
  <section data-reading-zone="V2" data-contract="L16" data-major-module="learning-path">
    <p data-chapter-label="learning-path">PATH</p>
    <span data-layout-chapter="learning-path" aria-hidden="true">02</span>
    <span data-internal-index aria-hidden="true">01</span>
    <h2 data-layout-role="module-title">模块标题</h2>
    <p data-layout-role="body">解释性说明</p>
  </section>
</main>
```

- `data-reading-zone` 标记真实 `Lxx`；`data-layout-role` 标在承载文字或二维码的叶子元素上，取值为 `title/module-title/body/price/action/meta/date/data/metric/qr`。
- `data-hero-cover` 只能标在第一阅读区，且不得含 `data-major-module` 或 `data-layout-chapter`。每个后续 `data-major-module` 必须恰有一个同阅读区内的 `data-layout-chapter`，并有同 ID 的 `data-chapter-label`；显示号从 `01` 连续递增。测量器导出右槽、眉题顶部、章节字号和 `data-internal-index` 的字号，以检查对齐、碰撞和“大导航号 > 内部序号”。
- `data-fullwidth-text-axis` 标在同一通栏轴的文字叶子上；测量器检查成员是否共享浏览器实测的左右边界。为章节碰撞检查，通栏中的必要事实文字仍须标 `data-protected-text`。
- 需要避让的事实文字标记 `data-protected-text`；容器使用 `data-layout-container`；价格与二维码用同一 `data-cta-group`。Manifest 必须由 Chromium 生成，改动 HTML 后必须重测。
