#!/usr/bin/env python3
"""
mr.py — CLI produksi Motion Reels (portable: Claude Code / Codex / Antigravity / terminal biasa)

  init      <dir> [--mode studio|auto] [--voice ari-santai] [--title ".."]   project + dokumen produksi
  status    <dir>                                   fase, approval, langkah berikutnya
  approve   <dir> brief|concept|storyboard|preview [--note ..]
  check-tts [<dir>] [--voice ..]                    preflight API TTS (wajib sebelum produksi)
  tts       <dir> [--scene id,id] [--force] [--draft]   VO per scene → build/timeline.js (sinkron jeda suara)
  stills    <dir> [--every 1.5 | --at 1,4.5]        contact sheet cepat
  preview   <dir> [--scale 0.5] [--fps 30]          video preview kualitas rendah
  render    <dir> [--workers N] [--scenes id,id] [--no-cache] [--allow-silent]   final 1080x1920 60fps
  qc        <dir> [--video file.mp4]                QC otomatis → production/qc-report.md
  publish-init  <dir>                               Fase 10: siapkan publishing/ (butuh QC lulus)
  publish-check <dir>                               validasi caption/hashtag TikTok, IG, FB → publishing/caption-qc.md

Kebutuhan: python3, ffmpeg/ffprobe, numpy, playwright (+ `python -m playwright install chromium`).
TTS: env TTS_API_KEY (wajib), TTS_URL (default https://tts-api.agjhub.site/v1/audio/speech).
"""
import argparse, hashlib, json, math, os, re, shutil, subprocess, sys, time, urllib.request, urllib.error, wave
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
GATES = ["brief", "concept", "storyboard", "preview", "publishing"]
DOCS = ["creative-brief.md", "concept.md", "storyboard.md", "visual-direction.md"]
DEFAULT_URL = "https://tts-api.agjhub.site/v1/audio/speech"


# ================================================================ util
def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def ffprobe_dur(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def die(msg, code=1):
    print(f"✗ {msg}")
    sys.exit(code)


def sha(*parts):
    h = hashlib.sha1()
    for p in parts:
        h.update(p if isinstance(p, bytes) else str(p).encode())
    return h.hexdigest()[:12]


def fhash(p):
    p = Path(p)
    return sha(p.read_bytes()) if p.exists() else "none"


# ================================================================ state & gates
def state_path(d):
    return Path(d) / "production" / "state.json"


def load_state(d):
    p = state_path(d)
    if p.exists():
        return json.loads(p.read_text())
    return {"mode": "studio", "approvals": {}, "created": datetime.now().isoformat(timespec="seconds")}


def save_state(d, st):
    state_path(d).parent.mkdir(parents=True, exist_ok=True)
    state_path(d).write_text(json.dumps(st, indent=2, ensure_ascii=False))


def gate_snapshot(d, gate):
    d = Path(d)
    files = {"brief": ["production/creative-brief.md"], "concept": ["production/concept.md"],
             "storyboard": ["production/storyboard.md", "script.json"],
             "preview": ["script.json", "scenes.js", "style.css"],
             "publishing": [f"publishing/{f}" for f in PUB_FILES]}[gate]
    return sha(*[fhash(d / f) for f in files])


def require_gate(d, gate, action):
    st = load_state(d)
    if st.get("mode") == "auto":
        return
    ap = st.get("approvals", {}).get(gate)
    if not ap:
        die(f"{action} butuh approval '{gate}' dulu (Studio Mode). Tampilkan ke user, lalu: mr.py approve {d} {gate}")
    if ap.get("snapshot") != gate_snapshot(d, gate):
        print(f"! file sudah berubah sejak '{gate}' di-approve ({ap['at']}). Pastikan perubahan sudah disetujui user.")


# ================================================================ init / status / approve
def cmd_init(a):
    d = Path(a.dir)
    d.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "engine", d / "engine", dirs_exist_ok=True)
    for f in (ROOT / "templates" / "project").iterdir():
        if not (d / f.name).exists():
            shutil.copy(f, d / f.name)
    prod = d / "production"
    prod.mkdir(exist_ok=True)
    for doc in DOCS + ["qc-checklist.md"]:
        if not (prod / doc).exists():
            shutil.copy(ROOT / "templates" / doc, prod / doc)
    (d / "build").mkdir(exist_ok=True)
    (d / "audio").mkdir(exist_ok=True)
    sc = json.loads((d / "script.json").read_text())
    if a.voice: sc["voice"] = a.voice
    if a.title: sc["title"] = a.title
    (d / "script.json").write_text(json.dumps(sc, indent=2, ensure_ascii=False))
    st = load_state(d)
    st["mode"] = a.mode
    save_state(d, st)
    print(f"✓ project {d} ({a.mode} mode)\n  Fase 1: isi production/creative-brief.md → tampilkan ke user → mr.py approve {d} brief")


NEXT = {
    None: "Fase 1 Briefing: lengkapi production/creative-brief.md, minta approval → approve brief",
    "brief": "Fase 2 Research & Concept: isi production/concept.md (3 hook, 3 storytelling, analogi) → approve concept",
    "concept": "Fase 3–4 Script & Storyboard: production/storyboard.md + script.json + visual-direction.md → approve storyboard",
    "storyboard": "Fase 5–7: check-tts → tts → koding scenes.js → stills → preview → tampilkan → approve preview",
    "preview": "Fase 8–9: render → qc → perbaiki sampai 0 error → Fase 10: publish-init → caption → publish-check → approve publishing",
    "publishing": "Siap publish — kirim paket publishing/ ke user; jangan publish otomatis tanpa izin",
}


def cmd_status(a):
    d = Path(a.dir)
    st = load_state(d)
    print(f"Project : {d}\nMode    : {st.get('mode')}")
    last = None
    for g in GATES:
        ap = st.get("approvals", {}).get(g)
        if ap:
            changed = ap.get("snapshot") != gate_snapshot(d, g)
            print(f"  ✓ {g:<10} {ap['at']}{'  (file berubah sejak approval)' if changed else ''}")
            last = g
        else:
            print(f"  · {g}")
    tl = d / "build" / "timeline.json"
    if tl.exists():
        t = json.loads(tl.read_text())
        print(f"Timeline: {len(t['scenes'])} scene, {t['total']:.2f}s, VO {'final' if t.get('voiced') else 'BELUM (estimasi)'}")
    for f in ["build/preview.mp4", f"{d.name}.mp4", "production/qc-report.md"]:
        if (d / f).exists(): print(f"  ▸ {f}")
    print(f"Berikut : {NEXT[last] if st.get('mode') != 'auto' else 'Auto Mode — lanjutkan fase berikutnya, QC tetap wajib'}")


def cmd_approve(a):
    d = Path(a.dir)
    st = load_state(d)
    st.setdefault("approvals", {})[a.gate] = {"at": datetime.now().isoformat(timespec="seconds"),
                                              "snapshot": gate_snapshot(d, a.gate), "note": a.note or ""}
    save_state(d, st)
    print(f"✓ approved: {a.gate}")


# ================================================================ TTS
def tts_conf(d=None):
    sc = {}
    if d and (Path(d) / "script.json").exists():
        sc = json.loads((Path(d) / "script.json").read_text())
    return sc, os.environ.get("TTS_URL", sc.get("ttsUrl", DEFAULT_URL)), os.environ.get("TTS_API_KEY", "")


def tts_request(text, voice, out, url, key, extra):
    body = json.dumps({"input": text, "voice": voice, **extra}).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "curl/8.5.0", "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} dari server TTS: {e.read()[:200]!r}")
    except urllib.error.URLError as e:
        hint = ""
        if "403" in str(e.reason) or "Tunnel" in str(e.reason):
            hint = " — kemungkinan domain diblokir proxy/allowlist environment agent (bukan salah API)."
        raise RuntimeError(f"tidak bisa konek ke {url}: {e.reason}{hint}")
    if len(data) < 500:
        raise RuntimeError(f"respons TTS terlalu kecil / bukan audio: {data[:200]!r}")
    out.write_bytes(data)


def cmd_check_tts(a):
    sc, url, key = tts_conf(a.dir)
    voice = a.voice or sc.get("voice", "ari-santai")
    if not key:
        die("TTS_API_KEY belum di-set. export TTS_API_KEY=... (jangan tulis di file project)")
    tmp = Path(a.dir or ".") / "build" / "tts-check.mp3"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    try:
        tts_request("Tes suara satu dua tiga.", voice, tmp, url, key, sc.get("ttsExtra", {}))
    except Exception as e:
        die(f"TTS tidak bisa dipakai: {e}")
    print(f"✓ TTS OK — voice '{voice}', {ffprobe_dur(tmp):.2f}s audio, {time.time() - t0:.1f}s respons ({url})")


def clean_vo(text):
    return re.sub(r"[*_]", "", text).strip()


def word_list(vo):
    out = []
    for tok in vo.split():
        w = tok.replace("*", "").replace("_", "")
        if w:
            out.append({"w": w, "em": "*" in tok})
    return out


def silences(path, noise="-35dB", dmin=0.12):
    err = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-af", f"silencedetect=noise={noise}:d={dmin}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(st, en + [None] * (len(st) - len(en))))


def weights(words):
    ws = []
    for w in words:
        wt = len(w["w"]) + 2.2
        if re.search(r"[,;:]$", w["w"]): wt += 4
        if re.search(r"[.!?…]$", w["w"]): wt += 7
        ws.append(wt)
    return ws


def time_words(words, t0, dur, audio=None):
    """timing per kata. Dengan audio: rentang bicara dari silencedetect, lalu titik jeda tanda baca
    di-'warp' ke jeda nyata di rekaman supaya caption nempel ke suara."""
    if not words:
        return words
    s0, s1, pauses = 0.0, dur, []
    if audio:
        sil = silences(audio)
        for a_, b_ in sil:
            b_ = dur if b_ is None else b_
            if a_ <= 0.02: s0 = max(s0, b_)
            elif b_ >= dur - 0.02: s1 = min(s1, a_)
            else: pauses.append((a_, b_))
    span = max(0.2, s1 - s0)
    ws = weights(words)
    tot = sum(ws)
    cum, prop = 0.0, []
    for w in ws:
        prop.append((s0 + span * cum / tot, s0 + span * (cum + w * 0.92) / tot))
        cum += w
    anchors = [(s0, s0), (s1, s1)]
    breaks = [i for i, w in enumerate(words[:-1]) if re.search(r"[,;:.!?…]$", w["w"])]
    used = set()
    for bi in breaks:
        exp = (prop[bi][1] + prop[bi + 1][0]) / 2
        best = None
        for j, (a_, b_) in enumerate(pauses):
            if j in used: continue
            mid = (a_ + b_) / 2
            if abs(mid - exp) < 0.7 and (best is None or abs(mid - exp) < abs((pauses[best][0] + pauses[best][1]) / 2 - exp)):
                best = j
        if best is not None:
            used.add(best)
            anchors.append((exp, (pauses[best][0] + pauses[best][1]) / 2))
    anchors.sort()
    clean = [anchors[0]]
    for x, y in anchors[1:]:
        if x > clean[-1][0] + 1e-3 and y > clean[-1][1] + 1e-3: clean.append((x, y))

    def warp(x):
        for (x0, y0), (x1, y1) in zip(clean, clean[1:]):
            if x <= x1:
                return y0 + (y1 - y0) * (x - x0) / max(1e-6, x1 - x0)
        return clean[-1][1]

    for w, (a_, b_) in zip(words, prop):
        w["s"], w["e"] = round(t0 + warp(a_), 3), round(t0 + warp(b_), 3)
    return words


def cmd_tts(a):
    d = Path(a.dir)
    sc, url, key = tts_conf(d)
    voice = sc.get("voice", "ari-santai")
    wps = sc.get("wps", 2.6)
    lead, tail, min_dur = sc.get("lead", 0.3), sc.get("tail", 0.35), sc.get("minDur", 1.6)
    only = set(a.scene.split(",")) if a.scene else None
    if not a.draft and not key:
        die("TTS_API_KEY belum di-set. Untuk timeline sementara tanpa suara pakai --draft (bukan untuk final).")
    (d / "audio").mkdir(exist_ok=True)
    (d / "build").mkdir(exist_ok=True)
    t, scenes, voiced = 0.0, [], not a.draft
    for i, s in enumerate(sc["scenes"]):
        vo = s.get("vo", "")
        text = clean_vo(vo)
        words = word_list(vo)
        audio, adur = None, None
        if text and not a.draft:
            h = sha(voice, text, json.dumps(sc.get("ttsExtra", {})))[:10]
            f = d / "audio" / f"{i:02d}-{s['id']}-{h}.mp3"
            force = a.force and (only is None or s["id"] in only)
            if force or not f.exists():
                for old in (d / "audio").glob(f"{i:02d}-{s['id']}-*.mp3"):
                    old.unlink()
                print(f"  ♪ TTS {s['id']}: {text[:60]}…")
                try:
                    tts_request(text, voice, f, url, key, sc.get("ttsExtra", {}))
                except Exception as e:
                    die(f"TTS gagal di scene '{s['id']}': {e}\n  Proses VO final dihentikan. Perbaiki akses/API, lalu jalankan ulang (scene lain sudah ter-cache).")
            audio, adur = f, ffprobe_dur(f)
        if adur is None:
            adur = len(words) / wps if words else 0.0
        dur = max(min_dur, s.get("minDur", 0), lead + adur + s.get("tail", tail), s.get("dur", 0))
        time_words(words, t + lead, adur, audio)
        scenes.append({"id": s["id"], "start": round(t, 3), "dur": round(dur, 3), "voStart": lead, "voDur": round(adur, 3),
                       "audio": str(audio.relative_to(d)) if audio else None, "words": words})
        t += dur
    tl = {"fps": sc.get("fps", 60), "total": round(t, 3), "handle": sc.get("handle", ""), "title": sc.get("title", ""),
          "voice": voice, "voiced": voiced, "scenes": scenes}
    (d / "build" / "timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False))
    (d / "build" / "timeline.js").write_text("window.TIMELINE = " + json.dumps(tl, ensure_ascii=False) + ";\n")
    print(f"✓ timeline: {len(scenes)} scene, total {t:.2f}s {'— VO final' if voiced else '— DRAFT tanpa suara'}")
    if t > sc.get("maxDur", 60):
        print(f"! durasi {t:.1f}s melebihi target — pangkas naskah, jangan percepat suara")


# ================================================================ audio
def synth(kind, np):
    def env_exp(n, k):
        return np.exp(-np.arange(n) / SR * k)

    rng = np.random.default_rng(7)

    def sweep_noise(n, cfun, amp):
        x = rng.standard_normal(n); t = np.arange(n) / n
        y = np.zeros(n); a = 0.0
        for i in range(n):
            a += cfun(t[i]) * (x[i] - a); y[i] = a
        return y * amp(t)

    if kind == "whoosh":
        return sweep_noise(int(SR * 0.6), lambda u: 0.02 + 0.35 * math.sin(math.pi * u) ** 2, lambda t: np.sin(np.pi * t) ** 2 * 0.9)
    if kind == "riser":
        return sweep_noise(int(SR * 1.0), lambda u: 0.01 + 0.5 * u ** 2, lambda t: t ** 2 * 0.7)
    if kind == "pop":
        n = int(SR * 0.14); tt = np.arange(n) / SR
        return np.sin(2 * np.pi * np.cumsum(500 + 900 * tt / tt[-1]) / SR) * env_exp(n, 38) * 0.7
    if kind == "hit":
        n = int(SR * 0.55); tt = np.arange(n) / SR
        body = np.sin(2 * np.pi * np.cumsum(45 + 110 * np.exp(-tt * 18)) / SR) * env_exp(n, 7)
        return (body + rng.standard_normal(n) * env_exp(n, 90) * 0.5) * 0.95
    if kind in ("tick", "type"):
        n = int(SR * 0.035); x = np.diff(np.concatenate([[0], rng.standard_normal(n)]))
        return x * env_exp(n, 160 if kind == "tick" else 220) * (0.45 if kind == "tick" else 0.3)
    if kind == "ding":
        n = int(SR * 0.9); tt = np.arange(n) / SR
        return (np.sin(2 * np.pi * 1318 * tt) + 0.45 * np.sin(2 * np.pi * 1976 * tt)) * env_exp(n, 5) * 0.4
    if kind == "glitch":
        n = int(SR * 0.25); x = rng.standard_normal(n)
        sq = np.sign(np.sin(2 * np.pi * 180 * np.arange(n) / SR))
        return (x * 0.4 + sq * 0.3) * (np.floor(np.arange(n) / (SR * 0.02)) % 2) * env_exp(n, 6) * 0.6
    return np.zeros(1)


def decode(path, np):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def build_audio(d, tl, events, out_wav, sc_json):
    import numpy as np
    n = int(SR * (tl["total"] + 0.5))
    vo, sfx = np.zeros(n), np.zeros(n)

    def place(buf, sig, t, gain=1.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        m = min(len(sig), n - i)
        buf[i:i + m] += sig[:m] * gain

    for s in tl["scenes"]:
        if s.get("audio") and (d / s["audio"]).exists():
            v = decode(d / s["audio"], np)
            f = min(len(v) // 4, int(SR * 0.012))  # fade anti-klik
            if f > 0:
                v[:f] *= np.linspace(0, 1, f); v[-f:] *= np.linspace(1, 0, f)
            place(vo, v, s["start"] + s["voStart"])
    cache, g0 = {}, sc_json.get("sfxVolume", 0.5)
    for e in events:
        cache.setdefault(e["type"], synth(e["type"], np))
        place(sfx, cache[e["type"]], e["t"], g0 * (e.get("gain") or 1.0))
    # SFX ikut sedikit turun saat ada suara supaya narasi tetap jelas
    envv = np.convolve(np.abs(vo), np.ones(2400) / 2400, mode="same")
    duck = 1 - 0.6 * np.clip(envv / 0.05, 0, 1)
    mix = vo + sfx * (1 - 0.35 * np.clip(envv / 0.05, 0, 1))
    bgm = sc_json.get("bgm")
    if bgm and (d / bgm).exists():
        b = decode(d / bgm, np)
        b = np.tile(b, int(math.ceil(n / max(1, len(b)))))[:n] * sc_json.get("bgmVolume", 0.16)
        fi = int(SR * 0.8); b[:fi] *= np.linspace(0, 1, fi)
        mix += b * duck
    fo = int(SR * 0.4); mix[-fo:] *= np.linspace(1, 0, fo)
    peak = np.max(np.abs(mix)) or 1
    mix = mix / peak * 0.9 if tl.get("voiced") else mix / max(peak, 1.0) * 0.6
    raw = out_wav.with_suffix(".raw.wav")
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        st = np.stack([mix, mix], axis=1)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())
    if tl.get("voiced"):  # loudness standar TikTok/IG
        sh(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-ar", str(SR), str(out_wav)])
        raw.unlink()
    else:
        raw.replace(out_wav)


# ================================================================ browser
CHROME_ARGS = ["--disable-web-security", "--allow-file-access-from-files", "--force-color-profile=srgb", "--disable-lcd-text"]


def open_page(p, d, scale=1.0):
    b = p.chromium.launch(args=CHROME_ARGS)
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=scale)
    pg.goto((Path(d).resolve() / "index.html").as_uri() + "?render", wait_until="load")
    pg.evaluate("document.fonts.ready.then(() => true)")
    pg.evaluate("window.__seek(0)")
    return b, pg


def page_info(d):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b, pg = open_page(p, d)
        info = {"meta": pg.evaluate("window.__meta()"), "events": pg.evaluate("window.__events()"),
                "scenes": pg.evaluate("window.__scenes()")}
        b.close()
    return info


def render_worker(job):
    d, f0, f1, fps, scale, out = job
    from playwright.sync_api import sync_playwright
    w, h = int(1080 * scale) // 2 * 2, int(1920 * scale) // 2 * 2
    tmp = out + ".part.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg",
                            "-i", "-", "-vf", f"scale={w}:{h}:flags=lanczos,format=yuv420p", "-c:v", "libx264",
                            "-preset", "veryfast", "-crf", "16" if scale >= 1 else "23", "-r", str(fps),
                            "-g", str(fps), str(tmp)], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        b, pg = open_page(p, d, scale)
        for f in range(f0, f1):
            pg.evaluate("t => window.__seek(t)", f / fps)
            enc.stdin.write(pg.screenshot(type="jpeg", quality=92 if scale >= 1 else 80, caret="hide"))
        b.close()
    enc.stdin.close(); enc.wait()
    os.replace(tmp, out)
    return out


def ensure_timeline(d, need_voice=False, allow_silent=False):
    tl = Path(d) / "build" / "timeline.json"
    if not tl.exists():
        if need_voice and not allow_silent:
            die("timeline belum ada. Jalankan check-tts lalu tts dulu.")
        cmd_tts(argparse.Namespace(dir=d, scene=None, force=False, draft=True))
    t = json.loads(tl.read_text())
    if need_voice and not t.get("voiced") and not allow_silent:
        die("timeline masih DRAFT (tanpa VO). Final render butuh VO dari TTS: jalankan `mr.py tts` tanpa --draft.")
    return t


def produce(d, fps, scale, workers, out, force_ids=None, no_cache=False, label="render"):
    from multiprocessing import Pool
    tl = json.loads((d / "build" / "timeline.json").read_text())
    sc_json = json.loads((d / "script.json").read_text())
    info = page_info(d)
    total = info["meta"]["total"]
    S = info["scenes"]
    profile = f"{int(1080 * scale)}x{int(1920 * scale)}@{fps}"
    cdir = d / "build" / "cache" / profile
    cdir.mkdir(parents=True, exist_ok=True)
    glob_h = sha(fhash(d / "engine" / "engine.js"), fhash(d / "engine" / "base.css"), fhash(d / "style.css"),
                 fhash(d / "index.html"), total, tl.get("handle"))
    jobs, segs, todo = [], [], 0
    nf = int(round(total * fps))
    for i, s in enumerate(S):
        f0 = int(round(s["start"] * fps))
        f1 = nf if i == len(S) - 1 else int(round((s["start"] + s["dur"]) * fps))
        neigh = [S[j] for j in (i - 1, i, i + 1) if 0 <= j < len(S)]
        tls = tl["scenes"][i] if i < len(tl["scenes"]) else {}
        h = sha(glob_h, f0, f1, json.dumps(tls, sort_keys=True), *[n["src"] + str(n["start"]) + str(n["dur"]) for n in neigh])
        seg = cdir / f"{i:02d}-{s['id']}-{h}.mp4"
        segs.append(seg)
        if no_cache or (force_ids and s["id"] in force_ids) or not seg.exists():
            todo += 1
            for old in cdir.glob(f"{i:02d}-{s['id']}-*.mp4"):
                old.unlink()
            # pecah scene panjang supaya worker seimbang
            parts = max(1, min(workers, (f1 - f0) // 240)) if len(S) < workers * 2 else 1
            if parts == 1:
                jobs.append((str(d), f0, f1, fps, scale, str(seg)))
            else:
                b = [f0 + round((f1 - f0) * k / parts) for k in range(parts + 1)]
                sub = [str(seg) + f".p{k}.mp4" for k in range(parts)]
                for k in range(parts):
                    jobs.append((str(d), b[k], b[k + 1], fps, scale, sub[k]))
                segs[-1] = ("multi", seg, sub)
    print(f"▶ {label}: {nf} frame @ {fps}fps {profile} — {todo} scene dirender, {len(S) - todo} dari cache, {workers} worker")
    t0 = time.time()
    if jobs:
        jobs.sort(key=lambda j: -(j[2] - j[1]))
        if workers > 1 and len(jobs) > 1:
            with Pool(min(workers, len(jobs))) as pool:
                pool.map(render_worker, jobs)
        else:
            for j in jobs: render_worker(j)
    files = []
    for s in segs:
        if isinstance(s, tuple):
            _, seg, sub = s
            lst = Path(str(seg) + ".txt")
            lst.write_text("".join(f"file '{Path(x).name}'\n" for x in sub))
            sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(seg)])
            for x in sub: Path(x).unlink()
            lst.unlink()
            s = seg
        files.append(s)
    wav = d / "build" / "mix.wav"
    build_audio(d, tl, info["events"], wav, sc_json)
    lst = d / "build" / f"{label}-list.txt"
    lst.write_text("".join(f"file '{f.resolve()}'\n" for f in files))
    sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav),
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}",
        "-movflags", "+faststart", str(out)])
    print(f"✓ {out}  ({time.time() - t0:.0f}s, {len(info['events'])} SFX{', + VO' if tl.get('voiced') else ', TANPA VO'})")
    return out


def cmd_preview(a):
    d = Path(a.dir).resolve()
    require_gate(d, "storyboard", "Preview")
    ensure_timeline(d)
    out = produce(d, a.fps, a.scale, a.workers, d / "build" / "preview.mp4", label="preview")
    cmd_stills(argparse.Namespace(dir=str(d), every=1.5, at=None))
    print(f"→ tampilkan {out} + build/contact.jpg ke user, minta approval: mr.py approve {a.dir} preview")


def cmd_render(a):
    d = Path(a.dir).resolve()
    require_gate(d, "preview", "Final render")
    ensure_timeline(d, need_voice=True, allow_silent=a.allow_silent)
    out = Path(a.out) if a.out else d / f"{d.name}.mp4"
    produce(d, 60 if not a.fps else a.fps, 1.0, a.workers, out,
            force_ids=set(a.scenes.split(",")) if a.scenes else None, no_cache=a.no_cache, label="final")
    print(f"→ lanjut wajib: mr.py qc {a.dir}")


def cmd_stills(a):
    from playwright.sync_api import sync_playwright
    d = Path(a.dir).resolve()
    tl = ensure_timeline(d)
    times = [float(x) for x in a.at.split(",")] if a.at else [round(x * a.every, 2) for x in range(int(tl["total"] / a.every) + 1)]
    out = d / "build" / "stills"; out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.jpg"): f.unlink()
    with sync_playwright() as p:
        b, pg = open_page(p, d, 0.4)
        for i, t in enumerate(times):
            pg.evaluate("t => window.__seek(t)", t)
            pg.screenshot(path=str(out / f"{i:03d}.jpg"), type="jpeg", quality=80)
        b.close()
    cols = min(6, len(times)); rows = math.ceil(len(times) / cols)
    sheet = d / "build" / "contact.jpg"
    sh(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", str(out / "%03d.jpg"), "-vf",
        f"drawtext=text='%{{n}}':x=10:y=10:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.6,tile={cols}x{rows}:padding=6",
        "-frames:v", "1", str(sheet)])
    print(f"✓ {sheet}  (kotak ke-n = detik: {', '.join(f'{i}:{t}' for i, t in enumerate(times))})")


# ================================================================ QC
def probe(video):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)],
                                  capture_output=True, text=True, check=True).stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), {})
    au = next((s for s in j["streams"] if s["codec_type"] == "audio"), {})
    num, den = (v.get("r_frame_rate", "0/1").split("/") + ["1"])[:2]
    return {"w": v.get("width"), "h": v.get("height"), "fps": float(num) / float(den or 1), "vcodec": v.get("codec_name"),
            "pix": v.get("pix_fmt"), "acodec": au.get("codec_name"), "dur": float(j["format"]["duration"])}


def ff_detect(video, vf=None, af=None):
    cmd = ["ffmpeg", "-v", "info", "-i", str(video)]
    if vf: cmd += ["-vf", vf, "-an"]
    if af: cmd += ["-af", af, "-vn"]
    return subprocess.run(cmd + ["-f", "null", "-"], capture_output=True, text=True).stderr


def cmd_qc(a):
    from playwright.sync_api import sync_playwright
    d = Path(a.dir).resolve()
    video = Path(a.video) if a.video else d / f"{d.name}.mp4"
    if not video.exists():
        die(f"video tidak ditemukan: {video}")
    tl = json.loads((d / "build" / "timeline.json").read_text())
    sc_json = json.loads((d / "script.json").read_text())
    is_final = video.name != "preview.mp4"
    issues = []

    def add(sev, typ, msg, t=None, scene=None):
        issues.append({"sev": sev, "type": typ, "msg": msg, "t": t, "scene": scene})

    # 1. spesifikasi
    pr = probe(video)
    exp = {"w": 1080, "h": 1920, "fps": 60.0, "vcodec": "h264", "acodec": "aac", "pix": "yuv420p"}
    if is_final:
        for k, v in exp.items():
            if (abs(pr[k] - v) > 0.01 if k == "fps" else pr[k] != v):
                add("error", "spesifikasi", f"{k} = {pr[k]} (harus {v})")
    if abs(pr["dur"] - tl["total"]) > 0.15:
        add("error", "durasi", f"durasi video {pr['dur']:.2f}s ≠ timeline {tl['total']:.2f}s")
    if pr["dur"] > sc_json.get("maxDur", 60) + 0.5:
        add("warn", "durasi", f"{pr['dur']:.1f}s melebihi target {sc_json.get('maxDur', 60)}s")
    # 2. frame hitam & visual diam
    out = ff_detect(video, vf="blackdetect=d=0.1:pix_th=0.04")
    for s, e in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", out):
        add("error", "frame-hitam", f"frame hitam {float(s):.2f}–{float(e):.2f}s", float(s))
    out = ff_detect(video, vf="freezedetect=n=0.0015:d=2.2")
    for s in re.findall(r"freeze_start: ([\d.]+)", out):
        add("warn", "visual-diam", f"layar hampir tidak berubah >2.2s mulai {float(s):.2f}s (animasi patah / kurang gerak?)", float(s))
    # 3. audio
    out = ff_detect(video, af="ebur128=peak=true")
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    peak = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", out)
    if tl.get("voiced") and lufs and not (-16.5 <= float(lufs[-1]) <= -11.5):
        add("warn", "loudness", f"loudness {lufs[-1]} LUFS (target -14)")
    if peak and float(peak[-1]) > -0.5:
        add("warn", "clipping", f"true peak {peak[-1]} dBFS")
    if not tl.get("voiced"):
        add("error" if is_final else "warn", "vo", "video tanpa voice-over final (timeline draft)")
    # 4. sinkron VO & caption
    for s in tl["scenes"]:
        if s.get("audio"):
            end = s["voStart"] + s.get("voDur", 0)
            if end > s["dur"] + 0.02:
                add("error", "vo-terpotong", f"VO {end:.2f}s > durasi scene {s['dur']:.2f}s", s["start"], s["id"])
        if s["words"] and s["words"][-1]["e"] > s["start"] + s["dur"] + 0.02:
            add("error", "caption-sync", "caption kata terakhir lewat dari akhir scene", s["start"], s["id"])
        if s.get("audio"):
            ws = s["words"]
            v0, v1 = s["start"] + s["voStart"], s["start"] + s["voStart"] + s["voDur"]
            if ws and (ws[0]["s"] < v0 - 0.05 or ws[-1]["e"] > v1 + 0.05):
                add("warn", "caption-sync", "timing caption di luar rentang audio", s["start"], s["id"])
    # 5. page: SFX, kamera, layout
    with sync_playwright() as p:
        b, pg = open_page(p, d)
        info = {"events": pg.evaluate("window.__events()"), "scenes": pg.evaluate("window.__scenes()")}
        S = info["scenes"]
        for s in S:
            ev = [e for e in info["events"] if e.get("scene") == s["id"]]
            if s["dur"] and len(ev) / s["dur"] > 1.6:
                add("warn", "sfx-rapat", f"{len(ev)} SFX dalam {s['dur']:.1f}s — kurangi", s["start"], s["id"])
            for e in ev:
                if not (s["start"] - 0.5 <= e["t"] <= s["start"] + s["dur"]):
                    add("warn", "sfx-timing", f"SFX {e['type']} @ {e['t']:.2f}s di luar scene", e["t"], s["id"])
        # kamera
        step = 1 / 30
        ts = [round(i * step, 4) for i in range(int(tl["total"] / step))]
        cams = pg.evaluate("ts => ts.map(t => window.__cam(t))", ts)
        run = 0
        for k in range(1, len(ts)):
            t = ts[k]
            s = next(x for x in reversed(S) if t >= x["start"])
            lt = t - s["start"]
            c0, c1 = cams[k - 1], cams[k]
            if c1["z"] > 2.3 or c1["z"] < 0.55:
                add("warn", "kamera-zoom", f"zoom {c1['z']:.2f}", t, s["id"])
            if abs(c1["r"]) > 10:
                add("warn", "kamera-rotasi", f"rotasi {c1['r']:.1f}°", t, s["id"])
            if lt < s["trans"] + 0.1:
                run = 0; continue
            v = math.hypot(c1["x"] - c0["x"], c1["y"] - c0["y"]) * c1["z"] / step
            run = run + 1 if v > 2400 else 0
            if run == 8:
                add("warn", "kamera-berlebihan", f"kamera bergerak sangat cepat ({v:.0f}px/s) >0.25s di luar transisi", t, s["id"])
        # layout
        seen = set()
        t = 0.0
        while t < tl["total"]:
            for it in pg.evaluate("t => window.__qc(t)", t):
                key = (it["type"], it["scene"], it.get("key") or it.get("text", ""))
                if key in seen: continue
                seen.add(key)
                msg = it["type"] + (f" «{it['text']}»" if it.get("text") else "") + f" box={it['box']}"
                add(it["sev"], it["type"], msg, round(t, 2), it["scene"])
            t += 0.2
        b.close()
    # 6. frame contoh di titik masalah (untuk dicek visual oleh agent)
    shots = d / "build" / "qc"
    shutil.rmtree(shots, ignore_errors=True); shots.mkdir(parents=True)
    pts = sorted({round(i["t"], 2) for i in issues if i["t"] is not None and i["sev"] == "error"})[:12]
    for k, t in enumerate(pts):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(video), "-frames:v", "1",
                        "-vf", "scale=432:-1", str(shots / f"{k:02d}-{t}s.jpg")])
    errs = [i for i in issues if i["sev"] == "error"]
    warns = [i for i in issues if i["sev"] == "warn"]
    rep = [f"# QC Report — {video.name}", "", f"_{datetime.now():%Y-%m-%d %H:%M}_", "",
           f"**{'LULUS' if not errs else 'GAGAL'}** — {len(errs)} error, {len(warns)} warning", "",
           f"Spesifikasi: {pr['w']}×{pr['h']} · {pr['fps']:.2f} fps · {pr['vcodec']}/{pr['pix']} · {pr['acodec']} · {pr['dur']:.2f}s"
           + (f" · {lufs[-1]} LUFS" if lufs else ""), "", "| Level | Waktu | Scene | Masalah |", "|---|---|---|---|"]
    tstr = lambda i: "" if i["t"] is None else "%.2fs" % i["t"]
    for i in errs + warns:
        rep.append(f"| {i['sev']} | {tstr(i)} | {i['scene'] or ''} | {i['msg']} |")
    rep += ["", "Checklist visual manual: lihat production/qc-checklist.md"]
    (d / "production").mkdir(exist_ok=True)
    (d / "production" / "qc-report.md").write_text("\n".join(rep) + "\n")
    (d / "build" / "qc.json").write_text(json.dumps(issues, indent=1, ensure_ascii=False))
    print("\n".join(rep[4:7]))
    for i in (errs + warns)[:25]:
        print(f"  [{i['sev']}] {tstr(i)} {i['scene'] or ''} {i['msg']}")
    print(f"→ production/qc-report.md{' · frame masalah di build/qc/' if pts else ''}")
    sys.exit(1 if errs else 0)


# ================================================================ main
# ================================================================ Fase 10: social publishing
PUB_FILES = ["tiktok-caption.md", "instagram-caption.md", "facebook-caption.md", "hashtags-research.md",
             "publishing-checklist.md", "content-metadata.json"]
# Aturan terverifikasi (lihat references/social-publishing.md untuk sumber & tanggal)
PUB_RULES = {
    "tiktok":    {"file": "tiktok-caption.md",    "max_tags": None, "preset": (3, 5), "max_utf16": 2200},
    "instagram": {"file": "instagram-caption.md", "max_tags": 5,    "preset": (1, 5), "max_utf16": None},
    "facebook":  {"file": "facebook-caption.md",  "max_tags": None, "preset": (0, 3), "max_utf16": None},
}
PUB_GENERIC = {"fyp", "foryou", "foryoupage", "fy", "viral", "reels", "explore", "explorepage", "trending", "xyzbca", "fypシ"}
PUB_BAIT = [r"wajib\s+komen", r"spam\s+komen", r"komen\s+(yang\s+)?banyak", r"follow\s+dulu\s+baru", r"like\s+dulu", r"tag\s+\d+\s+teman",
            r"jangan\s+di-?skip", r"auto\s+fyp", r"pasti\s+fyp", r"dijamin\s+viral",
            # English
            r"comment\s+[\"']?(yes|1|below\s+to\s+win)", r"smash\s+(that|the)\s+like", r"like\s+(and|&)\s+share\s+(if|or)", r"tag\s+\d+\s+friends",
            r"spam\s+the\s+comments", r"share\s+(this\s+)?or\s+(bad\s+luck|you)", r"guaranteed\s+(viral|fyp)", r"don'?t\s+scroll"]
PUB_SECTIONS = ["Caption final", "Keyword", "Hashtag", "Alasan", "Cover title", "CTA", "Alternatif hook", "Terakhir verifikasi"]


def utf16_len(text):
    return len(text.encode("utf-16-le")) // 2


def pub_caption(md):
    m = re.search(r"```caption\n(.*?)```", md, re.S)
    return m.group(1).strip() if m else None


def cmd_publish_init(a):
    d = Path(a.dir).resolve()
    rep = d / "production" / "qc-report.md"
    if not rep.exists() or "**LULUS**" not in rep.read_text():
        die("Fase 10 butuh QC video LULUS dulu: jalankan `mr.py qc` sampai 0 error.")
    out = d / "publishing"; out.mkdir(exist_ok=True)
    for f in PUB_FILES:
        if a.force or not (out / f).exists():
            shutil.copy(ROOT / "templates" / "publishing" / f, out / f)
    print(f"✓ {out}  — isi caption (baca brief/storyboard/VO dulu), lalu: mr.py publish-check {a.dir}")


def cmd_publish_check(a):
    d = Path(a.dir).resolve(); out = d / "publishing"
    if not out.exists():
        die("publishing/ belum ada — jalankan publish-init dulu.")
    errs, warns, caps = [], [], {}
    add = lambda lvl, plat, msg: (errs if lvl == "error" else warns).append(f"[{plat}] {msg}")
    meta = {}
    try:
        meta = json.loads((out / "content-metadata.json").read_text())
    except Exception as e:
        add("error", "meta", f"content-metadata.json tidak valid: {e}")
    brand = meta.get("brand") or {}
    if not brand.get("name"):
        add("warn", "brand", "brand.name kosong di content-metadata.json (isi dari brief; modul ini netral brand)")
    if not brand.get("language"):
        add("error", "brand", "brand.language belum diisi (bahasa caption)")
    banned = [w for w in brand.get("banned_words", []) if w]
    for plat, rule in PUB_RULES.items():
        f = out / rule["file"]
        if not f.exists():
            add("error", plat, f"{rule['file']} tidak ada"); continue
        md = f.read_text()
        cap = pub_caption(md)
        if not cap or "{" in cap and "}" in cap and "TODO" in cap.upper():
            add("error", plat, "caption final belum diisi (blok ```caption)"); continue
        caps[plat] = cap
        tags = re.findall(r"(?<!\w)#([\w\u00C0-\u024F]+)", cap)
        n = len(tags); lo, hi = rule["preset"]
        if rule["max_tags"] is not None and n > rule["max_tags"]:
            add("error", plat, f"{n} hashtag > batas platform {rule['max_tags']}")
        elif not (lo <= n <= hi):
            add("warn", plat, f"{n} hashtag di luar preset internal {lo}–{hi} (bukan aturan platform)")
        if len(set(t.lower() for t in tags)) < n:
            add("error", plat, "hashtag duplikat")
        gen = [t for t in tags if t.lower() in PUB_GENERIC]
        if gen:
            add("error", plat, f"hashtag generik/tidak relevan: {', '.join('#' + g for g in gen)}")
        if rule["max_utf16"] and utf16_len(cap) > rule["max_utf16"]:
            add("error", plat, f"caption {utf16_len(cap)} UTF-16 units > {rule['max_utf16']} (batas Content Posting API)")
        for w in banned:
            if re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", cap, re.I):
                add("error", plat, f"kata terlarang brand: '{w}'")
        for pat in PUB_BAIT:
            if re.search(pat, cap, re.I):
                add("error", plat, f"engagement bait terdeteksi: /{pat}/")
        emo = len(re.findall(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", cap))
        if emo > 4:
            add("warn", plat, f"{emo} emoji — terlalu banyak (maks ±3)")
        first = cap.split("\n", 1)[0]
        if len(first) > 120:
            add("warn", plat, "kalimat pertama (hook) terlalu panjang, > 120 karakter")
        for sec in PUB_SECTIONS:
            if sec.lower() not in md.lower():
                add("error", plat, f"bagian '{sec}' tidak ada")
        if re.search(r"Terakhir verifikasi[^\n]*\{", md):
            add("error", plat, "tanggal verifikasi aturan belum diisi")
        pm = meta.get("platforms", {}).get(plat, {})
        sc = (pm.get("score") or {}).get("total")
        if sc is None:
            add("error", plat, "skor rubrik belum diisi di content-metadata.json")
        elif sc < 85:
            add("error", plat, f"skor rubrik {sc}/100 < 85 → revisi caption")
        mt = [t.lower().lstrip("#") for t in pm.get("hashtags", [])]
        if mt and sorted(mt) != sorted(t.lower() for t in tags):
            add("error", plat, "hashtag di caption ≠ hashtag di content-metadata.json")
        if not pm.get("hard_checks_passed"):
            add("error", plat, "hard checks belum dikonfirmasi (hard_checks_passed=true setelah dicek manual)")
    vals = list(caps.values())
    for i in range(len(vals)):
        for j in range(i + 1, len(vals)):
            if re.sub(r"\s+", " ", vals[i]) == re.sub(r"\s+", " ", vals[j]):
                add("error", "semua", "caption identik antar platform — wajib diadaptasi")
    hr = (out / "hashtags-research.md").read_text() if (out / "hashtags-research.md").exists() else ""
    for plat, cap in caps.items():
        for t in re.findall(r"(?<!\w)#([\w\u00C0-\u024F]+)", cap):
            if f"#{t}".lower() not in hr.lower():
                add("error", plat, f"#{t} tidak punya alasan di hashtags-research.md")
    rep = [f"# Caption QC — {d.name}", "", f"_{datetime.now().isoformat(timespec='seconds')}_", "",
           f"**{'LULUS' if not errs else 'GAGAL'}** — {len(errs)} error, {len(warns)} warning", "",
           "Skor rubrik = alat editorial internal, bukan skor algoritma platform / prediksi FYP.", ""]
    for plat, cap in caps.items():
        tags = re.findall(r"(?<!\w)#\w+", cap)
        rep.append(f"- {plat}: {utf16_len(cap)} UTF-16 units · {len(tags)} hashtag · skor {meta.get('platforms', {}).get(plat, {}).get('score', {}).get('total', '?')}")
    rep += [""] + [f"- ✗ {e}" for e in errs] + [f"- ! {w}" for w in warns]
    (out / "caption-qc.md").write_text("\n".join(rep) + "\n")
    print("\n".join(rep[4:]))
    print(f"→ publishing/caption-qc.md" + ("" if errs else f" · tampilkan paket ke user → mr.py approve {a.dir} publishing"))
    if errs:
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    w_def = max(1, min(6, os.cpu_count() or 2))
    p = sp.add_parser("init"); p.add_argument("dir"); p.add_argument("--mode", choices=["studio", "auto"], default="studio")
    p.add_argument("--voice"); p.add_argument("--title"); p.set_defaults(fn=cmd_init)
    p = sp.add_parser("status"); p.add_argument("dir"); p.set_defaults(fn=cmd_status)
    p = sp.add_parser("approve"); p.add_argument("dir"); p.add_argument("gate", choices=GATES); p.add_argument("--note")
    p.set_defaults(fn=cmd_approve)
    p = sp.add_parser("check-tts"); p.add_argument("dir", nargs="?"); p.add_argument("--voice"); p.set_defaults(fn=cmd_check_tts)
    p = sp.add_parser("tts"); p.add_argument("dir"); p.add_argument("--scene"); p.add_argument("--force", action="store_true")
    p.add_argument("--draft", action="store_true"); p.set_defaults(fn=cmd_tts)
    p = sp.add_parser("stills"); p.add_argument("dir"); p.add_argument("--every", type=float, default=1.5); p.add_argument("--at")
    p.set_defaults(fn=cmd_stills)
    p = sp.add_parser("preview"); p.add_argument("dir"); p.add_argument("--scale", type=float, default=0.5)
    p.add_argument("--fps", type=int, default=30); p.add_argument("--workers", type=int, default=w_def); p.set_defaults(fn=cmd_preview)
    p = sp.add_parser("render"); p.add_argument("dir"); p.add_argument("--fps", type=int); p.add_argument("--workers", type=int, default=w_def)
    p.add_argument("--scenes"); p.add_argument("--no-cache", action="store_true"); p.add_argument("--allow-silent", action="store_true")
    p.add_argument("--out"); p.set_defaults(fn=cmd_render)
    p = sp.add_parser("qc"); p.add_argument("dir"); p.add_argument("--video"); p.set_defaults(fn=cmd_qc)
    p = sp.add_parser("publish-init"); p.add_argument("dir"); p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_publish_init)
    p = sp.add_parser("publish-check"); p.add_argument("dir"); p.set_defaults(fn=cmd_publish_check)
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
