// Photographs pages in headless Chrome, for review: every page at every
// width, in both themes, at the given scroll positions.
//
//   node tools/review/shoot.mjs --url http://localhost:8765/ --out shots \
//        --sizes 1440x900,390x844 --themes light,dark --at hero:0,0.5,1 --at y:1600
//
// `--eval <js>` runs an expression after each page has loaded (before the
// photographs) and prints its value; `--review 0` leaves `review=1` out of
// the URL, so the hero runs as for a reader (adaptive, eased); `--nojs 1`
// turns JavaScript off; `--full 1` photographs the whole page; `--select
// <css>` photographs one element (after the scroll position is set).
//
// Positions: `hero:f` scrolls to the fraction f of the hero's travel (the
// page's [data-hero] section), `y:px` to a pixel offset, `bottom` to the end.
// Needs Node 22 (its built-in WebSocket) and Google Chrome. WebGL2 runs on
// SwiftShader, so the hero is drawn in software: `review=1` is added to the
// URL, which makes the hero follow the scroll at once and never step down.
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync, mkdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const args = process.argv.slice(2);
const opt = { url: 'http://localhost:8765/', out: 'shots', sizes: '1440x900,390x844', themes: 'light,dark',
  at: [], wait: 2500, chrome: '/usr/bin/google-chrome', name: 'home', query: '', eval: '', review: '1', nojs: '0',
  full: '0', select: '' };
for (let i = 0; i < args.length; i += 2) {
  const k = args[i].replace(/^--/, ''), v = args[i + 1];
  if (k === 'at') opt.at.push(v); else opt[k] = v;
}
if (!opt.at.length) opt.at = ['y:0'];
const positions = opt.at.flatMap((a) => {
  const [kind, list] = a.includes(':') ? a.split(':') : [a, ''];
  return list ? list.split(',').map((v) => ({ kind, v: Number(v) })) : [{ kind, v: 0 }];
});

const profile = mkdtempSync(join(tmpdir(), 'shoot-'));
const chrome = spawn(opt.chrome, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
  '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', '--enable-unsafe-swiftshader',
  '--use-angle=swiftshader', '--ignore-gpu-blocklist', '--force-color-profile=srgb', 'about:blank'],
  { stdio: ['ignore', 'ignore', 'pipe'] });
const wsUrl = await new Promise((resolve, reject) => {
  let buf = '';
  chrome.stderr.on('data', (d) => {
    buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/); if (m) resolve(m[1]);
  });
  setTimeout(() => reject(new Error('Chrome did not start')), 20000);
});

const ws = new WebSocket(wsUrl);
await new Promise((r) => ws.addEventListener('open', r, { once: true }));
let seq = 0; const pending = new Map(); const waiters = [];
ws.addEventListener('message', (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { const { resolve, reject } = pending.get(msg.id); pending.delete(msg.id);
    msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result); }
  else if (msg.method) for (const w of waiters.splice(0)) w(msg);
});
const send = (method, params = {}, sessionId) => new Promise((resolve, reject) => {
  const id = ++seq; pending.set(id, { resolve, reject });
  ws.send(JSON.stringify({ id, method, params, sessionId }));
});
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
const s = (m, p) => send(m, p, sessionId);
await s('Page.enable');
await s('Runtime.enable');
if (opt.nojs === '1') await s('Emulation.setScriptExecutionDisabled', { value: true });
mkdirSync(opt.out, { recursive: true });

for (const size of opt.sizes.split(',')) {
  const [w, h] = size.split('x').map(Number);
  const mobile = w < 700;
  await s('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: mobile ? 2 : 1, mobile });
  await s('Emulation.setTouchEmulationEnabled', { enabled: mobile });
  for (const theme of opt.themes.split(',')) {
    await s('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: theme }] });
    const sep = opt.url.includes('?') ? '&' : '?';
    const q = [opt.review === '1' ? 'review=1' : '', opt.query].filter(Boolean).join('&');
    await s('Page.navigate', { url: q ? `${opt.url}${sep}${q}` : opt.url });
    await sleep(opt.wait * 1);
    if (opt.eval) {
      const r = await s('Runtime.evaluate', { expression: opt.eval, awaitPromise: true, returnByValue: true });
      console.log(`eval ${w}x${h} ${theme}:`, JSON.stringify(r.result.value ?? r.exceptionDetails?.text));
    }
    for (const p of positions) {
      const expr = p.kind === 'hero'
        ? `(() => { const h = document.querySelector('[data-hero]'); const st = h.firstElementChild;
             const travel = h.offsetHeight - st.offsetHeight; const top = parseFloat(getComputedStyle(st).top) || 0;
             window.scrollTo(0, h.offsetTop - top + ${p.v} * travel); return travel; })()`
        : p.kind === 'bottom' ? 'window.scrollTo(0, document.body.scrollHeight)' : `window.scrollTo(0, ${p.v})`;
      await s('Runtime.evaluate', { expression: expr });
      await sleep(1600);
      const stat = await s('Runtime.evaluate', { expression: 'JSON.stringify(window.__hero || null)', returnByValue: true });
      let shot = { format: 'png' };
      if (opt.full === '1') {  // the whole page, beyond the window
        const m = await s('Page.getLayoutMetrics');
        const size = m.cssContentSize || m.contentSize;
        shot = { format: 'png', captureBeyondViewport: true,
          clip: { x: 0, y: 0, width: w, height: Math.ceil(size.height), scale: 1 } };
      } else if (opt.select) {  // one element, scrolled into view
        const r = await s('Runtime.evaluate', { returnByValue: true, expression:
          `(() => { const e = document.querySelector(${JSON.stringify(opt.select)}); if (!e) return null;
             const b = e.getBoundingClientRect(); return { x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height }; })()` });
        const b = r.result.value;
        if (b) shot = { format: 'png', captureBeyondViewport: true,
          clip: { x: Math.max(0, b.x - 8), y: Math.max(0, b.y - 8), width: Math.min(w, b.w + 16), height: b.h + 16, scale: 1 } };
      }
      const { data } = await s('Page.captureScreenshot', shot);
      const file = join(opt.out, `${opt.name}-${w}-${theme}-${p.kind}${p.kind === 'bottom' ? '' : p.v}.png`);
      writeFileSync(file, Buffer.from(data, 'base64'));
      console.log(file, stat.result.value);
    }
  }
}
ws.close(); chrome.kill(); await sleep(300);
try { rmSync(profile, { recursive: true, force: true }); } catch {}
