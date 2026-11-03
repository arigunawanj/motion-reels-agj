# Contoh: Vlog "Malang ke Bali — pertama kali naik kereta"

Vlog pertama tipe Vlog Narasi (Nov 2026). 24 klip iPhone (portrait) sepanjang satu hari: rumah → Stasiun Malang → kereta → Stasiun Ketapang → pelabuhan → kapal → Pelabuhan Gilimanuk (Bali). 101 dtk.

- `vlog.json`: seluruh edit (22 scene). Footage tidak disertakan (privat); ganti `footageDir` ke folder klip sendiri.
- Suara asli user dipakai di 7 scene (hook di rumah, jalan kaki kepanasan, check-in pelabuhan, tips kapal); sisanya narasi TTS `ari-santai` + suasana asli.

```bash
V=~/.claude/skills/motion-reels-agj/scripts/vlog.py
python3 $V init malang-bali --voice ari-santai
cp examples/malang-bali-vlog/vlog.json malang-bali/    # lalu isi "footageDir" ke folder klip
python3 $V check-tts malang-bali
python3 $V build malang-bali --scenes 0-4 --takes 1    # uji cepat
python3 $V build malang-bali && python3 $V qc malang-bali
```

## Riwayat revisi (pelajaran)
1. **v1:** tebakan cerita dari tampilan saja ("perjalanan kereta") + TTS Edge. Salah konteks: ternyata tujuannya Bali, ada kapal, dan user sendiri bicara di banyak klip.
2. **v2:** setelah transkrip suara asli: cerita benar (Malang → Bali), suara asli dipertahankan di momen user bicara, TTS hanya penghubung.
3. **v3:** footage tambahan (pelabuhan, kapal, Gilimanuk), TTS `ari-santai` best-of-3, SFX halus, label lokasi. Feedback: TTS terdengar kurang natural → naskah ditulis ala ngobrol + pemilihan take + trim hening. Bug yang ditemukan di QC: narasi terpotong di jeda kalimat pertama (lihat Jebakan).
