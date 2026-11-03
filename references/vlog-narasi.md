# Tipe konten: Vlog Narasi (footage perjalanan/aktivitas sendiri)

Dipakai saat user **mengirim banyak klip rekaman sendiri** (perjalanan, liburan, event, behind-the-scenes) dan minta dijadikan vlog: "buatin vlog dari klip ini", "auto cut angle yang bagus", "kayak vlog liburan di TikTok ini", "kasih VO narasi".
Bedanya dengan tipe lain: **ceritanya dibangun dari urutan momen** (bukan dari naskah), suara = campuran **VO TTS (penghubung)** + **suara asli user (momen bicara ke kamera)** + **suasana asli** + SFX halus.
Produksi lewat `scripts/vlog.py`, contoh lengkap: [`examples/malang-bali-vlog/`](../examples/malang-bali-vlog/) (13 → 24 klip, Malang → Bali naik kereta + kapal, 101 dtk).

## Analogi singkat
Editor yang jadi pemandu wisata. Klip-klip itu seperti album foto yang berantakan. Tugas editor: menyusunnya sesuai jam rekam, memilih potongan terbaik tiap momen, lalu berdiri di samping penonton dan bercerita sebentar ("nah, ini kita udah sampai stasiun…") dan **diam** saat pemandangannya sudah bicara sendiri. Kalau user sendiri sedang ngomong ke kamera, pemandunya mundur dan biarkan suara aslinya yang tampil.

## Tema visual
`theme` di `vlog.json` memilih gaya. Sekarang tersedia **`clean`** (footage apa adanya, caption putih tebal di zona 560px dari bawah, label lokasi kotak hitam, judul besar di awal). Tema lain (mis. **motion grafik**: kinetic type, lower-third animasi, peta rute) ditambahkan sebagai satu entri di `THEMES` pada `scripts/vlog.py` + satu bagian di dokumen ini. Jangan buat tema baru tanpa diminta user.

## Anatomi (4 lapisan)
| Lapisan | Isi | Kapan |
|---|---|---|
| **Suara asli** (`mode: own`) | User bicara ke kamera, dibersihkan (highpass, denoise ringan, loudnorm) + caption hasil koreksi | Pembuka/penjelasan/curhat di lapangan; hook lebih kuat dengan suara user sendiri |
| **Narasi TTS** (`vo`) | Satu kalimat ≤ 12 kata, santai, penghubung antar lokasi | Perpindahan lokasi, momen yang user tidak ucapkan |
| **Suasana** (`mode: amb`) | Suara asli klip: kecil (0.2–0.3) di bawah narasi, besar (0.8–0.9) tanpa narasi | Peron, kereta jalan, ombak, pengumuman: **biarkan penonton merasakan tempatnya** |
| **Label & SFX** | Label lokasi + jam rekam, whoosh pindah bab, chime/klakson/arpeggio di momen khas | Awal tiap bab; maksimal ±1 SFX per 5 dtk |

## Ritme (pola yang lulus)
1. **Hook 0–9 dtk dengan suara asli user** ("hari ini aku mau ke X, pertama kali…") + judul besar 3 dtk.
2. Bab per lokasi: **label lokasi + jam rekam** → shot pembuka lokasi (papan nama/gedung) → 1–2 shot gerak → shot manusia.
3. Selang-seling: narasi (3–4 dtk) → **shot suasana tanpa narasi 2–3 dtk** → suara asli user → narasi. Ganti visual tiap 2–5 dtk.
4. Momen user bicara ke kamera dipotong **utuh di batas kalimat** (pakai timestamp dari `scan`), jangan di tengah kata.
5. Penutup: jumlah/ringkasan perjalanan (waktu, jarak) + reaksi singkat ("Capek? Iya. Seru? Banget."), chime sampai tujuan.
Durasi: 45–60 dtk ideal; vlog panjang (> 90 dtk) tawarkan versi ringkas atau pecah 2 part.

## Naskah narasi (TTS natural)
- Tulis seperti ngobrol: partikel ("nih", "dong", "sih"), kalimat pendek, tanya-jawab ("Capek? Iya. Seru? Banget."). Angka dieja ("jam tiga", "sembilan jam").
- **Hanya fakta yang terlihat di footage atau diucapkan user.** Jam dari nama file/EXIF boleh jadi label; tujuan/rute dari ucapan user. Tebakan → tanyakan, jangan tulis sebagai fakta (mis. siapa orang di klip, tujuan sebuah loket).
- Kata asing/singkatan dieja fonetik kalau TTS salah baca. Hindari kalimat > 12 kata: TTS jadi datar.
- `build` membuat **N take (default 3)** per kalimat dan memilih yang paling mirip teks (Whisper) dengan tempo paling natural (~3 kata/dtk). Lihat `production/build-report.md`: kemiripan < 0.85 → dengarkan, ganti kalimat, atau `--takes 5`.
- Voice per video disebut user ("voice suci"); tanpa instruksi pakai `ari-santai`. Daftar voice: `GET /v1/voices`.

## SFX
- Sintetis (tanpa aset berhak cipta): `pop` judul, `chime` stasiun, `whoosh` pindah bab (offset -0.25 supaya mendahului cut), `horn` klakson kapal, `final` tiba di tujuan.
- Level sangat halus di `THEMES[...]["sfx_gain"]`. **Selalu serahkan juga versi tanpa SFX** (`<dir>-tanpa-sfx.mp4`) supaya tim bisa menambah sound trending di aplikasi.
- Tanpa musik kecuali file milik user.

## Workflow (gerbang tetap berlaku)
| Fase | Langkah |
|---|---|
| G1 Brief | `vlog.py init <dir> --voice ari-santai` → isi `production/creative-brief.md` (cerita satu kalimat, durasi, voice, yang tidak boleh tampil). Tanya **hanya** yang kosong. |
| Inventaris | Taruh klip di `footage/` (atau pakai path absolut di `footageDir`). `vlog.py scan <dir> --footage <folder>` → `production/footage.md` + `build/sheets/*.jpg`. **Lihat semua contact sheet**, baca transkrip, kelompokkan klip per jam rekam jadi bab. Whisper sering salah dengar: baca ulang, jangan pakai mentah-mentah. |
| G3 Story plan | Isi `production/story-plan.md` (bab, klip & potongan, suara asli vs VO, label, **daftar tebakan**) + `vlog.json`. Tampilkan ringkasan, minta approval. Footage tambahan datang belakangan → scan lagi, sisipkan di urutan jam rekam. |
| Produksi | `vlog.py check-tts <dir>` (env `TTS_API_KEY`) → `vlog.py build <dir>` (uji dulu bagian kecil: `--scenes 0-4 --takes 1`). |
| G4 Preview | `vlog.py qc <dir>` → lihat `build/final-contact.jpg` + dengarkan. Kirim ke user dengan daftar tebakan yang belum dikonfirmasi. |
| Revisi | Edit `vlog.json` → `build` lagi (VO yang tekstnya tidak berubah dipakai dari cache `audio/`). |
| Publishing | `social-caption-publish` (subtitle = caption hasil koreksi + VO). |

## Format `vlog.json`
```jsonc
{
 "title": "Malang ke Bali", "subtitle": "pertama kali naik kereta",   // judul besar scene ber-"title"
 "voice": "ari-santai", "theme": "clean", "takes": 3, "footageDir": "footage",
 "scenes": [
  {"clip": "IMG_0277.MOV", "start": 3.1, "dur": 8.7,        // start & dur = detik di klip asli
   "mode": "own", "title": true, "sfx": [["pop", 0.25]],     // own = suara asli; caps = teks ucapan (detik relatif scene)
   "caps": [[0, 4.3, "Hari ini aku mau ke Bali naik kereta"]]},
  {"clip": "IMG_0280.MOV", "start": 0, "dur": 2.6, "mode": "none",   // none = senyap
   "label": "Stasiun Malang · 07.26", "sfx": [["chime", 0.1]],
   "vo": "Jam tujuh lewat, udah sampai Stasiun Malang."},               // vo = narasi TTS; durasi scene otomatis ≥ VO + 0.55
  {"clip": "IMG_0288.MOV", "start": 7, "dur": 3, "mode": "amb", "vol": 0.25, "zoom": 1.14}  // amb = suasana; zoom = punch-in jump cut
 ]
}
```
Klip yang lebih pendek dari `dur` otomatis diperlambat (slow-mo smooth untuk klip 150–240 fps). Orientasi rotasi iPhone ditangani otomatis → 1080×1920.

## Jebakan yang sudah pernah kena
- **Footage iPhone tersimpan landscape + tag rotasi -90** (1920×1080 rotate) dan klip slo-mo berukuran 1920×1440 dengan banyak stream video. `ffprobe` tampak landscape padahal vertikal; selalu `-map 0:v:0` dan biarkan ffmpeg autorotate.
- **`silenceremove` dengan `stop_periods=1` memotong TTS di jeda kalimat pertama** (durasi scene jadi salah, narasi terpotong). Trim hanya awal dan akhir (trik `areverse`). Sudah benar di `vlog.py`; jangan diubah.
- **Whisper:** jangan pakai `initial_prompt` (hasilnya cuma mengulang prompt), pakai `condition_on_previous_text=False`; klip pendek/senyap menghasilkan "Terima kasih sudah menonton" (halusinasi); istilah Inggris/nama tempat sering salah (cek manual).
- **Cache take TTS jangan di-key pakai nomor scene** (urutan berubah → suara salah teks). `vlog.py` memakai hash teks+voice.
- **ASS caption:** baris `Dialogue` harus `Layer,Start,End,Style,Name,Effect,Text` (nama & efek kosong = dua koma), kalau tidak teks tampil "0,0,,…".
- `pip install edge-tts`/TTS lain di environment ber-proxy gagal verifikasi TLS; TTS resmi skill ini lewat `TTS_URL` + `TTS_API_KEY`. Jangan ganti provider tanpa izin user.
- Jangan `pkill -f` dengan pola yang juga ada di perintahmu sendiri (shell ikut mati).
- File akhir 100 dtk bisa > 100 MB di CRF 20; `build --crf 23` + maxrate 6M → ±60 MB.
