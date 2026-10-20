/* The home page hero: spins coming into resonance.
 *
 * Every point is a spin of one software ecosystem (ANTs, AFNI, FSL,
 * FreeSurfer, Workbench), drawn in its pastel. At the top of the page the
 * spins sit in five ensembles, one per ecosystem, and precess about a vertical
 * field B0: the tip of each spin turns on a small horizontal circle, each
 * ensemble at its own frequency, each spin with its own phase. They are
 * dephased, and the coherence (the length of their mean transverse direction,
 * |<e^{i phi}>|) is close to 0.
 *
 * Scrolling brings every frequency to one Larmor frequency and locks the
 * phases: the coherence rises to 1, and the spins gather into one brain, a
 * point cloud of the MNI ICBM 152 template (static/hero/hero.bin, written by
 * tools/hero/make_hero.py), which turns slowly about B0. The shared
 * precession stays as a slight shimmer, and the ecosystems keep their colours.
 *
 * The phase of spin i is phi_i = phi0_i + theta(t) + eps_i * D(t), where
 * theta advances at the Larmor frequency and D accumulates the dephasing,
 * dD/dt = omega0 * (1 - convergence): when the frequencies converge D stops,
 * so nothing jumps however fast the reader scrolls. The lock blends each
 * spin's direction with the common one.
 *
 * Without WebGL2, with the effects off (the header's switch, off by default
 * when the system asks for reduced motion) or without JavaScript, the hero is
 * a still drawing of the brain. A slow machine is noticed by its frame time:
 * first the resolution goes down, then the number of spins. `?review=1`
 * (screenshots) makes the hero follow the scroll at once and never step down.
 */
(function () {
  'use strict';
  var doc = document.documentElement;
  var hero = document.querySelector('[data-hero]');
  if (!hero) return;
  var stage = hero.querySelector('.hero-stage');
  var canvas = hero.querySelector('.hero-canvas');
  var copy = hero.querySelector('.hero-copy');
  var end = hero.querySelector('.hero-end');
  var labelsHost = hero.querySelector('.hero-labels');
  var b0 = hero.querySelector('.hero-b0');
  var hudCoh = hero.querySelector('[data-hud-coh]');
  var hudSpread = hero.querySelector('[data-hud-spread]');
  var review = /[?&]review=1/.test(location.search);
  var stats = window.__hero = { mode: 'init', frames: 0, avg: 0, level: 0, n: 0, coherence: 0, progress: 0 };
  var fxOn = function () { return doc.getAttribute('data-fx') === 'on'; };

  var gl = canvas.getContext('webgl2', { alpha: false, antialias: false, premultipliedAlpha: false,
    preserveDrawingBuffer: review, powerPreference: 'default' });
  if (!gl) { stats.mode = 'no-webgl2'; return; }

  /* ------------------------------------------------------------ data */
  function parse(buf) {
    var dv = new DataView(buf);
    if (String.fromCharCode(dv.getUint8(0), dv.getUint8(1), dv.getUint8(2), dv.getUint8(3)) !== 'LXH1') throw new Error('not a hero file');
    var hl = dv.getUint32(4, true);
    var head = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 8, hl)));
    var n = head.n, o = 8 + hl;
    var xyz = new Int16Array(buf, o, 3 * n); o += 6 * n;
    var eco = new Uint8Array(buf, o, n); o += n;
    var val = new Uint8Array(buf, o, n);
    return { head: head, n: n, xyz: xyz, eco: eco, val: val };
  }
  function load(src) {
    var m = /^data:[^,]*;base64,(.*)$/.exec(src);
    if (m) {   // the self-contained preview: decode in place
      var bin = atob(m[1]), u = new Uint8Array(bin.length);
      for (var i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
      return Promise.resolve(u.buffer);
    }
    return fetch(src).then(function (r) { if (!r.ok) throw new Error('hero.bin: ' + r.status); return r.arrayBuffer(); });
  }

  /* The spins' own randomness, from a seeded generator: the same every visit. */
  var N_ECO = 5;
  var ECO_OFFSET = [0.16, -0.34, 0.34, -0.16, 0.0];   // each ensemble's frequency, relative to omega0
  var OMEGA0 = 2 * Math.PI / 3.4;                       // one turn in 3.4 s, a slowed-down picture
  function rng(seed) {
    return function () {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function gauss(r) { return Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(2 * Math.PI * r()); }
  var spins = null;   // phi0, eps per spin, for the readout (the shader has the same)
  function randomness(n, eco) {
    var r = rng(20261020), gas = new Float32Array(3 * n), spin = new Float32Array(4 * n);
    var phi0 = new Float32Array(n), eps = new Float32Array(n), sum = 0, sum2 = 0;
    for (var i = 0; i < n; i++) {
      // a point of the ensemble: a ring in the plane across B0, turning about it
      var a = 2 * Math.PI * r(), rad = 0.5 + 0.5 * Math.sqrt(r());
      gas[3 * i] = rad * Math.cos(a); gas[3 * i + 1] = 0.11 * gauss(r); gas[3 * i + 2] = rad * Math.sin(a);
      phi0[i] = 2 * Math.PI * r();
      eps[i] = ECO_OFFSET[eco[i]] + 0.07 * gauss(r);
      spin[4 * i] = phi0[i]; spin[4 * i + 1] = eps[i];
      spin[4 * i + 2] = r();                                  // when it sets off
      spin[4 * i + 3] = (r() < 0.5 ? -1 : 1) * (0.35 + 0.75 * r());  // how far it swirls on the way
      sum += eps[i]; sum2 += eps[i] * eps[i];
    }
    var mean = sum / n;
    spins = { phi0: phi0, eps: eps, sd: Math.sqrt(Math.max(0, sum2 / n - mean * mean)) };
    return { gas: gas, spin: spin };
  }

  /* --------------------------------------------------------- shaders */
  var VS = [
    '#version 300 es',
    'precision highp float;',
    'in vec3 aBrain; in float aEco; in float aVal; in vec3 aGas; in vec4 aSpin;',
    'uniform vec2 uRes; uniform float uDpr; uniform float uSize; uniform float uP;',
    'uniform float uTheta; uniform vec2 uCommon; uniform float uD; uniform float uLock;',
    'uniform vec4 uBrainRot; uniform vec4 uGasRot[5];',
    'uniform vec4 uGasC; uniform vec4 uBrainC; uniform vec4 uClu[5]; uniform vec3 uCol[5];',
    'out vec4 vCol;',
    // turn about the vertical axis, then tilt towards the viewer; r = (cos, sin) of each
    'vec3 view(vec3 p, vec4 r) {',
    '  vec3 q = vec3(p.x * r.x + p.z * r.y, p.y, -p.x * r.y + p.z * r.x);',
    '  return vec3(q.x, q.y * r.z - q.z * r.w, q.y * r.w + q.z * r.z);',
    '}',
    'void main() {',
    '  int k = int(aEco + 0.5);',
    // the spin's transverse direction: its own phase, blended into the common one
    '  float th = aSpin.x + uTheta + aSpin.y * uD;',
    '  vec2 u = mix(vec2(cos(th), sin(th)), uCommon, uLock);',
    '  float m = length(u);',
    '  u = m > 1e-3 ? u / m : uCommon;',
    // its journey from the ensemble into the brain, each spin setting off in turn
    '  float st = 0.06 + aSpin.z * 0.26;',
    '  float q = smoothstep(st, st + 0.40, uP);',
    '  float e = q * q * (3.0 - 2.0 * q);',
    // the tip on its circle about B0 (vertical), in each place's own units
    '  vec3 tipG = vec3(u.x, 0.0, u.y) * 0.10;',
    '  vec3 tipB = vec3(u.x, 0.0, u.y) * 0.009;',
    '  vec4 C = uClu[k];',
    '  vec3 g = view(aGas + tipG, uGasRot[k]);',
    '  vec2 gasXY = C.xy + vec2(g.x, -g.y) * (1.0 / (1.0 - g.z * 0.22)) * C.z;',
    '  vec3 b = view(aBrain + tipB, uBrainRot);',
    '  vec2 brainXY = uBrainC.xy + vec2(b.x, -b.y) * (1.0 / (1.0 - b.z * 0.18)) * uBrainC.z;',
    // the way in: a swirl about the axis of the cloud
    '  vec2 c = mix(uGasC.xy, uBrainC.xy, e);',
    '  vec2 d = mix(gasXY - uGasC.xy, brainXY - uBrainC.xy, e);',
    '  float sw = sin(3.14159265 * q) * aSpin.w;',
    '  float cs = cos(sw), sn = sin(sw);',
    '  d.y /= 0.72;',
    '  vec2 pos = c + vec2(d.x * cs - d.y * sn, (d.x * sn + d.y * cs) * 0.72);',
    '  vec2 clip = pos / uRes * 2.0 - 1.0;',
    '  gl_Position = vec4(clip.x, -clip.y, 0.0, 1.0);',
    // light: nearer is brighter; a spin facing the viewer glints (much in the
    // ensembles, a little in the brain)
    '  float depth = mix(g.z, b.z, e) * 0.5 + 0.5;',
    '  float glint = 0.5 + 0.5 * u.y;',
    '  float bright = (0.42 + 0.62 * depth) * mix(0.5 + 0.5 * glint, 0.86 + 0.14 * glint, e);',
    '  float size = uSize * (0.62 + 0.62 * depth) * mix(1.0, 0.8 + 0.4 * aVal, e);',
    '  gl_PointSize = max(1.0, size * uDpr);',
    '  vCol = vec4(uCol[k], clamp(bright, 0.12, 1.0));',
    '}'].join('\n');
  var FS = [
    '#version 300 es',
    'precision mediump float;',
    'in vec4 vCol; out vec4 o;',
    'void main() {',
    '  float r = length(gl_PointCoord - 0.5) * 2.0;',
    '  float a = smoothstep(1.0, 0.45, r);',
    '  if (a <= 0.0) discard;',
    '  o = vec4(vCol.rgb, vCol.a * a);',
    '}'].join('\n');

  function shader(type, src) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
    return s;
  }
  var prog;
  try {
    prog = gl.createProgram();
    gl.attachShader(prog, shader(gl.VERTEX_SHADER, VS));
    gl.attachShader(prog, shader(gl.FRAGMENT_SHADER, FS));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
  } catch (e) { stats.mode = 'shader-error'; stats.error = String(e); return; }
  var U = {};
  ['uRes', 'uDpr', 'uSize', 'uP', 'uTheta', 'uCommon', 'uD', 'uLock', 'uBrainRot', 'uGasRot', 'uGasC', 'uBrainC', 'uClu', 'uCol'].forEach(function (n) {
    U[n] = gl.getUniformLocation(prog, n);
  });

  var data, vao;
  function buffers() {
    var rnd = randomness(data.n, data.eco);
    vao = gl.createVertexArray();
    gl.bindVertexArray(vao);
    function attr(name, arr, size, type, norm) {
      var loc = gl.getAttribLocation(prog, name);
      if (loc < 0) return;
      var b = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, b);
      gl.bufferData(gl.ARRAY_BUFFER, arr, gl.STATIC_DRAW);
      gl.enableVertexAttribArray(loc);
      gl.vertexAttribPointer(loc, size, type, norm, 0, 0);
    }
    attr('aBrain', data.xyz, 3, gl.SHORT, true);
    attr('aEco', data.eco, 1, gl.UNSIGNED_BYTE, false);
    attr('aVal', data.val, 1, gl.UNSIGNED_BYTE, true);
    attr('aGas', rnd.gas, 3, gl.FLOAT, false);
    attr('aSpin', rnd.spin, 4, gl.FLOAT, false);
    gl.bindVertexArray(null);
  }

  /* ---------------------------------------------------------- layout */
  var W = 0, H = 0, dpr = 1, narrow = false;
  var maxDpr = Math.min(window.devicePixelRatio || 1, 2);
  var gasC = [0, 0, 1], brainC = [0, 0, 1], clusters = [], labels = [];
  function css(name) { return getComputedStyle(doc).getPropertyValue(name).trim(); }
  function rgb(hex) {
    var h = hex.replace('#', '');
    if (h.length === 3) h = h.replace(/./g, '$&$&');
    var v = parseInt(h, 16);
    return [((v >> 16) & 255) / 255, ((v >> 8) & 255) / 255, (v & 255) / 255];
  }
  var ECO_VARS = ['--deep-ants', '--deep-afni', '--deep-fsl', '--deep-freesurfer', '--deep-workbench'];
  var pal = null;
  function colours() {
    var cols = [];
    ECO_VARS.forEach(function (v) { cols.push.apply(cols, rgb(css(v) || '#888888')); });
    pal = { cols: new Float32Array(cols), bg: rgb(css('--bg') || '#000000') };
  }

  function makeLabels() {
    labelsHost.textContent = '';
    labels = data.head.ecosystems.map(function (e) {
      var el = document.createElement('div');
      el.className = 'hero-label eco-' + e.id;
      el.innerHTML = '<b><span class="dot"></span>' + e.name + '</b><span></span>';
      labelsHost.appendChild(el);
      return el;
    });
  }

  function layout() {
    W = Math.max(300, stage.clientWidth); H = Math.max(300, stage.clientHeight);
    stickyTop = parseFloat(getComputedStyle(stage).top) || 0;
    narrow = W < 900;
    var level = stats.level;
    dpr = level === 0 ? maxDpr : level === 1 ? Math.max(0.75, Math.min(1, maxDpr * 0.6)) : 0.7;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    var x0, x1, y0, y1, e0;
    if (narrow) {
      x0 = 14; x1 = W - 14;
      y0 = copy.offsetTop + copy.offsetHeight + 26; y1 = H - 58;
      e0 = end.offsetTop + end.offsetHeight + 18;
      e0 = Math.min(Math.max(e0, H * 0.30), y0);
    } else {
      x0 = copy.offsetLeft + copy.offsetWidth + 56; x1 = W - Math.max(36, (W - 1320) / 2 + 36);
      y0 = 34; y1 = H - 64; e0 = y0;
    }
    // s: the scale of the ensembles' layout, so that the rings fit; s1: the brain's
    var cx = (x0 + x1) / 2, s = Math.min((x1 - x0) / (narrow ? 2.05 : 2.5), (y1 - y0) * 0.6, 330);
    gasC = [cx, (y0 + y1) / 2, s];
    var s1 = Math.min((x1 - x0) * 0.47, (y1 - e0) * 0.6, 330);
    brainC = [cx, (e0 + y1) / 2, s1];
    // the five ensembles on an ellipse around the cloud's axis
    var rx = s * (narrow ? 0.78 : 1.0), ry = s * (narrow ? 0.58 : 0.70), blob = s * (narrow ? 0.26 : 0.30);
    clusters = [];
    for (var k = 0; k < N_ECO; k++) {
      // none at the top, so B0 can rise through the middle
      var a = -Math.PI / 2 + (k + 0.5) / N_ECO * 2 * Math.PI;
      var c = [gasC[0] + rx * Math.cos(a), gasC[1] + ry * Math.sin(a), blob];
      clusters.push(c);
      var el = labels[k];
      if (el) { el.style.left = c[0] + 'px'; el.style.top = (c[1] + blob * 0.62 + 8) + 'px'; }
    }
    // B0: the vertical axis everything turns about, through the middle; as
    // the brain forms, the arrow draws back above it
    var brainTop = brainC[1] - brainC[2] * 0.92 - 12;
    var top0 = narrow ? y0 + 30 : Math.max(48, gasC[1] - s * 0.95);
    var top1 = narrow ? Math.max(e0 + 28, brainTop - 64) : Math.max(48, Math.min(top0, brainTop - 96));
    b0geo = { top0: top0, top1: top1, from: gasC[1] + s * 0.28, to: brainTop };
    if (b0) b0.style.left = gasC[0] + 'px';
    placeB0();
  }
  var b0geo = null;
  function placeB0() {
    if (!b0 || !b0geo) return;
    var k = smooth(0.12, 0.62, progress);
    var top = b0geo.top0 + (b0geo.top1 - b0geo.top0) * k;
    var bottom = b0geo.from + (b0geo.to - b0geo.from) * k;
    b0.style.top = top + 'px';
    b0.style.height = Math.max(24, bottom - top) + 'px';
  }

  /* ----------------------------------------------------------- state */
  var running = false, live = false, last = 0, t0 = performance.now(), stepAt = 0;
  var progress = 0, theta = 0, D = 0, rot = -0.62, resonant = false, frame = 0;
  function smooth(a, b, x) { var t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); }
  var stickyTop = 0;   // the header's height: where the stage holds while the hero scrolls
  function target() {
    var travel = hero.offsetHeight - stage.offsetHeight;
    if (travel <= 1) return 0;
    return Math.max(0, Math.min(1, (stickyTop - hero.getBoundingClientRect().top) / travel));
  }
  function convergence(p) { return smooth(0.02, 0.5, p); }
  function lock(p) { return smooth(0.1, 0.62, p); }

  function coherence(L) {
    // the readout: |mean direction| over a sample of spins, as the shader has them
    var n = Math.min(1200, data.n), sx = 0, sy = 0, cx = Math.cos(theta), cy = Math.sin(theta);
    for (var i = 0; i < n; i++) {
      var th = spins.phi0[i] + theta + spins.eps[i] * D;
      var ux = (1 - L) * Math.cos(th) + L * cx, uy = (1 - L) * Math.sin(th) + L * cy;
      var m = Math.hypot(ux, uy) || 1;
      sx += ux / m; sy += uy / m;
    }
    return Math.hypot(sx, sy) / n;
  }

  var scratch = { rot: new Float32Array(4 * N_ECO), clu: new Float32Array(4 * N_ECO) };
  function draw() {
    var p = progress, L = lock(p);
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.clearColor(pal.bg[0], pal.bg[1], pal.bg[2], 1);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.useProgram(prog);
    gl.enable(gl.BLEND);
    gl.blendFuncSeparate(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA, gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    gl.uniform2f(U.uRes, W, H);
    gl.uniform1f(U.uDpr, dpr);
    gl.uniform1f(U.uSize, (narrow ? 1.9 : 2.3) * Math.min(1.2, Math.sqrt(Math.max(1, brainC[2] / 260))));
    gl.uniform1f(U.uP, p);
    gl.uniform1f(U.uTheta, theta);
    gl.uniform1f(U.uD, D);
    gl.uniform1f(U.uLock, L);
    gl.uniform2f(U.uCommon, Math.cos(theta), Math.sin(theta));
    gl.uniform4f(U.uBrainRot, Math.cos(rot), Math.sin(rot), Math.cos(0.30), Math.sin(0.30));
    var gr = scratch.rot;
    for (var k = 0; k < N_ECO; k++) {
      var a = rot * 1.7 + k * 1.3;
      gr[4 * k] = Math.cos(a); gr[4 * k + 1] = Math.sin(a); gr[4 * k + 2] = Math.cos(0.36); gr[4 * k + 3] = Math.sin(0.36);
    }
    gl.uniform4fv(U.uGasRot, gr);
    gl.uniform4f(U.uGasC, gasC[0], gasC[1], gasC[2], 0);
    gl.uniform4f(U.uBrainC, brainC[0], brainC[1], brainC[2], 0);
    var cl = scratch.clu;
    clusters.forEach(function (c, k) { cl[4 * k] = c[0]; cl[4 * k + 1] = c[1]; cl[4 * k + 2] = c[2]; });
    gl.uniform4fv(U.uClu, cl);
    gl.uniform3fv(U.uCol, pal.cols);
    gl.bindVertexArray(vao);
    var count = stats.level >= 3 ? Math.floor(data.n / 4) : stats.level >= 2 ? Math.floor(data.n / 2) : data.n;
    stats.n = count;
    gl.drawArrays(gl.POINTS, 0, count);
    gl.bindVertexArray(null);
  }

  function readout() {
    var p = progress, F = convergence(p);
    var c = coherence(lock(p));
    stats.coherence = c; stats.progress = p;
    stage.style.setProperty('--coh', c.toFixed(3));
    if (hudCoh) hudCoh.textContent = c.toFixed(2);
    if (hudSpread) hudSpread.textContent = '±' + (100 * (1 - F) * spins.sd).toFixed(1) + ' %';
    labels.forEach(function (el, k) {
      el.lastChild.textContent = (1 + (1 - F) * ECO_OFFSET[k]).toFixed(2) + ' ω₀';
    });
  }

  function tick(now) {
    if (!running) return;
    requestAnimationFrame(tick);
    var dt = last ? Math.min(0.05, (now - last) / 1000) : 1 / 60;
    var ms = last ? now - last : 16.7;
    last = now;
    stats.frames++;
    // a slow machine steps down, never back up: resolution first, then spins
    if (!review && stats.frames > 30) {
      stats.avg = stats.avg ? stats.avg * 0.94 + ms * 0.06 : ms;
      if (stats.frames > 90 && stats.avg > 24 && stats.level < 3 && now - stepAt > 2000) {
        stats.level++; stepAt = now; stats.avg = 17;
        if (stats.level === 1 && maxDpr <= 1) stats.level = 2;
        layout();
      }
    }
    var p = target();
    progress = review ? p : progress + (p - progress) * Math.min(1, dt * 7);
    if (Math.abs(p - progress) < 0.0004) progress = p;
    var F = convergence(progress);
    theta = (theta + OMEGA0 * dt) % (2 * Math.PI);
    D += OMEGA0 * (1 - F) * dt;
    rot += 0.10 * dt;
    hero.style.setProperty('--hp', progress.toFixed(4));
    placeB0();
    var r = progress > 0.8;
    if (r !== resonant) { resonant = r; hero.classList.toggle('is-resonant', r); }
    draw();
    if (frame++ % 4 === 0) readout();
  }

  function start() {
    if (running) return;
    running = true; last = 0;
    requestAnimationFrame(tick);
  }
  function stop() { running = false; }
  function setLive(on) {
    live = on;
    hero.classList.toggle('is-live', on);
    stats.mode = on ? 'live' : 'still';
    if (on) { layout(); start(); }
    else { stop(); hero.style.setProperty('--hp', '0'); hero.classList.remove('is-resonant'); resonant = false; }
  }

  /* ------------------------------------------------------------ boot */
  Promise.all([
    load(hero.getAttribute('data-src')),
    document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()
  ]).then(function (res) {
    data = parse(res[0]);
    buffers();
    colours();
    makeLabels();
    setLive(fxOn());
    var visible = true;
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        if (visible && live) start(); else stop();
      }).observe(hero);
    }
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) stop(); else if (visible && live) start();
    });
    document.addEventListener('lx-fx', function (e) { setLive(e.detail.on); });
    new MutationObserver(function () { colours(); }).observe(doc, { attributes: true, attributeFilter: ['data-theme'] });
    var rt;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () { if (live) layout(); }, 120);
    });
    canvas.addEventListener('webglcontextlost', function (e) { e.preventDefault(); setLive(false); stats.mode = 'context-lost'; });
  }).catch(function (e) { stats.mode = 'error'; stats.error = String(e); });
})();
