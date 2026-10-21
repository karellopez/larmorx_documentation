/* LARMORX evidence: the interactive parts of the validation pages.
 *
 * The page is complete without this script: every worked example shows still panels and its
 * metrics, every chart is HTML, every case is in the table. This script reads the same JSON
 * the page was built from (static/evidence/<tool>.json, exported by larmorx_validation) and
 * the images it names (content-addressed blobs: raw values, byte planes, zlib) and adds:
 *
 *   - the image viewer: planes, slices, volumes, zoom and pan, intensity windows, a crosshair
 *     with the exact value of every panel, difference panels on a stated symmetric scale
 *     (linear or log), side by side, swipe, blink and checkerboard, the largest difference;
 *   - the time series of the crosshair's voxel (4D examples);
 *   - the case explorer's search, filters, sorting and deep links (#case=<id>);
 *   - hover details on the charts, and the agreement chart's filter.
 *
 * Values are never rounded for display beyond what is stated: float32 values are printed with
 * the digits that identify them exactly, differences in float64 (exact for float32 inputs).
 * window.LX_EVIDENCE.check() compares every number a page shows with the JSON it came from
 * (tools/review/shoot.mjs --eval runs it in headless Chrome; README.md). Vanilla JavaScript, no
 * dependencies. Apache-2.0, as the site.
 */
(function () {
  'use strict';
  var doc = document, root = doc.documentElement;
  var EV = window.LX_EVIDENCE = { docs: {}, viewers: [] };

  /* ------------------------------------------------------------------ util */
  function el(tag, attrs, kids) {
    var e = doc.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      if (k === 'text') e.textContent = v;
      else if (k === 'html') e.innerHTML = v;
      else if (k.slice(0, 2) === 'on') e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? '' : v);
    });
    (kids || []).forEach(function (c) { if (c) e.appendChild(typeof c === 'string' ? doc.createTextNode(c) : c); });
    return e;
  }
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function dark() { return root.getAttribute('data-theme') === 'dark'; }
  function reduced() { return root.getAttribute('data-fx') === 'off'; }
  var MINUS = '−';
  function sig(x, n) {
    n = n || 3;
    if (x === null || x === undefined || isNaN(x)) return '–';
    if (x === 0) return '0';
    var s = Number(x).toPrecision(n);
    if (s.indexOf('e') >= 0) {
      var p = s.split('e'); var m = p[0];
      if (m.indexOf('.') >= 0) m = m.replace(/0+$/, '').replace(/\.$/, '');
      s = m + 'e' + parseInt(p[1], 10);
    } else if (s.indexOf('.') >= 0) {
      s = s.replace(/0+$/, '').replace(/\.$/, '');
    }
    var a = Math.abs(x);
    if (s.indexOf('e') < 0 && (a >= 1e5 || a < 1e-4)) { // as Python's g format
      s = Number(x).toExponential(n - 1).replace(/\.?0+e/, 'e').replace('e+', 'e');
    }
    return s.replace(/-/g, MINUS);
  }
  function count(n) { return Number(n).toLocaleString('en-US'); }
  /* A float32 value with the fewest digits that identify it. */
  /* The fewest significant digits that give back exactly v (as float32 or float64), in
     positional notation, or in exponent notation below 1e-3 and from 1e7. */
  function shortest(v, max, same) {
    var expo = Math.abs(v) < 1e-3 || Math.abs(v) >= 1e7;
    for (var p = 1; p <= max; p++) {
      var s = expo ? v.toExponential(p - 1) : v.toPrecision(p);
      if (same(parseFloat(s))) return tidy(s);
    }
    return tidy(expo ? v.toExponential(max - 1) : v.toPrecision(max));
  }
  function f32(v) {
    if (v === 0) return Object.is(v, -0) ? MINUS + '0' : '0';
    if (!isFinite(v)) return String(v);
    return shortest(v, 9, function (x) { return Math.fround(x) === v; });
  }
  function f64(v) {
    if (v === 0) return '0';
    if (!isFinite(v)) return String(v);
    return shortest(v, 17, function (x) { return x === v; });
  }
  function tidy(s) {
    if (s.indexOf('e') >= 0) {
      var p = s.split('e'), m = p[0];
      if (m.indexOf('.') >= 0) m = m.replace(/0+$/, '').replace(/\.$/, '');
      s = m + 'e' + parseInt(p[1], 10);
    } else if (s.indexOf('.') >= 0) s = s.replace(/0+$/, '').replace(/\.$/, '');
    return s.replace(/-/g, MINUS);
  }
  function signed(v, fmt) { return (v > 0 ? '+' : '') + fmt(v); }

  function loadDoc(src) {
    if (!EV.docs[src]) EV.docs[src] = fetch(src).then(function (r) {
      if (!r.ok) throw new Error(src + ': ' + r.status);
      return r.json();
    });
    return EV.docs[src];
  }

  /* --------------------------------------------------------------- blobs */
  var DT = {
    f4: { arr: Float32Array, bits: Uint32Array, size: 4 },
    f8: { arr: Float64Array, bits: Uint32Array, size: 8, k: 2 },
    i2: { arr: Int16Array, bits: Uint16Array, size: 2 },
    u2: { arr: Uint16Array, bits: Uint16Array, size: 2 },
    u1: { arr: Uint8Array, bits: Uint8Array, size: 1 },
    i4: { arr: Int32Array, bits: Uint32Array, size: 4 }
  };
  var blobCache = {};
  function fetchBlob(base, name) {
    if (!blobCache[base + name]) blobCache[base + name] = fetch(base + name).then(function (r) {
      if (!r.ok) throw new Error(name + ': ' + r.status);
      if (!window.DecompressionStream) throw new Error('this browser cannot decompress the images');
      return new Response(r.body.pipeThrough(new DecompressionStream('deflate'))).arrayBuffer();
    });
    return blobCache[base + name];
  }
  function unshuffle(buf, size) {
    var b = new Uint8Array(buf);
    if (size === 1) return b.buffer;
    var n = b.length / size, out = new Uint8Array(b.length);
    for (var k = 0; k < size; k++) {
      var off = k * n;
      for (var i = 0; i < n; i++) out[i * size + k] = b[off + i];
    }
    return out.buffer;
  }

  /* An example's arrays, decoded on first use; references resolved recursively. */
  function Store(ex, base) { this.ex = ex; this.base = base; this.memo = {}; this.mask = null; }
  Store.prototype.spec = function (key) {
    var p = key.split(':'), panel = this.ex.panelById[p[0]];
    if (!panel) throw new Error('no panel ' + p[0]);
    var s = panel.arrays[p[1]] || panel.arrays.all;
    if (!s) throw new Error('no array ' + key);
    return s;
  };
  Store.prototype.getMask = function () {
    var self = this;
    if (!this.maskP) this.maskP = fetchBlob(this.base, this.ex.mask.blob).then(function (buf) {
      self.mask = new Uint8Array(unshuffle(buf, 1)); return self.mask;
    });
    return this.maskP;
  };
  Store.prototype.get = function (key) {
    var self = this;
    if (this.memo[key]) return this.memo[key];
    var s = this.spec(key);
    var p;
    if (s.same) p = this.get(s.same);
    else if (s.neg) p = this.get(s.neg).then(function (a) {
      var out = new a.constructor(a.length);
      for (var i = 0; i < a.length; i++) out[i] = -a[i];
      return out;
    });
    else p = Promise.all([fetchBlob(this.base, s.blob), this.ref(s.xor)]).then(function (r) {
      var t = DT[s.dtype];
      var raw = new t.arr(unshuffle(r[0], t.size));
      if (!r[1]) return raw;
      var ref = r[1], x = new t.bits(raw.buffer), rb = new t.bits(ref.buffer, ref.byteOffset, ref.length * (t.k || 1));
      var out = new t.bits(x.length);
      for (var i = 0; i < x.length; i++) out[i] = x[i] ^ rb[i];
      return new t.arr(out.buffer);
    });
    this.memo[key] = p;
    return p;
  };
  /* The reference of an exclusive-or delta: another array, or a float32 quotient of two. */
  Store.prototype.ref = function (r) {
    var self = this;
    if (!r) return Promise.resolve(null);
    if (typeof r === 'string') return this.get(r);
    if (r.div) return Promise.all([this.get(r.div[0]), this.get(r.div[1]), this.getMask()]).then(function (a) {
      var n = a[0], d = a[1], m = a[2], out = new Float32Array(n.length);
      for (var i = 0; i < n.length; i++) out[i] = m[i] ? Math.fround(n[i] / d[i]) : 0;
      return out;
    });
    return Promise.reject(new Error('unknown reference'));
  };

  /* ------------------------------------------------------------- colours */
  var PAL = {
    light: { paper: [240, 235, 224], sunk: [221, 213, 196], neg: [70, 125, 234], pos: [199, 103, 23], cross: '#c76717', ink: '#16130f', ink2: '#4a453e', ink3: '#5b554c', line: 'rgba(22,19,15,0.20)', soft: 'rgba(22,19,15,0.11)', original: '#4a453e', larmorx: '#c76717', replica: '#467dea', input: '#8a847a' },
    dark: { paper: [26, 25, 22], sunk: [42, 40, 36], neg: [88, 144, 250], pos: [217, 117, 48], cross: '#f2b28a', ink: '#efebe2', ink2: '#b6b0a3', ink3: '#908a7f', line: 'rgba(240,235,226,0.20)', soft: 'rgba(240,235,226,0.11)', original: '#b6b0a3', larmorx: '#d97530', replica: '#5890fa', input: '#7d776d' }
  };
  function pal() { return PAL[dark() ? 'dark' : 'light']; }
  function mix(a, b, t) { return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]; }

  /* ---------------------------------------------------------------- planes
   * Display arrays are (x, y, z[, t]) in RAS, x fastest. Neurological convention: the subject's
   * left on the left. Axial: x across, y up (anterior at the top). Coronal: x across, z up.
   * Sagittal: y across (anterior on the left), z up. */
  var PLANES = {
    axial: { slice: 2, u: 0, v: 1, flipU: false, name: 'Axial', marks: ['L', 'R', 'A', 'P'] },
    coronal: { slice: 1, u: 0, v: 2, flipU: false, name: 'Coronal', marks: ['L', 'R', 'S', 'I'] },
    sagittal: { slice: 0, u: 1, v: 2, flipU: true, name: 'Sagittal', marks: ['A', 'P', 'S', 'I'] }
  };

  /* ============================================================== viewer */
  function Viewer(section, d, ex, base) {
    var self = this;
    this.section = section; this.doc = d; this.ex = ex;
    ex.panelById = {}; ex.panels.forEach(function (p) { ex.panelById[p.id] = p; });
    ex.diffById = {}; ex.diffs.forEach(function (x) { ex.diffById[x.id] = x; });
    this.store = new Store(ex, base);
    var g = ex.grid;
    this.shape = g.shape; this.nt = g.volumes || 1; this.sp = g.spacing;
    var def = ex['default'];
    this.s = {
      output: def.output, plane: def.plane, voxel: def.voxel.slice(0, 3), t: def.t || 0,
      zoom: 1, cx: 0.5, cy: 0.5, mode: 'grid', a: def.compare.a, b: def.compare.b, blinkB: false,
      scale: def.scale || 'linear', win: {}, panels: def.panels.slice(), diffs: def.diffs.slice(), swipe: 0.5
    };
    this.cells = {}; this.loaded = {};
    this.build();
    this.store.getMask().then(function () { self.update(); }).catch(function (e) { self.fail(e); });
  }

  Viewer.prototype.output = function () {
    var id = this.s.output;
    return this.ex.outputs.filter(function (o) { return o.id === id; })[0];
  };
  Viewer.prototype.key = function (pid) {
    var p = this.ex.panelById[pid];
    return pid + ':' + (p.arrays[this.s.output] ? this.s.output : 'all');
  };

  Viewer.prototype.fail = function (e) {
    this.status.textContent = 'The images could not be loaded (' + e.message + '); the still views and the metrics remain.';
    this.status.hidden = false;
    this.section.classList.add('ev-failed');
  };

  /* ---------------------------------------------------------- the controls */
  function segmented(label, items, current, onpick) {
    var group = el('div', { class: 'ev-seg', role: 'group', 'aria-label': label });
    items.forEach(function (it) {
      var b = el('button', { type: 'button', 'aria-pressed': String(it.id === current), 'data-id': it.id, text: it.label, title: it.title || null });
      b.addEventListener('click', function () {
        Array.prototype.forEach.call(group.children, function (c) { c.setAttribute('aria-pressed', String(c === b)); });
        onpick(it.id);
      });
      group.appendChild(b);
    });
    return group;
  }
  function field(label, control, cls) {
    return el('label', { class: 'ev-field' + (cls ? ' ' + cls : '') }, [el('span', { class: 'ev-field-label', text: label }), control]);
  }

  Viewer.prototype.build = function () {
    var self = this, ex = this.ex, s = this.s;
    var viewer = this.section.querySelector('.ev-viewer');
    this.viewer = viewer;
    viewer.classList.add('is-live');
    var bar = el('div', { class: 'ev-toolbar' });
    if (ex.outputs.length > 1) bar.appendChild(field('Output', segmented('Output', ex.outputs.map(function (o) { return { id: o.id, label: o.label }; }), s.output, function (id) { s.output = id; self.syncWindow(); self.update(); })));
    bar.appendChild(field('Plane', segmented('Plane', ['axial', 'coronal', 'sagittal'].map(function (p) { return { id: p, label: PLANES[p].name }; }), s.plane, function (id) { s.plane = id; s.zoom = 1; s.cx = s.cy = 0.5; self.layout(); self.update(); })));
    this.sliceInput = el('input', { type: 'range', min: 0, step: 1, 'aria-label': 'Slice' });
    this.sliceInput.addEventListener('input', function () { s.voxel[PLANES[s.plane].slice] = +self.sliceInput.value; self.update(); });
    this.sliceText = el('output', { class: 'ev-num' });
    bar.appendChild(el('div', { class: 'ev-field ev-slider' }, [el('span', { class: 'ev-field-label', text: 'Slice' }), this.sliceInput, this.sliceText]));
    if (this.nt > 1) {
      this.volInput = el('input', { type: 'range', min: 0, max: this.nt - 1, step: 1, value: s.t, 'aria-label': 'Volume' });
      this.volInput.addEventListener('input', function () { s.t = +self.volInput.value; self.update(); });
      this.volText = el('output', { class: 'ev-num' });
      bar.appendChild(el('div', { class: 'ev-field ev-slider' }, [el('span', { class: 'ev-field-label', text: 'Volume' }), this.volInput, this.volText]));
    }
    var bar2 = el('div', { class: 'ev-toolbar ev-toolbar--2' });
    bar2.appendChild(field('Compare', segmented('Compare', [
      { id: 'grid', label: 'Side by side' }, { id: 'swipe', label: 'Swipe' }, { id: 'blink', label: 'Blink' }, { id: 'checker', label: 'Checkerboard' }
    ], s.mode, function (id) { s.mode = id; self.layout(); self.update(); })));
    // the window of the outputs' images
    this.winSelect = el('select', { 'aria-label': 'Intensity window' });
    this.winSelect.addEventListener('change', function () { self.setWindow(self.winSelect.value); });
    this.winLo = el('input', { type: 'number', step: 'any', 'aria-label': 'Window minimum', class: 'ev-numin' });
    this.winHi = el('input', { type: 'number', step: 'any', 'aria-label': 'Window maximum', class: 'ev-numin' });
    [this.winLo, this.winHi].forEach(function (i) { i.addEventListener('change', function () {
      var w = s.win[s.output] || {}; w.lo = +self.winLo.value; w.hi = +self.winHi.value; w.id = 'manual'; s.win[s.output] = w;
      self.winSelect.value = 'manual'; self.update(); }); });
    bar2.appendChild(el('div', { class: 'ev-field ev-window' }, [el('span', { class: 'ev-field-label', text: 'Window' }), this.winSelect, this.winLo, el('span', { class: 'ev-dash', text: '–' }), this.winHi]));
    bar2.appendChild(field('Difference scale', segmented('Difference scale', [{ id: 'linear', label: 'Linear' }, { id: 'log', label: 'Log' }], s.scale, function (id) { s.scale = id; self.update(); })));
    var tools = el('div', { class: 'ev-field ev-actions' });
    this.goSel = el('select', { 'aria-label': 'Difference to locate' });
    ex.diffs.forEach(function (x) { if (!x.metrics[s.output] || !x.metrics[s.output].identical) self.goSel.appendChild(el('option', { value: x.id, text: x.label })); });
    var go = el('button', { type: 'button', class: 'ev-btn', text: 'Go to the largest difference' });
    go.addEventListener('click', function () { self.gotoLargest(self.goSel.value); });
    var zoomIn = el('button', { type: 'button', class: 'ev-btn ev-icon', 'aria-label': 'Zoom in', text: '+' });
    var zoomOut = el('button', { type: 'button', class: 'ev-btn ev-icon', 'aria-label': 'Zoom out', text: MINUS });
    var reset = el('button', { type: 'button', class: 'ev-btn', text: 'Reset view' });
    zoomIn.addEventListener('click', function () { self.zoomBy(1.6); });
    zoomOut.addEventListener('click', function () { self.zoomBy(1 / 1.6); });
    reset.addEventListener('click', function () { s.zoom = 1; s.cx = s.cy = 0.5; var d = ex['default']; s.voxel = d.voxel.slice(0, 3); s.t = d.t || 0; s.plane = d.plane; self.syncControls(); self.layout(); self.update(); });
    if (this.goSel.options.length) { tools.appendChild(this.goSel); tools.appendChild(go); }
    tools.appendChild(zoomOut); tools.appendChild(zoomIn); tools.appendChild(reset);
    bar2.appendChild(tools);
    // A/B for swipe, blink, checkerboard
    this.abBox = el('div', { class: 'ev-toolbar ev-ab', hidden: true });
    this.aSel = el('select', { 'aria-label': 'Image A' }); this.bSel = el('select', { 'aria-label': 'Image B' });
    ex.panels.forEach(function (p) {
      self.aSel.appendChild(el('option', { value: p.id, text: p.label }));
      self.bSel.appendChild(el('option', { value: p.id, text: p.label }));
    });
    this.aSel.value = s.a; this.bSel.value = s.b;
    this.aSel.addEventListener('change', function () { s.a = self.aSel.value; self.update(); });
    this.bSel.addEventListener('change', function () { s.b = self.bSel.value; self.update(); });
    this.blinkBtn = el('button', { type: 'button', class: 'ev-btn', text: 'Show B' });
    this.blinkBtn.addEventListener('click', function () { s.blinkB = !s.blinkB; self.update(); });
    this.abBox.appendChild(field('A', this.aSel)); this.abBox.appendChild(field('B', this.bSel)); this.abBox.appendChild(this.blinkBtn);
    // the panels chooser
    var chooser = el('details', { class: 'ev-chooser' }, [el('summary', { text: 'Panels shown' })]);
    var list = el('div', { class: 'ev-chooser-list' });
    function box(kind, id, label, sub, checked) {
      var i = el('input', { type: 'checkbox', checked: checked });
      i.addEventListener('change', function () {
        var arr = kind === 'p' ? s.panels : s.diffs;
        var at = arr.indexOf(id);
        if (i.checked && at < 0) arr.push(id); else if (!i.checked && at >= 0) arr.splice(at, 1);
        var order = kind === 'p' ? ex.panels.map(function (p) { return p.id; }) : ex.diffs.map(function (x) { return x.id; });
        arr.sort(function (a, b) { return order.indexOf(a) - order.indexOf(b); });
        self.layout(); self.update();
      });
      return el('label', { class: 'ev-check' }, [i, el('span', {}, [label, sub ? el('small', { text: sub }) : null])]);
    }
    list.appendChild(el('p', { class: 'ev-chooser-head', text: 'Images' }));
    ex.panels.forEach(function (p) { list.appendChild(box('p', p.id, p.label, p.sub, s.panels.indexOf(p.id) >= 0)); });
    list.appendChild(el('p', { class: 'ev-chooser-head', text: 'Differences' }));
    ex.diffs.forEach(function (x) { if (x.display) list.appendChild(box('d', x.id, x.label, x.role_label, s.diffs.indexOf(x.id) >= 0)); });
    chooser.appendChild(list);

    this.status = el('p', { class: 'ev-status', role: 'status', hidden: true });
    this.grid = el('div', { class: 'ev-panels ev-live' });
    this.single = el('div', { class: 'ev-single', hidden: true });
    this.colorbar = el('div', { class: 'ev-colorbar' });
    this.readout = el('div', { class: 'ev-readout', 'aria-live': 'polite' });
    var help = el('p', { class: 'ev-help', text: 'Select a point in any panel to move the crosshair; drag to pan when zoomed (Ctrl and the wheel, or two fingers, to zoom). Keys on a focused panel: arrows move the crosshair, Page Up and Page Down change the slice, + and − zoom.' });
    var old = viewer.querySelector('.ev-panels');
    var still = viewer.querySelector('.ev-still');
    viewer.insertBefore(bar, old);
    var more = el('details', { class: 'ev-more' }, [el('summary', { text: 'Compare, window, scale and zoom' }), bar2]);
    more.open = !window.matchMedia('(max-width: 760px)').matches;
    viewer.insertBefore(more, old);
    viewer.insertBefore(this.abBox, old);
    viewer.insertBefore(chooser, old);
    viewer.insertBefore(this.status, old);
    old.replaceWith(this.grid);
    if (still) still.remove();
    viewer.appendChild(this.single);
    viewer.appendChild(this.colorbar);
    viewer.appendChild(help);
    viewer.appendChild(this.readout);
    if (ex.timing) {
      this.series = el('figure', { class: 'ev-chart ev-series' });
      viewer.appendChild(this.series);
    }
    this.syncWindow();
    this.syncControls();
    this.layout();
    var self2 = this;
    new MutationObserver(function () { self2.update(); }).observe(root, { attributes: true, attributeFilter: ['data-theme'] });
    window.addEventListener('resize', function () { self2.update(); });
  };

  Viewer.prototype.syncWindow = function () {
    var self = this, o = this.output(), s = this.s;
    this.winSelect.innerHTML = '';
    o.windows.forEach(function (w) { self.winSelect.appendChild(el('option', { value: w.id, text: w.label })); });
    this.winSelect.appendChild(el('option', { value: 'manual', text: 'manual' }));
    if (!s.win[o.id]) s.win[o.id] = { id: o.windows[0].id, lo: o.windows[0].lo, hi: o.windows[0].hi };
    var w = s.win[o.id], own = w.id === 'own';
    this.winSelect.value = w.id;
    this.winLo.disabled = this.winHi.disabled = own;
    this.winLo.value = own ? '' : +w.lo.toPrecision(6); this.winHi.value = own ? '' : +w.hi.toPrecision(6);
    this.goSel.innerHTML = '';
    this.ex.diffs.forEach(function (x) {
      var m = x.metrics[o.id];
      if (m && !m.identical && x.display && x.display[o.id]) self.goSel.appendChild(el('option', { value: x.id, text: x.label }));
    });
  };
  Viewer.prototype.setWindow = function (id) {
    var o = this.output(), w = o.windows.filter(function (x) { return x.id === id; })[0];
    if (!w) return;
    this.s.win[o.id] = { id: id, lo: w.lo, hi: w.hi };
    var own = id === 'own';
    this.winLo.disabled = this.winHi.disabled = own;
    this.winLo.value = own ? '' : +w.lo.toPrecision(6); this.winHi.value = own ? '' : +w.hi.toPrecision(6);
    this.update();
  };
  Viewer.prototype.syncControls = function () {
    var s = this.s, P = PLANES[s.plane], n = this.shape[P.slice];
    this.sliceInput.max = n - 1; this.sliceInput.value = s.voxel[P.slice];
    this.sliceText.textContent = (s.voxel[P.slice] + 1) + ' of ' + n;
    if (this.volInput) {
      this.volInput.value = s.t;
      var ti = this.ex.grid.t_index;
      this.volText.textContent = ti ? 'file volume ' + ti[s.t] + ' (' + (s.t + 1) + ' of ' + this.nt + ' shown)' : (s.t + 1) + ' of ' + this.nt;
    }
    var segs = this.viewer.querySelectorAll('.ev-seg[aria-label="Plane"] button');
    Array.prototype.forEach.call(segs, function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-id') === s.plane)); });
  };

  /* The panels: one cell per image and per difference (side by side), or one canvas. */
  Viewer.prototype.layout = function () {
    var self = this, s = this.s, ex = this.ex;
    var P = PLANES[s.plane];
    var w = this.shape[P.u] * this.sp[P.u], h = this.shape[P.v] * this.sp[P.v];
    this.aspect = w / h;
    this.grid.innerHTML = ''; this.cells = {};
    this.abBox.hidden = s.mode === 'grid';
    this.blinkBtn.hidden = s.mode !== 'blink';
    this.grid.hidden = s.mode !== 'grid';
    this.single.hidden = s.mode === 'grid';
    if (s.mode === 'grid') {
      s.panels.forEach(function (id) { self.grid.appendChild(self.cell('p', id)); });
      s.diffs.forEach(function (id) { self.grid.appendChild(self.cell('d', id)); });
    } else {
      this.single.innerHTML = '';
      this.single.appendChild(this.cell('ab', 'ab'));
    }
    this.syncControls();
  };

  Viewer.prototype.cell = function (kind, id) {
    var self = this, ex = this.ex, s = this.s;
    var canvas = el('canvas', { tabindex: 0, role: 'img' });
    var box = el('div', { class: 'ev-canvas', style: 'aspect-ratio:' + this.aspect.toFixed(5) }, [canvas]);
    var cap, fig, label;
    if (kind === 'p') {
      var p = ex.panelById[id];
      label = p.label;
      cap = el('figcaption', {}, [el('span', { class: 'ev-role', text: roleLabel(p.role) }), el('span', { class: 'ev-label', text: p.label }), p.sub ? el('span', { class: 'ev-sub', text: p.sub }) : null]);
      fig = el('figure', { class: 'ev-panel role-' + p.role, 'data-panel': id }, [box, cap]);
    } else if (kind === 'd') {
      var x = ex.diffById[id];
      label = x.label;
      this.scaleNote = this.scaleNote || {};
      var sc = el('span', { class: 'ev-sub ev-range' });
      cap = el('figcaption', {}, [el('span', { class: 'ev-role', text: x.role_label }), el('span', { class: 'ev-label', text: x.label }), sc]);
      fig = el('figure', { class: 'ev-panel ev-diff kind-' + x.kind, 'data-diff': id }, [box, cap]);
      fig._range = sc;
    } else {
      label = 'A and B';
      cap = el('figcaption', { class: 'ev-ab-cap' });
      fig = el('figure', { class: 'ev-panel ev-abpanel' }, [box, cap]);
      fig._cap = cap;
      if (s.mode === 'swipe') {
        var handle = el('div', { class: 'ev-swipe', role: 'slider', tabindex: 0, 'aria-label': 'Swipe between A and B', 'aria-valuemin': 0, 'aria-valuemax': 100 });
        box.appendChild(handle);
        fig._handle = handle;
        var drag = function (e) {
          var r = box.getBoundingClientRect();
          s.swipe = clamp((e.clientX - r.left) / r.width, 0, 1); self.update();
        };
        handle.addEventListener('pointerdown', function (e) { e.stopPropagation(); handle.setPointerCapture(e.pointerId); handle.onpointermove = drag; });
        handle.addEventListener('pointerup', function () { handle.onpointermove = null; });
        handle.addEventListener('keydown', function (e) {
          if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') { e.preventDefault(); s.swipe = clamp(s.swipe + (e.key === 'ArrowLeft' ? -0.05 : 0.05), 0, 1); self.update(); }
        });
      }
    }
    canvas.setAttribute('aria-label', label);
    this.bindPointer(canvas, box);
    this.cells[kind + ':' + id] = { kind: kind, id: id, canvas: canvas, fig: fig, box: box };
    return fig;
  };

  function roleLabel(r) {
    return { input: 'Input', original: 'Original program', fmriprep: "fMRIPrep's own output", reference: 'Original, as a reference', larmorx: 'LARMORX' }[r] || r;
  }

  /* ---------------------------------------------------------- interaction */
  Viewer.prototype.bindPointer = function (canvas, box) {
    var self = this, s = this.s, pts = {}, start = null, pinch = null;
    canvas.addEventListener('pointerdown', function (e) {
      canvas.setPointerCapture(e.pointerId);
      pts[e.pointerId] = { x: e.clientX, y: e.clientY };
      var ids = Object.keys(pts);
      if (ids.length === 1) start = { x: e.clientX, y: e.clientY, cx: s.cx, cy: s.cy, moved: false };
      else if (ids.length === 2) { var a = pts[ids[0]], b = pts[ids[1]]; pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), z: s.zoom }; start = null; }
    });
    canvas.addEventListener('pointermove', function (e) {
      if (!pts[e.pointerId]) return;
      pts[e.pointerId] = { x: e.clientX, y: e.clientY };
      var ids = Object.keys(pts);
      if (pinch && ids.length === 2) {
        var a = pts[ids[0]], b = pts[ids[1]];
        s.zoom = clamp(pinch.z * Math.hypot(a.x - b.x, a.y - b.y) / pinch.d, 1, 16); self.update(); return;
      }
      if (!start) return;
      var r = box.getBoundingClientRect();
      var dx = (e.clientX - start.x) / r.width, dy = (e.clientY - start.y) / r.height;
      if (Math.abs(e.clientX - start.x) + Math.abs(e.clientY - start.y) > 4) start.moved = true;
      if (start.moved && s.zoom > 1) { s.cx = clamp(start.cx - dx / s.zoom, 0, 1); s.cy = clamp(start.cy - dy / s.zoom, 0, 1); self.update(); }
    });
    function end(e) {
      if (start && !start.moved && Object.keys(pts).length === 1) self.pick(e, box);
      delete pts[e.pointerId];
      if (Object.keys(pts).length < 2) pinch = null;
      start = null;
    }
    canvas.addEventListener('pointerup', end);
    canvas.addEventListener('pointercancel', function (e) { delete pts[e.pointerId]; start = null; pinch = null; });
    canvas.addEventListener('wheel', function (e) {
      if (!(e.ctrlKey || e.metaKey)) return;
      e.preventDefault(); self.zoomBy(e.deltaY < 0 ? 1.15 : 1 / 1.15);
    }, { passive: false });
    canvas.addEventListener('keydown', function (e) {
      var P = PLANES[s.plane], v = s.voxel, k = e.key, n = self.shape;
      var du = { ArrowLeft: -1, ArrowRight: 1 }[k], dv = { ArrowUp: 1, ArrowDown: -1 }[k];
      if (du) { v[P.u] = clamp(v[P.u] + (P.flipU ? -du : du), 0, n[P.u] - 1); }
      else if (dv) { v[P.v] = clamp(v[P.v] + dv, 0, n[P.v] - 1); }
      else if (k === 'PageUp' || k === ']') v[P.slice] = clamp(v[P.slice] + 1, 0, n[P.slice] - 1);
      else if (k === 'PageDown' || k === '[') v[P.slice] = clamp(v[P.slice] - 1, 0, n[P.slice] - 1);
      else if (k === '+' || k === '=') { self.zoomBy(1.6); e.preventDefault(); return; }
      else if (k === '-') { self.zoomBy(1 / 1.6); e.preventDefault(); return; }
      else return;
      e.preventDefault(); self.syncControls(); self.update();
    });
  };
  Viewer.prototype.zoomBy = function (f) {
    this.s.zoom = clamp(this.s.zoom * f, 1, 16);
    if (this.s.zoom === 1) this.s.cx = this.s.cy = 0.5;
    this.update();
  };
  /* The visible part of the slice, in [0, 1] of its width and height. */
  Viewer.prototype.view = function () {
    var s = this.s, half = 0.5 / s.zoom;
    var cx = clamp(s.cx, half, 1 - half), cy = clamp(s.cy, half, 1 - half);
    s.cx = cx; s.cy = cy;
    return { x0: cx - half, y0: cy - half, w: 2 * half, h: 2 * half };
  };
  Viewer.prototype.pick = function (e, box) {
    var r = box.getBoundingClientRect(), v = this.view(), s = this.s, P = PLANES[s.plane];
    var fx = v.x0 + v.w * (e.clientX - r.left) / r.width, fy = v.y0 + v.h * (e.clientY - r.top) / r.height;
    var nu = this.shape[P.u], nv = this.shape[P.v];
    var cu = clamp(Math.floor(fx * nu), 0, nu - 1), cv = clamp(Math.floor(fy * nv), 0, nv - 1);
    s.voxel[P.u] = P.flipU ? nu - 1 - cu : cu;
    s.voxel[P.v] = nv - 1 - cv;
    this.update();
  };
  Viewer.prototype.gotoLargest = function (id) {
    var x = this.ex.diffById[id], d = x && x.display && x.display[this.s.output];
    if (!d) return;
    this.s.voxel = d.at.slice(0, 3);
    if (d.at.length > 3) this.s.t = d.at[3];
    this.syncControls(); this.update();
    var c = this.cells['d:' + id];
    if (c) c.fig.classList.add('is-flash'), setTimeout(function () { c.fig.classList.remove('is-flash'); }, 900);
  };

  /* ----------------------------------------------------------- rendering */
  Viewer.prototype.index = function (x, y, z, t) {
    var n = this.shape;
    return x + n[0] * (y + n[1] * (z + n[2] * (t || 0)));
  };
  Viewer.prototype.update = function () {
    var self = this;
    if (this.pending) return;
    this.pending = true;
    requestAnimationFrame(function () { self.pending = false; self.render(); });
  };
  Viewer.prototype.needed = function () {
    var s = this.s, keys = {}, self = this;
    if (s.mode === 'grid') {
      s.panels.forEach(function (id) { keys[self.key(id)] = 1; });
      s.diffs.forEach(function (id) { var x = self.ex.diffById[id]; keys[self.key(x.a)] = 1; keys[self.key(x.b)] = 1; });
    } else { keys[this.key(s.a)] = 1; keys[this.key(s.b)] = 1; }
    if (this.ex.timing) this.ex.series.forEach(function (sr) { keys[self.key(sr.panel)] = 1; });
    return Object.keys(keys);
  };
  Viewer.prototype.render = function () {
    var self = this, keys = this.needed();
    var missing = keys.filter(function (k) { return !self.loaded[k]; });
    this.syncControls();
    if (missing.length) {
      this.status.textContent = 'Loading the images…'; this.status.hidden = false;
      Promise.all(missing.map(function (k) { return self.store.get(k).then(function (a) { self.loaded[k] = a; }); }))
        .then(function () { self.status.hidden = true; self.render(); })
        .catch(function (e) { self.fail(e); });
      return;
    }
    var s = this.s;
    if (s.mode === 'grid') {
      Object.keys(this.cells).forEach(function (k) { self.draw(self.cells[k]); });
    } else this.drawAB(this.cells['ab:ab']);
    this.drawColorbar();
    this.drawReadout();
    if (this.series) this.drawSeries();
    if (s.mode === 'blink' && !reduced()) {
      clearTimeout(this.blinkTimer);
      this.blinkTimer = setTimeout(function () { if (s.mode === 'blink' && !reduced()) { s.blinkB = !s.blinkB; self.update(); } }, 750);
    }
  };

  /* The slice of an array as RGBA, at one voxel per pixel. */
  Viewer.prototype.slice = function (fn) {
    var s = this.s, P = PLANES[s.plane], n = this.shape, nu = n[P.u], nv = n[P.v];
    var img = new ImageData(nu, nv), px = img.data, v = s.voxel.slice(), mask = this.store.mask;
    for (var j = 0; j < nv; j++) {
      for (var i = 0; i < nu; i++) {
        v[P.u] = P.flipU ? nu - 1 - i : i; v[P.v] = nv - 1 - j;
        var at = this.index(v[0], v[1], v[2], s.t), m3 = this.index(v[0], v[1], v[2], 0);
        var o = 4 * (j * nu + i);
        if (!mask[m3]) { px[o + 3] = 0; continue; }
        fn(at, px, o);
      }
    }
    return img;
  };
  Viewer.prototype.valueFn = function (key) {
    var a = this.loaded[key], spec = this.store.spec(key);
    var sc = spec.scale === undefined ? 1 : spec.scale, ic = spec.inter || 0;
    return function (i) { return a[i] * sc + ic; };
  };
  Viewer.prototype.gray = function (pid) {
    var key = this.key(pid), val = this.valueFn(key), p = this.ex.panelById[pid];
    var w = p.window ? { lo: p.window[0], hi: p.window[1] } : this.s.win[this.s.output];
    if (!p.window && w.id === 'own' && p.own && p.own[this.s.output]) w = { lo: p.own[this.s.output][0], hi: p.own[this.s.output][1] };
    var lo = w.lo, k = 255 / ((w.hi - w.lo) || 1);
    return this.slice(function (i, px, o) {
      var g = clamp((val(i) - lo) * k, 0, 255);
      px[o] = px[o + 1] = px[o + 2] = g; px[o + 3] = 255;
    });
  };
  Viewer.prototype.diffRange = function (ids) {
    var o = this.s.output, self = this, m = 0;
    ids.forEach(function (id) { var d = self.ex.diffById[id].display; if (d && d[o]) m = Math.max(m, d[o].max_abs); });
    return m;
  };
  Viewer.prototype.diffImg = function (did, range) {
    var x = this.ex.diffById[did], va = this.valueFn(this.key(x.a)), vb = this.valueFn(this.key(x.b));
    var P = pal(), log = this.s.scale === 'log', lo = range * 1e-6;
    var L = Math.log(range / lo), self = this;
    this.sliceDiffer = 0;
    return this.slice(function (i, px, o) {
      var dv = va(i) - vb(i), t = 0;
      if (dv !== 0) self.sliceDiffer++;
      if (dv !== 0 && range > 0) {
        var a = Math.abs(dv);
        t = log ? Math.max(0.12, a <= lo ? 0 : Math.log(a / lo) / L) : Math.min(1, a / range);
        if (!log) t = Math.max(t, 0.12);
      }
      var c = mix(P.paper, dv < 0 ? P.neg : P.pos, Math.min(1, t));
      px[o] = c[0]; px[o + 1] = c[1]; px[o + 2] = c[2]; px[o + 3] = 255;
    });
  };
  Viewer.prototype.paint = function (canvas, box, imgs, mode) {
    var r = box.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
    var W = Math.max(1, Math.round(r.width * dpr)), H = Math.max(1, Math.round(r.height * dpr));
    if (canvas.width !== W || canvas.height !== H) { canvas.width = W; canvas.height = H; }
    var ctx = canvas.getContext('2d'), v = this.view();
    ctx.clearRect(0, 0, W, H);
    var img0 = imgs[0], nu = img0.width, nv = img0.height;
    var pxPerVox = W / (nu * v.w);
    ctx.imageSmoothingEnabled = pxPerVox < 3;
    var self = this;
    imgs.forEach(function (img, k) {
      var off = self._off || (self._off = doc.createElement('canvas'));
      off.width = nu; off.height = nv;
      off.getContext('2d').putImageData(img, 0, 0);
      ctx.save();
      if (mode === 'swipe') { ctx.beginPath(); var sx = self.s.swipe * W; if (k === 0) ctx.rect(0, 0, sx, H); else ctx.rect(sx, 0, W - sx, H); ctx.clip(); }
      if (mode === 'checker' && k === 1) {
        ctx.beginPath();
        var tile = 8, tw = W / (nu * v.w) * tile, th = H / (nv * v.h) * tile;
        var ox = -v.x0 * nu / tile * tw, oy = -v.y0 * nv / tile * th;
        for (var ty = 0; ty * th + oy < H; ty++) for (var tx = 0; tx * tw + ox < W; tx++) if ((tx + ty) % 2) ctx.rect(ox + tx * tw, oy + ty * th, tw + 0.5, th + 0.5);
        ctx.clip();
      }
      ctx.drawImage(off, v.x0 * nu, v.y0 * nv, v.w * nu, v.h * nv, 0, 0, W, H);
      ctx.restore();
    });
    this.crosshair(ctx, W, H, v, nu, nv, dpr);
    if (mode === 'swipe') {
      ctx.fillStyle = pal().ink; ctx.fillRect(this.s.swipe * W - dpr / 2, 0, dpr, H);
    }
  };
  Viewer.prototype.crosshair = function (ctx, W, H, v, nu, nv, dpr) {
    var s = this.s, P = PLANES[s.plane];
    var cu = P.flipU ? nu - 1 - s.voxel[P.u] : s.voxel[P.u], cv = nv - 1 - s.voxel[P.v];
    var x = ((cu + 0.5) / nu - v.x0) / v.w * W, y = ((cv + 0.5) / nv - v.y0) / v.h * H;
    var gap = 6 * dpr;
    ctx.save();
    ctx.lineWidth = 3 * dpr; ctx.strokeStyle = 'rgba(' + pal().paper.join(',') + ',0.75)';
    var segs = [[0, y, x - gap, y], [x + gap, y, W, y], [x, 0, x, y - gap], [x, y + gap, x, H]];
    segs.forEach(function (sg) { ctx.beginPath(); ctx.moveTo(sg[0], sg[1]); ctx.lineTo(sg[2], sg[3]); ctx.stroke(); });
    ctx.lineWidth = 1 * dpr; ctx.strokeStyle = pal().cross;
    segs.forEach(function (sg) { ctx.beginPath(); ctx.moveTo(sg[0], sg[1]); ctx.lineTo(sg[2], sg[3]); ctx.stroke(); });
    ctx.restore();
    // orientation marks
    ctx.save();
    ctx.font = (11 * dpr) + 'px "JetBrains Mono", monospace'; ctx.textBaseline = 'middle';
    ctx.lineWidth = 3 * dpr; ctx.strokeStyle = 'rgba(' + pal().sunk.join(',') + ',0.9)'; ctx.fillStyle = pal().ink2;
    var m = P.marks, pad = 6 * dpr;
    var mark = function (t, x, y) { ctx.strokeText(t, x, y); ctx.fillText(t, x, y); };
    if (v.w === 1) {
      ctx.textAlign = 'left'; mark(m[0], pad, H / 2);
      ctx.textAlign = 'right'; mark(m[1], W - pad, H / 2);
      ctx.textAlign = 'center'; ctx.textBaseline = 'top'; mark(m[2], W / 2, pad);
      ctx.textBaseline = 'bottom'; mark(m[3], W / 2, H - pad);
    }
    ctx.restore();
  };
  Viewer.prototype.draw = function (c) {
    var s = this.s, o = s.output;
    if (c.kind === 'p') { this.paint(c.canvas, c.box, [this.gray(c.id)]); return; }
    var x = this.ex.diffById[c.id], m = x.metrics[o];
    var range = this.diffRange(this.sharedScale(c.id));
    var ident = m && m.identical;
    var note = c.box.querySelector('.ev-identical');
    if (ident) {
      if (!note) {
        note = el('p', { class: 'ev-identical' }, [el('b', { text: 'Bit-identical' }), el('span', { text: count(m.voxels) + ' of ' + count(m.voxels) + ' values equal' })]);
        c.box.appendChild(note);
      }
    } else if (note) note.remove();
    this.paint(c.canvas, c.box, [this.diffImg(c.id, range || 1)]);
    var n = this.sliceDiffer;
    c.fig._range.textContent = ident ? 'every value equal' : 'scale ±' + sig(range) + (s.scale === 'log' ? ', log' : '') +
      ' · ' + (n ? count(n) + ' differing voxel' + (n === 1 ? '' : 's') : 'none differs') + ' in this slice';
  };
  /* Differences shown next to each other share one scale: larmorx's against the original's
     own variability on the same footing. */
  Viewer.prototype.sharedScale = function (id) {
    var self = this, o = this.s.output;
    var shown = this.s.diffs.filter(function (d) { var m = self.ex.diffById[d].metrics[o]; return m && !m.identical; });
    return shown.indexOf(id) >= 0 ? shown : [id];
  };
  Viewer.prototype.drawAB = function (c) {
    var s = this.s, a = this.gray(s.a), b = this.gray(s.b), A = this.ex.panelById[s.a], B = this.ex.panelById[s.b];
    if (s.mode === 'blink') {
      this.paint(c.canvas, c.box, [s.blinkB ? b : a]);
      c.fig._cap.textContent = 'Showing ' + (s.blinkB ? 'B: ' + B.label : 'A: ' + A.label) + (reduced() ? ' (effects are off: switch with the button)' : '');
      this.blinkBtn.textContent = s.blinkB ? 'Show A' : 'Show B';
    } else {
      this.paint(c.canvas, c.box, [a, b], s.mode);
      if (c.fig._handle) { c.fig._handle.style.left = (100 * s.swipe) + '%'; c.fig._handle.setAttribute('aria-valuenow', Math.round(100 * s.swipe)); }
      c.fig._cap.textContent = (s.mode === 'swipe' ? 'Left: A, ' + A.label + ' · right: B, ' + B.label : 'Checkerboard of A, ' + A.label + ', and B, ' + B.label);
    }
  };
  Viewer.prototype.drawColorbar = function () {
    var s = this.s, o = s.output, self = this;
    var shown = s.mode === 'grid' ? s.diffs.filter(function (d) { var m = self.ex.diffById[d].metrics[o]; return m && !m.identical; }) : [];
    if (!shown.length) { this.colorbar.hidden = true; return; }
    this.colorbar.hidden = false;
    var r = this.diffRange(shown), P = pal();
    var grad = 'linear-gradient(90deg, rgb(' + P.neg.join(',') + '), rgb(' + P.paper.join(',') + ') 50%, rgb(' + P.pos.join(',') + '))';
    var unit = this.output().unit ? ' ' + this.output().unit : '';
    this.colorbar.innerHTML = '';
    this.colorbar.appendChild(el('span', { class: 'ev-cb-l', text: MINUS + sig(r) }));
    this.colorbar.appendChild(el('span', { class: 'ev-cb-bar', style: 'background:' + grad }));
    this.colorbar.appendChild(el('span', { class: 'ev-cb-r', text: '+' + sig(r) + unit }));
    this.colorbar.appendChild(el('span', { class: 'ev-cb-note', text: 'Differences, A − B, on one symmetric scale: ± the largest |Δ| of the shown differences inside the displayed brain' + (s.scale === 'log' ? '; log scale over six decades below it' : '') + '. Any non-zero difference is tinted; zero is the paper.' }));
  };

  /* The crosshair's voxel: its coordinates and the exact value of every panel there. */
  Viewer.prototype.drawReadout = function () {
    var self = this, s = this.s, ex = this.ex, v = s.voxel;
    var A = ex.grid.to_file, F = ex.grid.affine;
    var fi = [0, 1, 2].map(function (r) { return A[r][0] * v[0] + A[r][1] * v[1] + A[r][2] * v[2] + A[r][3]; });
    var mm = [0, 1, 2].map(function (r) { return F[r][0] * v[0] + F[r][1] * v[1] + F[r][2] * v[2] + F[r][3]; });
    var at = this.index(v[0], v[1], v[2], s.t);
    var inMask = this.store.mask[this.index(v[0], v[1], v[2], 0)];
    var tf = ex.grid.t_index ? ex.grid.t_index[s.t] : s.t;
    var where = 'Voxel ' + fi.join(', ') + (this.nt > 1 ? ', volume ' + tf : '') + ' of the file · ' + mm.map(function (x) { return sig(x, 4); }).join(', ') + ' mm';
    var rows = [];
    var panels = s.mode === 'grid' ? s.panels : [s.a, s.b];
    var labels = panels.map(function (id) { return ex.panelById[id].label; });
    panels.forEach(function (id) {
      var p = ex.panelById[id], key = self.key(id), a = self.loaded[key];
      var name = labels.filter(function (l) { return l === p.label; }).length > 1 && p.sub ? p.label + ', ' + p.sub : p.label;
      if (!a) return;
      var spec = self.store.spec(key), raw = a[at];
      var val = spec.scale === undefined ? raw : raw * spec.scale + (spec.inter || 0);
      var txt = spec.dtype === 'f4' ? f32(raw) : spec.dtype === 'f8' ? f64(raw) : (spec.scale !== undefined ? count(raw) + ' × ' + f32(Math.fround(spec.scale)) + ' = ' + f64(val) : count(raw));
      rows.push(el('tr', {}, [el('th', { scope: 'row', text: name }), el('td', { class: 'n', 'data-raw': String(raw), text: inMask ? txt : '(outside the shown brain)' })]));
    });
    if (s.mode === 'grid') s.diffs.forEach(function (id) {
      var x = ex.diffById[id], va = self.valueFn(self.key(x.a)), vb = self.valueFn(self.key(x.b));
      var dv = va(at) - vb(at);
      rows.push(el('tr', { class: 'is-diff' }, [el('th', { scope: 'row', text: x.label }), el('td', { class: 'n', text: inMask ? (dv === 0 ? '0 (equal)' : signed(dv, f64)) : '' })]));
    });
    this.readout.innerHTML = '';
    this.readout.appendChild(el('p', { class: 'ev-where', text: where }));
    this.readout.appendChild(el('table', {}, [el('tbody', {}, rows)]));
  };

  /* ----------------------------------------------- the time series (4D) */
  Viewer.prototype.drawSeries = function () {
    var self = this, s = this.s, ex = this.ex, tm = ex.timing, v = s.voxel, P = pal();
    var fig = this.series;
    var W = Math.max(280, fig.clientWidth || 600), narrow = W < 520;
    var H = narrow ? 250 : 280, ml = narrow ? 58 : 70, mr = 12, mt = 16, mb = 38;
    var z = v[2], st = tm.slice_times[z];
    var series = ex.series.map(function (sr) {
      var val = self.valueFn(self.key(sr.panel));
      var ys = [];
      for (var t = 0; t < self.nt; t++) ys.push(val(self.index(v[0], v[1], v[2], t)));
      return { sr: sr, ys: ys, t0: sr.acquired ? st : tm.tzero };
    });
    var all = [].concat.apply([], series.map(function (x) { return x.ys; }));
    var lo = Math.min.apply(null, all), hi = Math.max.apply(null, all);
    if (lo === hi) { lo -= 1; hi += 1; }
    var padv = (hi - lo) * 0.08; lo -= padv; hi += padv;
    var tmax = (this.nt - 1) * tm.tr + Math.max(tm.tzero, st) + 0.5;
    var X = function (t) { return ml + (W - ml - mr) * t / tmax; }, Y = function (y) { return mt + (H - mt - mb) * (1 - (y - lo) / (hi - lo)); };
    var NS = 'http://www.w3.org/2000/svg';
    function S(tag, a) { var e = doc.createElementNS(NS, tag); Object.keys(a || {}).forEach(function (k) { e.setAttribute(k, a[k]); }); return e; }
    var svg = S('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, role: 'img', 'aria-label': 'The time series of voxel ' + v.join(', ') });
    // grid and axes
    var yt = niceTicks(lo, hi, 4);
    yt.forEach(function (y) {
      svg.appendChild(S('line', { x1: ml, x2: W - mr, y1: Y(y), y2: Y(y), stroke: P.soft }));
      var tx = S('text', { x: ml - 6, y: Y(y) + 4, 'text-anchor': 'end', class: 'ev-tick' }); tx.textContent = tick(y); svg.appendChild(tx);
    });
    niceTicks(0, tmax, narrow ? 4 : 8).forEach(function (t) {
      if (t > tmax) return;
      var tx = S('text', { x: X(t), y: H - mb + 16, 'text-anchor': 'middle', class: 'ev-tick' }); tx.textContent = sig(t, 3); svg.appendChild(tx);
    });
    var xl = S('text', { x: (ml + W - mr) / 2, y: H - 6, 'text-anchor': 'middle', class: 'ev-axis' }); xl.textContent = 'time (s)'; svg.appendChild(xl);
    var yl = S('text', { x: 12, y: (mt + H - mb) / 2, 'text-anchor': 'middle', class: 'ev-axis', transform: 'rotate(-90 12 ' + ((mt + H - mb) / 2) + ')' }); yl.textContent = 'signal'; svg.appendChild(yl);
    // the current volume
    var tc = s.t * tm.tr;
    svg.appendChild(S('line', { x1: X(tc + tm.tzero), x2: X(tc + tm.tzero), y1: mt, y2: H - mb, stroke: P.line, 'stroke-dasharray': '2 3' }));
    series.forEach(function (x) {
      var col = P[x.sr.color] || P.ink, pts = x.ys.map(function (y, t) { return X(t * tm.tr + x.t0).toFixed(1) + ',' + Y(y).toFixed(1); });
      svg.appendChild(S('polyline', { points: pts.join(' '), fill: 'none', stroke: col, 'stroke-width': x.sr.width || 1.5, 'stroke-linejoin': 'round', 'stroke-dasharray': x.sr.dash || '' }));
      if (x.sr.marker) x.ys.forEach(function (y, t) {
        var cx = X(t * tm.tr + x.t0), cy = Y(y);
        if (x.sr.marker === 'x') { var r = 3; svg.appendChild(S('path', { d: 'M' + (cx - r) + ' ' + (cy - r) + 'l' + 2 * r + ' ' + 2 * r + 'm0 ' + (-2 * r) + 'l' + (-2 * r) + ' ' + 2 * r, stroke: col, 'stroke-width': 1.3 })); }
        else svg.appendChild(S('circle', { cx: cx, cy: cy, r: x.sr.marker === 'ring' ? 3.6 : 2.4, fill: x.sr.marker === 'ring' ? 'none' : col, stroke: x.sr.marker === 'ring' ? col : 'none', 'stroke-width': 1.2 }));
      });
    });
    // the differences from the original program, per volume
    var ref = ex.series.filter(function (sr) { return sr.reference; })[0];
    var diffs = [];
    if (ref) {
      var rv = series[ex.series.indexOf(ref)].ys;
      series.forEach(function (x) {
        if (!x.sr.compare) return;
        var n = 0, mx = 0;
        x.ys.forEach(function (y, t) { var dd = y - rv[t]; if (dd !== 0) { n++; mx = Math.max(mx, Math.abs(dd)); } });
        diffs.push(x.sr.label + ': ' + (n ? n + ' of ' + self.nt + ' volumes differ at this voxel, by up to ' + tick(mx) : 'identical in every volume at this voxel'));
      });
    }
    // the differences from the reference, volume by volume, on their own symmetric scale
    var strip = null;
    if (ref) {
      var rv2 = series[ex.series.indexOf(ref)].ys, comp = series.filter(function (x) { return x.sr.compare; });
      var M = 0;
      comp.forEach(function (x) { x.ys.forEach(function (y, t) { M = Math.max(M, Math.abs(y - rv2[t])); }); });
      var h2 = 92, mt2 = 14, mb2 = 22;
      strip = S('svg', { viewBox: '0 0 ' + W + ' ' + h2, width: W, height: h2, role: 'img', 'aria-label': 'Differences from ' + ref.label + ', per volume' });
      var Y2 = function (dv) { return mt2 + (h2 - mt2 - mb2) * (1 - (M ? (dv / M + 1) / 2 : 0.5)); };
      strip.appendChild(S('line', { x1: ml, x2: W - mr, y1: Y2(0), y2: Y2(0), stroke: P.line }));
      var lab = S('text', { x: ml - 6, y: Y2(0) + 4, 'text-anchor': 'end', class: 'ev-tick' }); lab.textContent = '0'; strip.appendChild(lab);
      if (M) {
        [M, -M].forEach(function (yv) {
          var tl = S('text', { x: ml - 6, y: Y2(yv) + 4, 'text-anchor': 'end', class: 'ev-tick' }); tl.textContent = (yv > 0 ? '+' : '') + tick(yv); strip.appendChild(tl);
          strip.appendChild(S('line', { x1: ml, x2: W - mr, y1: Y2(yv), y2: Y2(yv), stroke: P.soft }));
        });
      }
      comp.forEach(function (x, ci) {
        var col = P[x.sr.color] || P.ink, off = (ci - (comp.length - 1) / 2) * 3;
        x.ys.forEach(function (y, t) {
          var dv = y - rv2[t], cx = X(t * tm.tr + tm.tzero) + off;
          if (dv === 0) { strip.appendChild(S('circle', { cx: cx, cy: Y2(0), r: 1.3, fill: col })); return; }
          strip.appendChild(S('line', { x1: cx, x2: cx, y1: Y2(0), y2: Y2(dv), stroke: col, 'stroke-width': 2 }));
          strip.appendChild(S('circle', { cx: cx, cy: Y2(dv), r: 3, fill: col }));
        });
      });
      var cap2 = S('text', { x: ml, y: h2 - 4, class: 'ev-axis' });
      cap2.textContent = M ? 'difference from ' + ref.label + ', per volume (scale ±' + tick(M) + ')' : 'difference from ' + ref.label + ': none, in any volume';
      strip.appendChild(cap2);
    }
    fig.innerHTML = '';
    var key = el('ul', { class: 'ev-series-key' }, ex.series.map(function (sr) {
      return el('li', {}, [el('i', { class: 'mk-' + (sr.marker || 'line'), style: '--c:' + (P[sr.color] || P.ink) }), sr.label]);
    }));
    fig.appendChild(el('figcaption', { class: 'ev-chart-title', text: 'The crosshair’s voxel over time: slice ' + (ex.grid.to_file ? '' : '') + 'acquired ' + sig(st, 3) + ' s into each TR, shifted to ' + sig(tm.tzero, 3) + ' s' }));
    fig.appendChild(key);
    fig.appendChild(svg);
    if (strip) fig.appendChild(strip);
    fig.appendChild(el('p', { class: 'ev-chart-note', text: diffs.join(' · ') }));
  };
  function tick(y) {
    return Math.abs(y) >= 1e4 ? Math.round(y).toLocaleString('en-US').replace(/-/g, MINUS) : sig(y, 4);
  }
  function niceTicks(lo, hi, n) {
    var span = hi - lo, step = Math.pow(10, Math.floor(Math.log10(span / n)));
    [1, 2, 2.5, 5, 10].some(function (m) { if (span / (step * m) <= n) { step *= m; return true; } return false; });
    var out = [], t = Math.ceil(lo / step) * step;
    for (; t <= hi + 1e-9; t += step) out.push(+t.toPrecision(12));
    return out;
  }

  /* ========================================================= line charts
   * Panels of lines over one x axis (e.g. a run's motion parameters over its volumes), redrawn
   * to the column's width; the pointer reads every series' value at one x. */
  function Lines(fig, spec) {
    this.fig = fig; this.spec = spec; this.at = null;
    var self = this;
    this.box = fig.querySelector('.ev-lines-panels');
    this.read = el('p', { class: 'ev-lines-read', 'aria-live': 'polite' });
    this.box.after(this.read);
    this.draw();
    window.addEventListener('resize', function () { self.draw(); });
    new MutationObserver(function () { self.draw(); }).observe(root, { attributes: true, attributeFilter: ['data-theme'] });
  }
  Lines.prototype.draw = function () {
    var self = this, spec = this.spec, P = pal();
    var W = Math.max(280, this.box.clientWidth || 600), narrow = W < 520;
    var H = narrow ? 96 : 104, ml = narrow ? 50 : 62, mr = 8, mt = 18, mb = 6;
    var xs = spec.x, x0 = xs[0], x1 = xs[xs.length - 1];
    var NS = 'http://www.w3.org/2000/svg';
    function S(tag, a) { var e = doc.createElementNS(NS, tag); Object.keys(a || {}).forEach(function (k) { e.setAttribute(k, a[k]); }); return e; }
    function X(v) { return ml + (W - ml - mr) * (v - x0) / ((x1 - x0) || 1); }
    var colour = { original: P.original, larmorx: P.larmorx, replica: P.replica, input: P.input, band: P.replica };
    this.box.innerHTML = '';
    this.cursors = [];
    spec.panels.forEach(function (p, pi) {
      var ys = [];
      p.series.forEach(function (sr) { sr.y.forEach(function (v) { if (v !== null) ys.push(v); }); });
      (p.bands || []).forEach(function (b) { ys = ys.concat(b.lo, b.hi); });
      var lo = Math.min.apply(null, ys), hi = Math.max.apply(null, ys);
      if (lo === hi) { lo -= 1; hi += 1; }
      var pad = (hi - lo) * 0.06, y0 = lo - pad, y1 = hi + pad;
      function Y(v) { return mt + (H - mt - mb) * (1 - (v - y0) / (y1 - y0)); }
      var svg = S('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, role: 'img', 'aria-label': p.label, class: 'ev-lines-svg' });
      (p.bands || []).forEach(function (b) {
        var pts = xs.map(function (x, i) { return X(x).toFixed(1) + ',' + Y(b.hi[i]).toFixed(1); });
        for (var i = xs.length - 1; i >= 0; i--) pts.push(X(xs[i]).toFixed(1) + ',' + Y(b.lo[i]).toFixed(1));
        svg.appendChild(S('polygon', { points: pts.join(' '), class: 'ln-band ln-' + b.mark }));
      });
      if (y0 < 0 && y1 > 0) svg.appendChild(S('line', { x1: ml, x2: W - mr, y1: Y(0), y2: Y(0), class: 'ln-zero' }));
      p.series.forEach(function (sr) {
        var pts = [];
        sr.y.forEach(function (v, i) { if (v !== null) pts.push(X(xs[i]).toFixed(1) + ',' + Y(v).toFixed(1)); });
        svg.appendChild(S('polyline', { points: pts.join(' '), class: 'ln ln-' + sr.mark, stroke: colour[sr.mark] || P.ink }));
      });
      var lab = S('text', { x: ml, y: 12, class: 'ln-label' }); lab.textContent = p.label; svg.appendChild(lab);
      [hi, lo].forEach(function (v) { var t = S('text', { x: ml - 6, y: Y(v) + 4, 'text-anchor': 'end', class: 'ln-tick' }); t.textContent = sig(v, 3); svg.appendChild(t); });
      var cur = S('line', { x1: ml, x2: ml, y1: mt, y2: H - mb, class: 'ln-cursor', visibility: 'hidden' });
      svg.appendChild(cur); self.cursors.push(cur);
      svg.addEventListener('pointermove', function (e) {
        var r = svg.getBoundingClientRect(), fx = (e.clientX - r.left) * W / r.width;
        var v = x0 + (fx - ml) / (W - ml - mr) * (x1 - x0), best = 0;
        xs.forEach(function (x, i) { if (Math.abs(x - v) < Math.abs(xs[best] - v)) best = i; });
        self.pick(best);
      });
      self.box.appendChild(svg);
    });
    var ax = S('svg', { viewBox: '0 0 ' + W + ' 26', width: W, height: 26, class: 'ev-lines-svg' });
    niceTicks(x0, x1, narrow ? 4 : 8).forEach(function (t) {
      if (t < x0 || t > x1) return;
      var tx = S('text', { x: X(t), y: 12, 'text-anchor': 'middle', class: 'ln-tick' }); tx.textContent = sig(t, 4); ax.appendChild(tx);
    });
    var xl = S('text', { x: (ml + W - mr) / 2, y: 24, 'text-anchor': 'middle', class: 'ln-axis' }); xl.textContent = spec.x_label; ax.appendChild(xl);
    this.box.appendChild(ax);
    this.X = X;
    if (this.at !== null) this.pick(this.at);
  };
  Lines.prototype.pick = function (i) {
    var spec = this.spec, X = this.X, x = X(spec.x[i]);
    this.at = i;
    this.cursors.forEach(function (c) { c.setAttribute('x1', x); c.setAttribute('x2', x); c.setAttribute('visibility', 'visible'); });
    var parts = [spec.x_label + ' ' + spec.x[i]];
    spec.panels.forEach(function (p) {
      parts.push(p.label + ': ' + p.series.map(function (sr) { return sr.label + ' ' + (sr.y[i] === null ? '–' : sig(sr.y[i], 4)); }).join(', '));
    });
    this.read.textContent = parts.join(' · ');
  };

  /* ======================================================= case explorer */
  function Explorer(box) {
    var self = this;
    this.box = box; this.tbody = box.querySelector('tbody');
    this.rows = Array.prototype.slice.call(this.tbody.rows);
    this.impls = (box.getAttribute('data-impls') || '').split(',');
    this.f = { q: '', category: '', verdict: '', impl: this.impls[0] };
    var cats = uniq(this.rows.map(function (r) { return r.getAttribute('data-category'); }));
    var verdicts = uniq([].concat.apply([], this.rows.map(function (r) { return self.impls.map(function (i) { return r.getAttribute('data-v-' + i); }); })).filter(Boolean));
    var q = el('input', { type: 'search', placeholder: 'Search cases, options, reasons', 'aria-label': 'Search the cases' });
    q.addEventListener('input', function () { self.f.q = q.value.trim().toLowerCase(); self.apply(); });
    var cat = el('select', { 'aria-label': 'Category' }, [el('option', { value: '', text: 'every category' })].concat(cats.map(function (c) { return el('option', { value: c, text: c }); })));
    cat.addEventListener('change', function () { self.f.category = cat.value; self.apply(); });
    var labels = {};
    box.querySelectorAll('.verdict').forEach(function (v) { var m = v.className.match(/v-([\w-]+)/); if (m) labels[m[1]] = v.textContent; });
    var ver = el('select', { 'aria-label': 'Verdict' }, [el('option', { value: '', text: 'every verdict' })].concat(verdicts.map(function (v) { return el('option', { value: v, text: labels[v] || v }); })));
    ver.addEventListener('change', function () { self.f.verdict = ver.value; self.apply(); });
    var impl = null;
    if (this.impls.length > 1) {
      impl = el('select', { 'aria-label': 'Verdict of' }, this.impls.map(function (i, k) {
        var th = box.querySelector('th[data-sort="v-' + i + '"]');
        return el('option', { value: i, text: 'verdict of the ' + (th ? th.textContent : i) });
      }));
      impl.addEventListener('change', function () { self.f.impl = impl.value; self.apply(); });
    }
    this.counter = el('p', { class: 'ev-cases-count', 'aria-live': 'polite' });
    this.more = el('button', { type: 'button', class: 'ev-btn', text: 'Show every case' });
    this.more.addEventListener('click', function () { self.all = true; self.apply(); });
    this.controls = { q: q, cat: cat, ver: ver, impl: impl };
    var bar = el('div', { class: 'ev-cases-bar' }, [q, cat, impl, ver]);
    var old = box.querySelector('.ev-cases-count');
    old.replaceWith(bar);
    bar.after(this.counter);
    box.appendChild(this.more);
    box.querySelectorAll('th[data-sort]').forEach(function (th) {
      var b = el('button', { type: 'button', class: 'ev-sort', text: th.textContent });
      th.textContent = ''; th.appendChild(b); th.setAttribute('aria-sort', 'none');
      b.addEventListener('click', function () { self.sort(th); });
    });
    this.apply();
    window.addEventListener('hashchange', function () { self.fromHash(); });
    this.fromHash();
  }
  function uniq(a) { return a.filter(function (x, i) { return a.indexOf(x) === i; }); }
  Explorer.prototype.set = function (f) {
    var c = this.controls;
    if ('category' in f) { this.f.category = f.category; c.cat.value = f.category; }
    if ('verdict' in f) { this.f.verdict = f.verdict; c.ver.value = f.verdict; }
    if (f.impl && c.impl) { this.f.impl = f.impl; c.impl.value = f.impl; }
    this.all = true; this.apply();
  };
  Explorer.prototype.apply = function () {
    var f = this.f, shown = 0, limit = this.all ? Infinity : 20, total = 0;
    this.rows.forEach(function (r) {
      var ok = (!f.category || r.getAttribute('data-category') === f.category) &&
        (!f.verdict || r.getAttribute('data-v-' + f.impl) === f.verdict) &&
        (!f.q || r.textContent.toLowerCase().indexOf(f.q) >= 0);
      if (ok) total++;
      var show = ok && shown < limit;
      if (show) shown++;
      r.hidden = !show;
    });
    this.counter.textContent = 'Showing ' + shown + ' of ' + total + (total === this.rows.length ? ' cases' : ' matching cases (' + this.rows.length + ' in all)');
    this.more.hidden = shown >= total;
  };
  Explorer.prototype.sort = function (th) {
    var key = th.getAttribute('data-sort'), dir = th.getAttribute('aria-sort') === 'ascending' ? -1 : 1;
    this.box.querySelectorAll('th[data-sort]').forEach(function (h) { h.setAttribute('aria-sort', 'none'); });
    th.setAttribute('aria-sort', dir === 1 ? 'ascending' : 'descending');
    var get = function (r) { return key === 'id' ? r.getAttribute('data-id') : key === 'category' ? r.getAttribute('data-category') : r.getAttribute('data-' + key) || ''; };
    var self = this;
    this.rows.sort(function (a, b) { return dir * get(a).localeCompare(get(b)); });
    this.rows.forEach(function (r) { self.tbody.appendChild(r); });
    this.apply();
  };
  Explorer.prototype.fromHash = function () {
    var h = decodeURIComponent(location.hash.slice(1));
    if (h.indexOf('case=') !== 0) return;
    var row = doc.getElementById(h);
    if (!row || !this.box.contains(row)) return;
    this.set({ category: '', verdict: '' });
    this.rows.forEach(function (r) { r.classList.toggle('is-target', r === row); });
    row.hidden = false;
    row.scrollIntoView({ block: 'center' });
  };

  /* ============================================================== charts */
  function tooltips(scope) {
    var tip = el('div', { class: 'ev-tip', role: 'tooltip', hidden: true });
    doc.body.appendChild(tip);
    scope.querySelectorAll('[title]').forEach(function (t) {
      var text = t.getAttribute('title');
      t.removeAttribute('title'); t.setAttribute('data-tip', text);
      if (!t.getAttribute('aria-label') && !t.textContent.trim()) t.setAttribute('aria-label', text);
    });
    function show(t) {
      tip.textContent = t.getAttribute('data-tip'); tip.hidden = false;
      var r = t.getBoundingClientRect(), w = tip.offsetWidth;
      tip.style.left = clamp(r.left + r.width / 2 - w / 2 + scrollX, 8 + scrollX, scrollX + doc.documentElement.clientWidth - w - 8) + 'px';
      tip.style.top = (r.top + scrollY - tip.offsetHeight - 8) + 'px';
    }
    scope.addEventListener('pointerover', function (e) { var t = e.target.closest('[data-tip]'); if (t) show(t); });
    scope.addEventListener('pointerout', function (e) { if (e.target.closest('[data-tip]')) tip.hidden = true; });
    scope.addEventListener('focusin', function (e) { var t = e.target.closest('[data-tip]'); if (t) show(t); });
    scope.addEventListener('focusout', function () { tip.hidden = true; });
  }

  /* ========================================================= number check
   * Every number the page shows (data-ev="<tool>:<JSON pointer>") against the JSON. A number
   * agrees when the JSON's value, rounded to the digits shown, is what is shown. */
  function resolve(obj, pointer) {
    return pointer.split('/').slice(1).reduce(function (o, k) {
      k = k.replace(/~1/g, '/').replace(/~0/g, '~');
      return o === undefined || o === null ? undefined : o[k];
    }, obj);
  }
  function parseShown(text) {
    var t = text.replace(/−/g, '-').replace(/[,\s ]/g, '');
    var pct = /%$/.test(t); t = t.replace(/%$/, '').replace(/s$/, '').replace(/×$/, '');
    var m = t.match(/^([-+]?)(\d*)(?:\.(\d*))?(?:e([-+]?\d+))?$/);
    if (!m) return null;
    var digits = ((m[2] || '').replace(/^0+/, '') + (m[3] || '')).replace(/^0+/, '').length || 1;
    var v = parseFloat(t); if (pct) v /= 100;
    return { v: v, digits: digits, exact: !m[3] && !m[4] && !pct };
  }
  EV.check = function () {
    var els = Array.prototype.slice.call(doc.querySelectorAll('[data-ev]'));
    var tools = uniq(els.map(function (e) { return e.getAttribute('data-ev').split(':')[0]; }));
    var base = (doc.querySelector('link[rel=stylesheet][href*="site.css"]').getAttribute('href') || '').replace(/static\/css\/site\.css$/, '');
    return Promise.all(tools.map(function (t) { return loadDoc(base + 'static/evidence/' + t + '.json').then(function (j) { return [t, j]; }); })).then(function (pairs) {
      var docs = {}; pairs.forEach(function (p) { docs[p[0]] = p[1]; });
      var bad = [], ok = 0;
      els.forEach(function (e) {
        var spec = e.getAttribute('data-ev'), i = spec.indexOf(':'), tool = spec.slice(0, i), pointer = spec.slice(i + 1);
        var want = resolve(docs[tool], pointer), shown = parseShown(e.textContent);
        if (typeof want !== 'number' || !shown) { bad.push(spec + ': shown ' + JSON.stringify(e.textContent) + ', JSON ' + JSON.stringify(want)); return; }
        var tol = want === 0 ? 0 : Math.abs(want) * 0.5 * Math.pow(10, 1 - shown.digits) * (1 + 1e-9);
        if (Number.isInteger(want) && shown.exact ? shown.v === want : Math.abs(shown.v - want) <= tol + 1e-300) ok++;
        else bad.push(spec + ': shown ' + JSON.stringify(e.textContent) + ', JSON ' + want);
      });
      return { checked: els.length, agree: ok, disagree: bad };
    });
  };
  /* The viewers' readouts against the JSON: at each difference's largest displayed |Δ|, the
     two values the JSON records (a_at, b_at) and the panels' decoded values. */
  EV.checkViewers = function () {
    var out = [];
    return Promise.all(EV.viewers.map(function (vw) {
      var ex = vw.ex;
      return Promise.all(ex.diffs.map(function (x) {
        return Promise.all(Object.keys(x.display || {}).map(function (o) {
          var d = x.display[o];
          var ka = x.a + ':' + (ex.panelById[x.a].arrays[o] ? o : 'all'), kb = x.b + ':' + (ex.panelById[x.b].arrays[o] ? o : 'all');
          return Promise.all([vw.store.get(ka), vw.store.get(kb)]).then(function (r) {
            var sa = vw.store.spec(ka), sb = vw.store.spec(kb);
            var i = vw.index(d.at[0], d.at[1], d.at[2], d.at[3] || 0);
            var va = r[0][i] * (sa.scale === undefined ? 1 : sa.scale) + (sa.inter || 0);
            var vb = r[1][i] * (sb.scale === undefined ? 1 : sb.scale) + (sb.inter || 0);
            out.push({ diff: x.id, output: o, ok: va === d.a && vb === d.b && Math.abs(va - vb) === d.max_abs, shown: [va, vb], json: [d.a, d.b, d.max_abs] });
          });
        }));
      }));
    })).then(function () { return out; });
  };

  /* ================================================================ start */
  function start() {
    doc.querySelectorAll('.ev-example').forEach(function (sec) {
      var go = function () {
        loadDoc(sec.getAttribute('data-ev-src')).then(function (d) {
          var ex = d.examples.filter(function (e) { return e.id === sec.getAttribute('data-ev-example'); })[0];
          EV.viewers.push(new Viewer(sec, d, ex, sec.getAttribute('data-ev-blobs')));
        }).catch(function (e) { sec.classList.add('ev-failed'); console.error(e); });
      };
      if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (es) { if (es.some(function (e) { return e.isIntersecting; })) { io.disconnect(); go(); } }, { rootMargin: '600px 0px' });
        io.observe(sec);
      } else go();
    });
    var explorers = [];
    doc.querySelectorAll('.ev-cases').forEach(function (b) { explorers.push(new Explorer(b)); });
    doc.querySelectorAll('.ev-agree .seg').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var id = (a.getAttribute('href') || '').slice(1);
        var ex = explorers.filter(function (x) { return x.box.id === id; })[0] || explorers[0]; if (!ex) return;
        e.preventDefault();
        ex.set({ category: a.getAttribute('data-filter-category'), verdict: a.getAttribute('data-filter-verdict'), impl: a.getAttribute('data-filter-impl') });
        ex.box.scrollIntoView({ behavior: reduced() ? 'auto' : 'smooth', block: 'start' });
      });
    });
    doc.querySelectorAll('.ev-lines[data-ev-lines]').forEach(function (fig) {
      loadDoc(fig.getAttribute('data-ev-src')).then(function (d) {
        new Lines(fig, resolve(d, fig.getAttribute('data-ev-lines')));
      }).catch(function (e) { console.error(e); });
    });
    doc.querySelectorAll('.ev-chart').forEach(tooltips);
    doc.querySelectorAll('.ev-agree .seg').forEach(function (a) {
      var n = a.querySelector('.seg-n');
      if (n && n.scrollWidth + 8 > a.clientWidth) a.classList.add('is-tight');
    });
  }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', start); else start();
})();
