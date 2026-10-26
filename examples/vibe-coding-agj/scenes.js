/* 5 Tips Vibe Coding — AGJ Labs (v4, motion-reels engine)
 * Semua aksi dikunci ke kata VO via ctx.word(). SFX sengaja minim. */
const { p, lerp, clamp, css, enter, noise, rand, ease } = E;
const C = { blue: '#3B82F6', green: '#10B981', amber: '#FBBF24', red: '#F43F5E' };
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

/* ============ 1. HOOK — kode rontok ============ */
const LN = Array.from({ length: 14 }, (_, i) => {
  const ind = [0, 1, 1, 2, 2, 1, 0, 0, 1, 2, 3, 2, 1, 0][i] * 40;
  const cols = [C.blue, '#A78BFA', C.green, '#94A3B8', C.amber];
  const a = 80 + rand(i, 1) * 180, b = 60 + rand(i, 2) * 220;
  return `<div class="ln" data-r="ln[]"><span class="no" data-qc="ignore">${i + 1}</span><b style="margin-left:${ind}px;width:${a}px;background:${cols[i % 5]}"></b><b style="width:${b}px;background:${cols[(i + 2) % 5]};opacity:.75"></b></div>`;
}).join('');
E.scene({
  id: 'hook',
  at: { x: 0, y: 0 },
  hits: ctx => [ctx.word('berantakan')],
  build(el) {
    el.innerHTML = `
      <div class="card dark" data-r="ed" style="left:110px;top:330px;width:860px;height:720px">
        <div class="edbar"><i></i><i></i><i></i><span class="mono">app.js — dibuat AI</span></div>
        <div class="lines">${LN}</div>
      </div>
      <div class="errbadge mono" data-r="err">0 error</div>
      <div class="toast" data-r="toast[]" style="left:150px;top:520px">TypeError: undefined</div>
      <div class="toast" data-r="toast[]" style="left:470px;top:700px">500 Server Error</div>
      <div class="toast" data-r="toast[]" style="left:200px;top:880px">Cannot find module</div>`;
  },
  update(r, t, ctx) {
    const tb = ctx.word('berantakan');
    r.ln.forEach((l, i) => {
      const at = -0.7 + i * 0.11;                       // frame 0 sudah ada isi
      const q = Math.max(0, t - (tb + i * 0.035));
      css(l, { x: q * (rand(i, 4) - 0.5) * 500, y: 2600 * q * q, r: q * (rand(i, 5) - 0.5) * 160,
        o: E.p(t, at, at + 0.15, 'linear') * (1 - E.p(t, tb + 0.6 + i * 0.03, tb + 1.0 + i * 0.03, 'linear')) });
    });
    css(r.ed, { r: lerp(0, -3, p(t, tb, tb + 0.4, 'outBack')) });
    const n = Math.round(lerp(0, 47, p(t, tb - 0.2, tb + 0.7, 'outCubic')));
    r.err.textContent = `${n} error`;
    enter(r.err, t, tb - 0.25, { from: 'pop' });
    r.toast.forEach((x, i) => enter(x, t, tb + 0.08 + i * 0.12, { from: 'pop', extra: { r: [-6, 4, -3][i] + noise(t * 30, i) * 2 * p(t, tb, tb + 0.3) } }));
  },
  cam: (t, ctx) => {
    const tb = ctx.word('berantakan');
    return { y: lerp(-160, 20, p(t, 0, 1.4, 'outExpo')), /* qc: nomor baris jatuh = disengaja */
      z: lerp(1.6, 1.02, p(t, 0, 1.4, 'outExpo')) + 0.1 * p(t, tb, tb + 0.2, 'outExpo') - 0.04 * p(t, tb + 0.3, ctx.d, 'inOutCubic'),
      r: lerp(0, 1.5, p(t, tb, tb + 0.5)) };
  },
});

/* ============ 2. WARUNG — prompt asal = pesan "makanan satu" ============ */
E.scene({
  id: 'warung',
  at: { x: 1700, y: -300 },
  sfx: ctx => [[ctx.word('bingung'), 'pop', 0.7]],
  build(el) {
    el.innerHTML = `
      <div class="lbl" data-r="l1" style="position:absolute;left:110px;top:300px">PROMPT KAMU</div>
      <div class="bubble me" data-r="bub" style="right:130px;top:360px"><span data-r="bt"></span><i class="caret" data-r="car"></i></div>
      <div class="printer" data-r="prn"></div>
      <div class="rwrap"><div class="receipt" data-r="rcp">
        <div class="hd">WARUNG MAKAN</div><div style="text-align:center;font-size:28px;color:#64748B">Meja 03 · 12:30</div>
        <div class="dv"></div>
        <div class="row2"><span>1x <span class="mk" data-r="mk">MAKANAN</span></span><span class="red">???</span></div>
        <div class="row2" style="color:#64748B"><span>Lauk</span><span>???</span></div>
        <div class="row2" style="color:#64748B"><span>Minum</span><span>???</span></div>
        <div class="dv"></div>
        <div class="row2"><span>TOTAL</span><span class="red">???</span></div>
      </div></div>
      <div class="qm" data-r="q[]" style="left:90px;top:760px">?</div>
      <div class="qm" data-r="q[]" style="left:860px;top:640px">?</div>
      <div class="qm" data-r="q[]" style="left:820px;top:1020px;font-size:120px">?</div>`;
  },
  update(r, t, ctx) {
    enter(r.l1, t, 0.0, { from: 'left', dist: 60 });
    enter(r.bub, t, 0.05, { from: 'pop', e: 'outBack' });
    const txt = 'buatin aplikasi';
    r.bt.textContent = txt.slice(0, Math.round(clamp((t - 0.15) / 0.7) * txt.length));
    r.car.style.opacity = Math.sin(t * 12) > 0 ? 1 : 0;
    const tp = ctx.word('abang'), tm = ctx.word('makanan'), tg = ctx.word('bingung');
    enter(r.prn, t, tp - 0.5, { from: 'up', dist: 120 });
    const pr = p(t, tp - 0.2, tm + 0.3, 'outCubic');
    css(r.rcp, { y: lerp(-660, 0, pr) + Math.sin(t * 40) * 2 * (pr > 0 && pr < 1), r: lerp(0, 2.5, p(t, tg, tg + 0.4, 'outBack')) });
    const mk = p(t, tm, tm + 0.25, 'outBackBig');
    r.mk.style.background = mk > 0 ? `rgba(251,191,36,${0.9 * clamp(mk)})` : 'transparent';
    r.q.forEach((q, i) => enter(q, t, tg + i * 0.1, { from: 'pop', extra: { r: [-14, 12, -8][i] + Math.sin(t * 3 + i) * 6 } }));
  },
  cam: (t, ctx) => {
    const tp = ctx.word('abang'), tg = ctx.word('bingung');
    const k = p(t, tp - 0.6, tp + 0.1, 'inOutExpo');
    return { y: lerp(-240, 50, k), z: lerp(1.12, 1.04, k) + 0.06 * p(t, tg, tg + 0.25, 'outExpo'), r: lerp(0, -1.8, p(t, tg, tg + 0.5)) };
  },
});

/* ============ 3. JUDUL — 5 tips ============ */
E.scene({
  id: 'judul',
  at: { x: 1700, y: 2400 },
  transStyle: 'zoom',
  build(el) {
    const cols = ['#2563EB', '#FBBF24', '#10B981', '#3B82F6', '#0F172A'];
    const fan = cols.map((c, i) => `<div class="fan" data-r="fc[]" style="background:${c}"><b>0${i + 1}</b><i style="top:110px;width:60%"></i><i style="top:150px;width:40%"></i></div>`).join('');
    el.innerHTML = `${fan}
      <div class="big5" data-r="five">5</div>
      <div class="ttl1" data-r="t1">TIPS</div>
      <div class="ttl2" data-r="t2"><span style="color:#0F172A">VIBE</span> <span style="color:${C.blue}">CODING</span></div>`;
  },
  update(r, t, ctx) {
    const tl = ctx.word('lima'), tv = ctx.word('vibe');
    r.fc.forEach((c, i) => {
      const k = E.spring(t, tl + 0.05 + i * 0.04, { freq: 1.6, damp: 7 });
      css(c, { x: (i - 2) * 150 * k, y: Math.abs(i - 2) * 40 * k, r: (i - 2) * 11 * k, o: p(t, tl, tl + 0.2, 'linear') * 0.9 });
    });
    enter(r.five, t, tl - 0.05, { from: 'zoom', dur: 0.45 });
    enter(r.t1, t, tv - 0.15, { from: 'up', dist: 60 });
    enter(r.t2, t, tv, { from: 'up', dist: 90 });
  },
  cam: (t, ctx) => {
    const tl = ctx.word('lima');
    return { z: lerp(1.2, 1.0, p(t, 0, 0.8, 'outExpo')) + 0.08 * p(t, tl, tl + 0.2, 'outExpo') + 0.03 * p(t, tl, ctx.d, 'linear'),
      y: lerp(-60, 40, p(t, 0, ctx.d, 'inOutCubic')), r: lerp(-1, 1, p(t, 0, ctx.d, 'inOutCubic')) };
  },
});

/* ============ 4. TIP 1 — konteks ============ */
const CHIPS = [['Laravel', C.blue, 'framework', 40, 170], ['Tailwind', '#06B6D4', 'framework', 270, 170],
  ['validasi email', C.amber, 'fitur', 40, 270], ['remember me', '#A78BFA', 'fitur', 410, 270],
  ['sukses → /dashboard', C.green, 'hasil', 40, 370]];
E.scene({
  id: 'konteks',
  at: { x: 3300, y: 2200 },
  sfx: ctx => [[ctx.word('hasil') + 0.2, 'ding', 0.5]],
  build(el) {
    el.innerHTML = `${tipHead(1, 'KONTEKS', C.blue)}
      <div class="card pcard" data-r="pc"><div class="top"><span class="lbl">Prompt</span></div>
        <div class="txt mono">buatin login<span data-r="more" class="muted"></span></div>
        ${CHIPS.map(([n, c, , x, y]) => `<div class="chip" data-r="chip[]" style="left:${x}px;top:${y}px;background:${c}26;border:3px solid ${c};box-shadow:0 6px 0 ${c}">${n}</div>`).join('')}
      </div>
      <div class="card meter" data-r="mt"><span class="lbl">Kejelasan prompt</span><b class="pct mono" data-r="pct">18%</b>
        <div class="bar"><i data-r="bar"></i></div></div>`;
  },
  update(r, t, ctx) {
    tipHeadIn(r, t);
    const tk = ctx.word('konteks');
    enter(r.pc, t, 0.35, { from: 'up', dist: 120 });
    r.pc.style.height = lerp(200, 490, p(t, tk, tk + 0.5, 'outExpo')) + 'px';
    let v = 0.18;
    CHIPS.forEach(([, , w], i) => {
      const at = ctx.word(w) + (i % 2) * 0.12;
      enter(r.chip[i], t, at, { from: 'right', dist: 700, dur: 0.55, extra: { r: (1 - p(t, at, at + 0.55, 'outExpo')) * 12 } });
      if (t > at) v = [0.34, 0.5, 0.66, 0.8, 0.96][i];
    });
    enter(r.mt, t, tk + 0.2, { from: 'up', dist: 80 });
    const vv = lerp(0.18, v, 1); // step
    r.bar.style.transform = `scaleX(${vv})`;
    r.bar.style.background = E.mix('EF4444', '10B981', (vv - 0.18) / 0.78);
    r.pct.textContent = Math.round(vv * 100) + '%';
    r.pct.style.color = E.mix('EF4444', '10B981', (vv - 0.18) / 0.78);
  },
  cam: (t, ctx) => {
    const th = ctx.word('hasil'), tk = ctx.word('konteks');
    const k = p(t, th - 0.6, th, 'inOutExpo');
    return { y: lerp(-50, 20, k), z: 1.04 + 0.06 * p(t, tk, tk + 0.2, 'outExpo') - 0.03 * k };
  },
});

/* ============ 5. TIP 2 — pecah jadi langkah kecil ============ */
const STEPS = [['Database produk', C.blue], ['Form transaksi', C.amber], ['Laporan harian', C.green]];
E.scene({
  id: 'kecil',
  at: { x: 4800, y: 2500 },
  build(el) {
    const half = side => `<div class="block" data-r="${side}" style="clip-path:${side === 'bl'
      ? 'polygon(0 0,52% 0,46% 28%,55% 52%,44% 76%,50% 100%,0 100%)' : 'polygon(52% 0,100% 0,100% 100%,50% 100%,44% 76%,55% 52%,46% 28%)'}"><b>APP KASIR</b><small>1 PROMPT RAKSASA</small></div>`;
    el.innerHTML = `${tipHead(2, 'LANGKAH KECIL', C.amber)} ${half('bl')}${half('br')}
      ${STEPS.map(([s, c], i) => `<div class="card step" data-r="st[]" style="left:${100 + i * 100}px;top:${600 + i * 200}px"><div class="n" style="background:${c}">${i + 1}</div>${s}<div class="ck" data-r="ck[]">${CHECK}</div></div>`).join('')}`;
  },
  update(r, t, ctx) {
    tipHeadIn(r, t);
    const tk = ctx.word('kecil');
    [r.bl, r.br].forEach((b, s) => {
      const q = p(t, tk, tk + 0.55, 'inCubic'), dir = s ? 1 : -1;
      enter(b, t, 0.3, { from: 'pop', e: 'outBack', extra: { x: dir * q * 520 + noise(t * 30, s) * 8 * p(t, tk - 0.4, tk), r: dir * q * 25, o: 1 - p(t, tk + 0.25, tk + 0.55, 'linear') } });
    });
    const t1 = ctx.word('satu', 0), t2 = ctx.word('tugas');
    r.st.forEach((s, i) => enter(s, t, tk + 0.25 + i * 0.14, { from: 'drop', dist: 900 }));
    r.tick.forEach((tk2, i) => {
      const at = lerp(t1, t2 + 0.1, i / 2);
      const k = p(t, at, at + 0.3, 'outCubic');
      tk2.style.strokeDashoffset = 1 - k;
      r.ck[i].style.background = k > 0 ? C.green : 'transparent';
      r.ck[i].style.borderColor = k > 0 ? C.green : '#E2E8F0';
      css(r.ck[i], { s: 1 + 0.3 * Math.sin(p(t, at, at + 0.3) * Math.PI) });
    });
  },
  cam: (t, ctx) => {
    const tk = ctx.word('kecil');
    return { z: 1.03 + 0.1 * p(t, tk, tk + 0.18, 'outExpo') - 0.07 * p(t, tk + 0.3, tk + 1.2, 'inOutCubic') + 0.03 * p(t, tk, ctx.d, 'linear'),
      y: lerp(-60, 20, p(t, tk + 0.2, tk + 1.2, 'inOutExpo')), r: lerp(1.5, -1, p(t, 0, ctx.d, 'inOutCubic')) };
  },
});

/* ============ 6. TIP 3 — file aturan main ============ */
const RULES = [['# Aturan main', '#64748B'], ['- Pakai TypeScript', '#E2E8F0'], ['- Ikuti folder /src', '#E2E8F0'], ['- Jangan sentuh .env', '#FDA4AF'], ['- Tiap fitur ada test', '#E2E8F0']];
const BOT = `<svg viewBox="0 0 190 190"><line x1="95" y1="8" x2="95" y2="34" stroke="#60A5FA" stroke-width="8" stroke-linecap="round"/><circle cx="95" cy="10" r="10" fill="#FBBF24"/>
  <rect x="15" y="34" width="160" height="140" rx="44" fill="#3B82F6"/><rect x="38" y="70" width="114" height="70" rx="30" fill="#0B1533"/>
  <g data-r="eyes"><circle cx="72" cy="105" r="13" fill="#6EE7B7"/><circle cx="118" cy="105" r="13" fill="#6EE7B7"/></g></svg>`;
E.scene({
  id: 'aturan',
  at: { x: 6300, y: 2200 },
  build(el) {
    el.innerHTML = `${tipHead(3, 'ATURAN MAIN', C.green)}
      <div class="card dark ed2" data-r="ed"><div class="edbar"><i></i><i></i><i></i></div><div class="tab">AGENTS.md</div>
        <div class="code">${RULES.map(([s, c]) => `<div data-r="rl[]" style="color:${c}"></div>`).join('')}</div>
        <div class="scan" data-r="scan"></div></div>
      <div class="bot" data-r="bot">${BOT}</div>
      ${['inget ya, pakai TS', 'inget, folder /src!', 'jangan sentuh .env...'].map((s, i) => `<div class="rem" data-r="rem[]" style="top:${1040 + i * 88}px">${s}<s data-r="sk[]"></s></div>`).join('')}`;
  },
  update(r, t, ctx) {
    tipHeadIn(r, t);
    enter(r.ed, t, 0.3, { from: 'up', dist: 120 });
    const ta = ctx.word('aturan');
    r.rl.forEach((l, i) => {
      const s = RULES[i][0], at = ta - 0.3 + i * 0.32;
      l.textContent = s.slice(0, Math.round(p(t, at, at + 0.3, 'linear') * s.length)) || ' ';
    });
    const tai = ctx.word('ai'), td = ctx.word('diingetin'), tt = ctx.word('terus');
    enter(r.bot, t, tai - 0.35, { from: 'pop' });
    const sk = p(t, tai, tai + 1.1, 'inOutCubic');
    r.scan.style.top = lerp(70, 470, sk) + 'px';
    r.scan.style.opacity = sk > 0 && sk < 1 ? 1 : 0;
    r.eyes.setAttribute('transform', `translate(${Math.sin(t * 5) * 6 * (sk > 0 && sk < 1)},${lerp(-8, 8, sk)})`);
    r.rem.forEach((m, i) => {
      enter(m, t, td - 0.1 + i * 0.12, { from: 'right', dist: 300 });
      const k = p(t, tt + i * 0.08, tt + 0.25 + i * 0.08, 'outCubic');
      r.sk[i].style.transform = `scaleX(${k})`;
      m.style.opacity = Math.min(parseFloat(m.style.opacity || 1), 1 - 0.55 * k);
    });
  },
  cam: (t, ctx) => {
    const tb = ctx.word('biar');
    const k = p(t, tb - 0.5, tb + 0.15, 'inOutExpo');
    return { y: lerp(-100, 30, k), z: lerp(1.06, 1.03, k) + 0.03 * p(t, 0, ctx.d, 'linear'), x: lerp(0, -20, k) };
  },
});

/* ============ 7. TIP 4 — cek rute dulu ============ */
const WRONG = [[120, 600], [120, 420], [420, 420], [420, 660], [700, 660]];
const RIGHT = [[120, 600], [120, 420], [300, 420], [300, 220], [560, 220], [560, 150], [700, 150]];
const pts = a => a.map(q => q.join(',')).join(' ');
E.scene({
  id: 'rencana',
  at: { x: 7800, y: 2500 },
  sfx: ctx => [[ctx.word('jalan') + 0.1, 'ding', 0.5]],
  build(el) {
    let streets = '';
    for (let x = 60; x < 860; x += 120) streets += `<line x1="${x}" y1="0" x2="${x}" y2="740" stroke="#DCE5F7" stroke-width="18"/>`;
    for (let y = 80; y < 740; y += 120) streets += `<line x1="0" y1="${y}" x2="860" y2="${y}" stroke="#DCE5F7" stroke-width="18"/>`;
    el.innerHTML = `${tipHead(4, 'RENCANA', C.blue)}
      <div class="card map" data-r="map"><svg viewBox="0 0 860 740">${streets}
        <polyline data-r="wr" points="${pts(WRONG)}" pathLength="1" fill="none" stroke="#F43F5E" stroke-width="14" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1"/>
        <g data-r="x" transform="translate(700 660)"><path d="M-26-26L26 26M26-26L-26 26" stroke="#F43F5E" stroke-width="14" stroke-linecap="round"/></g>
        <polyline data-r="rt" points="${pts(RIGHT)}" pathLength="1" fill="none" stroke="#10B981" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1"/>
        <circle cx="120" cy="600" r="24" fill="#3B82F6" stroke="#fff" stroke-width="6"/>
        <g data-r="pinB" transform="translate(700 150)"><path d="M0 0C-34-40-40-60-40-74a40 40 0 0 1 80 0C40-60 34-40 0 0z" fill="#FBBF24"/><circle cy="-74" r="15" fill="#fff"/></g>
        <circle data-r="dot" r="18" fill="#0F172A" stroke="#fff" stroke-width="6"/>
      </svg><div class="pill2" data-r="pl">PLAN DULU</div></div>`;
  },
  update(r, t, ctx) {
    tipHeadIn(r, t);
    enter(r.map, t, 0.3, { from: 'up', dist: 120 });
    enter(r.pl, t, 0.6, { from: 'pop' });
    const tr = ctx.word('rencananya'), tru = ctx.word('rute'), tj = ctx.word('jalan');
    r.wr.style.strokeDashoffset = 1 - p(t, tr - 0.1, tr + 0.6, 'inOutCubic');
    const xk = E.ease.outBackBig(clamp((t - tr - 0.7) / 0.3));
    r.x.setAttribute('transform', `translate(700 660) scale(${xk})`);
    r.wr.style.opacity = 1 - 0.7 * p(t, tru - 0.2, tru, 'linear');
    r.x.style.opacity = 1 - 0.7 * p(t, tru - 0.2, tru, 'linear');
    const g = p(t, tru - 0.1, tj + 0.1, 'inOutCubic');
    r.rt.style.strokeDashoffset = 1 - g;
    const [dx, dy] = along(RIGHT, g);
    r.dot.setAttribute('cx', dx); r.dot.setAttribute('cy', dy);
    r.dot.style.opacity = t > tru - 0.1 ? 1 : 0;
    const bk = 1 + 0.25 * Math.sin(p(t, tj + 0.1, tj + 0.45) * Math.PI);
    r.pinB.setAttribute('transform', `translate(700 150) scale(${bk})`);
  },
  cam: (t, ctx) => {
    const tru = ctx.word('rute'), tj = ctx.word('jalan');
    const [dx, dy] = along(RIGHT, p(t, tru - 0.1, tj + 0.1, 'inOutCubic'));
    const f = p(t, tru - 0.6, tru, 'inOutCubic');
    return { x: (dx - 430) * 0.15 * f, y: lerp(-40, (dy - 370) * 0.12 + 40, f), z: lerp(1.03, 1.08, f) };
  },
});

/* ============ 8. TIP 5 — review, bukan autopilot ============ */
E.scene({
  id: 'review',
  at: { x: 9300, y: 2200 },
  hits: ctx => [ctx.word('autopilot')],
  build(el) {
    el.innerHTML = `${tipHead(5, 'REVIEW', C.green)}
      <div class="card diff" data-r="df"><div class="fn">LoginController.php</div>
        <div class="dl m" data-r="dl[]">- if ($user) {</div><div class="dl p" data-r="dl[]">+ if ($user?->isActive()) {</div></div>
      <div class="commit" data-r="cm">✓ committed</div>
      <div class="card tests" data-r="ts"><span class="lbl">Tests</span><b class="mono green" data-r="tn" style="position:absolute;right:34px;top:20px;font-size:40px">0/12</b>
        <div class="bar"><i data-r="tb"></i></div></div>
      <div class="card toggles" data-r="tg">
        <div class="tg"><span data-r="pl1">PARTNER</span><div class="sw" data-r="sw1"><i data-r="k1"></i></div></div>
        <div class="tg"><span data-r="pl2">AUTOPILOT</span><div class="sw" data-r="sw2"><i data-r="k2"></i></div></div></div>`;
  },
  update(r, t, ctx) {
    tipHeadIn(r, t);
    const trv = ctx.word('review'), tt = ctx.word('test'), tc = ctx.word('commit'), tp = ctx.word('partner'), ta = ctx.word('autopilot');
    enter(r.df, t, 0.3, { from: 'up', dist: 120 });
    r.dl.forEach((d, i) => enter(d, t, trv + i * 0.15, { from: 'left', dist: 60 }));
    enter(r.ts, t, tt - 0.25, { from: 'up', dist: 80 });
    const tk = p(t, tt, tc + 0.1, 'inOutCubic');
    r.tb.style.transform = `scaleX(${tk})`; r.tn.textContent = Math.round(12 * tk) + '/12';
    enter(r.cm, t, tc + 0.05, { from: 'pop', extra: { r: -4 } });
    enter(r.tg, t, tp - 0.7, { from: 'up', dist: 100 });
    const on1 = p(t, tp, tp + 0.25, 'outBack'), off2 = p(t, ta, ta + 0.25, 'outBack');
    css(r.k1, { x: 70 * on1 }); r.sw1.style.background = E.mix('CBD5E1', '10B981', on1);
    css(r.k2, { x: 70 * (1 - off2) }); r.sw2.style.background = E.mix('2563EB', 'CBD5E1', off2);
    r.pl1.style.color = E.mix('94A3B8', '0F172A', on1);
    r.pl2.style.color = E.mix('0F172A', '94A3B8', off2);
    r.pl2.style.textDecoration = off2 > 0.5 ? 'line-through' : 'none';
  },
  cam: (t, ctx) => {
    const tp = ctx.word('partner'), ta = ctx.word('autopilot');
    const k = p(t, tp - 0.8, tp - 0.1, 'inOutExpo');
    return { y: lerp(-60, 25, k), z: 1.03 + 0.08 * p(t, ta, ta + 0.2, 'outExpo') };
  },
});

/* ============ 9. SOFT SELLING — AGJ Labs ============ */
const SVC = [['Website & Web App', 'Company profile, dashboard, sistem', C.blue,
  `<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.8 3 2.8 15 0 18M12 3c-2.8 3-2.8 15 0 18"/></svg>`],
  ['Aplikasi Mobile', 'Android & iOS', C.amber,
  `<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2"><rect x="6" y="2.5" width="12" height="19" rx="3"/><path d="M10.5 18.5h3"/></svg>`],
  ['AI & Otomasi', 'Chatbot, workflow otomatis', C.green,
  `<svg width="48" height="48" viewBox="0 0 24 24" fill="#fff"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg>`]];
E.scene({
  id: 'jasa',
  at: { x: 9300, y: -300 },
  transStyle: 'zoom',
  sfx: ctx => [[ctx.word('agj'), 'pop', 0.6]],
  build(el) {
    const rays = Array.from({ length: 10 }, (_, i) => `<line x1="250" y1="40" x2="250" y2="90" transform="rotate(${i * 36} 250 250)" stroke="#FBBF24" stroke-width="12" stroke-linecap="round"/>`).join('');
    el.innerHTML = `
      <svg class="rays" data-r="rays" viewBox="0 0 500 500">${rays}</svg>
      <svg class="bulb" data-r="bulb" viewBox="0 0 300 360">
        <path data-r="glass" d="M150 20a110 110 0 0 0-70 195c18 16 26 32 26 50h88c0-18 8-34 26-50A110 110 0 0 0 150 20z" fill="#E2E8F0" stroke="#0F172A" stroke-width="10"/>
        <rect x="106" y="280" width="88" height="22" rx="10" fill="#94A3B8"/><rect x="114" y="310" width="72" height="22" rx="10" fill="#64748B"/>
        <path d="M120 200l30-50 30 50" fill="none" stroke="#0F172A" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" data-r="fil"/></svg>
      <div class="card cal" data-r="cal"><span class="lbl">Jadwal kamu minggu ini</span><div class="grid">${Array.from({length:21},()=>'<i data-r="cell[]"></i>').join('')}</div></div>
      <div class="agjpill" data-r="ap"><img src="icon.png">AGJ Labs</div>
      ${SVC.map(([n, s, c, ic], i) => `<div class="card svc" data-r="sv[]" style="top:${800 + i * 160}px"><div class="ic" style="background:${c}">${ic}</div><div><b>${n}</b><small>${s}</small></div></div>`).join('')}`;
  },
  update(r, t, ctx) {
    const ti = ctx.word('ide'), ts = ctx.word('sempat'), tg = ctx.word('agj');
    enter(r.bulb, t, 0.05, { from: 'pop', e: 'outBack' });
    const lit = p(t, ti, ti + 0.3) * (1 - 0.8 * (p(t, ts, ts + 0.1, 'linear') - p(t, ts + 0.5, ts + 0.6, 'linear')) * (Math.sin(t * 40) > 0)) ;
    const full = Math.max(lit, p(t, tg - 0.1, tg + 0.2));
    r.glass.setAttribute('fill', E.mix('E2E8F0', 'FBBF24', full));
    r.fil.setAttribute('stroke', E.mix('94A3B8', 'FFFFFF', full));
    css(r.rays, { s: lerp(0.6, 1, full) + 0.04 * Math.sin(t * 6), r: t * 12, o: full });
    enter(r.cal, t, ti + 0.2, { from: 'up', dist: 120, extra: { y: -200 * p(t, tg - 0.1, tg + 0.3, 'inCubic') } });
    r.cal.style.opacity = Math.min(parseFloat(r.cal.style.opacity), 1 - p(t, tg - 0.1, tg + 0.2, 'linear'));
    r.cell.forEach((c, i) => { const at = ts - 0.2 + rand(i, 9) * 0.9; const k = p(t, at, at + 0.15, 'linear');
      c.style.background = k > 0 ? E.mix('EDF2FB', i % 4 ? 'EF4444' : 'FBBF24', k) : '#EDF2FB'; });
    enter(r.ap, t, tg - 0.05, { from: 'pop' });
    r.sv.forEach((s, i) => {
      const at = tg + 0.25 + i * 0.16, k = p(t, at, at + 0.6, 'outExpo');
      css(s, { x: lerp(0, 0, k), y: lerp(-420 - i * 160, 0, k), s: lerp(0.3, 1, k), o: p(t, at, at + 0.2, 'linear') });
    });
  },
  cam: (t, ctx) => {
    const tg = ctx.word('agj');
    const k = p(t, tg - 0.3, tg + 0.5, 'inOutExpo');
    return { z: lerp(1.18, 1.05, p(t, 0, 0.9, 'outExpo')) - 0.03 * k, y: lerp(-130, 40, k) };
  },
});

/* ============ 10. CTA ============ */
const HAND = `<svg viewBox="0 0 24 24"><path d="M9 11V4.5a1.5 1.5 0 0 1 3 0V10l.5-.1a1.5 1.5 0 0 1 2.5.6l.2-.1a1.5 1.5 0 0 1 2.3 1l.2-.1a1.5 1.5 0 0 1 2.3 1.3V16a6 6 0 0 1-6 6h-1a6 6 0 0 1-4.6-2.2L4.6 15.6a1.6 1.6 0 0 1 2.3-2.2L9 15z" fill="#fff" stroke="#0F172A" stroke-width="1.2" stroke-linejoin="round"/></svg>`;
E.scene({
  id: 'cta',
  at: { x: 10900, y: -100 },
  sfx: ctx => [[ctx.word('save') + 0.55, 'pop', 0.6]],
  build(el) {
    el.innerHTML = `
      <div class="logo" data-r="lg"><img src="stacked.png"></div>
      <div class="savebtn" data-r="sb"><svg width="54" height="54" viewBox="0 0 24 24" fill="#fff"><path d="M6 3h12v18l-6-4.5L6 21z"/></svg><span data-r="sbt">Save</span></div>
      <div class="hand" data-r="hd">${HAND}</div>
      <div class="follow" data-r="fl">+ Follow <span class="blue">@agjlabs</span></div>`;
  },
  update(r, t, ctx) {
    const tsv = ctx.word('save'), tf = ctx.word('follow');
    enter(r.lg, t, 0.0, { from: 'zoom', dur: 0.6 });
    enter(r.sb, t, tsv - 0.1, { from: 'up', dist: 120 });
    const tap = tsv + 0.55, tk = p(t, tap, tap + 0.12) - p(t, tap + 0.12, tap + 0.3);
    const done = t > tap + 0.1;
    r.sb.style.background = done ? C.green : C.blue;
    r.sb.style.boxShadow = `0 ${12 - 8 * tk}px 0 ${done ? '#047857' : '#1E40AF'}, 0 30px 60px rgba(0,0,0,.4)`;
    r.sbt.textContent = done ? 'Tersimpan' : 'Save';
    css(r.sb, { y: 8 * tk, o: p(t, tsv - 0.1, tsv + 0.1, 'linear') });
    const hk = p(t, tsv + 0.1, tap, 'outCubic');
    css(r.hd, { x: lerp(320, 0, hk), y: lerp(380, 0, hk) + 10 * tk, s: 1 - 0.12 * tk, o: hk * (1 - p(t, tap + 0.5, tap + 0.8, 'linear')) });
    enter(r.fl, t, tf - 0.05, { from: 'pop' });
  },
  cam: (t, ctx) => ({ z: lerp(1.14, 1.0, p(t, 0, 1.0, 'outExpo')) + 0.04 * p(t, 1, ctx.d, 'linear'), y: lerp(-80, 30, p(t, 0, ctx.d, 'inOutCubic')) }),
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
