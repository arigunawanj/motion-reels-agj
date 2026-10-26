/* Website lemot = customer kabur — AGJ Labs
 * Semua timing diambil dari kata di VO via ctx.word('...') supaya visual sinkron suara. */

const { p, lerp, clamp, css, enter, noise, rand, ease } = E;

/* ============ 1. HOOK ============ */
E.scene({
  id: 'hook',
  at: { x: 0, y: 0 },
  hits: ctx => [ctx.word('setengah')],
  sfx: ctx => [[ctx.word('kabur'), 'whoosh'], [ctx.wordEnd('detik'), 'ding']],
  build(el) {
    const ppl = Array.from({ length: 10 }, (_, i) =>
      `<div class="person" data-r="ppl[]" style="left:${70 + (i % 5) * 112}px;top:${i < 5 ? 0 : 120}px;background:${['#c6ff3d','#ff3d7f','#3da9ff','#ff8a1f','#8b5cff'][i % 5]}"><i></i></div>`).join('');
    el.innerHTML = `
      <div class="card phone" data-r="phone">
        <div class="url"><span class="lock">●</span> tokokamu.id</div>
        <div class="load"><i data-r="bar"></i></div>
        <div class="spin" data-r="spin"></div>
        <div class="timer mono" data-r="timer">0.0s</div>
        <div class="ppl">${ppl}</div>
      </div>
      <div class="stamp" data-r="stamp"><b>53%</b><span>PENGUNJUNG KABUR</span></div>`;
  },
  update(r, t, ctx) {
    const tEnd = ctx.wordEnd('detik') + 0.2;
    const k = p(t, 0, tEnd, 'linear');
    r.timer.textContent = (3 * k).toFixed(1) + 's';
    r.timer.style.color = E.mix('f5f5f7', 'ff3b47', p(t, tEnd * 0.5, tEnd));
    r.bar.style.transform = `scaleX(${0.08 + 0.55 * ease.outCubic(k) - 0.02 * Math.sin(t * 9) * k})`;
    css(r.spin, { r: t * 420 });
    const tk = ctx.word('kabur');
    r.ppl.forEach((el, i) => {
      const at = tk + i * 0.04, q = p(t, at, at + 0.7, 'inCubic');
      const dir = i % 2 ? 1 : -1;
      css(el, { x: dir * q * (600 + rand(i) * 300), y: -q * (500 + rand(i, 2) * 700), r: dir * q * 300,
        s: 1 + 0.3 * Math.sin(p(t, at, at + 0.25) * Math.PI), o: 1 - p(t, at + 0.4, at + 0.7, 'linear') });
    });
    const ts = ctx.word('setengah');
    enter(r.stamp, t, ts, { from: 'zoom', dur: 0.35, e: 'outExpo', extra: { r: -9 } });
  },
  cam: (t, ctx) => {
    const ts = ctx.word('setengah');
    return {
      y: lerp(-90, 0, p(t, 0, 1.4, 'outExpo')),
      z: lerp(1.5, 1, p(t, 0, 1.4, 'outExpo')) + 0.12 * p(t, ts, ts + 0.2, 'outExpo') - 0.05 * p(t, ts + 0.2, ctx.d, 'inOutCubic'),
    };
  },
});

/* ============ 2. CHAT GEBETAN ============ */
const HEART = `<svg viewBox="0 0 100 90" width="100%" height="100%"><path d="M50 88 C20 65 0 48 0 26 C0 10 12 0 27 0 C38 0 46 6 50 14 C54 6 62 0 73 0 C88 0 100 10 100 26 C100 48 80 65 50 88Z" fill="#ff3d7f"/></svg>`;
E.scene({
  id: 'chat',
  at: { x: 1500, y: -300 },
  hits: ctx => [ctx.word('ilfeel')],
  sfx: ctx => [[0.35, 'pop'], [ctx.word('centang') + 0.1, 'tick'], [ctx.word('centang') + 0.25, 'tick'], [ctx.word('ilfeel') - 0.05, 'glitch']],
  build(el) {
    el.innerHTML = `
      <div class="card chat" data-r="chat">
        <div class="chead"><div class="ava">😍</div><div><b>doi 💘</b><small data-r="status">online</small></div></div>
        <div class="bub me" data-r="bub">lagi apa? 👀<span class="meta"><span data-r="clock">20.02</span> <span class="ck" data-r="ck">✓✓</span></span></div>
        <div class="bub them typing" data-r="typing"><i></i><i></i><i></i></div>
      </div>
      <div class="bigclock mono" data-r="big">20.02</div>
      <div class="heart">
        <div class="hh l" data-r="hl">${HEART}</div><div class="hh r" data-r="hr">${HEART}</div>
      </div>
      <div class="ilfeel h-xl" data-r="ilf">ILFEEL<span class="pink">.</span></div>`;
  },
  update(r, t, ctx) {
    enter(r.chat, t, 0, { from: 'up', dist: 200 });
    enter(r.bub, t, 0.3, { from: 'pop', e: 'outBack' });
    const tc = ctx.word('centang'), tb = ctx.word('dibales'), ti = ctx.word('ilfeel');
    r.ck.style.opacity = t > tc ? 1 : 0;
    // jam berjalan cepat: 20.02 → 23.47
    const mins = Math.floor(lerp(2, 225, p(t, tc + 0.3, ti, 'inQuad')));
    const hm = `${20 + Math.floor(mins / 60)}.${String(mins % 60).padStart(2, '0')}`;
    r.clock.textContent = hm; r.big.textContent = hm;
    enter(r.big, t, tc + 0.3, { from: 'down', dist: 60 });
    r.big.style.color = E.mix('8b8b9a', 'ff3b47', p(t, tc + 0.3, ti));
    // "sedang mengetik..." muncul lalu hilang (PHP 😭)
    const ty = E.io(t, tc + 0.5, tc + 0.7, tb + 0.1, tb + 0.3);
    css(r.typing, { s: ty, o: ty });
    r.typing.querySelectorAll('i').forEach((d, i) => (d.style.transform = `translateY(${-10 * Math.max(0, Math.sin(t * 9 - i))}px)`));
    r.status.textContent = t > tb + 0.2 ? 'terakhir dilihat 20.03' : t > tc + 0.5 ? 'sedang mengetik…' : 'online';
    // hati retak
    const hk = p(t, ti, ti + 0.6, 'outExpo');
    const hp = enter(r.hl.parentElement, t, tb + 0.1, { from: 'pop', extra: { s: 1 + 0.06 * Math.sin(t * 8) * (1 - hk) } });
    css(r.hl, { x: -hk * 70, y: hk * 40, r: -hk * 22 });
    css(r.hr, { x: hk * 70, y: hk * 40, r: hk * 22 });
    enter(r.ilf, t, ti, { from: 'zoom', dur: 0.3, extra: { skx: noise(t * 40) * 12 * (1 - p(t, ti, ti + 0.4)), x: noise(t * 50, 2) * 20 * (1 - p(t, ti, ti + 0.4)) } });
  },
  cam: (t, ctx) => {
    const ti = ctx.word('ilfeel');
    const k = p(t, ti - 0.5, ti + 0.1, 'inOutExpo');
    return { y: lerp(-180, 240, k), z: lerp(1.18, 1.05, k) + 0.03 * p(t, 0, ti, 'linear'), r: lerp(-1.5, 1, k) };
  },
});

/* ============ 3. 3 TERSANGKA ============ */
E.scene({
  id: 'tersangka',
  at: { x: 1500, y: 2300 },
  transStyle: 'zoom',
  handheld: 1.6,
  hits: ctx => [ctx.word('tiga')],
  sfx: ctx => [[0.05, 'riser']],
  build(el) {
    const tape = Array(14).fill('TERSANGKA ⚠ ').join('');
    el.innerHTML = `
      <div class="tape t1" data-r="t1" data-qc="ignore"><span>${tape}</span></div>
      <div class="tape t2" data-r="t2" data-qc="ignore"><span>${tape}</span></div>
      <div class="center"><div class="h-mega lime glow-lime" data-r="three" style="font-size:520px">3</div>
      <div class="h-m" data-r="lbl">PELAKU UTAMA</div></div>`;
  },
  update(r, t, ctx) {
    const tt = ctx.word('tiga');
    css(r.t1, { x: lerp(-1400, 0, p(t, 0, 0.6, 'outExpo')), r: -12 });
    css(r.t2, { x: lerp(1400, 0, p(t, 0.15, 0.75, 'outExpo')), r: 9 });
    r.t1.firstChild.style.transform = `translateX(${-t * 120}px)`;
    r.t2.firstChild.style.transform = `translateX(${t * 120 - 400}px)`;
    enter(r.three, t, tt, { from: 'zoom', dur: 0.35 });
    enter(r.lbl, t, tt + 0.25, { from: 'up', dist: 50 });
  },
  cam: (t, ctx) => ({ z: 1.08 + 0.1 * p(t, ctx.word('tiga'), ctx.d, 'outCubic'), r: lerp(3, -2, p(t, 0, ctx.d, 'inOutCubic')) }),
});

/* ============ 4. GAMBAR 8MB ============ */
E.scene({
  id: 'gambar',
  at: { x: 3000, y: 2100 },
  hits: ctx => [ctx.word('lemari') + 0.15],
  sfx: ctx => [[ctx.word('delapan'), 'pop']],
  build(el) {
    el.innerHTML = `
      <div class="num h-l" data-r="num"><span class="lime">01</span></div>
      <div class="card file" data-r="file">
        <div class="ficon">JPG</div>
        <div class="finfo"><b>produk-final-fix-<br>banget2.jpg</b>
          <div class="fbar"><i data-r="fb"></i></div>
          <div class="fsize mono" data-r="fs">0.0 MB</div></div>
      </div>
      <div class="road" data-r="road"></div>
      <div class="moto" data-r="moto">
        <div class="lemari" data-r="lem"><i></i><i></i><b>8.4 MB</b></div>
        <div class="rider">🧑‍🦱</div>
        <div class="mbody"></div><div class="wheel w1" data-r="w1"></div><div class="wheel w2" data-r="w2"></div>
      </div>`;
  },
  update(r, t, ctx) {
    const t8 = ctx.word('delapan'), tl = ctx.word('lemari');
    enter(r.num, t, 0, { from: 'left', dist: 100 });
    enter(r.file, t, 0.15, { from: 'up' });
    const k = p(t, 0.5, t8 + 0.3, 'inQuad');
    r.fs.textContent = (8.4 * k).toFixed(1) + ' MB';
    r.fs.style.color = E.mix('c6ff3d', 'ff3b47', k);
    r.fb.style.width = 100 * k * 1.6 + '%';
    r.fb.style.background = E.mix('c6ff3d', 'ff3b47', k);
    // motor masuk dari kiri, lemari goyang
    const mk = p(t, tl - 0.6, tl + 0.2, 'outExpo');
    const wob = Math.sin(t * 7) * 7 * (0.4 + p(t, tl, tl + 0.3));
    css(r.moto, { x: lerp(-1100, 0, mk) + Math.sin(t * 3) * 10, y: Math.abs(Math.sin(t * 14)) * -6 });
    css(r.lem, { r: wob + (1 - mk) * -20, y: -Math.abs(wob) * 2 });
    css(r.w1, { r: t * 720 }); css(r.w2, { r: t * 720 });
    r.road.style.backgroundPosition = `${-t * 900}px 0`;
  },
  cam: (t, ctx) => {
    const k = p(t, ctx.word('lemari') - 1.0, ctx.word('lemari') - 0.3, 'inOutExpo');
    return { y: lerp(-180, 220, k), z: lerp(1.12, 1.02, k), x: lerp(0, 30, k) };
  },
});

/* ============ 5. PLUGIN NUMPUK ============ */
const PLUG = ['SEO Pro', 'Slider 3D', 'Popup Promo', 'Live Chat', 'Analytics', 'Analytics (lagi)', 'Countdown', 'Social Share', 'Page Builder', 'Wishlist'];
E.scene({
  id: 'plugin',
  at: { x: 4500, y: 2400 },
  hits: ctx => [ctx.word('ditutup')],
  sfx: ctx => PLUG.filter((_, i) => i % 2 === 0).map((_, k) => [0.35 + 2 * k * (ctx.word('chrome') - 0.4) / PLUG.length, 'tick', 0.8]),
  build(el) {
    const tabs = Array.from({ length: 48 }, (_, i) => `<div class="tab" data-r="tab[]"><i></i></div>`).join('');
    const chips = PLUG.map((n, i) => `<div class="chip" data-r="chip[]" style="background:${['#c6ff3d','#ff3d7f','#3da9ff','#ff8a1f','#8b5cff'][i % 5]}">🧩 ${n}</div>`).join('');
    el.innerHTML = `
      <div class="num h-l" data-r="num"><span class="lime">02</span></div>
      <div class="stack">${chips}</div>
      <div class="card browser" data-r="br">
        <div class="tabs">${tabs}</div>
        <div class="ram"><span>RAM</span><div class="rbar"><i data-r="rb"></i></div><b class="mono" data-r="rp">12%</b></div>
      </div>`;
  },
  update(r, t, ctx) {
    enter(r.num, t, 0, { from: 'left', dist: 100 });
    const span = ctx.word('chrome') - 0.4;
    r.chip.forEach((c, i) => {
      const at = 0.35 + i * span / PLUG.length;
      const sway = Math.sin(t * 2.4 + i * 0.4) * (i * 0.9) * p(t, at, at + 0.4);
      enter(c, t, at, { from: 'drop', dist: 900, extra: { y: 0, r: (rand(i) - 0.5) * 10 + sway, x: sway * 3 } });
    });
    const tc = ctx.word('chrome'), td = ctx.word('ditutup');
    enter(r.br, t, tc - 0.3, { from: 'down', dist: 300 });
    const n = Math.max(1, Math.round(lerp(1, 48, p(t, tc, td, 'inQuad'))));
    r.tab.forEach((tb, i) => { tb.style.display = i < n ? 'block' : 'none'; });
    const ram = lerp(12, 99, p(t, tc, td + 0.2, 'inQuad'));
    r.rb.style.width = ram + '%';
    r.rb.style.background = E.mix('c6ff3d', 'ff3b47', ram / 100);
    r.rp.textContent = Math.round(ram) + '%';
    if (t > td) r.br.style.transform += ` translateX(${noise(t * 40) * 10}px)`;
  },
  cam: (t, ctx) => {
    const k = p(t, ctx.word('chrome') - 0.5, ctx.word('chrome') + 0.1, 'inOutExpo');
    return { y: lerp(40, -60, k), z: lerp(1.0, 1.07, k), r: lerp(1.5, -1, k) };
  },
});

/* ============ 6. HOSTING = ANGKOT ============ */
E.scene({
  id: 'hosting',
  at: { x: 5800, y: 1700 },
  hits: ctx => [ctx.word('angkot')],
  sfx: ctx => [[ctx.word('angkot'), 'pop'], [ctx.word('puluh'), 'pop']],
  build(el) {
    const heads = Array.from({ length: 30 }, (_, i) =>
      `<div class="head" data-r="head[]" style="left:${30 + (i % 10) * 62 + rand(i) * 14}px;top:${20 + Math.floor(i / 10) * 52 + rand(i, 3) * 10}px;background:${['#ffd6a5','#e0a370','#c68642','#8d5524'][i % 4]}"></div>`).join('');
    el.innerHTML = `
      <div class="num h-l" data-r="num"><span class="lime">03</span></div>
      <div class="card rack" data-r="rack">
        <div class="ru"><span class="led" data-r="led[]"></span>server-murah-01</div>
        <div class="ru"><span class="led" data-r="led[]"></span>CPU <b class="mono red" data-r="cpu">40%</b></div>
        <div class="ru"><span class="led" data-r="led[]"></span>1.247 website lain 😬</div>
      </div>
      <div class="angkot" data-r="ang">
        <div class="aroof">SHARED HOSTING</div>
        <div class="awin">${heads}</div>
        <div class="awheel a1" data-r="aw1"></div><div class="awheel a2" data-r="aw2"></div>
      </div>
      <div class="cnt mono" data-r="cnt">0 / 12 penumpang</div>
      <div class="slow" data-r="slow">🐢 2 km/jam</div>`;
  },
  update(r, t, ctx) {
    enter(r.num, t, 0, { from: 'left', dist: 100 });
    enter(r.rack, t, 0.1, { from: 'up' });
    const cpu = lerp(40, 100, p(t, 0.4, ctx.word('rame'), 'inQuad'));
    r.cpu.textContent = Math.round(cpu) + '%';
    r.led.forEach((l, i) => (l.style.background = cpu > 95 && Math.sin(t * 20 + i) > 0 ? '#ff3b47' : '#c6ff3d'));
    const ta = ctx.word('angkot');
    enter(r.ang, t, ta - 0.4, { from: 'right', dist: 1200 });
    const tp = ctx.word('puluh');
    const n = Math.round(lerp(0, 30, p(t, ta, tp + 0.3, 'linear')));
    r.head.forEach((h, i) => css(h, { s: i < n ? E.ease.outBackBig(clamp((t - ta - i * (tp + 0.3 - ta) / 30) * 6)) : 0 }));
    r.cnt.textContent = `${n} / 12 penumpang`;
    r.cnt.style.color = n > 12 ? '#ff3b47' : '#f5f5f7';
    const squish = n / 30;
    r.ang.style.transform += ` scale(${1 + squish * 0.06 + Math.sin(t * 12) * 0.01 * squish},${1 - squish * 0.05})`;
    css(r.aw1, { r: t * 60 }); css(r.aw2, { r: t * 60 });
    enter(r.cnt, t, ta, { from: 'up', dist: 40 });
    enter(r.slow, t, tp + 0.2, { from: 'pop' });
  },
  cam: (t, ctx) => {
    const k = p(t, ctx.word('angkot') - 0.6, ctx.word('angkot'), 'inOutExpo');
    return { y: lerp(-200, 150, k), z: lerp(1.15, 1.03, k) + 0.04 * p(t, ctx.word('puluh'), ctx.d) };
  },
});

/* ============ 7. SOLUSI + GAUGE ============ */
E.scene({
  id: 'solusi',
  at: { x: 4400, y: -200 },
  transStyle: 'zoom',
  hits: ctx => [ctx.word('naik')],
  sfx: ctx => [[ctx.word('webp'), 'ding'], [ctx.word('kepake'), 'ding'], [ctx.word('cache'), 'ding'], [ctx.word('skor') - 0.1, 'riser']],
  build(el) {
    const items = [['Kompres gambar → WebP', 'webp'], ['Buang plugin zombie', 'kepake'], ['Pasang cache + CDN', 'cache']];
    el.innerHTML = `
      <div class="h-l sol" data-r="ttl">FIX-NYA <span class="lime">.</span></div>
      <div class="card checks" data-r="card">${items.map(([s], i) => `
        <div class="ci" data-r="ci[]"><div class="box" data-r="box[]"><svg viewBox="0 0 24 24"><path data-r="tick[]" d="M4 12.5l5 5L20 6.5" pathLength="1"/></svg></div>${s}</div>`).join('')}
      </div>
      <div class="gauge" data-r="gauge">
        <svg viewBox="0 0 400 230"><path d="M30 210 A170 170 0 0 1 370 210" class="gtrack" pathLength="1"/>
          <path d="M30 210 A170 170 0 0 1 370 210" class="gval" data-r="gv" pathLength="1"/></svg>
        <div class="needle" data-r="nd"></div>
        <div class="score mono" data-r="sc">32</div>
        <div class="glbl">PageSpeed</div>
      </div>`;
    el.dataset.words = JSON.stringify(items.map(i => i[1]));
  },
  update(r, t, ctx) {
    enter(r.ttl, t, 0.05, { from: 'zoom', dur: 0.4 });
    enter(r.card, t, 0.2, { from: 'up' });
    ['webp', 'kepake', 'cache'].forEach((w, i) => {
      const at = ctx.word(w);
      enter(r.ci[i], t, 0.3 + i * 0.12, { from: 'left', dist: 80 });
      const k = p(t, at, at + 0.35, 'outCubic');
      r.tick[i].style.strokeDashoffset = 1 - k;
      r.box[i].style.background = k > 0 ? E.mix('15151f', 'c6ff3d', k) : '#15151f';
      css(r.box[i], { s: 1 + 0.25 * Math.sin(p(t, at, at + 0.3) * Math.PI) });
    });
    const tn = ctx.word('skor'), tk = ctx.word('naik');
    enter(r.gauge, t, tn - 0.35, { from: 'up', dist: 200 });
    const v = lerp(32, 94, p(t, tk - 0.1, tk + 0.9, 'outElastic'));
    const vc = clamp(v, 0, 100);
    r.sc.textContent = Math.round(lerp(32, 94, p(t, tk - 0.1, tk + 0.7, 'outCubic')));
    const col = vc < 50 ? '#ff3b47' : vc < 90 ? '#ff8a1f' : '#c6ff3d';
    r.sc.style.color = col; r.gv.style.stroke = col;
    r.gv.style.strokeDashoffset = 1 - vc / 100;
    r.nd.style.transform = `rotate(${-90 + 180 * vc / 100}deg)`;
    if (t > tk) ctx.flash = 0.25 * Math.exp(-(t - tk) * 6);
  },
  cam: (t, ctx) => {
    const k = p(t, ctx.word('skor') - 0.6, ctx.word('skor'), 'inOutExpo');
    return { y: lerp(-170, 240, k), z: lerp(1.1, 1.08, k) + 0.08 * p(t, ctx.word('naik'), ctx.word('naik') + 0.3, 'outExpo') };
  },
});

/* ============ 8. CTA ============ */
E.scene({
  id: 'cta',
  at: { x: 2800, y: -1900 },
  capY: 1240,
  hits: ctx => [ctx.word('roast') + 0.55],
  sfx: ctx => [[ctx.word('roast'), 'pop'], [ctx.word('roast') + 0.36, 'pop'], [ctx.word('nanti'), 'type'], [ctx.word('nanti') + 0.14, 'type'], [ctx.word('nanti') + 0.28, 'type']],
  build(el) {
    el.innerHTML = `
      <div class="q h-m" data-r="q">Website kamu<br><span class="lime">sehat</span> atau <span class="red">sekarat?</span></div>
      <svg class="ekg" data-r="ekg" viewBox="0 0 900 260"><polyline data-r="ekgl" pathLength="1" points="0,130 220,130 260,130 290,40 330,230 370,10 410,200 440,130 900,130"/></svg>
      <div class="roast">${'ROAST'.split('').map(c => `<span class="rl" data-r="rl[]">${c}</span>`).join('')}</div>
      <div class="cbar" data-r="cbar"><div class="cava">🙂</div><div class="cin" data-r="cin"><span data-r="ctx">Tambah komentar…</span><i class="caret" data-r="caret"></i></div><div class="send" data-r="send">➤</div></div>
      <div class="dm" data-r="dm"><span class="pill">DICEK & DI-DM TIM AGJ LABS</span></div>`;
  },
  update(r, t, ctx) {
    enter(r.q, t, 0.1, { from: 'up' });
    const tr = ctx.word('roast');
    r.ekgl.style.strokeDashoffset = 1 - p(t, 0.3, tr - 0.4, 'inOutCubic');
    css(r.ekg, { o: 1 - p(t, tr - 0.2, tr + 0.1, 'linear'), sy: 1 + 0.15 * Math.sin(t * 10) });
    r.rl.forEach((l, i) => {
      enter(l, t, tr + i * 0.09, { from: 'drop', dist: 700, extra: { r: (i - 2) * 3 } });
    });
    r.rl.forEach((l, i) => (l.style.backgroundPosition = `0 ${50 + Math.sin(t * 4 + i) * 50}%`));
    enter(r.cbar, t, ctx.word('nanti') - 0.4, { from: 'up', dist: 120 });
    const typed = Math.round(clamp((t - ctx.word('nanti')) / 0.35) * 6);
    r.ctx.textContent = typed > 0 ? 'ROAST🔥'.slice(0, typed === 6 ? 7 : typed) : 'Tambah komentar…';
    r.ctx.style.color = typed > 0 ? '#fff' : '#777';
    r.caret.style.opacity = Math.sin(t * 12) > 0 ? 1 : 0;
    const ts = ctx.word('nanti') + 0.5;
    css(r.send, { s: 1 + 0.25 * Math.sin(p(t, ts, ts + 0.3) * Math.PI) + 0.04 * Math.sin(t * 6) * (t > ts) });
    r.send.style.background = t > ts ? '#c6ff3d' : '#333';
    enter(r.dm, t, ctx.word('cek') - 0.1, { from: 'pop' });
  },
  cam: (t, ctx) => ({ z: lerp(1.2, 1, p(t, 0, 1, 'outExpo')) + 0.07 * p(t, ctx.word('roast'), ctx.d, 'linear'), y: lerp(-60, 30, p(t, 0, ctx.d, 'inOutCubic')) }),
});
