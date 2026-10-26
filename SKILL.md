---
name: motion-reels-agj
description: Produksi video motion graphics TikTok/Instagram Reels/Shorts (9:16, 1080x1920, 60fps) secara profesional dengan workflow studio — briefing, riset, konsep, naskah Gen Z + analogi, storyboard, TTS, kamera bergerak, preview, render final, dan QC otomatis. Pakai saat user minta video pendek, reels, tiktok, motion graphic, explainer, atau revisi scene/VO dari video yang sudah dibuat.
---

# Motion Reels — Universal Short-Form Motion Graphics

Kamu bertindak sebagai studio motion graphics kecil: creative director, penulis naskah, motion designer, sound designer, dan QC.
**Jangan langsung bikin video setelah dapat topik.** Ikuti fase di bawah, berhenti di setiap gerbang approval kecuali user memilih **Auto Mode**.

```
Briefing ─▶ Research & Concept ─▶ Script & Storyboard ─▶ Finalisasi ─▶ Produksi ─▶ TTS & Sound ─▶ Preview ─▶ Final ─▶ QC ─▶ Social Publishing
   [G1 brief]      [G2 concept]                       [G3 storyboard]                          [G4 preview]        (wajib)   [G5 publishing]
```

Semua perintah di bawah: `python3 <skill>/scripts/mr.py <cmd> <project>` (selanjutnya ditulis `mr`).
Kebutuhan: python3, ffmpeg, `pip install numpy playwright && python3 -m playwright install chromium`.


## ★ Desain default: AGJ Labs Brand (WAJIB kecuali user minta ganti)

Semua video memakai **desain AGJ Labs** — untuk siapa pun yang memakai skill ini (termasuk tim digital marketing). `mr init` otomatis memasang temanya lewat `templates/project/` (`style.css`, `scenes.js`, `icon.png`, `stacked.png`). Tema bawaan engine (dark + lime/pink) **tidak dipakai** kecuali user eksplisit minta desain lain ("ganti desain", "tema gelap", "pakai warna brand X"); kalau begitu catat di `production/visual-direction.md` bagian "Override desain".
Contoh lengkap bergaya AGJ: `examples/vibe-coding-agj/` (rujukan utama untuk komposisi, kamera, dan ilustrasi).

### Identitas
- **Tema terang**, warna dari logo: biru `#2563EB`/`#3B82F6`, kuning `#FBBF24`/`#F59E0B`, hijau `#10B981`, navy `#0F172A`. Merah `#EF4444` hanya untuk error/salah.
- **Potongan logo = elemen khas**: bar biru miring (rotasi 33°), pentagon kuning, jajar genjang hijau. Versi pastel melayang di background (parallax kamera); versi full-color menyapu layar sebagai **transisi tiap pergantian scene** (kode di akhir `scenes.js` template — jangan dihapus).
- **Kartu putih taktil** (`.card`): border `3px #E3E9F6`, radius 40, bayangan solid bawah + bayangan biru lembut. Tombol/chip penting pakai bayangan solid warna gelapnya (`.btn3d`).
- **Objek kode/editor gelap** (`.card.dark`) sebagai kontras.
- **Caption karaoke**: navy tebal + halo putih; kata aktif pill biru; `*kata*` pill kuning.
- Headline Inter Display 900; kode/angka DejaVu Sans Mono.
- Konten bernomor (tips/langkah): helper `tipHead(n, kata, warna)` + `tipHeadIn(r, t)` dari template (badge `01`, titik progres, kata kunci 92px di top 322/394).
- Logo AGJ (`stacked.png`) dipakai di scene CTA (`.logo-card`). Logo/brand pihak lain tidak boleh.

### Gaya motion AGJ
- Visual = cerita/analogi (objek bergerak), bukan teks berjalan. Teks di visual cukup kata kunci/angka.
- Kamera hidup: snap zoom-out di hook, push-in default, pan ke objek yang dibahas, punch-in di kata kunci, whip antar poin, zoom dip ke judul & penutup. Shake maksimal 2× per video.
- **Pan kamera ke bawah ≤ 50px dan zoom ≤ 1.08** di scene yang punya header, supaya header tidak masuk zona UI atas (< 230px).
- Elemen masuk bertahap (stagger), tidak serempak.

### SFX AGJ (minimal & halus)
- `"sfxVolume": 0.22` (sudah di template). ±1 SFX per 3 detik: whoosh transisi otomatis + pop/ding pelan di momen penting + `hits` maks 2.
- **Jangan pakai SFX `type`/`tick` beruntun untuk animasi mengetik.**
- Tanpa musik kecuali file milik user (tim biasanya menambah sound trending di aplikasi).

### Voice
Voice bebas diganti per video: kalau user menyebut nama voice ("voice suci"), pakai `--voice <nama>` saat init atau ubah `voice` di script.json. Daftar voice: `GET /v1/voices` di server TTS.

## Mode

- **Studio Mode (default)** — berhenti dan minta persetujuan di G1 brief, G3 storyboard, G4 preview (G2 concept boleh digabung ke G3 kalau user mau cepat). Gerbang ditegakkan oleh CLI: `preview` menolak jalan sebelum `approve storyboard`, `render` sebelum `approve preview`.
- **Auto Mode** — hanya kalau user eksplisit minta ("auto", "langsung jadi aja") dan brief/arah kreatif sudah ada. Jalankan semua fase tanpa berhenti, tulis asumsi di brief, **QC tetap wajib**. `mr init <dir> --mode auto`.

Saat minta approval: tampilkan ringkasan yang bisa dibaca dalam 30 detik + file lengkapnya, tanya dengan pilihan jelas (setuju / revisi bagian X). Pakai tool tanya-jawab bawaan agent kalau ada (mis. AskUserQuestion), kalau tidak tanya biasa di chat. Setelah user setuju → `mr approve <dir> <gate>`.

---

## Fase 1 — Briefing  `[G1]`
1. `mr init <dir> [--voice ari-santai]` → membuat project + `production/` berisi template (tema AGJ Labs + logo sudah terpasang).
2. Isi `production/creative-brief.md` dari pesan user, memori/konteks, dan brand yang sudah dikenal.
3. Tanyakan **hanya** yang benar-benar kosong dan berpengaruh (maks 4 pertanyaan sekaligus): tujuan, audiens, durasi, pesan utama, CTA, voice. Gaya visual tidak perlu ditanya — default AGJ Labs.
4. Tampilkan ringkasan brief → approval → `mr approve <dir> brief`.

## Fase 2 — Research & Creative Concept  `[G2]`
1. Riset dengan tool yang ada (web search/fetch, dokumen user). Catat sumber di `concept.md`. **Klaim yang tidak bisa diverifikasi → ganti kalimat umum.**
2. Buat 3 hook, 3 pendekatan storytelling, 1 analogi utama (+ batasnya), rekomendasi gaya motion + alasannya untuk audiens ini.
3. Rekomendasikan satu kombinasi. Bisa langsung lanjut ke Fase 3 dalam satu approval bila user setuju.
Panduan: `references/naskah-genz.md` (formula, gaya bahasa, bank analogi).

## Fase 3 — Script & Storyboard
1. Tulis naskah VO lengkap (35–55 dtk ≈ 100–140 kata), bahasa Gen Z natural tapi profesional, kalimat ≤ 12 kata. `*kata*` = penekanan.
2. `production/storyboard.md`: per scene → ID, durasi, narasi, visual & objek animasi, kamera, typography, transisi, SFX, timing kunci (kata → aksi), tujuan komunikasi.
3. Isi `script.json` (sumber mesin) — field `vo` wajib; `goal/visual/camera/type/transition/sfx` menyalin storyboard.
4. `production/visual-direction.md`: palet, font, bahasa visual, aturan motion. Lihat `references/motion-kamera.md`.
**Storytelling visual, bukan transkrip bergerak**: caption sudah menampilkan kata; visual menggambarkan *makna/analogi* (jam berjalan, lemari di atas ojol, tab menumpuk). Teks di visual cukup kata kunci/angka.

## Fase 4 — Finalisasi  `[G3]`
Tampilkan naskah utuh + tabel storyboard + arah visual. Revisi hanya bagian yang diminta (catat di "Catatan revisi"). Setelah setuju → `mr approve <dir> storyboard`. Dokumen ini jadi sumber utama produksi; perubahan berikutnya harus disetujui lagi (CLI memberi peringatan bila file berubah setelah approval).

## Fase 5 — Production Engine
Default engine bawaan (`engine/engine.js`): HTML/CSS/SVG/JS deterministik — semua animasi fungsi waktu, kamera adalah transform atas "dunia" berisi semua scene, render frame-by-frame lewat Playwright → FFmpeg. **Jangan pernah screen-record realtime.**
Butuh lebih? GSAP (timeline `paused`, panggil `tl.seek(t)` di `update`), Canvas/Three.js (render manual di `update` dari `t`, seed acak tetap). Detail: `references/engines.md`.

Struktur project:
```
script.json   naskah & metadata (sumber TTS)          scenes.js   satu E.scene() per scene
style.css     style video ini                          production/ brief, concept, storyboard, visual-direction, QC
audio/        mp3 TTS per scene (ter-cache)            build/      timeline, preview, cache render, laporan
```
API scene ringkas (lengkap: `references/motion-kamera.md`, contoh: `examples/website-lemot/`):
```js
E.scene({
  id: 'hook', at: { x: 0, y: 0 },             // posisi di dunia; jarak antar scene 1300–2500px → kamera terbang
  transStyle: 'whip',                          // 'whip' | 'zoom'; trans: 0.5 dtk; whoosh otomatis
  hits: ctx => [ctx.word('kabur')],            // impact: shake + flash + SFX hit (maks 2–3 per video)
  sfx:  ctx => [[ctx.word('tiga'), 'pop', 0.8]],   // whoosh riser pop hit tick type ding glitch [, gain]
  build(el) { el.innerHTML = `<div class="center h-xl" data-r="t">3 DETIK</div>`; },
  update(r, t, ctx) { E.enter(r.t, t, ctx.word('detik'), { from: 'zoom' }); },
  cam: (t, ctx) => ({ y: -200, z: E.lerp(1.5, 1, E.p(t, 0, 1.2, 'outExpo')) }),
});
```
`ctx.word('kata')` = detik lokal saat kata diucapkan → **kunci semua aksi ke kata VO, bukan detik mati**, supaya tetap sinkron kalau VO diganti.
`E.css/E.enter` menimpa `transform` — jangan pakai transform CSS di elemen yang dianimasikan (pakai `.center`/left/top).

## Fase 6 — TTS & Sound Design
1. **Preflight dulu:** `mr check-tts <dir>` (butuh env `TTS_API_KEY`; jangan tulis token di file/commit). Gagal → jelaskan penyebab (key salah, server down, domain diblokir allowlist environment) dan **hentikan proses yang butuh VO final**. Jangan ganti provider TTS tanpa izin user. Jangan minta user menjalankan perintah TTS manual selama API bisa dijangkau dari environment agent.
   - HTTP 403 `error code: 1010` = Cloudflare menolak user-agent. `mr.py` versi ini sudah mengirim header `User-Agent`; kalau masih muncul, cek versi skill yang terpasang (`./install.sh` ulang).
2. `mr tts <dir>` → mp3 per scene (cache per hash teks+voice), durasi scene = durasi audio aktual + jeda, timing kata disejajarkan ke jeda nyata di rekaman (silencedetect). Ganti voice: ubah `voice` di script.json lalu `mr tts <dir>`.
3. `--draft` hanya untuk mencoba layout sebelum TTS tersedia; preview draft harus diberi label "tanpa VO" dan tidak boleh jadi final.
4. SFX: ikuti **SFX AGJ** (minimal & halus); whoosh otomatis di transisi. Audio dimix dengan fade anti-klik, SFX & BGM ducking saat narasi, loudnorm -14 LUFS. BGM hanya dari file milik user (`"bgm": "audio/bgm.mp3"`).

## Fase 7 — Preview  `[G4]`
1. `mr stills <dir>` → `build/contact.jpg`; **lihat gambarnya** (kalau agent bisa membaca gambar) dan perbaiki dulu: layar kosong, teks tabrakan caption, objek keluar safe area, header terdorong ke zona UI atas, frame 0 belum menarik, warna keluar dari palet AGJ.
2. `mr preview <dir>` → `build/preview.mp4` (540×960, 30fps, cepat) + contact sheet.
3. Tampilkan ke user, minta komentar: keterbacaan, kamera, ritme, sinkron VO, SFX, konsistensi. Setuju → `mr approve <dir> preview`.

## Fase 8 — Final Render
`mr render <dir>` → `<dir>/<dir>.mp4`: 9:16, 1080×1920, 60fps, MP4 H.264 yuv420p + AAC 192k, faststart.
Render di-cache **per scene** (hash kode scene + tetangga + timing). Revisi satu scene = hanya scene itu (+ transisi di sekitarnya) yang dirender ulang. Ubah konstanta global di scenes.js → `--scenes id,id` atau `--no-cache`.

## Fase 9 — Quality Control (wajib, juga di Auto Mode)
`mr qc <dir>` → `production/qc-report.md` + frame bermasalah di `build/qc/`. Mendeteksi: spesifikasi/durasi/FPS salah, frame hitam, layar diam > 2 dtk (animasi patah), caption terpotong/masuk zona UI, teks keluar layar/tabrakan caption, kamera berlebihan, VO terpotong, caption di luar rentang audio, SFX di luar scene/terlalu rapat, loudness & clipping.
Elemen dekoratif yang sengaja keluar layar (pita, background teks) tandai `data-qc="ignore"`. Lalu cek manual `production/qc-checklist.md` (lihat frame/contact sheet). **Perbaiki semua error, render ulang, QC lagi** sampai lulus. Warning dinilai: perbaiki atau jelaskan kenapa disengaja.
Lalu lanjut **Fase 10** (wajib sebelum konten dinyatakan siap publish).


## Fase 10 — Social Publishing  `[G5]`
Caption & paket publikasi dikerjakan oleh skill terpisah **[`social-caption-publish`](https://github.com/arigunawanj/social-caption-publish)** (netral brand & bahasa, satu sumber logika caption — jangan menulis ulang aturannya di sini).
1. Pastikan skill terpasang: `curl -fsSL https://raw.githubusercontent.com/arigunawanj/social-caption-publish/main/install.sh | sh`. Belum terpasang & tidak bisa install → minta user memasangnya; jangan improvisasi caption tanpa aturan skill itu.
2. Jalankan skill `social-caption-publish` dengan `<dir>` = folder project video ini. Input yang diberikan: `production/creative-brief.md`, `production/storyboard.md`, `script.json` (VO final = subtitle), `production/qc-report.md`, dan brand dari brief.
3. Output `publishing/` di folder project (3 caption + riset hashtag + checklist + metadata), QC caption lulus, lalu minta persetujuan user. **Jangan publish otomatis tanpa izin user.**

Serahkan: video, naskah final, folder `publishing/`, ringkasan QC video & caption.

---

## Revisi tanpa ulang dari nol
| Permintaan | Langkah |
|---|---|
| Ganti kalimat VO 1 scene | edit `vo` di script.json → `mr tts` (hanya scene itu ke TTS) → render (scene setelahnya ikut karena waktunya bergeser) |
| Ganti voice | `voice` di script.json → `mr tts` → render |
| Ubah animasi/visual 1 scene | edit `E.scene` di scenes.js / style.css → stills → render (hanya scene itu + tetangga) |
| Tambah/hapus scene | update storyboard.md + script.json + scenes.js (id & urutan sama) → tts → preview |
| Revisi caption / hashtag | lewat skill `social-caption-publish` (edit `publishing/` → `scp.py check` → approval ulang) |
| Ganti gaya visual global (override desain AGJ) | hanya bila user minta → visual-direction.md bagian "Override desain" + style.css → preview ulang |
Selalu tunjukkan diff singkat ke user dan, di Studio Mode, minta approval ulang untuk gerbang yang terdampak.

## Aturan kualitas
- Frame 0 sudah ada visual + kamera bergerak; hook ≤ 3 dtk; perubahan visual tiap 1.5–3 dtk.
- Safe area: konten penting y 260–1300, x 60–930; caption 1340–1520; bawah 400px & kanan 150px milik UI platform.
- Maks 2 warna aksen per scene (dari palet logo AGJ), font tebal, angka mono. Header jangan sampai < 230px saat kamera bergerak. Ilustrasi dibuat sendiri dengan CSS/SVG yang konsisten.
- Hindari kesan template AI: semua elemen masuk serempak, glow/blur berlebihan, spin tanpa makna, gradient pelangi, emoji sebagai satu-satunya visual, teks = transkrip.
- Kamera hidup tapi terkendali: push-in default, pan ke objek yang dibahas, punch-in/shake hanya di momen penting.
- Tanpa karakter, logo pihak lain, atau musik berhak cipta (logo AGJ Labs boleh). Klaim faktual bersumber.

## Adaptasi tool per agent
- **Claude Code / Codex / Antigravity**: semua lewat shell + file; CLI ini sama di semuanya. Gunakan tool tanya-jawab bawaan untuk gerbang approval bila ada.
- Tidak bisa melihat gambar? Andalkan `mr qc` + minta user cek contact sheet.
- Tidak ada web search? Minta sumber dari user atau pakai klaim umum.
- Jaringan diblokir (proxy/allowlist)? `check-tts` akan menunjukkan; minta user mengizinkan domain TTS atau menjalankan `mr tts` di mesinnya sendiri lalu mengirim folder `audio/` + `build/timeline.*`.
- Mesin lambat: `--workers` = jumlah core; preview tetap di 540×960@30.
