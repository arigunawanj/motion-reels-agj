/* =====================================================================
 * Motion Reels Engine — AGJ Labs
 * Deterministic motion-graphics engine untuk video 9:16 (1080x1920).
 * Semua animasi = fungsi waktu murni → bisa dirender frame-by-frame 60fps.
 *
 *   window.__seek(t)    render frame pada detik t
 *   window.__meta()     {W, H, fps, total}
 *   window.__events()   daftar SFX [{t, type}] (whoosh/pop/hit/tick/ding/riser)
 * ===================================================================== */
(() => {
  const W = 1080, H = 1920;
  const E = (window.E = {});

  /* ---------- math & easing ---------- */
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const ease = {
    linear: t => t,
    inQuad: t => t * t,
    outQuad: t => 1 - (1 - t) * (1 - t),
    inCubic: t => t * t * t,
    outCubic: t => 1 - Math.pow(1 - t, 3),
    inOutCubic: t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
    outQuint: t => 1 - Math.pow(1 - t, 5),
    inExpo: t => (t === 0 ? 0 : Math.pow(2, 10 * t - 10)),
    outExpo: t => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t)),
    inOutExpo: t =>
      t === 0 ? 0 : t === 1 ? 1 : t < 0.5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2,
    outBack: t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
    outBackBig: t => { const c1 = 3.2, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
    outElastic: t =>
      t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * ((2 * Math.PI) / 3)) + 1,
  };
  const ef = e => (typeof e === 'function' ? e : ease[e] || ease.outCubic);
  Object.assign(E, { W, H, clamp, lerp, ease });

  /** progress 0..1 antara detik a..b dengan easing */
  E.p = (t, a, b, e = 'outCubic') => ef(e)(clamp((t - a) / Math.max(1e-6, b - a)));
  /** naik a→b, turun c→d */
  E.io = (t, a, b, c, d, e = 'outCubic') => Math.min(E.p(t, a, b, e), 1 - E.p(t, c, d, 'inOutCubic'));
  /** pegas: 0→1 dengan overshoot yang meredam */
  E.spring = (t, at, { freq = 2.2, damp = 7 } = {}) => {
    const x = t - at; if (x <= 0) return 0;
    return 1 - Math.exp(-damp * x) * Math.cos(freq * 2 * Math.PI * x);
  };

  const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
  E.rand = (i, seed = 0) => hash(i * 1.618 + seed * 91.7);
  /** value-noise halus -1..1 */
  E.noise = (x, seed = 0) => {
    const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
    return lerp(hash(i + seed * 57.3), hash(i + 1 + seed * 57.3), u) * 2 - 1;
  };
  E.count = (from, to, k, dec = 0) => (from + (to - from) * k).toFixed(dec);
  E.mix = (c1, c2, k) => { // hex mix
    const a = c1.match(/\w\w/g).map(h => parseInt(h, 16)), b = c2.match(/\w\w/g).map(h => parseInt(h, 16));
    return `rgb(${a.map((v, i) => Math.round(lerp(v, b[i], clamp(k)))).join(',')})`;
  };

  /* ---------- DOM helpers ---------- */
  E.tf = ({ x = 0, y = 0, s = 1, sx, sy, r = 0, skx = 0 } = {}) =>
    `translate(${x}px,${y}px) rotate(${r}deg) skewX(${skx}deg) scale(${sx ?? s},${sy ?? s})`;
  /** set transform/opacity/blur sekaligus */
  E.css = (el, o = {}) => {
    if (!el) return;
    el.style.transform = E.tf(o);
    if (o.o !== undefined) el.style.opacity = clamp(o.o);
    if (o.blur !== undefined) el.style.filter = o.blur > 0.15 ? `blur(${o.blur.toFixed(2)}px)` : 'none';
  };
  /** entrance preset: 'up' | 'down' | 'left' | 'right' | 'pop' | 'zoom' | 'drop' */
  E.enter = (el, t, at, { from = 'up', dist = 140, dur = 0.5, e, extra = {} } = {}) => {
    const k = E.p(t, at, at + dur, e || (from === 'pop' ? 'outBackBig' : 'outExpo'));
    const o = { o: E.p(t, at, at + dur * 0.4, 'linear'), ...extra };
    if (from === 'up') o.y = (extra.y || 0) + (1 - k) * dist;
    if (from === 'down') o.y = (extra.y || 0) - (1 - k) * dist;
    if (from === 'left') o.x = (extra.x || 0) - (1 - k) * dist;
    if (from === 'right') o.x = (extra.x || 0) + (1 - k) * dist;
    if (from === 'pop') o.s = (extra.s ?? 1) * k;
    if (from === 'zoom') { o.s = (extra.s ?? 1) * lerp(2.4, 1, k); o.blur = (1 - k) * 18; }
    if (from === 'drop') { o.y = (extra.y || 0) - (1 - E.spring(t, at, { damp: 8 })) * dist; o.o = t >= at ? 1 : 0; }
    E.css(el, o);
    return k;
  };
  /** ambil elemen ber-atribut data-r; "nama[]" jadi array */
  E.refs = root => {
    const r = { root };
    root.querySelectorAll('[data-r]').forEach(el => {
      const k = el.dataset.r;
      if (k.endsWith('[]')) (r[k.slice(0, -2)] ||= []).push(el);
      else r[k] = el;
    });
    return r;
  };
  /** teks per-karakter untuk kinetic typography */
  E.chars = (text, cls = '') =>
    [...text].map(c => `<span class="ch ${cls}" data-r="ch[]">${c === ' ' ? '&nbsp;' : c}</span>`).join('');

  /* ---------- registry & timeline ---------- */
  const defs = [];
  E.scene = def => defs.push(def);
  let S = [], TOTAL = 0, FPS = 60, stage, world, bg, blobs, caps, hud, fxFlash, fxGrain, mbBlur, chunks = [];
  let lastT = 0;

  const norm = s => s.toLowerCase().normalize('NFKD').replace(/[^\p{L}\p{N}%]/gu, '');

  function makeCtx(sc) {
    const words = sc.words || [];
    return {
      d: sc.dur,
      vo: sc.voStart ?? 0,
      /** detik lokal saat kata `q` diucapkan (nth = kemunculan ke-n). Sinkron ke VO. */
      word(q, nth = 0, fallback = 0.5) {
        const nq = norm(q); let n = 0;
        for (const w of words) {
          if (norm(w.w).startsWith(nq)) { if (n === nth) return w.s - sc.start; n++; }
        }
        return typeof fallback === 'number' && fallback <= 1 ? sc.dur * fallback : fallback;
      },
      wordEnd(q, nth = 0) {
        const nq = norm(q); let n = 0;
        for (const w of words) if (norm(w.w).startsWith(nq)) { if (n === nth) return w.e - sc.start; n++; }
        return sc.dur * 0.6;
      },
      flash: 0,
    };
  }

  E.boot = () => {
    const tl = window.TIMELINE || { fps: 60, scenes: [] };
    FPS = tl.fps || 60;
    stage = document.getElementById('stage');
    stage.innerHTML = `
      <svg width="0" height="0" style="position:absolute"><filter id="mb" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur id="mbBlur" stdDeviation="0 0"/></filter></svg>
      <div id="bg"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div></div>
      <div id="world"></div>
      <div id="fx"><div class="vignette"></div><div class="grain"></div><div class="flash"></div></div>
      <div id="caps"></div>
      <div id="hud"><div class="bar"><i></i></div><div class="handle">${tl.handle || '@agjlabs'}</div></div>`;
    world = document.getElementById('world');
    bg = document.getElementById('bg');
    blobs = [...bg.querySelectorAll('.blob')];
    caps = document.getElementById('caps');
    hud = document.getElementById('hud');
    fxFlash = stage.querySelector('.flash');
    fxGrain = stage.querySelector('.grain');
    mbBlur = document.getElementById('mbBlur');

    // gabungkan definisi scene dengan durasi dari timeline (urutan = id)
    let t = 0;
    S = defs.map((def, i) => {
      const tlS = (tl.scenes || []).find(s => s.id === def.id) || {};
      const dur = tlS.dur ?? def.dur ?? 3;
      const sc = { ...def, i, start: tlS.start ?? t, dur, words: tlS.words || [], voStart: tlS.voStart };
      t = sc.start + dur;
      sc.at = def.at || { x: (i % 3) * 1500, y: Math.floor(i / 3) * 2400 + (i % 2) * 500 };
      sc.trans = i === 0 ? 0 : def.trans ?? 0.5;
      const el = document.createElement('section');
      el.className = 'scene ' + (def.cls || '');
      el.style.left = sc.at.x + 'px';
      el.style.top = sc.at.y + 'px';
      world.appendChild(el);
      sc.el = el;
      sc.ctx = makeCtx(sc);
      sc.refs = def.build ? def.build(el, sc.ctx) || E.refs(el) : E.refs(el);
      sc.hitsL = typeof def.hits === 'function' ? def.hits(sc.ctx) : def.hits || [];
      sc.sfxL = typeof def.sfx === 'function' ? def.sfx(sc.ctx) : def.sfx || [];
      return sc;
    });
    TOTAL = tl.total ?? t;
    buildChunks();
    E.ready = true;
  };

  /* ---------- kamera ---------- */
  function sceneCam(sc, lt) {
    const d = sc.dur;
    const c = sc.cam ? sc.cam(lt, sc.ctx) || {} : {};
    const z = c.z ?? 1 + 0.06 * E.p(lt, 0, d, 'linear'); // default: slow push-in
    const hand = sc.handheld ?? 1;
    const hx = E.noise(lt * 0.55, sc.i) * 7 * hand, hy = E.noise(lt * 0.5, sc.i + 9) * 7 * hand;
    const hr = E.noise(lt * 0.4, sc.i + 3) * 0.4 * hand;
    let sh = 0;
    for (const h of sc.hitsL) if (lt >= h) sh += Math.exp(-(lt - h) * 9);
    sh = Math.min(sh, 1.4);
    const sx = E.noise(lt * 32, sc.i + 1) * 30 * sh, sy = E.noise(lt * 32, sc.i + 2) * 30 * sh;
    const sr = E.noise(lt * 26, sc.i + 4) * 1.4 * sh;
    return {
      x: sc.at.x + W / 2 + (c.x || 0) + hx + sx,
      y: sc.at.y + H / 2 + (c.y || 0) + hy + sy,
      z, r: (c.r || 0) + hr + sr,
    };
  }
  function sceneIndex(t) {
    for (let i = S.length - 1; i >= 0; i--) if (t >= S[i].start) return i;
    return 0;
  }
  function camAt(t) {
    const i = sceneIndex(t), sc = S[i], lt = t - sc.start;
    const cur = sceneCam(sc, lt);
    if (i > 0 && lt < sc.trans) {
      const pv = S[i - 1], prev = sceneCam(pv, pv.dur + lt);
      const k = ease.inOutExpo(lt / sc.trans), dip = Math.sin(Math.PI * k);
      const dir = sc.at.x >= pv.at.x ? 1 : -1;
      const style = sc.transStyle || 'whip';
      const zoomDip = style === 'zoom' ? 0.45 : 0.2;
      return {
        x: lerp(prev.x, cur.x, k), y: lerp(prev.y, cur.y, k),
        z: lerp(prev.z, cur.z, k) * (1 - zoomDip * dip),
        r: lerp(prev.r, cur.r, k) + (style === 'whip' ? dir * 6 * dip : 0),
      };
    }
    return cur;
  }

  /* ---------- captions (karaoke, kata aktif di-highlight) ---------- */
  function buildChunks() {
    chunks = [];
    for (const sc of S) {
      if (sc.captions === false) continue;
      let cur = null;
      const push = () => { if (cur && cur.words.length) chunks.push(cur); cur = null; };
      sc.words.forEach((w, idx) => {
        if (!cur) cur = { sc, words: [], s: w.s };
        cur.words.push(w);
        const len = cur.words.reduce((a, b) => a + b.w.length + 1, 0);
        if (/[.,!?…:;]$/.test(w.w) || cur.words.length >= 3 || len > 15) push();
      });
      push();
    }
    chunks.forEach((c, i) => {
      const last = c.words[c.words.length - 1];
      const nxt = chunks[i + 1];
      c.e = nxt && nxt.sc === c.sc ? nxt.s : Math.min(last.e + 0.35, c.sc.start + c.sc.dur);
    });
  }
  let capKey = '';
  function renderCaps(t) {
    const c = chunks.find(c => t >= c.s && t < c.e);
    if (!c) { caps.innerHTML = ''; capKey = ''; return; }
    const y = c.sc.capY ?? 1340;
    let active = c.words.findIndex(w => t >= w.s && t < w.e);
    if (active < 0) active = c.words.filter(w => t >= w.s).length - 1;
    const key = c.s + ':' + active;
    if (key !== capKey) {
      caps.innerHTML = `<div class="cap">${c.words
        .map((w, i) => `<span class="w ${w.em ? 'em' : ''} ${i === active ? 'on' : ''} ${i > active ? 'next' : ''}">${w.w}</span>`)
        .join(' ')}</div>`;
      capKey = key;
    }
    const k = E.p(t, c.s, c.s + 0.22, 'outBackBig');
    const cap = caps.firstChild;
    cap.style.top = y + 'px';
    cap.style.transform = `translateX(-50%) scale(${lerp(0.7, 1, k)}) rotate(${lerp(-4, 0, k)}deg)`;
    cap.style.opacity = E.p(t, c.s, c.s + 0.08, 'linear');
    const on = cap.querySelector('.on');
    if (on) {
      const w = c.words[active];
      on.style.transform = `scale(${lerp(1.18, 1.06, E.p(t, w.s, w.s + 0.18))})`;
    }
  }

  /* ---------- seek ---------- */
  window.__seek = t => {
    if (!E.ready) E.boot();
    t = clamp(t, 0, TOTAL);
    const dt = 1 / (FPS * 2);
    const cam = camAt(t), cam0 = camAt(Math.max(0, t - dt));
    world.style.transform =
      `translate(${W / 2}px,${H / 2}px) scale(${cam.z}) rotate(${cam.r}deg) translate(${-cam.x}px,${-cam.y}px)`;

    // motion blur arah gerak kamera
    const vx = Math.abs(cam.x - cam0.x) * cam.z, vy = Math.abs(cam.y - cam0.y) * cam.z;
    const vz = Math.abs(cam.z - cam0.z) * 900;
    const bx = Math.min(70, vx * 0.55 + vz * 0.3), by = Math.min(70, vy * 0.55 + vz * 0.3);
    if (bx + by > 0.6) { mbBlur.setAttribute('stdDeviation', `${bx.toFixed(1)} ${by.toFixed(1)}`); world.style.filter = 'url(#mb)'; }
    else world.style.filter = 'none';

    // background parallax
    bg.style.backgroundPosition = `${(-cam.x * 0.25) % 90}px ${(-cam.y * 0.25) % 90}px`;
    blobs.forEach((b, i) => {
      const px = E.noise(t * 0.15, i + 20) * 260 - cam.x * 0.05 * (i + 1) % 400;
      const py = E.noise(t * 0.12, i + 40) * 300 - cam.y * 0.04 * (i + 1) % 500;
      b.style.transform = `translate(${px}px,${py}px)`;
    });

    // scenes
    let flash = 0;
    for (const sc of S) {
      const lt = t - sc.start;
      const vis = lt > -0.6 && lt < sc.dur + 0.7;
      sc.el.style.display = vis ? 'block' : 'none';
      if (!vis) continue;
      sc.ctx.flash = 0;
      if (sc.update) sc.update(sc.refs, lt, sc.ctx);
      for (const h of sc.hitsL) if (lt >= h) flash = Math.max(flash, 0.35 * Math.exp(-(lt - h) * 14));
      flash = Math.max(flash, sc.ctx.flash || 0);
    }
    fxFlash.style.opacity = flash;
    fxGrain.style.backgroundPosition = `${Math.floor(E.rand(Math.floor(t * FPS), 3) * 256)}px ${Math.floor(E.rand(Math.floor(t * FPS), 7) * 256)}px`;

    renderCaps(t);
    hud.querySelector('.bar i').style.transform = `scaleX(${t / TOTAL})`;
    lastT = t;
    return true;
  };

  window.__meta = () => { if (!E.ready) E.boot(); return { W, H, fps: FPS, total: TOTAL }; };
  window.__events = () => {
    if (!E.ready) E.boot();
    const ev = [];
    S.forEach((sc, i) => {
      // puncak whoosh (≈0.21 dtk) jatuh di tengah transisi
      if (i > 0 && sc.trans > 0 && sc.whoosh !== false) ev.push({ t: sc.start + sc.trans / 2 - 0.21, type: 'whoosh', scene: sc.id });
      for (const h of sc.hitsL) ev.push({ t: sc.start + h, type: 'hit', scene: sc.id });
      for (const [lt, type, gain] of sc.sfxL) ev.push({ t: sc.start + lt, type, gain, scene: sc.id });
    });
    return ev.filter(e => e.t >= 0 && e.t < TOTAL).sort((a, b) => a.t - b.t);
  };

  /* ---------- hook untuk render cache & QC ---------- */
  const fnSrc = f => (typeof f === 'function' ? f.toString() : JSON.stringify(f ?? null));
  window.__scenes = () => {
    if (!E.ready) E.boot();
    return S.map(sc => ({
      id: sc.id, start: sc.start, dur: sc.dur, trans: sc.trans,
      src: [sc.build, sc.update, sc.cam, sc.hits, sc.sfx].map(fnSrc).join('\n') +
        JSON.stringify({ at: sc.at, capY: sc.capY, transStyle: sc.transStyle, handheld: sc.handheld, cls: sc.cls, captions: sc.captions }),
    }));
  };
  window.__cam = t => { if (!E.ready) E.boot(); return camAt(clamp(t, 0, TOTAL)); };

  const effOpacity = el => {
    let o = 1;
    for (let e = el; e && e !== stage; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
      o *= parseFloat(cs.opacity);
    }
    return o;
  };
  const hit = (a, b) => !(a.right <= b.left || a.left >= b.right || a.bottom <= b.top || a.top >= b.bottom);
  const box = r => ({ x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height) });

  /** cek satu frame: caption terpotong / masuk zona UI, teks keluar layar, teks tabrakan caption */
  window.__qc = t => {
    window.__seek(t);
    const issues = [];
    const i = sceneIndex(t), sc = S[i], lt = t - sc.start;
    const moving = (i > 0 && lt < sc.trans + 0.2) || lt > sc.dur - 0.15; // abaikan saat transisi
    const cap = caps.firstChild;
    let capR = null;
    if (cap) {
      // ukur kata yang benar-benar tampil (bukan lebar kotak), abaikan 0.25 dtk pertama animasi pop
      const ws = [...cap.querySelectorAll('.w')].map(w => w.getBoundingClientRect());
      if (ws.length) capR = ws.reduce((a, r) => ({ left: Math.min(a.left, r.left), right: Math.max(a.right, r.right),
        top: Math.min(a.top, r.top), bottom: Math.max(a.bottom, r.bottom) }), { left: 1e9, right: -1e9, top: 1e9, bottom: -1e9 });
      const ch = chunks.find(c => t >= c.s && t < c.e);
      const settling = ch && t - ch.s < 0.25;
      if (capR && !settling) {
        capR.width = capR.right - capR.left; capR.height = capR.bottom - capR.top;
        if (capR.left < 20 || capR.right > W - 20) issues.push({ sev: 'error', type: 'caption-terpotong', scene: sc.id, box: box(capR) });
        if (capR.bottom > 1560) issues.push({ sev: 'error', type: 'caption-masuk-zona-ui-bawah', scene: sc.id, box: box(capR) });
        else if (capR.right > 960) issues.push({ sev: 'warn', type: 'caption-kena-tombol-kanan', scene: sc.id, box: box(capR) });
      }
    }
    if (!moving) {
      const els = sc.el.querySelectorAll('*');
      for (const el of els) {
        const tn = [...el.childNodes].find(n => n.nodeType === 3 && n.textContent.trim().length > 1);
        if (!tn || el.closest('[data-qc="ignore"]')) continue;
        const rg = document.createRange(); rg.selectNodeContents(tn);
        const r = rg.getBoundingClientRect();   // batas teks sebenarnya
        if (r.width < 4 || r.height < 4) continue;
        if (effOpacity(el) < 0.5) continue;
        const label = el.textContent.trim().slice(0, 28);
        const key = el.dataset.r || (el.className && String(el.className)) || el.tagName;
        const inside = r.right > 0 && r.left < W && r.bottom > 0 && r.top < H;
        if (!inside) continue;
        if (r.left < 0 || r.right > W || r.top < 0 || r.bottom > H)
          issues.push({ sev: 'warn', type: 'teks-terpotong-tepi', scene: sc.id, text: label, key, box: box(r) });
        else if (r.bottom > 1560 || r.top < 200)
          issues.push({ sev: 'warn', type: 'teks-di-zona-ui', scene: sc.id, text: label, key, box: box(r) });
        if (capR && hit(r, capR)) issues.push({ sev: 'warn', type: 'teks-tabrakan-caption', scene: sc.id, text: label, key, box: box(r) });
      }
    }
    return issues;
  };

  /* ---------- preview realtime di browser ---------- */
  window.addEventListener('load', () => {
    if (new URLSearchParams(location.search).has('render')) return;
    E.boot();
    const fit = () => {
      const s = Math.min(innerWidth / W, (innerHeight - 70) / H);
      stage.style.transform = `scale(${s})`; stage.style.transformOrigin = 'top left';
      document.body.style.width = W * s + 'px';
    };
    fit(); addEventListener('resize', fit);
    const ui = document.createElement('div');
    ui.id = 'previewUI';
    ui.innerHTML = `<button id="pp">▶</button><input id="sc" type="range" min="0" max="${TOTAL}" step="0.001" value="0"><span id="tc">0.00</span>`;
    document.body.appendChild(ui);
    const audio = new Audio('build/mix.wav');
    let playing = false, t0 = 0, tStart = 0;
    const sc = ui.querySelector('#sc'), tc = ui.querySelector('#tc'), pp = ui.querySelector('#pp');
    const draw = t => { window.__seek(t); sc.value = t; tc.textContent = t.toFixed(2) + 's'; };
    const loop = now => {
      if (!playing) return;
      const t = tStart + (now - t0) / 1000;
      if (t >= TOTAL) { playing = false; pp.textContent = '▶'; return; }
      draw(t); requestAnimationFrame(loop);
    };
    const toggle = () => {
      playing = !playing; pp.textContent = playing ? '❚❚' : '▶';
      if (playing) { tStart = +sc.value; t0 = performance.now(); audio.currentTime = tStart; audio.play().catch(() => {}); requestAnimationFrame(loop); }
      else audio.pause();
    };
    pp.onclick = toggle;
    addEventListener('keydown', e => { if (e.code === 'Space') { e.preventDefault(); toggle(); } });
    sc.oninput = () => { if (playing) toggle(); draw(+sc.value); };
    draw(0);
  });
})();
