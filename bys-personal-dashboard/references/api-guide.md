# 联网功能指南

用户选了〔联网〕类功能时，第 6 步读这个。

## 先想清楚：这个功能真的需要联网吗

在动手之前，对每个联网功能问一遍："有没有一个不联网的做法，能解决用户 80% 的需求？"

| 用户想要 | 他真正的需求 | 零门槛替代方案 |
|---|---|---|
| 每日热点新闻 | 想知道今天发生了什么 | 几个热榜网站的快捷跳转入口 |
| 天气 | 今天穿什么/带不带伞 | **劝退**——手机自带天气，边际价值极低 |
| 汇率/股价 | 偶尔看一眼 | 跳转链接 |
| AI 对话 | 随时能问点什么 | 无可替代，**值得做** |

跳转入口的实现就是几个 `<a href>`，五分钟的事，而且永远不会坏。**主动把这个选项给用户**，让他自己权衡要不要为了"数据显示在工作台里"去申请 key。

很多用户听完会说"那就跳转吧"——这是好结果，不是失败。

## CORS：联网功能真正的拦路虎

这是新手最容易踩的坑，而且**跟代码写得好不好完全无关**。

浏览器有同源策略：你的页面在 `abc.edgeone.app`，去 fetch `api.example.com`，浏览器会先问对方"你允许 abc.edgeone.app 调你吗"。对方没在响应头里回一个 `Access-Control-Allow-Origin`，浏览器就**直接把响应扔掉**，你的代码连数据的边都摸不到。

关键认知：**这不是你能在前端修复的问题。** 没有任何 JS 写法能绕过它，改 header、加参数都没用。只能换 API 或者加代理。

**所以：动手写之前先测。** 不要等功能写完了才发现调不通。

### 怎么测一个 API 能不能直连

**macOS / Linux**

```bash
curl -s -I "https://目标API地址" -H "Origin: https://test.example.com" | grep -i "access-control"
```

**Windows PowerShell**（没有 `grep`，用 `-match`）

```powershell
(curl.exe -s -I "https://目标API地址" -H "Origin: https://test.example.com") -match "access-control"
```

有 `access-control-allow-origin: *`（或回显了你的 Origin）→ 能直连。
什么都没有 → 不能直连，走下面的 B/C 方案。

**两条都跑不动时**（没装 curl、公司网络拦截、沙箱不通外网）——**不要猜，也不要硬写**。如实告诉用户：

> 我在这儿没法实测这个接口能不能被网页直接调用。两个办法：要么先按跳转方案做（五分钟，永远不会坏）；要么我先按直连写，你部署完打开页面如果这块是空的，回来找我改成跳转。

**默认走前者。** 猜着写直连、让用户部署完才发现是空的，比一开始就用跳转方案糟糕得多。

**测出来的结果要如实告诉用户。** 不能直连就当场说，别硬做。

### 大致规律（仍然要实测，别直接信）

- **大模型 API**：多数厂商的 OpenAI 兼容接口支持浏览器直连（他们需要支持前端应用）。这是联网功能里成功率最高的一类。
- **国内的天气/新闻/数据聚合 API**：多数**不支持**，因为它们的设计假设是服务端调用。
- **公开的免费 API（无需 key 那种）**：一半一半，且随时可能关停——不要把工作台的核心功能架在这种 API 上。

## 三条解法

### A. 换一个能直连的 API（首选）

实测通过就直接用。简单、可靠、不绑定部署方式。

### B. 降级成跳转（次选）

测不通就退回上面那张替代方案表。诚实告诉用户：

> 我试了下，这个接口不允许网页直接调用（技术上叫跨域限制，绕不过去）。两个选择：
> - 换成一键跳转到 XX，点一下就打开，效果差不多，零门槛
> - 或者我们给工作台加一层代理，能真的把数据显示在页面里，但这样工作台就必须部署在 EdgeOne 上，不能随便挪地方了
>
> 你怎么想？

### C. 边缘函数代理（有代价，慎选）

EdgeOne Pages 支持边缘函数，可以在 `functions/` 目录放一个转发脚本，由服务端去调 API 再返回给前端，绕过 CORS。

**代价必须说清楚**：工作台从此和 EdgeOne 绑定了——本地双击打不开、换托管平台要重做。对一个"本地也能跑"的个人工作台来说，这是不小的损失。

只在满足全部三条时才选 C：用户明确要这个功能、没有替代方案、且已经决定部署到 EdgeOne。

## API key 的处理

### 存哪

一律走 `Store.setSecret()`，存在 `bysdash$secret:` 命名空间。

**为什么单独一个命名空间**：这个空间不会被 `Store.exportAll()` 导出。用户备份数据、把 JSON 发给别人或存到网盘时，key 不会跟着泄漏。这是个真实的泄漏路径，很多人栽在这。

### key 在前端安全吗

**在这个场景下，安全。** key 存在用户自己手机的浏览器里，只有他自己能看到。这和"把 key 写死在代码里然后部署到公网"完全是两回事——后者是所有人都能看到源码里的 key。

要跟用户讲清楚这个区别，否则他会不敢填。

但有两条必须提醒用户：
1. 别把 key 截图发给别人（包括发给你）
2. 备份文件不含 key，所以换手机后需要重新填一次

### 设置页写法

骨架的设置页已有 `apiCard`，每个联网功能加一组：

```html
<div style="margin-bottom:12px">
  <label style="font-size:14px;display:block;margin-bottom:6px">DeepSeek</label>
  <input type="password" id="key_deepseek" placeholder="粘贴你的 key">
  <p class="hint">在 platform.deepseek.com 注册后，「API Keys」里创建一个</p>
</div>
```

并在 `Settings.keys` 里登记标识：

```javascript
keys: ['deepseek'],
```

`type="password"` 不是为了防黑客，是为了用户在公共场合打开设置页时不被瞄到。

### 没配 key 时的表现

功能不能白屏或报错，要给出可操作的提示：

```javascript
const key = Store.getSecret('deepseek');
if (!key) {
  box.innerHTML = `<div class="empty">
    还没配置 key<br>
    <button class="btn" style="margin-top:10px" onclick="App.go('settings')">去设置</button>
  </div>`;
  return;
}
```

### 请求失败时

网络会断、key 会过期、额度会用完。每个联网请求都要有 try/catch，失败时显示人话而不是错误码：

```javascript
try {
  const r = await fetch(url, { headers:{ Authorization: 'Bearer ' + key } });
  if (r.status === 401) throw new Error('key 好像不对，去设置里检查一下');
  if (!r.ok) throw new Error('接口暂时用不了（' + r.status + '）');
  // ...
} catch (e) {
  box.innerHTML = `<div class="empty">${Util.esc(e.message)}</div>`;
}
```

## 用户需要自己申请 key 时的引导

在第 8 步之后、交付之前，给一份**具体到点哪个按钮**的步骤，别只给个网址：

> **申请 XX 的 key（大概 10 分钟）**
> 1. 打开 xxx.com，用手机号注册
> 2. 完成实名认证（国内的服务基本都要，身份证 + 人脸）
> 3. 进「控制台」→「API Keys」→「创建」
> 4. 复制那串字符（**只显示一次，关掉就看不到了，先粘到备忘录**）
> 5. 打开你的工作台 → 设置 → 粘贴 → 保存

第 4 步那个提醒很重要，大部分平台的 key 只显示一次，用户关掉页面就得重新创建。
