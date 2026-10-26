# Engine & integrasi library

Prinsip: **setiap frame = fungsi murni dari waktu `t`.** Tidak boleh ada `setTimeout`, `requestAnimationFrame`, CSS `animation/transition`, `Math.random()` tanpa seed, atau video/GIF yang berjalan sendiri. Renderer memanggil `window.__seek(t)` lalu memotret.

## Default: engine bawaan
DOM + CSS + SVG, dikendalikan `update(refs, t, ctx)`. Cocok untuk 90% konten explainer (kartu, ikon, angka, chart, UI mockup, kinetic type).

## GSAP
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>  <!-- di index.html sebelum scenes.js -->
```
```js
E.scene({
  id: 'gsap-demo',
  build(el) {
    el.innerHTML = `<div class="center h-xl" data-r="a">GSAP</div>`;
    const r = E.refs(el);
    r.tl = gsap.timeline({ paused: true })
      .from(r.a, { y: 200, opacity: 0, duration: 0.6, ease: 'expo.out' })
      .to(r.a, { rotate: -6, scale: 1.2, duration: 0.4, ease: 'back.out(3)' }, 1.2);
    return r;
  },
  update(r, t) { r.tl.seek(Math.max(0, t), false); },   // deterministik
});
```
Kunci waktu ke VO: bangun timeline di `build(el, ctx)` memakai `ctx.word('kata')` sebagai posisi.

## Canvas 2D / partikel
Hitung posisi partikel dari `t` dan indeks (`E.rand(i)`), bukan dari state frame sebelumnya. Gambar ulang penuh setiap `update`.

## Three.js (kedalaman 3D)
```js
build(el) {
  const c = document.createElement('canvas'); c.width = 1080; c.height = 1920; el.appendChild(c);
  const renderer = new THREE.WebGLRenderer({ canvas: c, antialias: true, preserveDrawingBuffer: true });
  const scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(40, 1080 / 1920, 0.1, 100);
  const mesh = new THREE.Mesh(new THREE.TorusKnotGeometry(1, .3, 200, 32), new THREE.MeshNormalMaterial());
  scene.add(mesh); cam.position.z = 6;
  return { renderer, scene, cam, mesh };
},
update(r, t) { r.mesh.rotation.y = t * 0.8; r.renderer.render(r.scene, r.cam); },
```
`preserveDrawingBuffer: true` wajib supaya screenshot tidak kosong. Headless Chromium memakai SwiftShader (lambat) — jaga jumlah poligon wajar.

## Aset gambar / video
- Gambar: taruh di `assets/`, pakai `<img>`; tunggu siap sebelum render (engine menunggu `document.fonts.ready`, untuk gambar tambahkan `decode()` di build).
- Klip video: jangan diputar; ekstrak frame dengan ffmpeg ke PNG sequence lalu pilih frame dari `t`.

## FFmpeg
Encoding final: H.264 `yuv420p`, CRF 16, `-movflags +faststart`, audio AAC 192k loudnorm -14 LUFS. Segmen per scene digabung dengan concat demuxer `-c copy`.
