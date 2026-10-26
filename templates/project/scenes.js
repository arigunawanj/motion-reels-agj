// Satu E.scene per entry di script.json (id harus sama, urutan sama).
// Desain default AGJ Labs: lihat style.css. Transisi sapuan logo ada di akhir file — JANGAN dihapus.
const { p, lerp, clamp, css, enter, noise, rand, ease } = E;
const C = { blue: '#2563EB', green: '#10B981', amber: '#FBBF24', red: '#EF4444', navy: '#0F172A' };
const CHECK = `<svg viewBox="0 0 24 24"><path pathLength="1" data-r="tick[]" d="M5 12.5l4.5 4.5L19 7"/></svg>`;

/* ---------- helper header tip ---------- */
function tipHead(n, word, col) {
  const dots = [1, 2, 3, 4, 5].map(i => `<i class="${i <= n ? 'on' : ''}"></i>`).join('');
  return `<div class="tiphead" data-r="head"><div class="tnum mono">0${n}</div><div class="tdots">${dots}</div></div>
    <div class="tword h-l" data-r="tword" style="color:${col}">${E.chars(word)}</div>`;
}
function tipHeadIn(r, t, at = 0.1) {
  enter(r.head, t, at, { from: 'left', dist: 80 });
  r.ch.forEach((c, i) => enter(c, t, at + 0.12 + i * 0.035, { from: 'up', dist: 90, dur: 0.45 }));
}
// titik di sepanjang polyline (deterministik, dipakai SVG & kamera)
function along(pts, k) {
  const seg = []; let tot = 0;
  for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); seg.push(d); tot += d; }
  let L = clamp(k) * tot;
  for (let i = 0; i < seg.length; i++) {
    if (L <= seg[i] || i === seg.length - 1) { const q = seg[i] ? L / seg[i] : 0; return [lerp(pts[i][0], pts[i + 1][0], q), lerp(pts[i][1], pts[i + 1][1], q)]; }
    L -= seg[i];
  }
  return pts[pts.length - 1];
}


E.scene({
  id: 'hook',
  at: { x: 0, y: 0 },
  hits: ctx => [ctx.word('masalah')],
  build(el) {
    el.innerHTML = `<div class="card" data-r="card" style="left:120px;top:520px;width:840px;padding:60px;text-align:center">
      <div class="lbl">Hook</div><div class="h-xl" style="color:${C.blue}">MASALAH<span style="color:${C.amber}">.</span></div></div>`;
  },
  update(r, t, ctx) { enter(r.card, t, ctx.word('masalah') - 0.15, { from: 'zoom' }); },
  cam: (t, ctx) => ({ z: lerp(1.4, 1, p(t, 0, 1.2, 'outExpo')) }),
});

E.scene({
  id: 'cta',
  at: { x: 1600, y: -300 },
  build(el) {
    el.innerHTML = `<div class="logo-card" data-r="lg" style="top:420px"><img src="stacked.png"></div>
      <div class="abs" style="left:0;right:0;top:1000px;text-align:center"><span class="btn3d" data-r="btn">Follow @agjlabs</span></div>`;
  },
  update(r, t, ctx) { enter(r.lg, t, 0.0, { from: 'zoom', dur: 0.6 }); enter(r.btn, t, 0.4, { from: 'pop' }); },
  cam: (t, ctx) => ({ z: lerp(1.14, 1.0, p(t, 0, 1.0, 'outExpo')) + 0.04 * p(t, 1, ctx.d, 'linear') }),
});

/* ===== transisi brand: potongan logo AGJ menyapu layar di tiap pergantian scene ===== */
(() => {
  const orig = window.__seek;
  let wipe = null, pieces = [];
  window.__seek = t => {
    const r = orig(t);
    if (!wipe) {
      wipe = document.createElement('div'); wipe.id = 'wipe';
      wipe.innerHTML = '<div class="wb"></div><div class="wy"></div><div class="wg"></div>';
      const caps = document.getElementById('caps');
      caps.parentNode.insertBefore(wipe, caps);
      pieces = [...wipe.children];
    }
    const sc = (window.TIMELINE && TIMELINE.scenes) || [];
    let k = -1;
    for (let i = 1; i < sc.length; i++) {           // transisi i: puncak di start + 0.25
      const c = sc[i].start + 0.25, d = t - c;
      if (d > -0.42 && d < 0.42) { k = (d + 0.42) / 0.84; break; }
    }
    pieces.forEach((el, i) => {
      if (k < 0) { el.style.display = 'none'; return; }
      el.style.display = 'block';
      const q = E.ease.inOutCubic(E.clamp(k * 1.25 - i * 0.12));
      const x = E.lerp(1500, -1700, q), y = E.lerp(-900, 1000, q);
      el.style.transform = i === 0 ? `translate(${x}px,${y}px) rotate(33deg)` : `translate(${x * (1 + i * 0.15)}px,${y * 0.4}px) rotate(${-10 + i * 12}deg)`;
    });
    return r;
  };
})();
