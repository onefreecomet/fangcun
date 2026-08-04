# 生成指南

第 6 步用。从 `assets/skeleton/` 出发，产出用户自己的工作台。

## 产物结构

```
<work>/                # 目录名 = 工作台名；已在第 3 步定下（见 SKILL.md「路径约定」），第 6 步不再问
├── index.html        # 界面 + 逻辑全内联
├── manifest.json     # PWA，加桌面必需
└── icon.png          # 桌面图标 512×512
                      # （《工作台配置.md》第 10 步才追加，第 6 步验收时不该有）
```

功能多了以后（见下方拆分阈值）会多出 `features/` 目录，但部署方式不变——EdgeOne Pages Drop 是拖文件夹上传，多几个文件不增加任何难度。

## 生成步骤

1. 复制 `<skill>/assets/skeleton/` 到 `<work>`（目录名用工作台名）
2. 替换所有 `{{占位符}}`（主题变量、工作台名、短名称、品牌 emoji、色值）
3. **删掉示例功能**（`==== 功能：示例 START/END ====` 之间的 HTML 和 JS，以及 routes 里那一条）
4. 按功能清单逐个实现，**分批写入，不要一次 Write 出整个文件**：
   - 先 Write 一版只含骨架 + 第 1 个功能的 index.html
   - 之后每个功能用 Edit 插入，锚点固定用设置页的分区标记：HTML 插在 `<!-- ==== 功能：设置 START ==== -->` 之前，JS 插在 `/* ==== 功能：设置 START ==== */` 之前
   - 每加完 2 个功能跑一次静态检查，不要 5 个都写完才跑——错早发现早改，攒着改要重读整个文件
   - 单个功能 JS 超过 150 行 → 先按「6. 拆分阈值」拆到 `features/`，别硬塞
5. 更新 `App.routes`
6. 没有联网功能就删掉设置页的 `apiCard` 那张卡；有的话按 `api-guide.md` 配置
7. 生成 icon.png
8. 跑验收脚本（命令和跑不动时的降级路径**以 SKILL.md 第 6 步的分支表为准**）

## 硬性规范

这几条是骨架能长期活下去的前提，违反了短期看不出问题，三个月后会很难受。

### 1. 分区标记必须严格

每个功能的 HTML 和 JS 都要被标记包裹，且**名字必须一致**：

```html
<!-- ==== 功能：记账 START ==== -->
<section class="page" id="page-money"> ... </section>
<!-- ==== 功能：记账 END ==== -->
```

```javascript
/* ==== 功能：记账 START ==== */
const Money = { ... };
/* ==== 功能：记账 END ==== */
```

这不是洁癖。以后用户说"把记账删掉"或"记账加个分类统计"，AI 靠这个标记做定点编辑。没有标记，在两千行文件里靠猜位置改，出错率会很高。

### 2. 数据读写只走 Store

```javascript
Store.get('money', [])         // ✅
localStorage.getItem('money')  // ❌ 以后没法平滑上云
```

按天记录的用 `Store.getDaily/setDaily`，会自动带上今天的日期。

API key 一律走 `Store.setSecret/getSecret`——这个命名空间不会被导出到备份文件里。用户把备份发给别人时，key 不会跟着泄漏。

### 3. 模块命名规范

每个功能一个全局对象，PascalCase，至少有 `render()`：

```javascript
const Money = {
  render(){ /* 渲染到 DOM */ },
  add(){ /* 增 */ },
  del(id){ /* 删 */ }
};
```

在 `App.routes` 里挂上 `onShow: () => Money.render()`。

### 4. 移动端硬要求

| 要求 | 为什么 |
|---|---|
| 输入框 `font-size` ≥ 16px | 小于 16px 时 iOS 会自动放大整个页面，且退不回去 |
| 底部留 `env(safe-area-inset-bottom)` | 全面屏底部横条会盖住内容 |
| 顶部留 `env(safe-area-inset-top)` | 加到桌面全屏后，状态栏会盖住顶部 |
| 可点区域 ≥ 40×40px | 手指点不准 |
| 用 `Util.esc()` 转义用户输入 | 用户输入 `<b>` 会破坏页面结构 |

骨架的 CSS 已经处理好这些，**新写的样式不要绕过它们**。

### 5. 图片必须压缩

```javascript
const dataUrl = await Util.compressImage(file, 800);  // ✅
```

localStorage 只有 5-10MB。手机原图一张就 3-5MB，存两张就满了，然后**所有功能一起失效**——用户会以为工作台坏了。

拍照/上传类功能一律先过 `Util.compressImage`。默认宽度 800px、质量 0.72，在手机上看足够清楚。

### 6. 拆分阈值

**index.html 超过 1500 行，或功能超过 8 个**时拆分（这是"代码该拆文件了"的阈值；侧边栏"看起来挤了"是另一个阈值 9 个，两者不是一回事）：

```
index.html          # 保留：样式、Store、Util、UI、App、设置页
features/记账.js     # 每个功能一个文件
features/体重.js
```

用 `<script src="features/记账.js"></script>` 引入，**放在 App.init() 之前**。HTML 结构仍留在 index.html 里（拆 HTML 反而更难维护）。

拆完记得跟用户说一句：文件变多了，但部署还是拖整个文件夹，一样简单。

## 常见功能的实现要点

具体功能的数据结构和坑见 `feature-library.md`。这里只讲骨架层面容易做错的：

### 「今日」类功能必须处理跨天

固定行程、每日打卡这类功能，第二天打开必须自动重置。用 `Store.getDaily` 就自动做到了：

```javascript
// 今天的勾选状态；换一天自动是空的
const done = Store.getDaily('plan_done', []);
// 行程模板本身不带日期，是长期的
const template = Store.get('plan_template', []);
```

不这么做，用户第二天打开看到的是昨天勾满的死页面，这个工作台就废了。

### 「内容型」功能怎么翻页

一次性生成的内容（单词、知识卡）按天数取模：

```javascript
const START = '2026-08-01';                       // 生成日
const CONTENT = [ /* 60 天的内容 */ ];
const dayIndex = Math.floor((new Date(Util.today()) - new Date(START)) / 864e5);
const today = CONTENT[dayIndex % CONTENT.length];
```

用取模而不是越界报错，这样内容用完会自动从头循环，不会白屏。同时在页面底部显示「第 N/60 天」，用户看到快用完了会来找你续。

### 简单图表不要引库

体重、记账趋势这类用 SVG 手画，二十行就够，不用加载 CDN（部署到国内后加载外部 CDN 会明显变慢）：

```javascript
const pts = data.map((d,i) =>
  `${i / (data.length-1) * 300},${100 - (d.value - min) / (max - min) * 90}`
).join(' ');
svg.innerHTML = `<polyline points="${pts}" fill="none"
  stroke="var(--accent)" stroke-width="2" stroke-linejoin="round"/>`;
```

## 图标生成

`icon.png` 需要 512×512。三条路，按用户情况选：

**A. 纯色 + 文字（默认，零依赖）**

```bash
python3 "<skill>/scripts/make_icon.py" --out "<work>/icon.png" --bg "{{sidebar色值}}" --text "{{一到两个字}}"
```

用主题的侧边栏色打底，配工作台名的首字。简洁、和整体风格自动一致。

**B. 用户自己的图**

用户给了照片或喜欢的图，裁成正方形 512×512 即可：

```bash
python3 "<skill>/scripts/make_icon.py" --out "<work>/icon.png" --from "用户的图.jpg"
```

注意提醒：**图标会打包进部署文件**，如果是私人照片，等于公开了。

**C. 生图模型（强风格时）**

用户配了 `baoyu-image-gen` 且选了国风/二次元这类强风格时，可以调它生成。提示词要点：

> App 图标，{{风格}}，主体是{{一个简单的象征物}}，正方形构图，主体居中占画面 60%，背景是{{sidebar色值}}纯色，扁平化，无文字，无边框，高清

**图标必须能在小尺寸下认出来**——桌面上它只有指甲盖大。复杂的插画缩小后是一团色块。生成后缩到 60px 看一眼，认不出就重来。

### 7. 私人图片走设置页上传，不进部署包

用户的照片（自己/家人/伴侣）如果打包进工程，等于发布到互联网。默认做法是**不打包**，改成在设置页里让用户自己传，图片只存在他手机的浏览器里：

```javascript
// 设置页：上传头像/背景
async function uploadAvatar(file){
  const dataUrl = await Util.compressImage(file, 400);   // 头像 400px 够了
  Store.set('avatar', dataUrl);
  render();
}
```

这样别人打开部署链接看到的是默认占位，看不到用户的照片。用户明确说"这张图我不介意公开"时才打包进 `<work>`。

## 生成后自检

跑脚本之前，自己先过一遍：

- [ ] 示例功能删干净了（HTML、JS、routes 三处）
- [ ] 所有 `{{占位符}}` 都替换了，包括 manifest.json
- [ ] 每个功能都有闭合的分区标记
- [ ] 没有裸的 `localStorage.` 调用
- [ ] 侧边栏功能数和 routes 数一致
- [ ] 没有联网功能时，apiCard 已删除
- [ ] 有图片上传的功能都过了 `Util.compressImage`

然后跑静态检查和冒烟测试。**命令原文和跑不动时的降级路径见 SKILL.md 第 6 步，那里是唯一副本**——命令涉及引号和跨平台差异，在两处各写一份必然漂移。

两个查的东西不一样，缺一不可：静态检查看得见占位符残留、分区标记不闭合、字号小于 16px；冒烟测试在无头 DOM 里真的把页面跑一遍，能抓到 route 指向不存在的页面、`Util.esc` 漏了导致 XSS、备份把 API key 带出去了这类**静态检查看不出来的逻辑错误**。

装不上 jsdom 就跳过第 2 步，但要在交付时告诉用户"逻辑没跑过自动测试，麻烦你在浏览器里多点几下"。

`smoke_test.js` 末尾有个 EXTRA 区，建议给核心功能补两三条断言（比如"记账合计算得对"），成本很低但能挡住真实的 bug。
