# Adapter untuk agent yang membaca AGENTS.md (OpenAI Codex, dll.)

Saat user minta video TikTok/Reels/Shorts, motion graphic, atau explainer pendek:
baca dan ikuti `SKILL.md` di folder ini (workflow 9 fase dengan gerbang approval, Studio/Auto Mode).
Semua produksi lewat `python3 scripts/mr.py` — jangan screen-record, jangan lewati QC.
Kalau user mengirim rekaman dirinya bicara dan minta diedit (footage sendiri + B-roll + motion grafik), baca `references/talking-head-broll.md` dan pakai `python3 scripts/aroll.py`.
Kalau user mengirim banyak klip perjalanan/aktivitas dan minta dijadikan vlog (auto cut + narasi VO), baca `references/vlog-narasi.md` dan pakai `python3 scripts/vlog.py`.
