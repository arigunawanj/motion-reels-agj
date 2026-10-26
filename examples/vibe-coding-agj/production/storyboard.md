# Storyboard — 5 Tips Vibe Coding

**Target:** ±50 dtk (durasi final = durasi audio TTS) · **Voice:** suci · **FPS:** 60 · **Kanvas:** 1080×1920
Status: draft v4 (revisi: SFX halus, kamera bergerak, visual analogi)

## Naskah utuh (107 kata)
> Pakai AI buat ngoding, tapi hasilnya malah berantakan? Masalahnya bukan di AI. Prompt kamu kayak pesen ke abang warung: makanan satu. Ya bingung lah. Nih, lima tips vibe coding biar hasilnya rapi. Satu, kasih konteks. Sebut framework, fitur, sampai hasil akhirnya. Dua, pecah jadi langkah kecil. Satu prompt, satu tugas. Tiga, bikin file aturan main. Biar AI nggak perlu diingetin terus. Empat, minta rencananya dulu. Kayak cek rute di Maps sebelum jalan. Lima, review dan test dulu, baru commit. AI itu partner, bukan autopilot. Punya ide aplikasi tapi nggak sempat ngoding? Biar AGJ Labs yang bantu bikinin. Save dulu biar nggak lupa, terus follow AGJ Labs ya!

## Scene
| ID | Narasi (VO) | Visual & objek animasi | Kamera | Typography | Transisi | SFX | Tujuan |
|---|---|---|---|---|---|---|---|
| hook | Pakai AI buat ngoding, tapi hasilnya malah *berantakan*? | Editor kode yang barisnya rontok + badge error menghitung | snap zoom-out 1.6→1, punch-in + shake di 'berantakan' | kata kunci: ERROR counter mono | - | hit di 'berantakan' | Stop scroll: masalah yang relate |
| warung | Masalahnya bukan di AI. Prompt kamu kayak pesen ke abang warung: *makanan* satu. Ya bingung lah. | Bubble prompt 'buatin aplikasi' → nota warung tercetak '1x MAKANAN ???' → tanda tanya bermunculan | pan dari bubble (atas) ke nota (bawah), tilt saat 'bingung' | nota mono | whip | pop di 'bingung' | Analogi: perintah nggak jelas |
| judul | Nih, *lima* tips vibe coding biar hasilnya rapi. | Angka 5 raksasa gradien + 5 kartu tips mengipas | zoom dip masuk, punch-in di 'lima' | 5 + VIBE CODING | zoom | — | Janji isi |
| konteks | Satu, kasih *konteks*. Sebut framework, fitur, sampai hasil akhirnya. | Kartu prompt 'buatin login' membesar; chip Laravel/Tailwind/validasi/→dashboard terbang masuk; meter kejelasan merah→hijau | pan ke meter di 'hasil' | 01 KONTEKS | whip | ding pelan di 'hasil' | Tip 1 |
| kecil | Dua, pecah jadi langkah *kecil*. Satu prompt, satu tugas. | Balok raksasa 'APP KASIR' retak jadi 3 anak tangga tercentang | punch-in di 'kecil', push-in | 02 LANGKAH KECIL | whip | — | Tip 2 |
| aturan | Tiga, bikin file *aturan* main. Biar AI nggak perlu diingetin terus. | Editor AGENTS.md mengetik aturan; bot AI memindai file; bubble 'inget ya…' berulang dicoret | pan dari editor ke bot | 03 ATURAN MAIN | whip | — | Tip 3 |
| rencana | Empat, minta *rencananya* dulu. Kayak cek rute di Maps sebelum jalan. | Peta: rute merah salah dicoret, rute hijau tergambar ke pin tujuan | push-in + pan ikut rute | 04 RENCANA | whip | ding pelan saat rute hijau sampai | Tip 4 |
| review | Lima, *review* dan test dulu, baru commit. AI itu partner, bukan *autopilot*. | Diff card + bar test 12/12; saklar AUTOPILOT dimatikan, PARTNER nyala | pan ke saklar, punch-in + shake di 'autopilot' | 05 REVIEW | whip | hit di 'autopilot' | Tip 5 |
| jasa | Punya ide aplikasi tapi nggak sempat ngoding? Biar *AGJ Labs* yang bantu bikinin. | Bohlam ide menyala → 3 kartu layanan (Website & Web App, Aplikasi Mobile, AI & Otomasi) keluar dari bohlam | zoom dip masuk, pan turun ke kartu | AGJ LABS | zoom | pop pelan di 'AGJ' | Soft selling |
| cta | Save dulu biar nggak lupa, terus follow *AGJ Labs* ya! | Logo AGJ Labs, tombol Save ditap jadi hijau, pill Follow @agjlabs | push-in pelan | logo + tombol | whip | pop pelan saat tap | Satu aksi |

Semua aksi dikunci ke kata VO (`ctx.word`). SFX total ±14 event di 50 dtk (whoosh transisi pelan + 2 hit + beberapa pop/ding), volume rendah, otomatis turun saat ada narasi.

## Catatan revisi
| Tanggal | Scene | Perubahan |
|---|---|---|
| 2026-10-26 | semua | v4: rebuild di engine skill — kamera, visual analogi, SFX dikurangi, recap diganti analogi |
