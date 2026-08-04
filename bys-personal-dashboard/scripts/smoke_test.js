#!/usr/bin/env node
/**
 * 工作台冒烟测试 —— 在无头 DOM 里真的把页面跑一遍。
 *
 *   npm install jsdom          # 只需装一次
 *   node smoke_test.js <工作台目录>
 *
 * validate_dashboard.py 查的是"代码长得对不对"，这个查的是"跑起来对不对"。
 * 两个都过，才算真的能交付。
 *
 * 这里只做与功能无关的通用检查。功能特定的断言（比如记账合计算得对不对）
 * 建议按需在下面的 EXTRA 区补几条，成本很低但能挡住真实的 bug。
 */
const fs = require('fs');
const path = require('path');

let JSDOM;
try { ({ JSDOM } = require('jsdom')); }
catch { console.error('需要 jsdom：npm install jsdom'); process.exit(2); }

const dir = process.argv[2];
if (!dir) { console.error('用法：node smoke_test.js <工作台目录>'); process.exit(2); }

const file = path.join(dir, 'index.html');
if (!fs.existsSync(file)) { console.error('找不到 ' + file); process.exit(2); }

const pass = [], fail = [];
const t = (name, fn) => { try { fn(); pass.push(name); } catch (e) { fail.push(`${name} → ${e.message}`); } };
const assert = (cond, msg) => { if (!cond) throw new Error(msg); };

const dom = new JSDOM(fs.readFileSync(file, 'utf8'), {
  runScripts: 'dangerously',
  url: 'https://smoke.test/',
  virtualConsole: new (require('jsdom').VirtualConsole)().on('jsdomError', e => {
    fail.push('页面抛出未捕获错误 → ' + e.message);
  })
});
const w = dom.window, d = w.document;

// 顶层 const 声明不会挂到 window 上（浏览器里内联 onclick 能访问，这里要 eval 取）
const G = name => { try { return w.eval(name); } catch { return undefined; } };
const App = G('App'), Store = G('Store'), Util = G('Util');

t('App / Store / Util 都存在', () => {
  assert(App, '找不到 App —— 路由没定义？');
  assert(Store, '找不到 Store —— 存储抽象层被删了？');
  assert(Util, '找不到 Util');
});

t('侧边栏渲染数量与可见 routes 一致', () => {
  const btns = d.querySelectorAll('#nav button').length;
  const visible = App.routes.filter(r => !r.hidden).length;
  assert(btns > 0, '侧边栏一个按钮都没渲染出来');
  assert(btns === visible, `侧边栏 ${btns} 个，可见 routes ${visible} 条（hidden 路由不占 tab），对不上`);
});

t('每个 route 都有对应页面，且能切过去', () => {
  App.routes.forEach(r => {
    assert(d.getElementById('page-' + r.id), `route「${r.id}」找不到 #page-${r.id}`);
    App.go(r.id);
    const cur = d.querySelector('.page.on');
    assert(cur && cur.id === 'page-' + r.id, `切到「${r.id}」失败`);
  });
});

t('有设置页', () => {
  assert(App.routes.some(r => r.id === 'settings'), '没有设置页，用户丢了数据无法恢复');
});

t('Store 读写往返正常', () => {
  Store.set('__smoke', { a: 1, b: '中文' });
  const v = Store.get('__smoke');
  assert(v && v.a === 1 && v.b === '中文', 'Store 存进去读不回来');
  Store.remove('__smoke');
  assert(Store.get('__smoke', 'DEFAULT') === 'DEFAULT', 'remove 后默认值没生效');
});

t('按天存储会随日期隔离', () => {
  Store.setDaily('__smokeDaily', 5);
  assert(Store.get('__smokeDaily:' + Util.today()) === 5, '今天的数据没存对');
  assert(Store.get('__smokeDaily:2099-01-01', 0) === 0, '未来某天不该有数据（跨天没重置）');
});

t('备份包含业务数据，且不含 API key', () => {
  Store.set('__smokeBiz', 'BIZ_DATA_MARK');
  Store.setSecret('__smokeKey', 'sk-SHOULD-NOT-LEAK-MARK');
  const dump = JSON.stringify(Store.exportAll());
  assert(dump.includes('BIZ_DATA_MARK'), '备份里没有业务数据');
  assert(!dump.includes('SHOULD-NOT-LEAK-MARK'), 'API key 被导出进备份了 —— 用户转发备份时会泄漏');
  Store.remove('__smokeBiz');
});

t('存储写满时不会崩', () => {
  // 模拟 localStorage 配额耗尽，Store.set 应该温和失败而不是抛异常炸掉整个页面
  const orig = w.localStorage.setItem;
  w.localStorage.setItem = () => { const e = new Error('quota'); e.name = 'QuotaExceededError'; throw e; };
  try { Store.set('__smokeQuota', 'x'); }
  finally { w.localStorage.setItem = orig; }
});

/* ═══════════ EXTRA：功能特定断言写在这里 ═══════════
   例：
   t('记账合计算得对', () => {
     const M = G('Money');
     d.getElementById('moneyAmount').value = '10';
     M.add('out');
     assert(d.getElementById('moneySum').innerHTML.includes('10.00'), '合计没算出来');
   });
*/

// 用户输入必须转义 —— 挨个模块试一遍能找到的输入框
t('用户输入被转义（无 XSS）', () => {
  const payload = '<img src=x onerror="window.__xss=1">';
  let tried = 0;
  d.querySelectorAll('input[type=text], textarea').forEach(el => {
    el.value = payload;
    const card = el.closest('.card');
    const btn = card && card.querySelector('.btn');
    if (btn) { tried++; try { btn.click(); } catch {} }
  });
  assert(!w.__xss, '注入的脚本被执行了 —— 检查是不是漏了 Util.esc()');
  assert(!d.querySelector('.main img[src="x"]'), '注入的标签进了 DOM —— 检查 Util.esc()');
  if (!tried) console.log('  （提示：没找到可点的输入框，XSS 这项没真正测到）');
});

console.log();
pass.forEach(x => console.log('  \x1b[32m✓\x1b[0m ' + x));
if (fail.length) {
  console.log();
  fail.forEach(x => console.log('  \x1b[31m✗\x1b[0m ' + x));
  console.log(`\n\x1b[31m${fail.length} 项失败\x1b[0m\n`);
  process.exit(1);
}
console.log(`\n\x1b[32m全部通过（${pass.length} 项）\x1b[0m\n`);
