# Tipe konten: Talking-head + B-roll (footage sendiri)

Dipakai saat user **mengirim rekaman dirinya bicara ke kamera** dan minta diedit: "edit ini", "kasih B-roll", "bikin kayak video X", "footage sendiri + motion grafik + monolog".
Bedanya dengan jalur utama skill: **suara = rekaman asli (tanpa TTS), visual utama = wajah orangnya**, motion grafik jadi penguat, bukan dunia animasi penuh.

Referensi gaya: video edukasi bisnis YouTube @agusleohalim (talking head studio gelap + kinetic type + B-roll + diagram neon).
Contoh lengkap yang sudah disetujui Ari: [`examples/nocap-skill-ai-talkinghead/`](../examples/nocap-skill-ai-talkinghead/).

## Analogi singkat
Dosen karismatik dengan papan tulis ajaib. Dosennya (A-roll) tetap jadi pusat. Setiap kali dia menyebut hal yang susah dibayangkan, papan menyala:
gambar (B-roll), papan judul (kartu hitam), atau diagram. Penonton tidak pernah bosan, tapi juga tidak kehilangan orangnya.

## Anatomi (4 lapisan)
| Lapisan | Isi | Kapan |
|---|---|---|
| **A-roll** | Wajah bicara, grade gelap moody, jump-cut wide ↔ close-up | Kalimat opini, emosi, penegasan, CTA |
| **Kinetic type** | Frasa kunci diketik huruf demi huruf: baris **sans tebal** + baris *serif italic* | Hampir tiap kalimat; di area dada saat A-roll, di tengah saat B-roll |
| **B-roll** | Foto stok (Pexels) + Ken Burns + light-leak, teks ketik di atasnya, chip UI/keycap kaca | Kalimat yang menyebut sesuatu yang bisa dilihat (orang, HP, keyboard, bingung, robot) |
| **Motion grafik** | Kartu judul hitam + coretan merah, judul glitch RGB, diagram arang + thumbnail neon | Konsep, perbandingan "bukan X tapi Y", daftar langkah |

## Ritme (pola yang lulus)
1. **Hook 0–3 dtk**: A-roll wide + teks ketik → jump-cut close-up di kata "tapi…".
2. **B-roll pertama ≤ 5 dtk**, lalu **kartu judul hitam ±1 dtk** yang merangkum hook dengan coretan merah (mis. "Pakai AI / ~~Jago AI~~").
3. Selang-seling: 2–3 B-roll → balik ke A-roll (hard cut, tanpa transisi) → B-roll lagi. Ganti visual tiap 2–4 dtk.
4. **Konsep inti → judul glitch (±1,3 dtk) → diagram alur** (bertahap, ±10 dtk boleh karena isinya terus bertambah).
5. **Daftar/poin → diagram tangga** dengan ikon garis.
6. **Penutup**: A-roll, teks pertanyaan CTA ditahan ≥ 2 dtk sampai akhir.
Jangan ada satu tampilan diam > 4 dtk tanpa elemen baru.

## Bahasa visual (angka pasti)
- **Tanpa subtitle karaoke.** Hanya frasa kunci (ringkas, ≤ 5 kata per baris, boleh parafrase sedikit dari ucapan).
- Sans: Inter 800, 64px, tracking -0.025em. Serif: Playfair Display italic 600, 84px. Caps (stack fakta): Inter 800 72px uppercase.
- Glow teks: `0 0 24px rgba(255,255,255,.3)` + bayangan gelap. Ketik: tiap huruf blur 10px→0, 0,16 dtk, jarak antarhuruf = durasi baris / jumlah huruf. Mulai baris = detik kata pertama diucapkan.
- **Posisi teks A-roll: bawah blok di y=1450 (bottom 470px)**, duduk di dada/baju. Close-up memakai fokus y=950 supaya dagu naik dan teks tidak menutup mulut. Cek di snapshot.
- Jump-cut: wide = skala 1,0; close-up = 1,36. Ganti mendadak di batas kalimat + drift +0,035 sepanjang segmen.
- Grade A-roll: lebih gelap, kontras naik, saturasi -30%, sedikit dingin, vignette.
- B-roll: grade gelap desaturasi (merah dibiarkan merah untuk suasana tegang), Ken Burns 1,04→1,16, light-leak oranye-merah 0,6 dtk saat masuk.
- Coretan merah `#E11D2E` gaya kuas digambar 0,2 dtk + stempel X merah (pengganti tengkorak referensi). Merah hanya untuk "salah/bukan".
- Diagram: latar gradasi arang `#2b2b2b→#0c0c0c` + scanline 1px/5px + vignette; label putih glow; garis 3,5px putih glow yang **tergambar** (dashoffset); chip judul outline putih radius 16; **thumbnail A-roll kiri, border 4px `#39ff3c` + glow**, video tetap jalan sinkron (lip-sync).
- Glitch: teks Inter 900 dengan salinan merah/cyan bergeser + 2 irisan sobek, 2 ledakan glitch (awal & akhir), latar foto biru-ungu + scanline tebal.

## SFX (feedback Ari: SFX ramai = berisik)
- Maksimal **±5 SFX per menit**, volume 0,10–0,12: whoosh halus saat masuk B-roll (jarak ≥ 8 dtk) + 1 glitch di judul glitch. **Tanpa pop, impact, atau whoosh panjang.**
- Selalu serahkan juga **versi tanpa SFX** (`aroll.py mix`) supaya tim bisa menambah sound trending di aplikasi.
- Suara asli tidak diproses selain kompresi AAC.

## Desain
Tipe ini memakai **gaya editorial gelap referensi** (bukan tema terang AGJ), karena rekaman wajah + teks putih butuh latar gelap. Logo/brand AGJ tidak wajib di tiap video; badge rubrik opsional.
Foto stok: Pexels (gratis, tanpa atribusi wajib, tetap cantumkan sumber di laporan). Foto produk/brand pihak lain boleh muncul sebagai B-roll foto asli, tapi **jangan menggambar ulang logo brand**.

## Workflow (gerbang tetap berlaku)
| Fase | Langkah |
|---|---|
| G1 Brief | `aroll.py init <dir> --footage file.mov --rubrik <id>` → isi `production/creative-brief.md` (tujuan, rubrik, CTA, hal yang tidak boleh tampil). |
| Transkrip | `prep` (HDR iPhone → SDR otomatis, grade dipanggang) → `words` → baca `production/words.txt`. Kata salah dengar ("EI"→AI) masuk `fixes`. |
| G3 Rencana edit | Isi `production/edit-plan.md` (tabel beat: detik, ucapan, visual, teks) + `edit.json`. Cari foto Pexels via web search, tulis id-nya. Minta approval. |
| Produksi | `stock` (cek `build/crops.jpg`) → `build` → `check` → `snap --at …` (lihat semua scene). |
| G4 Preview | Kirim contact sheet ke user. Setelah setuju: `render --range 8,10` dulu kalau mesin lambat, lalu `render`. |
| QC | Lihat frame final + `mr.py qc` tidak berlaku (tanpa timeline TTS). Cek manual: teks tidak menutup wajah, tidak ada frame hitam, audio -14 s.d. -23 LUFS, SFX tidak menutupi suara. |
| Publishing | `social-caption-publish` seperti biasa (subtitle = transkrip `words.txt`). |

## Format `edit.json`
Semua waktu = detik global dari rekaman (ambil dari `words.txt`).
```jsonc
{
  "footage": "IMG_5731.mov", "rubrik": "nocap", "duration": 71.1,
  "fixes": {"EI": "AI"},                                  // koreksi transkrip
  "framing": [[0, 2.9, "wide"], [2.9, 4.45, "close"]],     // jump-cut A-roll
  "kinetic": [{"id": "k1", "lines": [["s","Sekarang semua orang",0.55,1.75],["i","udah pakai AI",1.85,2.6]], "out": 2.88,
               "strike": null}],                            // strike: detik coretan merah + X di baris terakhir
  "broll": [{"id": "br-1", "start": 4.45, "end": 6.95, "img": "crowd1", "pexels": 8088495, "pos": 50, "grade": "dark",
             "kb": [1.04,1.16], "pan": [0,-30], "lines": [["s",…],["i",…],["c",…]],
             "chips": [["Tanya AI…","?",90,360,4.65]], "keys": [["Ctrl + C",150,470,12.73]]}],
  "titles": [{"id": "tc", "start": 6.95, "end": 7.85, "top": "Pakai AI", "bottom": "Jago AI", "strike": 7.43}],
  "glitch": [{"id": "gt", "start": 22.15, "end": 23.5, "text": "SKILL AI", "img": "darkkeys", "pexels": 5926370}],
  "diagrams": [
    {"id": "dg1", "type": "flow", "start": 23.5, "end": 33.75, "chip": "Skill AI",
     "struck": {"pre": "bukan cuma", "text": "bikin prompt", "t": 25.45, "strike_t": 26.0, "post": "tapi"},
     "nodes": [["Ngerti masalah",27.93],["Ngerti konteks",29.91],["Evaluasi hasil",31.43]], "loop_t": 32.4},
    {"id": "dg2", "type": "stairs", "start": 53.35, "end": 59.55, "head": [["s","Skill AI",53.5,53.85],["i","yang paling penting:",53.9,54.4]],
     "steps": [["bulb","Berpikir<br>kritis",54.5],["target","Menyelesaikan<br>masalah",55.8],["shield","Tahu kapan AI<br>bisa diandalkan",57.3]]}],
  "sfx": null      // null = otomatis pelan; atau [["whoosh", 4.2, 0.12], ["glitch", 22.15, 0.1]]
}
```
Jenis baris: `s` sans, `i` serif italic, `c` caps. Ikon tangga: bulb, target, shield, chat, spark, check, bolt, users. `pos` = posisi horizontal crop foto 0–100.
Diagram flow 2–4 node, tangga 2–4 anak tangga. Scene tidak boleh tumpang tindih waktunya (build memberi peringatan).

## Jebakan yang sudah pernah kena
- **Footage iPhone = HDR (HLG).** Tanpa tonemap, warna pucat dan render jatuh ke jalur HDR yang sangat lambat. `prep` menanganinya otomatis.
- **Grade jangan lewat shader saat render** (`media-treatment`): tanpa GPU render jadi ±1 fps (> 1 jam untuk 70 dtk). Grade dipanggang ke file oleh `prep`/`stock` → ±4 fps (±10 menit).
- Grain bergerak di video membuat file 700 MB → grain hanya di foto B-roll.
- Teks di bottom 590px menutup mulut saat close-up → bottom 470px + fokus close-up 950.
- Transkrip Whisper bahasa Indonesia salah baca istilah Inggris ("EI", "CCPT", "prom") → selalu baca ulang dan isi `fixes`.
- Jangan `pkill -f` dengan pola yang juga ada di perintahmu sendiri (shell ikut mati).
- Render panjang: jalankan di background dengan timeout ≥ 1 jam; uji kecepatan dulu dengan `render --range`.
