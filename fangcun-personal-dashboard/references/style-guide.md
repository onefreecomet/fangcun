# 风格指南

第 3-4 步用。目标是让用户在**真实可点的预览**里选定风格，而不是靠文字想象。

## 铁律：不要用生图模型画 UI 效果图

生图模型画出来的界面是"想象中的界面"——渐变、投影、字体、排版都实现不出来。用户选了图，做出来的东西不像，会觉得你水平不行。

**正确做法：出真实 HTML 预览。** 用户在手机上真的打开、真的点、真的输入。所见即所得，零落差，而且预览的 CSS 变量直接复用到正式版，一点不浪费。

生图模型（`baoyu-image-gen`）在本 Skill 里只有两个用途：
1. 生成**桌面图标**（第 6 步首次生成，第 9 步用户不满意时重生成）
2. 强风格（二次元/国风）时生成**背景图或装饰图**，且必须是在配色定下来之后

## 第 3 步：先聊大方向

只问两件事，问完就停：

**「你希望它看起来是什么感觉？」** 给预置风格包让他挑，或者接受这三种输入：
- 挑一个预置包
- 丢一张参考图（截图、别人的工作台、喜欢的 App）
- 给一张自己的照片 / 喜欢的角色图，从图里取色

**「有没有特别喜欢或者特别不想要的颜色？」**

**不要问**圆角多大、阴影多重、字体多粗——用户答不上来，那是预览环节用眼睛定的事。

## 预置风格包

每个包给出完整参数，直接可用。所有包共享同一套结构（左侧常驻栏 + 右侧卡片流），只换视觉。

### 🌿 森系（默认推荐）
参考案例同款，最百搭，男女通吃。
```css
--bg: #eef2e6;          /* 页面底 */
--sidebar: #7d9471;     /* 侧边栏 */
--sidebar-text: #f0f4ea;
--sidebar-active: #a8bc9c;
--card: #ffffff;
--text: #2f3a2c;
--text-dim: #7a8574;
--accent: #4a6741;      /* 主按钮、强调 */
--radius: 18px;
--shadow: 0 2px 12px rgba(80,100,70,.08);
--font: -apple-system, "PingFang SC", system-ui, sans-serif;
```

### ⚪ 极简
克制、留白多、几乎无色彩，适合不想被打扰的人。
```css
--bg: #f7f7f8;
--sidebar: #ffffff;
--sidebar-text: #3a3a3c;
--sidebar-active: #ececee;
--card: #ffffff;
--text: #1c1c1e;
--text-dim: #8e8e93;
--accent: #1c1c1e;
--radius: 12px;
--shadow: 0 1px 3px rgba(0,0,0,.06);
--font: -apple-system, "PingFang SC", system-ui, sans-serif;
```

### 🏮 国风
低饱和的宣纸色 + 朱砂点缀，配衬线字体。
```css
--bg: #f2ece1;
--sidebar: #5c4a3d;
--sidebar-text: #f2ece1;
--sidebar-active: #7a6455;
--card: #fdfaf4;
--text: #3b322b;
--text-dim: #8c7f73;
--accent: #a8443a;      /* 朱砂 */
--radius: 8px;
--shadow: 0 2px 10px rgba(90,70,50,.10);
--font: "Songti SC", "STSong", serif;
```
装饰建议：卡片标题左侧加一道 3px 朱砂竖线；可选生成水墨背景图（低透明度）。

### 🌸 二次元
高饱和、圆润、可爱。适合放角色图。
```css
--bg: #fdf0f4;
--sidebar: #ffffff;
--sidebar-text: #6b5b73;
--sidebar-active: #ffd9e5;
--card: #ffffff;
--text: #4a3f52;
--text-dim: #a396ad;
--accent: #ff6b9d;
--radius: 24px;
--shadow: 0 4px 16px rgba(255,107,157,.12);
--font: -apple-system, "PingFang SC", system-ui, sans-serif;
```
装饰建议：侧边栏顶部放角色头像（圆形），卡片可加细边框 `1px solid #ffe0ea`。

### 🌌 科技 / 暗色
参考案例 01 的蓝色科技风的暗色版本，适合夜间使用和开发者。
```css
--bg: #0f1419;
--sidebar: #161b22;
--sidebar-text: #8b949e;
--sidebar-active: #1f6feb;
--card: #161b22;
--text: #e6edf3;
--text-dim: #7d8590;
--accent: #1f6feb;
--radius: 10px;
--shadow: 0 0 0 1px rgba(255,255,255,.06);
--font: -apple-system, "PingFang SC", system-ui, sans-serif;
```
注意：暗色下 `--shadow` 用边框代替投影，投影在暗背景上看不见。

### 💙 清爽蓝
参考案例 01 同款亮色科技感，信息密度高时最耐看。
```css
--bg: #f0f6fc;
--sidebar: #ffffff;
--sidebar-text: #4a5568;
--sidebar-active: #dbeafe;
--card: #ffffff;
--text: #1a202c;
--text-dim: #718096;
--accent: #2b7fff;
--radius: 14px;
--shadow: 0 2px 8px rgba(43,127,255,.08);
--font: -apple-system, "PingFang SC", system-ui, sans-serif;
```

### 🍂 暖棕 / 日系
参考案例 02 同款，米色打底，温柔耐看。
```css
--bg: #ebe3d9;
--sidebar: #f5f0e8;
--sidebar-text: #6b5f52;
--sidebar-active: #2d2620;
--card: #ffffff;
--text: #3d352c;
--text-dim: #9c8f80;
--accent: #2d2620;
--radius: 14px;
--shadow: 0 2px 10px rgba(120,100,80,.07);
--font: -apple-system, "PingFang SC", system-ui, sans-serif;
```
注意这个包的 `--sidebar-active` 是深色反色块（选中项白字黑底），是它的识别特征。

### 🌙 夜安
低亮度暖色暗色，适合睡前用、不刺眼。
```css
--bg: #1c1917;
--sidebar: #262220;
--sidebar-text: #a8a29e;
--sidebar-active: #44403c;
--card: #262220;
--text: #e7e5e4;
--text-dim: #a8a29e;
--accent: #d4a373;
--radius: 16px;
--shadow: 0 0 0 1px rgba(255,255,255,.05);
--font: -apple-system, "PingFang SC", system-ui, sans-serif;
```

## 从用户的图取色

用户给了参考图 / 自己的照片 / 角色图时：

1. 用 Read 工具看图，提取 4-6 个主色
2. 按用途分配：最大面积的浅色 → `--bg`，中等饱和的深色 → `--sidebar`，最鲜艳的 → `--accent`
3. **必须检查对比度**：`--sidebar-text` 和 `--sidebar` 的对比度不够会看不清。深色底配浅字，浅色底配深字，中间色最危险
4. 取完色告诉用户你取了什么，比如「我从你这张照片里取了海水的青灰做侧边栏、夕阳的橙做强调色」

## 照片的隐私处理（重要）

用户想放自己/家人/伴侣的照片时，**必须**说清楚：

> 提醒一下：如果这张照片打包进部署文件，等于把它发布到互联网上了——虽然没人知道链接，但技术上是公开的。
>
> 两个做法：
> - **想让照片跟着工作台走**（换手机也在）→ 打包进去，但请确认这张图你不介意被陌生人看到
> - **不想公开** → 做成在设置页里自己上传，图片只存在你手机的浏览器里，别人打开链接看不到

默认选后者。做法见 `build-guide.md` 的「7. 私人图片走设置页上传」（记得压缩，否则爆 localStorage）。

## 第 4 步：出真实 HTML 预览

### 输出形式

生成**一个** `风格预览.html` 文件，顶部有风格切换按钮，内含 3 版倾向。用户在手机上打开，点着切换对比。

三版怎么选：
- 一版是用户明确倾向的那个包
- 一版是同方向的变体（比如更深/更浅、更圆/更方）
- 一版是你觉得可能更适合他的另一个方向（给一个跳出来的选项，常常用户会选这个）

### 预览必须包含

1. **完整的侧边栏**，用**用户真实的功能名和 emoji**，不是"功能一 功能二"
2. **2-3 张真实卡片**，装用户真实的功能内容（他的记账分类、他的打卡项目）——风格好不好看，很大程度取决于放进去的是什么内容
3. **至少一个能真的输入的输入框**和一个能真的点的按钮 —— 让用户感受手感
4. **正确的移动端尺寸**：`<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`

### 预览模板

用 `assets/style-preview.html` 作为起点，替换里面的 `{{}}` 占位符。切换器的实现就是给 `<body>` 换 class，每个 class 下一套 CSS 变量——这样三套风格共用一份 HTML 结构，改起来也快。

### 给用户的话

**话术原文和交付方式（含微信传手机、打不开怎么办）见 SKILL.md 第 3-4 步，那里是唯一副本**——同一句要念给用户的话在两处各写一份必然漂移。

### 迭代

用户提修改就重新出，不要嫌麻烦——**这一步多花 10 分钟，比做完了返工强 10 倍**。但**有上限**：改到第 4 轮还定不下来，按 SKILL.md 的 CHECKPOINT 2 收口，归纳成一句话出最后一版往下走。无限打磨会耗光用户的耐心，而配色是后期改起来最便宜的东西。

常见的修改请求和对应参数：
- "太素了" → 提高 `--accent` 饱和度，或给卡片加细边框
- "太花了" → 降饱和，减少 emoji，`--shadow` 调轻
- "看不清" → 提高 `--text` 和 `--card` 的对比度，或加大字号
- "太挤了" → 加大卡片 padding 和间距，不是缩小字号
- "不够高级" → 通常是指要更克制：降饱和、加大留白、统一圆角、减少颜色种类

用户明确说"就这版"才进第 5 步。**把选定的全部 CSS 变量记下来**，第 6 步原样写进工程。
