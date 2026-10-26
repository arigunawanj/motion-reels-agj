# Katalog gerak kamera & motion

## API engine
| Fungsi | Guna |
|---|---|
| `E.scene({...})` | id, at{x,y}, trans, transStyle 'whip'/'zoom', handheld, capY, captions, whoosh:false, cls, hits(ctx), sfx(ctx), build(el,ctx), update(r,t,ctx), cam(t,ctx) |
| `ctx.word(q, nth)` / `ctx.wordEnd(q)` | detik lokal saat kata diucapkan / selesai |
| `ctx.d`, `ctx.flash` | durasi scene, flash layar 0..1 |
| `E.p(t,a,b,ease)` | progress 0..1 |
| `E.io(t,a,b,c,d)` | masuk a→b, keluar c→d |
| `E.spring(t,at,{freq,damp})` | pegas overshoot |
| `E.enter(el,t,at,{from,dist,dur,e,extra})` | from: up down left right pop zoom drop |
| `E.css(el,{x,y,s,sx,sy,r,skx,o,blur})` | set transform/opacity/blur |
| `E.refs(root)` | `data-r="nama"` → refs.nama, `data-r="x[]"` → array |
| `E.lerp E.clamp E.noise(x,seed) E.rand(i,seed) E.mix(hexA,hexB,k) E.count(a,b,k,dec) E.chars(text)` | util |
| Easing | linear inQuad outQuad inCubic outCubic inOutCubic outQuint inExpo outExpo inOutExpo outBack outBackBig outElastic |

Kelas CSS: `.center .row .card .h-mega .h-xl .h-l .h-m .t-s .mono .pill .lime .pink .red .orange .glow-lime .glow-pink .stroke`

Kamera = `cam(t, ctx)` per scene, mengembalikan offset `{x, y, z, r}` dari tengah scene.
Engine otomatis menambah: handheld noise, shake dari `hits`, transisi antar scene, dan motion blur arah gerak.

| Gerak | Kapan | Kode |
|---|---|---|
| Slow push-in | default, biar nggak statis | `z: 1 + 0.06 * E.p(t, 0, ctx.d, 'linear')` |
| Snap zoom-out (hook) | frame 0, buka dari detail ke gambaran utuh | `z: E.lerp(1.6, 1, E.p(t, 0, 1.4, 'outExpo'))` |
| Punch-in | kata penting / angka | `z: 1 + 0.12 * E.p(t, tk, tk + 0.2, 'outExpo')` |
| Pan ke objek | pindah fokus dalam scene (atas → bawah) | `y: E.lerp(-250, 220, E.p(t, tk - 0.5, tk + 0.1, 'inOutExpo'))` |
| Dutch tilt | ketegangan / masalah | `r: E.lerp(-2, 2, k)` |
| Shake | impact, error, "boom" | tambah waktu ke `hits` |
| Whip pan | ganti topik | `transStyle: 'whip'` + `at` beda jauh di sumbu x |
| Zoom dip | ganti babak (tersangka → solusi) | `transStyle: 'zoom'` |
| Flash | momen "aha"/hasil | `ctx.flash = 0.25 * Math.exp(-(t - tk) * 6)` |

Gunakan `inOutExpo` untuk pan (cepat di tengah → motion blur kuat), `outExpo` untuk zoom/entrance, `outBackBig` untuk pop.

## Animasi elemen yang "mahal"
- **Counter**: angka naik + warna bergeser hijau→merah (`E.count`, `E.mix`).
- **Progress/meter**: bar melebihi batas kartu = "kebablasan".
- **Stack/drop**: `E.enter(el, t, at, {from:'drop'})` berurutan + goyang `Math.sin(t*2.4+i)`.
- **Multiply**: elemen berlipat (tab, kepala penumpang) dengan `display` sesuai `n(t)`.
- **Split/crack**: dua clip-path dari objek yang sama dipisah + rotasi.
- **Glitch**: `skx` & `x` diisi `E.noise(t*40)`, text-shadow merah/biru.
- **Stroke draw**: SVG `pathLength="1"` + `stroke-dasharray:1` + `strokeDashoffset = 1 - k` (centang, garis EKG, gauge).
- **Gauge**: busur stroke + jarum `rotate(-90 + 180*v/100)` dengan `outElastic`.
- **Typing**: potong string per waktu + caret kedip + SFX `type`.

## Layout 1080×1920
```
0    ┌──────────── progress bar ─────────────┐
230  │ @handle                               │  ← UI atas TikTok sampai ±220
260  │ ─────── zona konten utama ──────────  │
     │                                  [UI] │  ← kanan 150px: tombol like/komen
1300 │ ─────── batas konten ───────────────  │
1340 │        caption karaoke (2 baris)      │
1520 │ ░░░░ deskripsi & musik platform ░░░░  │  ← jangan taruh apa pun penting
1920 └───────────────────────────────────────┘
```
Saat kamera zoom/pan, cek ulang di contact sheet: objek bisa terdorong ke zona caption.
