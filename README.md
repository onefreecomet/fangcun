# 方寸工作台（FangCun）

国风日夜双主题的个人工作台：站桩打卡、Alpha 日志（WorldQuant 双账户）、农历·八字（干支 200 年考据）、待办（含目标日倒计时）、密码本、江湖（网址收藏）、排盘跳转、设置（备份/初始数据）。

线上地址：https://ficp.fun/s/2U2yUe/

## 仓库结构

```
fangcun/
├── index.html                  # 工作台本体：全部界面+逻辑+样式（单文件）
├── manifest.json               # PWA 清单
├── icon.png                    # 桌面图标（enso 禅意圆 + 毛笔方寸 + 朱砂小印）
├── 工作台配置.md                # 迭代配置文档：加功能/改样式前先读它
├── bys-personal-dashboard/     # 生成器 skill：复现/修改整个工作台的核心
│   ├── SKILL.md                # skill 主文档（触发词：初始化不一书个人工作台生成器）
│   ├── scripts/                # validate_dashboard.py / smoke_test.js / make_icon.py
│   ├── references/             # build-guide / deploy-guide / 主题库 / 配置模板
│   ├── assets/                 # skeleton 骨架（Store 抽象层 / 分区标记）
│   └── examples/ test-prompts.json
```

## 如何复现 / 修改

1. 克隆本仓库：`git clone git@github.com:onefreecomet/fangcun.git`
2. 把 `bys-personal-dashboard/` 放到 `~/.workbuddy/skills/` 下（skill 安装目录）
3. 在 `bys-personal-dashboard/` 下 `npm install`（smoke_test.js 依赖 jsdom）
4. 告诉 agent「初始化不一书个人工作台生成器」，它会读取 SKILL.md 开始引导式重建
5. 直接改 `index.html`（单文件内联），改完跑验证：
   ```bash
   python3 bys-personal-dashboard/scripts/validate_dashboard.py ./
   node bys-personal-dashboard/scripts/smoke_test.js ./
   ```

## 验证口径

- **干支农历**：与 lunar_python 69 项对拍全过（含立春/立秋换界、闰月、2033 闰十一月、子初换日、五鼠遁）
- 修改 LUNAR_INFO / JQ_STR 数据后必须重跑对拍：`node /tmp/gz_check.js`（基准生成见 memory 日志）
