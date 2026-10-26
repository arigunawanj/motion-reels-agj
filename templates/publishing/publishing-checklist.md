# Publishing Checklist

## Hard checks (wajib semua ✓)
- [ ] Hashtag tidak melebihi batas platform (IG ≤ 5)
- [ ] Caption TikTok ≤ 2.200 UTF-16 units (bila via API)
- [ ] Klaim faktual di caption sesuai sumber / isi video
- [ ] Tidak ada keyword atau hashtag menyesatkan
- [ ] Caption tidak bertentangan dengan isi video
- [ ] Tidak ada engagement bait manipulatif ("wajib komen", "tag 3 teman", "comment YES", dll.)
- [ ] Tidak ada kata terlarang brand (`brand.banned_words`) dan gaya sesuai `brand.persona`
- [ ] Caption tiap platform diadaptasi (tidak identik)

## Skor rubrik (internal, bukan skor algoritma / prediksi FYP) — revisi bila < 85
| Platform | Relevansi 25 | Hook 20 | Natural 15 | Keyword 15 | Platform-fit 15 | CTA 10 | Total |
|---|---|---|---|---|---|---|---|
| TikTok | | | | | | | |
| Instagram | | | | | | | |
| Facebook | | | | | | | |

## Siap publish
- [ ] `mr.py publish-check` lulus
- [ ] User sudah menyetujui paket (`mr.py approve <dir> publishing`)
- [ ] Video final, cover title, dan caption sudah dicocokkan
- [ ] Jangan publish otomatis tanpa izin user
