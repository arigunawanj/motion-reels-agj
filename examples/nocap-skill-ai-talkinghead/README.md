# Contoh: NO CAP. — "Pakai AI ≠ Jago AI" (talking-head + B-roll)

Edit pertama tipe talking-head yang disetujui Ari (Nov 2026). Rekaman selfie 71 dtk (iPhone, HDR, 9:16) berisi monolog soal skill AI. Hasil akhirnya dibuat meniru skema video referensi @agusleohalim.

- `edit.json`: seluruh edit (framing, kinetic type, 8 B-roll Pexels, kartu judul, judul glitch, 2 diagram). Footage tidak disertakan (privat).
- `production/creative-brief.md`, `production/edit-plan.md`: brief dan tabel beat.

Reproduksi dengan rekaman sendiri:
```bash
A=~/.claude/skills/motion-reels-agj/scripts/aroll.py
python3 $A init nocap-01-skill-ai --footage IMG_5731.mov --rubrik nocap
cp examples/nocap-skill-ai-talkinghead/edit.json nocap-01-skill-ai/   # lalu ganti "footage" ke path rekaman
python3 $A prep nocap-01-skill-ai && python3 $A stock nocap-01-skill-ai && python3 $A build nocap-01-skill-ai
python3 $A snap nocap-01-skill-ai --at 1.9,7.5,12.9,22.4,33.2,40.4,58.5,70.8
python3 $A render nocap-01-skill-ai && python3 $A mix nocap-01-skill-ai
```

## Riwayat revisi (pelajaran)
1. **v1 (ditolak):** caption karaoke + kartu navy bergaya AGJ terang. Feedback: "motion grafiknya ga mirip referensi". Yang diminta itu gaya visualnya (ketik per huruf, B-roll gambar lain, diagram neon), bukan cuma skemanya.
2. **v2 (disetujui):** gaya editorial gelap, B-roll foto, diagram arang. Render pertama > 1 jam karena grade lewat shader WebGL, jadi grade dipanggang ke file (±10 menit).
3. **v2 audio:** feedback "sound effectnya berisik". SFX dikurangi dari 16 ke 5 (whoosh 0,12 + glitch 0,10), ditambah versi tanpa SFX. Ini sekarang jadi default.

## Sumber foto (Pexels)
8088495, 15940005, 31421513, 6517090, 8386422, 6497924, 4327409, 8088451, 5926370 (lihat `pexels` di edit.json; URL `https://www.pexels.com/photo/<id>/`).
