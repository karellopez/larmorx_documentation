/* The site's controls: the colour theme (system, light or dark), the effects
 * switch, the menu on narrow screens, the copy buttons of code blocks and the
 * table of contents' place. Every stored choice is a convenience: when storage
 * is not available the page works the same, and forgets. */
(function () {
  'use strict';
  var d = document.documentElement;
  function store(key, value) { try { localStorage.setItem(key, value); } catch (e) { /* not kept */ } }

  /* ------------------------------------------------------------- theme */
  var mq = window.matchMedia('(prefers-color-scheme: dark)');
  var themeButton = document.querySelector('[data-theme-button]');
  var menu = document.getElementById('theme-menu');
  var items = menu ? Array.prototype.slice.call(menu.querySelectorAll('[data-set-theme]')) : [];
  function applyTheme(pref) {
    var dark = pref === 'dark' || (pref === 'system' && mq.matches);
    d.setAttribute('data-theme-pref', pref);
    d.setAttribute('data-theme', dark ? 'dark' : 'light');
    items.forEach(function (b) { b.setAttribute('aria-checked', String(b.getAttribute('data-set-theme') === pref)); });
    if (themeButton) themeButton.setAttribute('aria-label', 'Colour theme: ' + pref);
  }
  applyTheme(d.getAttribute('data-theme-pref') || 'system');
  var onSystem = function () { if (d.getAttribute('data-theme-pref') === 'system') applyTheme('system'); };
  if (mq.addEventListener) mq.addEventListener('change', onSystem); else if (mq.addListener) mq.addListener(onSystem);

  function openMenu(open, focus) {
    if (!menu) return;
    menu.hidden = !open;
    themeButton.setAttribute('aria-expanded', String(open));
    if (open && focus) {
      var current = items.filter(function (b) { return b.getAttribute('aria-checked') === 'true'; })[0] || items[0];
      current.focus();
    }
  }
  if (themeButton && menu) {
    themeButton.addEventListener('click', function () { openMenu(menu.hidden, true); });
    themeButton.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); openMenu(true, true); }
    });
    items.forEach(function (b, i) {
      b.addEventListener('click', function () {
        var pref = b.getAttribute('data-set-theme');
        applyTheme(pref); store('lx-theme', pref);
        openMenu(false); themeButton.focus();
      });
      b.addEventListener('keydown', function (e) {
        var n = items.length;
        if (e.key === 'ArrowDown') { e.preventDefault(); items[(i + 1) % n].focus(); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); items[(i + n - 1) % n].focus(); }
        else if (e.key === 'Home') { e.preventDefault(); items[0].focus(); }
        else if (e.key === 'End') { e.preventDefault(); items[n - 1].focus(); }
        else if (e.key === 'Escape') { e.preventDefault(); openMenu(false); themeButton.focus(); }
        else if (e.key === 'Tab') { openMenu(false); }
      });
    });
    document.addEventListener('click', function (e) {
      if (!menu.hidden && !menu.contains(e.target) && !themeButton.contains(e.target)) openMenu(false);
    });
  }

  /* ----------------------------------------------------------- effects */
  var fxButton = document.querySelector('[data-fx-toggle]');
  function syncFx() {
    var on = d.getAttribute('data-fx') === 'on';
    if (!fxButton) return;
    fxButton.setAttribute('aria-pressed', String(on));
    fxButton.title = on ? 'Effects are on: select to stop the animations' : 'Effects are off: select to start the animations';
  }
  syncFx();
  if (fxButton) fxButton.addEventListener('click', function () {
    var on = d.getAttribute('data-fx') !== 'on';
    d.setAttribute('data-fx', on ? 'on' : 'off');
    store('lx-fx', on ? 'on' : 'off');
    syncFx();
    document.dispatchEvent(new CustomEvent('lx-fx', { detail: { on: on } }));
  });

  /* ------------------------------------------------- menu (narrow screens) */
  var toggle = document.querySelector('.nav-toggle');
  var mobile = document.getElementById('mobile-nav');
  function openNav(open) {
    if (!mobile) return;
    mobile.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
  }
  if (toggle && mobile) {
    toggle.addEventListener('click', function () { openNav(!mobile.classList.contains('is-open')); });
    mobile.addEventListener('click', function (e) { if (e.target.closest('a')) openNav(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && mobile.classList.contains('is-open')) { openNav(false); toggle.focus(); }
    });
  }

  /* ------------------------------------------------------- copy buttons */
  Array.prototype.forEach.call(document.querySelectorAll('.code-copy'), function (b) {
    b.addEventListener('click', function () {
      var code = b.parentNode.querySelector('pre').innerText.replace(/\n$/, '');
      var done = function () {
        b.textContent = 'Copied'; b.classList.add('is-done');
        setTimeout(function () { b.textContent = 'Copy'; b.classList.remove('is-done'); }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(code).then(done, function () {});
    });
  });

  /* ---------------------------------------------- the table of contents */
  var toc = document.querySelector('.toc') || document.querySelector('.side-toc');
  if (toc && 'IntersectionObserver' in window) {
    var links = Array.prototype.slice.call(toc.querySelectorAll('a'));
    var heads = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); }).filter(Boolean);
    var visible = new Set();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) visible.add(en.target.id); else visible.delete(en.target.id); });
      var active = null;
      for (var i = 0; i < heads.length; i++) {
        if (visible.has(heads[i].id)) { active = heads[i].id; break; }
        if (heads[i].getBoundingClientRect().top < 120) active = heads[i].id;
      }
      links.forEach(function (a) { a.classList.toggle('is-active', a.getAttribute('href') === '#' + active); });
    }, { rootMargin: '-60px 0px -55% 0px' });
    heads.forEach(function (h) { io.observe(h); });
  }
})();
