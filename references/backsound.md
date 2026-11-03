# Backsound kantor AGJ Labs

Sumber: folder Google Drive "BACKSOUND" milik kantor (`https://drive.google.com/drive/folders/1mpqcdTqcNUsWe5rJiwcGwYkM_V6YnQBH`).
**File audio tidak disimpan di repo ini** (repo publik). Unduh folder itu ke mesin, lalu arahkan skill ke sana:

```bash
export BACKSOUND_DIR=~/BACKSOUND     # dicari rekursif berdasarkan nama file
```

Keputusan user: seluruh isi folder ini **boleh dipakai bebas** untuk konten AGJ Labs. Catatan praktis: sebagian besar rilisan komersial. Kalau TikTok/IG membisukan atau meng-claim video, ganti dengan versi `-tanpa-sfx.mp4` lalu tambahkan sound dari library aplikasi.

## Cara pakai
- Taruh lagu pilihan di `sound/` proyek (dicari lebih dulu), atau cukup nama file + `BACKSOUND_DIR`.
- **Vlog** (`vlog.py`): di `vlog.json` tambah `"bgm": {"file": "Synthwave goose - Blade Runner 2049.mp3", "volume": 0.30}`. Musik di-loudnorm dulu, ducking otomatis saat ada suara (VO/suara asli), fade in 1 dtk, fade out 1,5 dtk. Hanya masuk ke versi utama; `-tanpa-sfx.mp4` tetap bersih tanpa musik.
- **Motion graphic** (`mr.py`): di `script.json` isi `"bgm": "audio/bgm.mp3"` (salin file ke folder `audio/` proyek) dan atur `bgmVolume` (default 0.16).
- File tidak ketemu → build jalan tanpa musik + peringatan. Jangan menebak file lain.

## Katalog
Kolom "Cocok untuk" adalah **tebakan dari judul**; dengarkan dulu dan koreksi kalau meleset.

### STORYTELLING / Instrument (untuk vlog, cerita, narasi)
| File | Cocok untuk |
|---|---|
| Progressive Progress - Howard Harper-Barnes (Vlog No Copyright Music).mp3 | vlog perjalanan ceria, pilihan pertama |
| "Echo Sax End (Original)" by Caleb Arredondo.mp3 | penutup / momen reflektif |
| A Good Man with a Broken Heart.mp3 | emosional, cerita pelan |
| Can You Hear The Music.mp3 | pembuka sinematik |
| If you don't want my love - Jalen Ngonda (test karaoke 2).mp3 | santai, sore hari |
| Kanye West - Runaway (Instrumental).mp3 | dramatis, montase |
| Synthwave goose - Blade Runner 2049.mp3 | malam / kota / futuristik |

### STORYTELLING / Vocal (ada lirik; pakai di bagian tanpa VO)
4 Non Blondes - What's Up (Lyrics).mp3 · Jalen Ngonda - If You Don't Want My Love (Official Audio).mp3 · yung kai - blue (Lyrics).mp3

### EDUCATIONAL / Instrument (untuk motion grafik, explainer, edukasi)
Le Monde (From Talk to Me).mp3 · Lil Uzi Vert- 20 Min (Instrumental).mp3 · Tommy Richman - Million Dollar Baby [Instrumental].mp3 · VØJ x Narvent Memory Reboot (Slowed).mp3 · Yeat - Money So Big (Instrumental TikTok Remix).mp3

### EDUCATIONAL / Vocal
Jéja - Bad Habit (feat. Zaug) [NCS Release].mp3 · Tommy Richman - MILLION DOLLAR BABY (Lyrics).mp3

## Aturan pakai
1. Narasi/VO harus tetap jelas: pilih **Instrument** untuk video yang banyak bicara; **Vocal** hanya di bagian tanpa suara.
2. Volume default sudah ducking; jangan naikkan di atas 0.5.
3. Satu lagu per video, tidak dipotong di tengah kata; durasi lagu pendek akan di-loop.
4. Tulis lagu yang dipakai di `production/build-report.md` / caption supaya mudah dilacak.
