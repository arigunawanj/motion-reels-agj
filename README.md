# motion-reels-agj

Skill AI agent untuk memproduksi **video motion graphics TikTok / Instagram Reels / Shorts** secara profesional:
9:16 · 1080×1920 · **60 fps** · H.264 + AAC · kamera bergerak · caption karaoke · voice-over TTS · SFX · QC otomatis.

Bekerja di **Claude Code, OpenAI Codex, dan Google Antigravity** (instruksi `SKILL.md` + CLI Python yang sama).

## Workflow
```
Briefing → Research & Concept → Script & Storyboard → Finalisasi → Produksi → TTS & Sound → Preview → Final → QC
   [✓]            [✓]                                    [✓]                                  [✓]
```
- **Studio Mode** (default): agent berhenti minta approval di brief, storyboard, dan preview. Gerbang ditegakkan oleh CLI.
- **Auto Mode**: jalan terus dari brief yang ada; QC tetap wajib.


## Desain default: AGJ Labs
Semua video otomatis memakai desain brand AGJ Labs (tema terang, warna logo biru-kuning-hijau, potongan logo melayang di background, transisi sapuan logo, kartu putih taktil, caption pill biru/kuning). Temanya terpasang saat `mr init` lewat `templates/project/`. Ganti desain hanya kalau diminta.
Contoh lengkap: [`examples/vibe-coding-agj/`](examples/vibe-coding-agj/).

## Rubrik konten AGJ Labs
Setiap video masuk satu rubrik, dengan badge di hook, formula naskah, dan CTA masing-masing ([`references/rubrik-konten.md`](references/rubrik-konten.md)):

| Rubrik | Badge | Isi |
|---|---|---|
| **PULSE.** | Kabar Tech | Berita tech → artinya buat bisnis |
| **NO CAP.** | Ngomong Jujur | Opini & bongkar mitos tech/bisnis |
| **DECODE.** | Biar Gampang | Masalah operasional + solusi via analogi |
| **LAB MODE.** | Kami Coba | Eksperimen & demo yang dibangun tim |
| **UNPACK.** | Bedah Bisnis | Roast website, studi kasus, before-after |

```bash
python3 $S init decode-01-admin-fotokopi --rubrik decode --voice ari-santai
```

## Fase 10 — Social Publishing
Setelah QC video lulus, caption TikTok, Instagram Reels, dan Facebook Reels dibuat oleh skill terpisah [**social-caption-publish**](https://github.com/arigunawanj/social-caption-publish) (netral brand & bahasa). Pasang juga skill itu:
```bash
curl -fsSL https://raw.githubusercontent.com/arigunawanj/social-caption-publish/main/install.sh | sh
```

## Install
```bash
git clone https://github.com/arigunawanj/motion-reels-agj && cd motion-reels-agj
./install.sh                # global; atau ./install.sh --project di dalam repo kamu
brew install ffmpeg         # atau apt install ffmpeg
pip install numpy playwright && python3 -m playwright install chromium
export TTS_API_KEY=...      # simpan di ~/.zshrc — jangan pernah commit
```

## Pakai
Bilang ke agent: *"Bikin reels motion graphic kenapa website lemot bikin customer kabur, analogi gen z, 45 detik."*
Agent akan briefing dulu, kasih konsep & storyboard, preview, baru render final.

CLI manual:
```bash
S=~/.claude/skills/motion-reels-agj/scripts/mr.py
python3 $S init  konten-1 --rubrik decode --voice ari-santai   # project + dokumen produksi
python3 $S status konten-1                       # fase & langkah berikutnya
python3 $S approve konten-1 brief                # setelah user setuju (brief/concept/storyboard/preview)
python3 $S check-tts konten-1                    # preflight API TTS
python3 $S tts konten-1                          # VO per scene → timeline sinkron
python3 $S stills konten-1                       # contact sheet
python3 $S preview konten-1                      # 540×960@30 cepat
python3 $S render konten-1 --workers 8           # final 1080×1920@60, cache per scene
python3 $S qc konten-1                           # laporan QC → production/qc-report.md
```
Coba contoh: `cp -R ~/.claude/skills/motion-reels-agj/examples/website-lemot . && python3 $S init website-lemot` (melengkapi engine & index.html), lalu `tts` → `preview`.

Preview interaktif: buka `konten-1/index.html` di browser (spasi = play).

## Revisi
- Ganti kalimat 1 scene → hanya scene itu yang ke TTS.
- Ubah animasi 1 scene → hanya scene itu (+ transisi tetangga) yang dirender ulang.
- Ganti voice → ubah `voice` di `script.json`, jalankan `tts` + `render`.

## Isi
```
SKILL.md                 instruksi agent (9 fase, gerbang, aturan kualitas)
AGENTS.md                adapter Codex
templates/               creative-brief, concept, storyboard, visual-direction, qc-checklist, project/
engine/                  engine.js (kamera, easing, caption, SFX, hook QC) + base.css
scripts/mr.py            CLI produksi & validasi
references/              naskah-genz.md, motion-kamera.md, engines.md (GSAP/Three.js/Canvas)
examples/website-lemot/  contoh 8 scene lengkap
```
