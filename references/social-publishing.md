# Modul `social-publishing` — Caption & Discovery (Fase 10)

Berjalan **setelah QC video LULUS**, sebelum konten dinyatakan siap publish. Wajib menghasilkan caption khusus **TikTok, Instagram Reels, dan Facebook Reels**. Tidak mengganti workflow produksi video sebelumnya.

```
Video QC Passed → Content Analysis → Platform Research → Keyword Research → Caption Drafting
→ Hashtag Filtering → Caption QC → Publishing Package → User Approval → Ready to Publish
```
CLI: `mr publish-init <dir>` → isi file → `mr publish-check <dir>` → tampilkan ke user → `mr approve <dir> publishing`.

## 1. Content understanding
Baca dulu: `production/creative-brief.md`, `production/storyboard.md`, `script.json` (VO final = subtitle), judul, pesan utama, kesimpulan, target audiens, brand guideline, tujuan konten (awareness / education / engagement / conversion).
- Caption tidak boleh bertentangan dengan isi video.
- Jangan mengarang statistik, fakta, atau klaim tanpa sumber.

## 2. Platform research
Kalau ada akses web, cek ulang aturan & panduan resmi sebelum menulis. Prioritas: TikTok Creative Center / TikTok for Business / TikTok for Developers; Instagram Creators & Meta; Facebook Creators & Meta.
Pisahkan tiga jenis info dan beri label di file caption bila dirujuk:
1. **Official Rule** — aturan/batas platform yang terverifikasi (dengan sumber).
2. **Best Practice** — rekomendasi platform atau observasi bersumber.
3. **Experiment** — hipotesis internal, diuji lewat analytics. Jangan pernah disebut aturan resmi.

Tanpa internet: pakai tabel di bawah, tulis tanggal verifikasinya, dan **jangan klaim hashtag apa pun sedang trending**.

### Aturan terdokumentasi (terakhir diverifikasi 2026-10-26)
| Platform | Jenis | Aturan | Sumber |
|---|---|---|---|
| Instagram (post & reels) | Official Rule | Maksimal **5 hashtag** per caption, diluncurkan bertahap; diumumkan akun @creators Instagram, Des 2025 | [Social Samosa, 19 Des 2025](https://www.socialsamosa.com/news-2/instagram-hashtags-five-per-post-10923075), [BetaNews](https://betanews.com/2025/12/19/instagram-puts-a-limit-on-hashtag-usage/) |
| Instagram | Best Practice | Sedikit hashtag spesifik lebih efektif daripada hashtag generik (#reels, #explore) | sumber yang sama |
| TikTok Content Posting API | Official Rule | `post_info.title` (caption) maks **2.200 UTF-16 runes**; hashtag & mention dipisah spasi/baris baru | [TikTok for Developers — Direct Post](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post) |
| TikTok | Experiment (preset internal) | 3–5 hashtag relevan | internal |
| Facebook Reels | Experiment (preset internal) | 0–3 hashtag relevan; tidak ditemukan batas resmi | internal |

Periksa ulang sebelum integrasi API atau bila tanggal di atas sudah > 3 bulan.

## 3. TikTok caption engine
- Kalimat pertama = hook relevan dengan isi video.
- Keyword utama masuk secara natural (TikTok juga berperan sebagai mesin pencari — tulis kata yang benar-benar diketik orang).
- Jelaskan manfaat/konteks singkat, bahasa sehari-hari.
- Ajak diskusi hanya bila relevan. Tanpa clickbait menyesatkan dan engagement bait berlebihan.
- 3–5 hashtag (preset eksperimen). **Jangan otomatis** pakai #fyp, #foryou, #viral, atau hashtag populer tak relevan.
- Via Content Posting API: caption + hashtag ≤ 2.200 UTF-16 units (dicek `publish-check`).

## 4. Instagram Reels caption engine
Struktur: **Hook → insight/penjelasan → nilai praktis → CTA natural (jika relevan) → hashtag.**
- Maks 5 hashtag (Official Rule); tidak wajib penuh.
- Kombinasi prioritas: keyword topik · niche spesifik · kategori konten · audiens/komunitas · branded hashtag (mis. #agjlabs) bila relevan.
- Hindari #reels, #explore, #viral otomatis.

## 5. Facebook Reels caption engine
- Konteks jelas, bahasa mudah dipahami (audiens FB cenderung lebih luas/umur beragam).
- Relevan dengan video; ajak diskusi bermakna bila cocok.
- Jangan memanjangkan caption demi keyword; tanpa hashtag stuffing; 0–3 hashtag (preset internal).
- Utamakan konten orisinal; jangan anjurkan repost konten pihak lain tanpa transformasi bermakna.

## 6. Hashtag research engine
Nilai tiap kandidat dari: relevansi semantik ke isi video · relevansi audiens · niche & industri · bahasa & wilayah target · data tren yang **benar-benar tersedia** · potensi misleading/spam.
- Setiap hashtag terpilih punya alasan di `hashtags-research.md` (dicek CLI).
- Data tren: catat sumber + tanggal. Tidak ada data → tulis begitu.
- Jangan mengarang volume, popularitas, ranking. Jangan pakai paket hashtag yang sama di semua video tanpa evaluasi.

## 7. Caption style rules
Natural, Gen Z, tetap profesional (selaras naskah VO).
**Dilarang:** emoji berlebihan (±3 maks) · kalimat template ala AI ("Di era digital ini…", "Yuk simak!", "Jangan lupa like, comment, share") · hashtag dumping · clickbait palsu · manipulasi engagement · CTA "wajib komen"/"spam komentar" · caption identik di semua platform · semua konten jadi hard selling.
**Pendekatan** (pilih berdasar isi video, bukan acak): curiosity · problem-solution · storytelling · educational insight · myth vs fact · opinion/discussion · soft selling.

## 8. Caption quality control
Rubrik internal per platform — **alat editorial, bukan skor algoritma dan bukan prediksi FYP**:

| Kriteria | Bobot |
|---|---|
| Relevansi dengan isi video | 25 |
| Kekuatan hook | 20 |
| Keterbacaan & naturalitas | 15 |
| Keyword & discoverability | 15 |
| Kesesuaian platform | 15 |
| Kualitas CTA | 10 |

Total < 85 → revisi caption. Tulis skor di `content-metadata.json`.
**Hard checks** (semua wajib lulus): hashtag ≤ batas platform · klaim faktual sesuai sumber · tidak ada keyword/hashtag menyesatkan · caption tidak bertentangan dengan video · tidak ada engagement bait manipulatif. Setelah dicek manual set `hard_checks_passed: true`.

`mr publish-check` otomatis memeriksa: blok caption terisi, jumlah hashtag vs batas/preset, hashtag duplikat & generik, UTF-16 TikTok, pola engagement bait, emoji berlebihan, hook terlalu panjang, bagian wajib lengkap, tanggal verifikasi, skor ≥ 85, hashtag caption = metadata, caption identik antar platform, alasan hashtag ada di riset. Laporan: `publishing/caption-qc.md`.

## 9. Output — `publishing/`
| File | Isi |
|---|---|
| `tiktok-caption.md`, `instagram-caption.md`, `facebook-caption.md` | caption final (blok ```caption```), keyword utama & pendukung, hashtag terpilih + alasan, cover title, CTA, alternatif hook, tanggal verifikasi aturan |
| `hashtags-research.md` | kandidat, penilaian, ditolak + alasan, sumber & tanggal |
| `publishing-checklist.md` | hard checks, tabel skor, status persetujuan |
| `content-metadata.json` | ringkasan mesin-baca per platform + slot analytics |
| `caption-qc.md` | hasil `publish-check` |

**Jangan publish konten tanpa persetujuan user.**

## 10. Post-publish analytics
Bila data tersedia (user kirim angka/screenshot atau ada konektor): views & reach · average watch time · completion/retention · shares · saves · komentar berkualitas · profile visits · follows & konversi. Bandingkan per platform dan per tujuan konten, simpan di `content-metadata.json` → `analytics`, beri rekomendasi untuk video berikutnya.
Jangan menyimpulkan hashtag tertentu menyebabkan kenaikan views tanpa bukti memadai (mis. uji A/B atau pola konsisten di banyak video).
