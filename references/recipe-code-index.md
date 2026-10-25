# 历史案例提取的 HTML 配方

先按 `layout-recipes.md` 选信息关系，再按下表取代码。代码是布局起点，不是新的路由白名单；没有代码的合法配方仍可按原契约实现。本轮不要求覆盖全部配方。

## 使用

1. 文案确认并放行后，复制 `assets/template/render.html` 为新案例 `render.html`。它已含基础样式、连续轨道与 L01 → L04 → L14 → L10 示范链路；按内容保留、替换或删除模块，不是固定四段方案。替换模块时同时带入片段的 scoped CSS 与 HTML，保留唯一 `#longform-canvas`；种子已有的公共样式不重复粘贴，独立使用片段时才额外粘贴 [common.css](../assets/recipes/common.css)。在 Plan 逐区记录代码来源与必要调整，不需要运行时组件或依赖。
2. 替换示意文字和 `{{图片槽}}`，只引用当前输入白名单中的素材。图片槽是待替换路径，不是模板引擎。种子封面以 `.recipe-L01 .visual { background-image: url("assets/hero.png"); }` 接入当前主题图，避免打包后的长 data URI 经过 CSS 自定义属性失效；默认空槽仅便于查看排版。主题槽使用竖向场景，上缘随标题底部定位，副标叠图时保留透图的局部暗化和上下渐隐，不改为横向图片卡。待提供二维码和示意文案未替换前不可发布。
3. 重复使用时同步更换阅读区 ID、人物 unit ID、章节绑定、通栏轴与 CTA group；正文大模块重新从 01 连续编号，封面始终不编号。主标题金词逐项写入 Plan。
4. 按实际文字调整高度，不缩字。通栏共享 x=112–968；章节号用顶部独立导航空间，不挤窄正文。保留配方的结构差异，不把各模块都改成列表。
   正文模块头从种子的紧凑间距起排；若标题较长，改为短标题＋说明，再看实际字形与右侧章节号是否相撞。
5. 替换人像后重新校准可见头部、肩部、完整肢体、图文绑定和下缘渐隐。首帧片段里的测量节点/坐标来自历史素材，只是可编辑起点，绝不是新素材的测量结果；必须更新节点及当前资产 QA/hash，再由原测量器导出 Manifest。正文片段不继承历史 passed 状态。

片段不是已经验收的正式海报。现有打包、测量、渲染与验收流程不变；视觉质量和语义仍为 `human-review-needed`。历史素材不随代码打包，也不自动进入新案例白名单。

## 人像：首帧

| 配方 | 人数与关系 | 代码 |
|---|---|---|
| P02 | 单人焦点，头侧说明 | [hero/P02.html](../assets/recipes/hero/P02.html) |
| P03 | 双人等权，下方同基线说明 | [hero/P03.html](../assets/recipes/hero/P03.html) |
| P01 | 三人等尺度，中心人物在前 | [hero/P01.html](../assets/recipes/hero/P01.html) |
| P04 | 四人两层，外侧身份说明 | [hero/P04.html](../assets/recipes/hero/P04.html) |

来源为项目 `cases/portrait-{solo,dual-equal,three-equal,four-tiered}-contract-test/render.html`。提取人物分组、叠放、说明与下缘蒙版，移除历史验收状态与 hash；改用当前字体家族和字号下限。P02 的整体高度扩展，以容纳源案例伸出原画布的下缘。只用于 L01，不用于正文。

## 人像：正文

| 配方 | 人数与关系 | 代码 |
|---|---|---|
| IP01 | 双人交替信息卡，首行左图次行右图 | [body/IP01.html](../assets/recipes/body/IP01.html) |
| IP02 | 三人资料列表，固定头像列和文字列 | [body/IP02.html](../assets/recipes/body/IP02.html) |
| IP04 | 四人独立容器，同宽、底部对齐、文字共顶线 | [body/IP04.html](../assets/recipes/body/IP04.html) |
| L13 单人 | 左人像、右履历 | [content/L13-single.html](../assets/recipes/content/L13-single.html) |

双/三/四人来源为 `portrait-inner-recipes-2026-10-05-v2/{dual,triple,quad}/render.html`。去掉测试封面，保留人物信息关系；旧 16–25px 正文不继承，解释文字改为 36px 并流式扩高。IP04 仅用于姓名和短身份，其历史 195px 容器高差收至 72px，以符合现契约；不放长履历。单人来源为产品拆解营导师区。IP03 是另一种 4–8 人短名册网格，本轮没有冒充为四人容器，也没有新造代码。

## 内容配方

| 配方 | 结构 | 来源 | 代码 |
|---|---|---|---|
| L01 | 主题封面、竖向满幅暗场景 | 产品拆解营首帧 | [L01](../assets/recipes/content/L01.html) |
| L02 | 核心判断与短解释 | 产品拆解营 START HERE | [L02](../assets/recipes/content/L02.html) |
| L02 受众变体 | 年限数据锚点＋身份／基础／目标 | 已认可的求职陪跑案例结构 | [L02-audience](../assets/recipes/content/L02-audience.html) |
| L04 | 四项并列、2×2 网格 | 产品拆解营四格区 | [L04](../assets/recipes/content/L04.html) |
| L12 | 六项并列、2×3 网格 | 新配色课程长图第 02 段 | [L12](../assets/recipes/content/L12.html) |
| L14 | 编号、交付标题、解释的价值清单 | 产品拆解营 TAKE AWAYS | [L14](../assets/recipes/content/L14.html) |
| L15-H3 | 方节点、细轨道、三段历史演进 | 新配色课程长图第 04 段 | [L15-H3](../assets/recipes/content/L15-H3.html) |
| L09-H2 | 上文下图、完整横向证据 | 新配色课程长图第 14–15 段 | [L09-H2](../assets/recipes/content/L09-H2.html) |
| L10 | 行动信息与二维码同组 | 产品拆解营 CTA | [L10](../assets/recipes/content/L10.html) |

FFmpeg 来源已转换为流式 HTML，不复制 1920px 固定帧高、烘焙文字或旧小字号；不是原图逐像素复刻。来源路径、源文件 hash 和提取方式记录在 [sources.json](../assets/recipes/sources.json)，仅用于审计，不授权复用素材。L01 的来源同产品拆解营 `render.html`。

## 检查边界

浏览器冒烟测试检查 P/IP 分类、人数、正文安全轴、CSS 隔离和不继承 passed。字体加载、真实素材、头部尺度、溢出、二维码及完整发布流程仍须在实际案例验证。背景融合、裁切完整度、人物视觉重量、金色语义以及模块节奏不能由示意片段自动证明。
