# 方寸工作台（FangCun）

> **一切福田，不离方寸；从心而觅，感无不通。** ——《六祖坛经》

一个完全属于你自己的手机端个人工作台：国风日夜双主题，数据只存在你自己的浏览器里，不上传、不泄露。

## 🌐 在线体验

| 入口 | 地址 | 说明 |
|---|---|---|
| **GitHub Pages**（推荐） | https://onefreecomet.github.io/fangcun/ | 开源部署，稳定永久 |
| Ficp.fun（备用） | https://ficp.fun/s/2U2yUe/ | 国内访问更快 |

> 打开链接即可使用；在手机上「添加到主屏幕」可获得 App 体验（独立图标、全屏、无地址栏）。
> 所有数据存于本地 localStorage——**网页谁都能访问，但数据只在你自己的手机上**。

## ✨ 功能一览

- **📅 今日干支**：一打开就是今天的干支五行，出自《六祖坛经》的「方寸」之意
- **💬 今日语录**：自己填、每次打开随机展示，像过去的自己在跟现在的自己对话
- **🧘 站桩打卡**：一键记录天数与感受，内置计时器（开始/暂停/结束），每 10 分钟轻柔磬声提醒，iOS 锁屏后台照常计时
- **📊 Alpha 日志**：WorldQuant 多账号（冰神/涵涵）提交统计，地区/类型/备注一应俱全
- **🔮 八字排盘**：子平盲派双核、刑冲合害可视化，一键跳转
- **🗡️ 江湖**：私人网址收藏夹，自定义分类标签，一键直达
- **🔐 密码本**：本地统一管理，导出导入方便，换机直接迁移
- **✅ 待办事项**：极简「记一件」，目标日倒计时
- **🌓 日夜自动切换**：晚 7 点入夜、早 7 点日出，跟着天走
- **☁️ 云同步**：一键推送/拉取到 GitHub 私有仓库（token 本地存储、不进备份）

## 🎨 设计

- 国风视觉：宣纸纹理底、朱砂印章、卷轴式干支卡、水墨空状态插画
- 内嵌**马善政毛笔楷书**（Ma Shan Zheng，OFL 开源）——标题/语录/印章用毛笔笔锋，正文/数字用宋体保持清晰
- 单文件 PWA：`index.html` 内联全部 CSS/JS/字体（约 230KB），可离线运行

## 仓库结构

```
fangcun/
├── index.html                  # 工作台本体：全部界面+逻辑+样式（单文件）
├── manifest.json               # PWA 清单
├── icon.png                    # 桌面图标（enso 禅意圆 + 毛笔方寸 + 朱砂小印）
├── 工作台配置.md                # 迭代配置文档：加功能/改样式前先读它
├── fangcun-personal-dashboard/     # 生成器 skill：复现/修改整个工作台的核心
│   ├── SKILL.md                # skill 主文档（触发词：初始化个人工作台生成器）
│   ├── scripts/                # validate_dashboard.py / smoke_test.js / make_icon.py
│   ├── references/             # build-guide / deploy-guide / 主题库 / 配置模板
│   ├── assets/                 # skeleton 骨架（Store 抽象层 / 分区标记）
│   └── examples/ test-prompts.json
```

## 如何复现 / 修改

1. 克隆本仓库：`git clone git@github.com:onefreecomet/fangcun.git`
2. 把 `fangcun-personal-dashboard/` 放到 `~/.workbuddy/skills/` 下（skill 安装目录）
3. 在 `fangcun-personal-dashboard/` 下 `npm install`（smoke_test.js 依赖 jsdom）
4. 告诉 agent「初始化个人工作台生成器」，它会读取 SKILL.md 开始引导式重建
5. 直接改 `index.html`（单文件内联），改完跑验证：
   ```bash
   python3 fangcun-personal-dashboard/scripts/validate_dashboard.py ./
   node fangcun-personal-dashboard/scripts/smoke_test.js ./
   ```

## 更新日志

- **v1.5.1** · 云同步：一键推/拉到 GitHub 私有仓库（token 本地存，不进备份）
- **v1.5** · 站桩计时器 + 10 分钟磬声提醒 + iOS 锁屏后台计时；设置页版本号显示
- **v1.2.x** · 内嵌毛笔楷书、字排纸感、动效润色、Alpha 地区扩展
- **v1.1.x** · 国风风格统一升级（SVG 图标系统 / 设计令牌 / 宣纸便条 / 朱砂印章 / 墨色玄夜）
- **v1.0.0** · 首个发布版本：国风日夜双主题个人工作台

## 验证口径

- **干支农历**：与 lunar_python 69 项对拍全过（含立春/立秋换界、闰月、2033 闰十一月、子初换日、五鼠遁）
- 修改 LUNAR_INFO / JQ_STR 数据后必须重跑对拍：`node /tmp/gz_check.js`（基准生成见 memory 日志）

## License

MIT
