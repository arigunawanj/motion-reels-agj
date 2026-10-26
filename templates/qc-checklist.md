# QC Checklist

Otomatis (`mr.py qc`) — harus 0 error:
- [ ] 1080×1920 · 60 fps · H.264 yuv420p · AAC · durasi = timeline
- [ ] Tidak ada frame hitam tak disengaja
- [ ] Tidak ada layar diam > 2 dtk (animasi patah)
- [ ] Caption tidak terpotong / tidak masuk zona UI
- [ ] Teks tidak keluar layar / tidak tabrakan dengan caption
- [ ] Kamera tidak berlebihan (zoom/rotasi/kecepatan di luar transisi)
- [ ] VO tidak terpotong, caption dalam rentang audio
- [ ] SFX dalam scene-nya dan tidak terlalu rapat
- [ ] Loudness ±-14 LUFS, true peak < -0.5 dBFS

Visual manual (lihat build/contact.jpg + frame di build/qc/ + tonton preview):
- [ ] Frame pertama sudah menarik, hook ≤ 3 dtk
- [ ] Setiap scene punya objek yang menggambarkan analogi (bukan teks doang)
- [ ] Ritme: ada perubahan tiap 1.5–3 dtk, tidak ada momen kosong
- [ ] Transisi terasa natural, arah gerak kamera konsisten dengan alur cerita
- [ ] Warna & font konsisten dengan visual-direction.md
- [ ] Kata yang diucapkan = aksi visual yang terjadi (sinkron)
- [ ] SFX mendukung, tidak mengganggu narasi
- [ ] Klaim faktual sesuai concept.md (bersumber)
- [ ] CTA jelas dan cuma satu
