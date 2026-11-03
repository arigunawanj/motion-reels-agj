#!/usr/bin/env python3
"""
vlog.py — tipe konten VLOG NARASI (footage perjalanan/aktivitas sendiri + auto-cut + VO TTS + suara asli + SFX halus).

Satu sumber kebenaran: <dir>/vlog.json (daftar scene). Semua render lewat ffmpeg (tanpa Playwright/HyperFrames).
Tema visual dipilih lewat "theme" di vlog.json (lihat THEMES di bawah; tambah tema baru = tambah satu entri).

  init     <dir> [--voice ari-santai] [--theme clean]   project + vlog.json + dokumen produksi
  scan     <dir> --footage <folder|file ...>            inventaris klip: durasi, orientasi, contact sheet, transkrip suara asli
  check-tts <dir>                                       preflight API TTS (butuh env TTS_API_KEY)
  build    <dir> [--scenes 0-5] [--takes 3] [--crf 23]  vlog.json → TTS (best-of-N) → potong → mix → caption → <dir>/<dir>.mp4
  qc       <dir>                                        spesifikasi, loudness, frame hitam → production/qc-report.md

Kebutuhan: python3, ffmpeg, pip install numpy faster-whisper (whisper opsional untuk scan & pemilihan take TTS).
TTS: env TTS_API_KEY (wajib, jangan ditulis di file), TTS_URL (default https://tts.venturo.pro/v1/audio/speech).
"""
import argparse, difflib, hashlib, json, os, re, shutil, subprocess, sys, urllib.request, wave
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import assets

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
DEFAULT_URL = "https://tts.venturo.pro/v1/audio/speech"
SR = 44100
W, H = 1080, 1920

# ------------------------------------------------------------------ tema
# Tambah tema baru di sini (mis. "motion" untuk vlog + motion grafik). Semua nilai dipakai builder; tidak ada if per-nama tema.
THEMES = {
    "clean": dict(
        desc="Vlog bersih: footage apa adanya, caption putih tebal, label lokasi kotak hitam, SFX sangat halus.",
        sat=1.10, contrast=1.03, loudness=-15,
        font="Poppins",
        cap=dict(size=74, outline=5, shadow=2, margin_v=560),
        title=dict(size=104, margin_v=330), sub=dict(size=52, margin_v=470, color="&H0000D7FF"),
        label=dict(size=44, margin_v=230),
        sfx_gain=dict(whoosh=0.30, chime=0.22, horn=0.30, pop=0.35, final=0.28),
    ),
}


def die(m):
    print("✗ " + m); sys.exit(1)


def run(cmd, **kw):
    r = subprocess.run(cmd, **kw)
    if r.returncode != 0:
        die("gagal: " + " ".join(map(str, cmd))[:220])
    return r


def sh_out(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def load(d):
    p = Path(d) / "vlog.json"
    if not p.exists():
        die(f"{p} tidak ada — jalankan init dulu")
    return json.loads(p.read_text())


def dur_of(p):
    return float(sh_out(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]).stdout.strip() or 0)


# ------------------------------------------------------------------ init
def cmd_init(a):
    d = Path(a.dir)
    if (d / "vlog.json").exists():
        die(f"{d}/vlog.json sudah ada")
    if a.theme not in THEMES:
        die(f"tema '{a.theme}' tidak ada. Tersedia: {', '.join(THEMES)}")
    for sub in ("production", "audio", "build"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    assets.scaffold(d, "vlog")
    tpl = SKILL / "templates" / "vlog"
    spec = json.loads((tpl / "vlog.json").read_text())
    spec["voice"] = a.voice
    spec["theme"] = a.theme
    (d / "vlog.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False))
    for f in ("creative-brief.md", "story-plan.md"):
        shutil.copy(tpl / f, d / "production" / f)
    print(f"✓ project {d}  →  lanjut: taruh/isi footage, scan, isi story-plan + vlog.json, build")


# ------------------------------------------------------------------ scan
def _whisper(model="small"):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    return WhisperModel(model, compute_type="int8")


def _audio_np(path):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0", "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def cmd_scan(a):
    d = Path(a.dir)
    files = []
    for f in a.footage:
        p = Path(f)
        files += sorted(x for x in p.iterdir() if x.suffix.lower() in (".mov", ".mp4", ".m4v")) if p.is_dir() else [p]
    if not files:
        die("tidak ada klip")
    sheets = d / "build" / "sheets"; sheets.mkdir(parents=True, exist_ok=True)
    wm = None if a.no_speech else _whisper(a.model)
    if wm is None and not a.no_speech:
        print("! faster-whisper belum terpasang → transkrip dilewati (pip install faster-whisper numpy)")
    rows, trans = [], {}
    for f in files:
        j = json.loads(sh_out(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(f)]).stdout or "{}")
        v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
        has_a = any(s.get("codec_type") == "audio" for s in j.get("streams", []))
        dur = float(j.get("format", {}).get("duration", 0))
        rot = 0
        for sd in v.get("side_data_list", []) or []:
            rot = sd.get("rotation", rot)
        wh = (v.get("width"), v.get("height")); portrait = (wh[1] > wh[0]) != (abs(int(rot or 0)) == 90)
        step = max(2.0, dur / 18)
        run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-map", "0:v:0", "-vf",
             f"fps=1/{step:.2f},scale=-2:300,drawtext=text='%{{pts\\:hms}}':x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=9x2",
             "-frames:v", "1", str(sheets / f"{f.stem}.jpg")])
        speech = []
        if wm is not None and has_a:
            segs, _ = wm.transcribe(_audio_np(f), language=a.lang, vad_filter=True, condition_on_previous_text=False)
            speech = [[round(s.start, 1), round(s.end, 1), s.text.strip()] for s in segs]
        trans[f.name] = speech
        rows.append((f.name, dur, f"{wh[0]}x{wh[1]}", "portrait" if portrait else "LANDSCAPE", "ya" if has_a else "tidak", len(speech)))
        print(f"… {f.name} {dur:.1f}s {'ucapan: ' + str(len(speech)) + ' segmen' if speech else ''}")
    (d / "build" / "transcripts.json").write_text(json.dumps(trans, ensure_ascii=False, indent=1))
    md = ["# Inventaris footage", "", "| Klip | Durasi | Ukuran | Orientasi | Audio | Segmen ucapan |", "|---|---|---|---|---|---|"]
    md += [f"| {n} | {du:.1f}s | {r} | {o} | {au} | {s} |" for n, du, r, o, au, s in rows]
    md += ["", "## Transkrip suara asli (otomatis — BACA ULANG, jangan dipercaya mentah-mentah)", ""]
    for n, sp in trans.items():
        md.append(f"### {n}")
        md += [f"- [{s:5.1f}–{e:5.1f}] {t}" for s, e, t in sp] or ["- (tidak ada ucapan)"]
        md.append("")
    md += ["Contact sheet per klip: `build/sheets/<klip>.jpg`. **Lihat semuanya** sebelum menulis story-plan.",
           "Kalimat \"Terima kasih sudah menonton\" di klip pendek/senyap = halusinasi Whisper, abaikan."]
    (d / "production" / "footage.md").write_text("\n".join(md) + "\n")
    print(f"✓ production/footage.md + build/sheets/*.jpg ({len(files)} klip)")


# ------------------------------------------------------------------ TTS
def find_bgm(d, name):
    return assets.find_sound(d, name)


def tts_conf():
    key = os.environ.get("TTS_API_KEY", "")
    return os.environ.get("TTS_URL", DEFAULT_URL), key


def tts_call(text, voice, out):
    url, key = tts_conf()
    if not key:
        die("TTS_API_KEY belum di-set. export TTS_API_KEY=... (jangan tulis di file project)")
    req = urllib.request.Request(url, data=json.dumps({"input": text, "voice": voice}).encode(), headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "curl/8.5.0", "Accept": "*/*"})
    try:
        data = urllib.request.urlopen(req, timeout=120).read()
    except Exception as e:
        die(f"TTS gagal ({e}). Cek key, server, atau allowlist domain environment.")
    if len(data) < 1000:
        die(f"TTS membalas terlalu kecil: {data[:200]!r}")
    Path(out).write_bytes(data)


def cmd_check_tts(a):
    sp = load(a.dir)
    t = Path(a.dir) / "build" / "_ttscheck.mp3"
    tts_call("Halo, ini tes suara.", sp.get("voice", "ari-santai"), t)
    print(f"✓ TTS ok — voice {sp.get('voice')}, {dur_of(t):.1f}s")


def _norm(s):
    return re.sub(r"[^a-z ]", "", s.lower().replace("-", " ")).strip()


def tts_best(d, text, voice, takes, wm):
    """Generate N take, pilih yang paling jelas (mirip teks menurut Whisper) dan tempo paling natural (~3 kata/dtk)."""
    h = hashlib.sha1(f"{voice}|{text}".encode()).hexdigest()[:10]
    final = d / "audio" / f"vo_{h}.wav"
    info = d / "audio" / f"vo_{h}.json"
    if final.exists():
        return final, json.loads(info.read_text()) if info.exists() else {}
    best, bscore, bsim = None, -9, None
    words = len(text.split())
    for k in range(takes):
        f = d / "audio" / f"take_{h}_{k}.mp3"
        if not f.exists() or f.stat().st_size < 1000:
            tts_call(text, voice, f)
        du = dur_of(f)
        sim = None
        if wm is not None:
            segs, _ = wm.transcribe(_audio_from(f), language="id", beam_size=3, condition_on_previous_text=False)
            sim = difflib.SequenceMatcher(None, _norm(text), _norm(" ".join(s.text for s in segs))).ratio()
        score = (sim if sim is not None else 0.9) - abs(words / du - 3.0) * 0.05
        print(f"   take {k}: {du:.1f}s sim={'-' if sim is None else f'{sim:.2f}'} skor={score:.2f}", flush=True)
        if score > bscore:
            best, bscore, bsim = f, score, sim
    # trim hening awal/akhir SAJA (jangan stop_periods: memotong di jeda antar kalimat), kompres ringan, presence
    run(["ffmpeg", "-v", "error", "-y", "-i", str(best), "-af",
         "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.04,areverse,"
         "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12,areverse,"
         "highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=80:makeup=3,"
         "equalizer=f=3200:t=q:w=1:g=1.5,aresample=44100,aformat=channel_layouts=mono", str(final)])
    meta = {"sim": bsim, "text": text}
    info.write_text(json.dumps(meta))
    return final, meta


def _audio_from(path):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


# ------------------------------------------------------------------ SFX sintetis (halus, tanpa aset eksternal)
def make_sfx(outdir):
    try:
        import numpy as np
    except ImportError:
        die("pip install numpy")
    outdir.mkdir(parents=True, exist_ok=True)

    def save(name, x):
        x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
        w = wave.open(str(outdir / f"{name}.wav"), "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()

    def env(n, at, rl):
        e = np.ones(n); na, nr = int(at * SR), int(rl * SR)
        e[:na] = np.linspace(0, 1, na) ** 2; e[-nr:] = np.linspace(1, 0, nr) ** 2
        return e

    def tone(f, d):
        t = np.arange(int(d * SR)) / SR
        return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.15 * np.sin(2 * np.pi * 3 * f * t)) * np.exp(-t * 4.5)

    rng = np.random.default_rng(7)
    n = int(0.75 * SR); noise = rng.standard_normal(n); out = np.zeros(n); y = 0.0
    for t in range(n):                                   # whoosh: noise dengan cutoff naik-turun
        a_ = 0.03 + 0.35 * np.sin(np.pi * t / n) ** 1.5
        y += a_ * (noise[t] - y); out[t] = y
    save("whoosh", out * env(n, 0.3, 0.4))
    c = np.zeros(int(1.5 * SR)); a1, b1 = tone(880, 0.9), tone(659, 1.0)                   # chime ding-dong stasiun
    c[:len(a1)] += a1; c[int(0.45 * SR):int(0.45 * SR) + len(b1)] += b1; save("chime", c)
    t = np.arange(int(1.6 * SR)) / SR                                                       # klakson kapal
    hn = sum(np.sin(2 * np.pi * f * t) * g for f, g in [(98, 1), (147, .7), (196, .5), (294, .25)])
    save("horn", hn * env(len(t), 0.18, 0.7))
    t = np.arange(int(0.18 * SR)) / SR; f = 500 + 900 * t / 0.18                            # pop judul
    save("pop", np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22))
    fin = np.zeros(int(2.0 * SR))                                                           # arpeggio sampai tujuan
    for k, fr in enumerate([523.25, 659.25, 783.99, 1046.5]):
        s = tone(fr, 1.2); o = int(k * 0.16 * SR); fin[o:o + len(s)] += s[:len(fin) - o]
    save("final", fin)


# ------------------------------------------------------------------ build
def _parse_scenes(spec, s):
    if not s:
        return list(range(len(spec["scenes"])))
    out = []
    for part in s.split(","):
        if "-" in part:
            x, y = part.split("-"); out += list(range(int(x), int(y) + 1))
        else:
            out.append(int(part))
    return [i for i in out if 0 <= i < len(spec["scenes"])]


def _chunk(text, a, b, ev):
    words, chunks, cur = text.replace("{", "(").replace("}", ")").split(), [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or re.search(r"[.,!?…]$", w):
            chunks.append(" ".join(cur)); cur = []
    if cur:
        chunks.append(" ".join(cur))
    tot = sum(len(c) for c in chunks) or 1; x = a
    for c in chunks:
        y = x + (b - a) * len(c) / tot
        ev.append((x, y, c.rstrip(".,"))); x = y


def _ts(x):
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


def _font_dir(font):
    r = sh_out(["fc-match", "-f", "%{file}", f"{font}:bold"]).stdout.strip()
    return str(Path(r).parent) if r and font.lower() in r.lower() else None


def cmd_build(a):
    d = Path(a.dir).resolve(); spec = load(d)
    th = THEMES.get(spec.get("theme", "clean"))
    if th is None:
        die(f"tema '{spec.get('theme')}' tidak ada. Tersedia: {', '.join(THEMES)}")
    voice = spec.get("voice", "ari-santai")
    takes = a.takes or spec.get("takes", 3)
    fdir = Path(spec.get("footageDir", "footage"))
    fdir = fdir if fdir.is_absolute() else (d / fdir)
    idx = _parse_scenes(spec, a.scenes)
    bd = d / "build" / "seg"; bd.mkdir(parents=True, exist_ok=True); (d / "audio").mkdir(exist_ok=True)
    sfxdir = d / "build" / "sfx"; make_sfx(sfxdir)
    wm = None if a.no_whisper else _whisper("small")
    if wm is None:
        print("! tanpa faster-whisper: take TTS dipilih dari tempo saja")
    segs, t, report = [], 0.0, []
    for n_, i in enumerate(idx):
        sc = spec["scenes"][i]; vod = 0.0; meta = {}
        clip = Path(sc["clip"]); src = clip if clip.is_absolute() else fdir / clip
        if not src.exists():
            die(f"scene {i}: klip tidak ada: {src}")
        if sc.get("vo"):
            print(f"· scene {i} VO: {sc['vo'][:60]}")
            vo, meta = tts_best(d, sc["vo"], voice, takes, wm); sc["_vo"] = str(vo); vod = dur_of(vo)
        dd = max(sc.get("dur", 3.0), vod + 0.55) if sc.get("vo") else sc.get("dur", 3.0)
        cd = dur_of(src); st = sc.get("start", 0.0); avail = cd - st
        if avail < 0.3:
            st = max(0, cd - dd); avail = cd - st
        slow = max(1.0, dd / avail); need = dd / slow
        z = sc.get("zoom", 1.0)
        vf = (f"fps=60,setpts=PTS-STARTPTS,setpts={slow:.4f}*PTS,fps=30,"
              f"scale={int(W * z)}:{int(H * z)}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"eq=saturation={th['sat']}:contrast={th['contrast']},format=yuv420p")
        out = bd / f"seg_{i:03d}.mp4"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{st:.3f}", "-t", f"{need:.3f}", "-i", str(src)]
        mode = sc.get("mode", "none")
        probe_a = sh_out(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(src)]).stdout.strip()
        if mode in ("own", "amb") and not probe_a:
            mode = "none"
        if mode == "own":      # suara asli: bersihkan angin ringan + samakan level
            af = ("highpass=f=90,afftdn=nf=-28,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100,"
                  f"apad,atrim=0:{dd:.3f},aformat=channel_layouts=stereo")
            cmd += ["-map", "0:v:0", "-map", "0:a:0", "-vf", vf, "-af", af]
        elif mode == "amb":    # suasana: kecil di bawah narasi, besar kalau tanpa narasi
            af = (f"volume={sc.get('vol', 0.5)},aresample=44100,apad,atrim=0:{dd:.3f},"
                  f"afade=t=in:d=0.08,afade=t=out:st={dd - 0.15:.3f}:d=0.15,aformat=channel_layouts=stereo")
            cmd += ["-map", "0:v:0", "-map", "0:a:0", "-vf", vf, "-af", af]
        else:
            cmd += ["-f", "lavfi", "-t", f"{dd:.3f}", "-i", "anullsrc=r=44100:cl=stereo", "-map", "0:v:0", "-map", "1:a:0", "-vf", vf]
        cmd += ["-t", f"{dd:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "160k", str(out)]
        run(cmd)
        segs.append((t, dd, vod, i, out)); report.append((i, sc["clip"], round(t, 1), round(dd, 1), mode, meta.get("sim")))
        t += dd
    total = t
    lst = bd / "list.txt"
    lst.write_text("".join(f"file '{o.name}'\n" for *_, o in segs))
    base = d / "build" / "base.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(base)])

    # ---- caption + label + judul (ASS)
    f = th["font"]
    st_ = lambda n, sz, col, bs, ol, sh, al, mv: f"Style: {n},{f},{sz},{col},&H000000FF,&H00000000,{bs},-1,0,0,0,100,100,0,0,{3 if n == 'Lbl' else 1},{ol},{sh},{al},{60 if n != 'Cap' else 90},{60 if n != 'Cap' else 90},{mv},1"
    ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "", "[V4+ Styles]",
           "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
           st_("Cap", th["cap"]["size"], "&H00FFFFFF", "&H64000000", th["cap"]["outline"], th["cap"]["shadow"], 2, th["cap"]["margin_v"]),
           st_("Title", th["title"]["size"], "&H00FFFFFF", "&H64000000", 6, 3, 8, th["title"]["margin_v"]),
           st_("Sub", th["sub"]["size"], th["sub"]["color"], "&H64000000", 4, 2, 8, th["sub"]["margin_v"]),
           st_("Lbl", th["label"]["size"], "&H00FFFFFF", "&H78000000", 10, 0, 8, th["label"]["margin_v"]),
           "", "[Events]", "Format: Layer,Start,End,Style,Name,Effect,Text"]
    ev = []
    for (t0, dd, vod, i, _) in segs:
        sc = spec["scenes"][i]
        if sc.get("vo"):
            _chunk(sc["vo"], t0 + 0.15, t0 + 0.15 + vod, ev)
        for ra, rb, txt in sc.get("caps", []):
            _chunk(txt, t0 + ra, t0 + rb, ev)
        if sc.get("label"):
            ass.append(f"Dialogue: 1,{_ts(t0 + 0.15)},{_ts(t0 + min(dd - 0.1, 3.2))},Lbl,,,{{\\fad(200,250)}}{sc['label']}")
        if sc.get("title"):
            ass.append(f"Dialogue: 1,{_ts(t0 + 0.2)},{_ts(t0 + 3.4)},Title,,,{{\\fad(250,300)}}{spec.get('title', '')}")
            ass.append(f"Dialogue: 1,{_ts(t0 + 0.2)},{_ts(t0 + 3.4)},Sub,,,{{\\fad(250,300)}}{spec.get('subtitle', '')}")
    ass += [f"Dialogue: 0,{_ts(x)},{_ts(y)},Cap,,,{c}" for x, y, c in ev]
    (d / "build" / "cap.ass").write_text("\n".join(ass))
    fd = _font_dir(f)
    vfilter = f"ass={d / 'build' / 'cap.ass'}" + (f":fontsdir={fd}" if fd else "")
    if not fd:
        print(f"! font {f} tidak ditemukan di sistem — caption pakai font cadangan (install {f} untuk hasil sesuai desain)")
    vid = d / "build" / "video_cap.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(base), "-vf", vfilter, "-c:v", "libx264", "-preset", "medium",
         "-crf", str(a.crf), "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p", "-an", str(vid)])

    # ---- backsound (opsional): "bgm": {"file": "nama.mp3", "volume": 0.12} — dicari di BACKSOUND_DIR / footage / path
    bgm_cfg = spec.get("bgm") or {}
    bgm_path = find_bgm(d, bgm_cfg["file"]) if bgm_cfg.get("file") else None
    if bgm_cfg.get("file") and not bgm_path:
        print(f"! backsound '{bgm_cfg['file']}' tidak ditemukan (set BACKSOUND_DIR atau beri path penuh) — build tanpa musik")

    # ---- audio: suara scene + narasi + SFX (+ backsound) → dua versi (dengan & tanpa SFX/musik)
    def mix(with_sfx, dest):
        inputs, filt, labs = [], [], []
        def add(path, t_abs, gain):
            k = len(labs); inputs.extend(["-i", str(path)]); ms = max(0, int(t_abs * 1000))
            filt.append(f"[{k + 1}:a]aresample=44100,volume={gain},adelay={ms}|{ms}[a{k}]"); labs.append(f"[a{k}]")
        for (t0, dd, vod, i, _) in segs:
            sc = spec["scenes"][i]
            if sc.get("_vo"):
                add(sc["_vo"], t0 + 0.15, 1.0)
            if with_sfx:
                for name, off in sc.get("sfx", []):
                    add(sfxdir / f"{name}.wav", t0 + off, th["sfx_gain"].get(name, 0.25))
        mixer = (f"[0:a]{''.join(labs)}amix=inputs={len(labs) + 1}:normalize=0:duration=first,alimiter=limit=0.95" if labs
                 else "[0:a]anull")
        tail = f"loudnorm=I={th['loudness']}:TP=-1.5:LRA=9[aout]"
        if with_sfx and bgm_path:
            k = len(labs) + 1; inputs.extend(["-stream_loop", "-1", "-i", str(bgm_path)])
            bv = float(bgm_cfg.get("volume", 0.30)); fo = max(0.0, total - 1.5)
            filt.append(mixer + "[m];[m]asplit=2[m1][m2]")
            filt.append(f"[{k}:a]aresample=44100,aformat=channel_layouts=stereo,loudnorm=I=-18:TP=-2:LRA=11,aresample=44100,volume={bv},afade=t=in:d=1.0,"
                        f"afade=t=out:st={fo:.2f}:d=1.5,atrim=0:{total:.2f}[bg]")
            filt.append("[bg][m2]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=500[bgd]")
            chain = f"[m1][bgd]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95,{tail}"
        else:
            chain = mixer + "," + tail
        filt.append(chain)
        wav = d / "build" / ("mix_sfx.m4a" if with_sfx else "mix_nosfx.m4a")
        run(["ffmpeg", "-v", "error", "-y", "-i", str(base), *inputs, "-filter_complex", ";".join(filt), "-map", "[aout]", "-vn",
             "-c:a", "aac", "-b:a", "192k", str(wav)])
        run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest",
             "-movflags", "+faststart", str(dest)])

    final = d / f"{d.name}.mp4"
    mix(True, final)
    mix(False, d / f"{d.name}-tanpa-sfx.mp4")
    rep = ["# Laporan build", "", f"Total {total:.1f} dtk · tema {spec.get('theme')} · voice {voice}", "",
           "| # | Klip | Mulai | Durasi | Audio | Kemiripan VO |", "|---|---|---|---|---|---|"]
    rep += [f"| {i} | {c} | {s}s | {du}s | {m} | {'-' if sim is None else f'{sim:.2f}'} |" for i, c, s, du, m, sim in report]
    low = [r for r in report if r[5] is not None and r[5] < 0.85]
    if low:
        rep += ["", "**VO kemiripan < 0.85 (dengarkan ulang / ganti kalimat / naikkan --takes):** " + ", ".join(str(r[0]) for r in low)]
    (d / "production" / "build-report.md").write_text("\n".join(rep) + "\n")
    print(f"✓ {final}  ({total:.0f} dtk)\n✓ {d / (d.name + '-tanpa-sfx.mp4')}  (tanpa SFX & backsound, untuk menambah sound trending di aplikasi)\n→ lanjut: qc")


# ------------------------------------------------------------------ qc
def cmd_qc(a):
    d = Path(a.dir).resolve(); vid = d / f"{d.name}.mp4"
    if not vid.exists():
        die("build dulu")
    pj = json.loads(sh_out(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(vid)]).stdout)
    v = next(s for s in pj["streams"] if s["codec_type"] == "video")
    du = float(pj["format"]["duration"])
    res = []
    ok = lambda c, m: res.append(("✓" if c else "✗", m))
    ok((v["width"], v["height"]) == (W, H), f"ukuran {v['width']}x{v['height']} (harus {W}x{H})")
    ok(du <= 120, f"durasi {du:.1f}s ({'ok' if du <= 90 else 'cukup panjang, pertimbangkan versi ringkas'})")
    ln = sh_out(["ffmpeg", "-i", str(vid), "-af", "ebur128=peak=true", "-vn", "-f", "null", "-"]).stderr
    lufs = re.findall(r"I:\s+(-?\d+\.\d+) LUFS", ln); peak = re.findall(r"Peak:\s+(-?\d+\.\d+) dBFS", ln)
    if lufs:
        ok(-17 <= float(lufs[-1]) <= -13, f"loudness {lufs[-1]} LUFS (target -17…-13)")
    if peak:
        ok(float(peak[-1]) <= -1.0, f"true peak {peak[-1]} dBFS (maks -1.0)")
    bl = sh_out(["ffmpeg", "-i", str(vid), "-vf", "blackdetect=d=0.3:pix_th=0.05", "-an", "-f", "null", "-"]).stderr
    blk = re.findall(r"black_start:(\S+) black_end:(\S+)", bl)
    ok(not blk, "tidak ada frame hitam" if not blk else f"frame hitam: {blk[:3]}")
    md = ["# QC Vlog", ""] + [f"- {s} {m}" for s, m in res] + ["", "Cek manual: lihat contact sheet frame (label tidak menutup wajah, caption di zona 1340–1520, tidak ada klaim yang tidak diucapkan/dilihat), dengarkan SFX (tidak menutupi suara)."]
    (d / "production" / "qc-report.md").write_text("\n".join(md) + "\n")
    print("\n".join(f"{s} {m}" for s, m in res))
    sheet = d / "build" / "final-contact.jpg"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-vf", f"fps=1/{max(2, du / 18):.1f},scale=-2:340,tile=10x2", "-frames:v", "1", str(sheet)])
    print(f"✓ production/qc-report.md · contact sheet {sheet} (lihat gambarnya)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init"); p.add_argument("dir"); p.add_argument("--voice", default="ari-santai"); p.add_argument("--theme", default="clean"); p.set_defaults(fn=cmd_init)
    p = sp.add_parser("scan"); p.add_argument("dir"); p.add_argument("--footage", nargs="+", required=True)
    p.add_argument("--model", default="small"); p.add_argument("--lang", default="id"); p.add_argument("--no-speech", action="store_true"); p.set_defaults(fn=cmd_scan)
    p = sp.add_parser("check-tts"); p.add_argument("dir"); p.set_defaults(fn=cmd_check_tts)
    p = sp.add_parser("build"); p.add_argument("dir"); p.add_argument("--scenes"); p.add_argument("--takes", type=int)
    p.add_argument("--crf", type=int, default=23); p.add_argument("--no-whisper", action="store_true"); p.set_defaults(fn=cmd_build)
    p = sp.add_parser("qc"); p.add_argument("dir"); p.set_defaults(fn=cmd_qc)
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
