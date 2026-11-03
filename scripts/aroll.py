#!/usr/bin/env python3
"""
aroll.py — tipe konten TALKING-HEAD + B-ROLL (footage sendiri + gambar lain + motion grafik + monolog).

Gaya: editorial gelap ala YouTube edukasi (kinetic type sans + serif italic diketik per huruf, jump-cut,
B-roll foto + light-leak, kartu judul hitam + coretan merah, judul glitch RGB, diagram arang ber-scanline
dengan thumbnail neon hijau). Satu sumber kebenaran: <dir>/edit.json. Render lewat HyperFrames (HTML → video).

  init     <dir> --footage file.mov [--rubrik nocap]   project + edit.json + dokumen produksi
  prep     <dir>                                       HDR→SDR, H.264 keyframe/1s, grade dipanggang → assets/aroll_g.mp4
  words    <dir> [--model small] [--lang id]           transkrip per kata → production/words.txt (+ words.json)
  stock    <dir>                                       unduh foto Pexels di edit.json, grade dipanggang, cek crop 9:16
  build    <dir>                                       edit.json → index.html + compositions/*.html
  check    <dir>                                       npx hyperframes check (lint, layout, kontras)
  snap     <dir> --at 1.5,8,22                         snapshot frame → build/snap/contact-sheet*.jpg
  render   <dir> [--range 8,10]                        final 1080×1920@30 → <dir>/<dir>.mp4 (atau potongan uji)
  mix      <dir>                                       versi tanpa SFX (suara asli saja) → <dir>/<dir>-tanpa-sfx.mp4

Kebutuhan: python3, ffmpeg, node (npx), pip install faster-whisper numpy.
"""
import argparse, html, json, math, os, re, shutil, subprocess, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
HF = ["npx", "-y", "hyperframes@0.9.2"]
W, H = 1080, 1920

GRADES = {  # dipanggang dengan ffmpeg (shader grade saat render = ±1 fps tanpa GPU)
    "aroll": "eq=brightness=-0.06:contrast=1.16:saturation=0.70:gamma=0.95,colorbalance=bs=0.05:bm=0.03:rh=-0.02,vignette=angle=PI/3.6",
    "dark": "eq=brightness=-0.07:contrast=1.15:saturation=0.62:gamma=0.92,vignette=angle=PI/3.4,noise=alls=8",
    "red": "eq=brightness=-0.04:contrast=1.15:saturation=0.95,vignette=angle=PI/3.4,noise=alls=8",
    "cool": "eq=brightness=-0.15:contrast=1.2:saturation=0.3,colorbalance=bs=0.25:bm=0.15:rs=-0.1,vignette=angle=PI/3.2,noise=alls=10",
    "none": "null",
}


def die(m):
    print("✗ " + m); sys.exit(1)


def run(cmd, **kw):
    r = subprocess.run(cmd, **kw)
    if r.returncode != 0:
        die("gagal: " + " ".join(map(str, cmd))[:200])
    return r


def load(d):
    p = Path(d) / "edit.json"
    if not p.exists():
        die(f"{p} tidak ada — jalankan init dulu")
    return json.loads(p.read_text())


def probe(f):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(f)],
                                  capture_output=True, text=True).stdout or "{}")
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
    return {"dur": float(j.get("format", {}).get("duration", 0)), "w": v.get("width"), "h": v.get("height"),
            "trc": v.get("color_transfer", ""), "rot": v.get("side_data_list", [{}])[0].get("rotation", 0) if v.get("side_data_list") else 0}


# ================================================================ init / prep / words / stock
def cmd_init(a):
    d = Path(a.dir)
    if (d / "edit.json").exists():
        die(f"{d}/edit.json sudah ada")
    src = Path(a.footage)
    if not src.exists():
        die(f"footage tidak ditemukan: {src}")
    (d / "assets" / "broll").mkdir(parents=True, exist_ok=True)
    (d / "assets" / "sfx").mkdir(parents=True, exist_ok=True)
    (d / "production").mkdir(exist_ok=True)
    (d / "compositions").mkdir(exist_ok=True)
    tpl = SKILL / "templates" / "aroll"
    spec = json.loads((tpl / "edit.json").read_text())
    spec["footage"] = str(src.resolve())
    if a.rubrik:
        spec["rubrik"] = a.rubrik
    (d / "edit.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False))
    for f in ("creative-brief.md", "edit-plan.md"):
        shutil.copy(tpl / f, d / "production" / f)
    (d / "hyperframes.json").write_text(json.dumps({"paths": {"blocks": "compositions", "assets": "assets"}, "media": {"autoProxy": True}}, indent=1))
    (d / "package.json").write_text(json.dumps({"name": d.name, "private": True, "type": "module"}, indent=1))
    # GSAP lokal (render tanpa jaringan); gagal → CDN
    try:
        tmp = d / "build" / "gsap"; tmp.mkdir(parents=True, exist_ok=True)
        subprocess.run(["npm", "pack", "gsap@3.12.5", "--silent"], cwd=tmp, capture_output=True, timeout=120, check=True)
        subprocess.run(["tar", "xzf", "gsap-3.12.5.tgz", "package/dist/gsap.min.js"], cwd=tmp, check=True)
        shutil.copy(tmp / "package" / "dist" / "gsap.min.js", d / "assets" / "gsap.min.js")
        print("✓ gsap lokal")
    except Exception:
        print("! npm pack gsap gagal — index.html memakai CDN jsdelivr")
    print(f"✓ project {d}  →  lanjut: prep, words, isi edit.json, stock, build")


def cmd_prep(a):
    d = Path(a.dir); sp = load(d)
    src = Path(sp["footage"])
    pr = probe(src)
    hdr = pr["trc"] in ("arib-std-b67", "smpte2084")
    vf = []
    if hdr:  # iPhone HLG/HDR → SDR bt709 (kalau tidak, warna pucat & render jatuh ke jalur HDR yang sangat lambat)
        vf.append("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv")
    vf.append(f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}")
    vf.append(GRADES[sp.get("grade", {}).get("aroll", "aroll")])
    vf.append("format=yuv420p")
    out = d / "assets" / "aroll_g.mp4"
    print(f"… {src.name}: {pr['w']}x{pr['h']} {pr['dur']:.1f}s {'HDR→SDR' if hdr else 'SDR'}")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-map", "0:v:0", "-map", "0:a:0", "-vf", ",".join(vf),
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-g", "30", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(out)])
    run(["ffmpeg", "-v", "error", "-y", "-i", str(out), "-vn", "-ac", "1", "-ar", "16000", str(d / "build" / "voice16k.wav")])
    sp["duration"] = round(probe(out)["dur"], 2)
    (d / "edit.json").write_text(json.dumps(sp, indent=1, ensure_ascii=False))
    print(f"✓ assets/aroll_g.mp4 ({sp['duration']}s) — durasi ditulis ke edit.json")


def cmd_words(a):
    d = Path(a.dir); sp = load(d)
    wav = d / "build" / "voice16k.wav"
    if not wav.exists():
        die("jalankan prep dulu")
    try:
        import numpy as np
        from faster_whisper import WhisperModel
    except ImportError:
        die("pip install faster-whisper numpy")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32)
    m = WhisperModel(a.model, compute_type="int8")
    segs, _ = m.transcribe(audio, language=a.lang, vad_filter=True, word_timestamps=True)
    fixes = sp.get("fixes", {})
    words, lines = [], []
    for s in segs:
        row = []
        for w in s.words:
            t = w.word.strip()
            key = re.sub(r"[^\w-]", "", t)
            if key in fixes:
                t = t.replace(key, fixes[key])
            words.append([t, round(w.start, 2), round(w.end, 2)])
            row.append(f"{t}@{w.start:.2f}")
        lines.append(f"[{s.start:6.2f}–{s.end:6.2f}] " + " ".join(row))
    (d / "production" / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    (d / "production" / "words.txt").write_text("\n".join(lines) + "\n")
    print(f"✓ {len(words)} kata → production/words.txt (kata@detik). Salah dengar? tambah ke edit.json \"fixes\" lalu ulang.")


def cmd_stock(a):
    d = Path(a.dir); sp = load(d)
    items = [(b["img"], b.get("pexels"), b.get("grade", "dark")) for b in sp.get("broll", [])]
    items += [(g["img"], g.get("pexels"), g.get("grade", "cool")) for g in sp.get("glitch", [])]
    out = d / "assets" / "broll"; out.mkdir(parents=True, exist_ok=True)
    for name, pid, grade in items:
        raw = out / f"{name}.jpg"
        if not raw.exists():
            if not pid:
                die(f"assets/broll/{name}.jpg belum ada dan tidak ada id pexels")
            url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&h=2200"
            print(f"… unduh {name} ← pexels {pid}")
            req = urllib.request.Request(url, headers={"User-Agent": "motion-reels-agj/1.0"})
            raw.write_bytes(urllib.request.urlopen(req, timeout=60).read())
        run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-vf", GRADES[grade], "-q:v", "3", str(out / f"{name}_g.jpg")])
    # contact sheet crop 9:16 sesuai object-position
    try:
        from PIL import Image, ImageDraw
        th = []
        for b in sp.get("broll", []) + sp.get("glitch", []):
            im = Image.open(out / f"{b['img']}_g.jpg").convert("RGB"); iw, ih = im.size
            cw = min(iw, int(ih * 9 / 16)); x = int((iw - cw) * b.get("pos", 50) / 100)
            c = im.crop((x, 0, x + cw, ih)).resize((216, 384)); ImageDraw.Draw(c).text((6, 6), b["id"], fill="yellow"); th.append(c)
        if th:
            S = Image.new("RGB", (216 * len(th), 384))
            for i, c in enumerate(th):
                S.paste(c, (i * 216, 0))
            S.save(d / "build" / "crops.jpg")
            print("✓ build/crops.jpg — cek subjek tidak terpotong; atur \"pos\" (0–100) per B-roll")
    except ImportError:
        pass
    print(f"✓ {len(items)} gambar siap (kredit: Pexels, gratis dipakai)")


# ================================================================ build
TEXT_CSS = """
.blk{text-align:center;color:#fff}
.ln{display:block}
.ln.s{font-family:'Inter',sans-serif;font-weight:800;font-size:64px;letter-spacing:-0.025em;line-height:1.08}
.ln.i{font-family:'Playfair Display',serif;font-style:italic;font-weight:600;font-size:84px;letter-spacing:-0.01em;line-height:1.02;margin-top:-4px}
.ln.c{font-family:'Inter',sans-serif;font-weight:800;font-size:72px;line-height:1.04;text-transform:uppercase}
.blk .ln{text-shadow:0 0 24px rgba(255,255,255,.30),0 6px 26px rgba(0,0,0,.85),0 2px 4px rgba(0,0,0,.6)}
.wd{display:inline-block;white-space:nowrap}
.ch{display:inline-block;opacity:0}
"""

JS_HELP = r"""
const TYPE=(sel,t0,t1)=>{const cs=document.querySelectorAll(sel+' .ch');const n=cs.length;const st=n>1?(t1-t0)/(n-1):0;
 cs.forEach((c,i)=>tl.fromTo(c,{opacity:0,filter:'blur(10px)',y:6},{opacity:1,filter:'blur(0px)',y:0,duration:.16,ease:'power2.out',immediateRender:true},t0+i*st));};
const OUT=(sel,t)=>{tl.to(sel,{opacity:0,filter:'blur(8px)',duration:.18,ease:'power2.in'},t-.18);tl.set(sel,{opacity:0,visibility:'hidden'},t);};
const POP=(sel,t,o)=>tl.fromTo(sel,Object.assign({opacity:0,scale:.6,y:20},o||{}),{opacity:1,scale:1,y:0,duration:.32,ease:'back.out(2.2)'},t);
const DRAW=(sel,t,d)=>{document.querySelectorAll(sel).forEach(p=>{const L=p.getTotalLength();p.style.strokeDasharray=L;tl.fromTo(p,{strokeDashoffset:L},{strokeDashoffset:0,duration:d||.35,ease:'power2.inOut'},t);});};
"""

STRIKE = ('<svg class="strike" viewBox="0 0 600 60" preserveAspectRatio="none" style="{st}">'
          '<path d="M8 38 C 120 22, 260 44, 380 28 S 560 20, 592 30" fill="none" stroke="#E11D2E" stroke-width="16" stroke-linecap="round"/></svg>')
XSTAMP = ('<svg class="xst" id="{id}" viewBox="0 0 200 200" style="{st}"><g fill="none" stroke="#E11D2E" stroke-width="26" stroke-linecap="round">'
          '<path d="M38 40 C 80 90, 120 120, 165 165"/><path d="M162 36 C 120 80, 84 124, 36 166"/></g></svg>')

ICONS = {
    "bulb": '<path d="M22 40c-5-4-8-9-8-15a18 18 0 0 1 36 0c0 6-3 11-8 15v6H22z"/><path d="M24 52h16M27 58h10"/>',
    "target": '<circle cx="32" cy="32" r="24"/><circle cx="32" cy="32" r="14"/><circle cx="32" cy="32" r="4"/>',
    "shield": '<path d="M32 6l22 8v16c0 14-10 23-22 28C20 53 10 44 10 30V14z"/><path d="M22 32l7 7 13-14"/>',
    "chat": '<path d="M10 14h44a4 4 0 0 1 4 4v22a4 4 0 0 1-4 4H30l-12 10V44h-8a4 4 0 0 1-4-4V18a4 4 0 0 1 4-4z"/>',
    "spark": '<path d="M32 6l6 20 20 6-20 6-6 20-6-20-20-6 20-6z"/>',
    "check": '<rect x="8" y="8" width="48" height="48" rx="10"/><path d="M20 33l8 8 16-17"/>',
    "bolt": '<path d="M36 6L14 36h16l-4 22 24-32H34z"/>',
    "users": '<circle cx="24" cy="22" r="9"/><path d="M8 54c0-10 7-16 16-16s16 6 16 16"/><circle cx="44" cy="24" r="7"/><path d="M42 38c8 0 14 6 14 14"/>',
}


def chars(text):
    return " ".join('<span class="wd">' + "".join('<span class="ch">%s</span>' % html.escape(c) for c in w) + "</span>"
                    for w in text.split(" "))


def block(bid, lines, off=0.0, style="", strike=None):
    """lines: [[kind s|i|c, teks, t0, t1], ...] waktu global; off = start scene."""
    h, js = ['<div id="%s" class="blk" style="%s">' % (bid, style)], []
    for k, (kind, text, t0, t1) in enumerate(lines):
        lid = f"{bid}-l{k}"
        last = k == len(lines) - 1
        if strike and last:
            h.append('<span id="%s" class="ln %s" style="position:relative;display:inline-block">%s%s%s</span>' % (
                lid, kind, chars(text),
                STRIKE.format(st="position:absolute;left:-4%;width:108%;top:38%;height:48px"),
                XSTAMP.format(id=bid + "-x", st="position:absolute;right:-150px;top:-56px;width:140px;height:140px;opacity:0")))
        else:
            h.append('<span id="%s" class="ln %s">%s</span>' % (lid, kind, chars(text)))
        js.append("TYPE('#%s',%.2f,%.2f);" % (lid, t0 - off, t1 - off))
    if strike:
        st = strike - off
        js.append("DRAW('#%s .strike path',%.2f,.2);tl.fromTo('#%s-x',{opacity:0,scale:1.8,rotation:-12},{opacity:1,scale:1,rotation:0,duration:.18,ease:'power4.out'},%.2f);"
                  % (bid, st, bid, st + 0.17))
    h.append("</div>")
    return "\n".join(h), "\n".join(js)


def scene(sid, css, body, js, bg="#000"):
    return ("<template>\n<style>\n#root{position:absolute;inset:0;overflow:hidden;background:%s}\n" % bg + TEXT_CSS + css + "\n</style>\n"
            + '<div id="root" data-composition-id="%s" data-width="1080" data-height="1920">\n' % sid + body
            + "\n</div>\n<script>\nconst tl = gsap.timeline({ paused: true });\n" + JS_HELP + js
            + '\nwindow.__timelines["%s"] = tl;\n</script>\n</template>\n' % sid)


BROLL_CSS = """
.kb{position:absolute;left:0;top:0;width:1080px;height:1920px}
.kb img{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover}
.shade{position:absolute;inset:0;background:radial-gradient(ellipse 80% 55% at 50% 52%,rgba(0,0,0,.42),rgba(0,0,0,.12) 70%),linear-gradient(180deg,rgba(0,0,0,.35),rgba(0,0,0,0) 30%,rgba(0,0,0,0) 70%,rgba(0,0,0,.45))}
.mid{position:absolute;left:60px;width:960px;top:0;height:1920px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding-bottom:40px}
.chip{position:absolute;display:flex;align-items:center;gap:14px;padding:14px 24px 14px 14px;border-radius:20px;background:rgba(20,20,24,.55);
  border:1.5px solid rgba(255,255,255,.28);color:#fff;font-family:'Inter',sans-serif;font-weight:700;font-size:30px;box-shadow:0 10px 30px rgba(0,0,0,.45);opacity:0}
.chip i{width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.18);display:flex;align-items:center;justify-content:center;font-style:normal;font-size:24px}
.key{position:absolute;padding:22px 34px;border-radius:22px;background:rgba(15,15,18,.72);border:2px solid rgba(255,255,255,.55);
  box-shadow:0 8px 0 rgba(255,255,255,.18),0 0 26px rgba(255,255,255,.25);color:#fff;font-family:'JetBrains Mono',monospace;font-weight:700;font-size:44px;opacity:0}
"""

DIAG_CSS = """
.scan{position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 1px,transparent 1px 5px)}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse 90% 70% at 50% 45%,transparent 50%,rgba(0,0,0,.65))}
.bgd{position:absolute;inset:0;background:linear-gradient(180deg,#2b2b2b 0%,#181818 38%,#0c0c0c 100%)}
.thumb{position:absolute;overflow:hidden;border-radius:20px;border:4px solid #39ff3c;box-shadow:0 0 22px rgba(57,255,60,.75),0 0 60px rgba(57,255,60,.25),inset 0 0 12px rgba(57,255,60,.4)}
.thumb video{position:absolute;object-fit:cover}
.lab{position:absolute;font-family:'Inter',sans-serif;font-weight:700;color:#fff;text-shadow:0 0 16px rgba(255,255,255,.5);opacity:0}
.it{font-family:'Playfair Display',serif;font-style:italic;font-weight:600}
.chipo{position:absolute;padding:12px 30px;border:3px solid #fff;border-radius:16px;font-family:'Inter',sans-serif;font-weight:800;color:#fff;
  box-shadow:0 0 18px rgba(255,255,255,.55),inset 0 0 12px rgba(255,255,255,.25);text-shadow:0 0 14px rgba(255,255,255,.6);opacity:0;white-space:nowrap}
svg.ln2{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible}
svg.ln2 path{fill:none;stroke:#fff;stroke-width:3.5;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 6px rgba(255,255,255,.7))}
.ico{position:absolute;opacity:0}
.ico path,.ico circle,.ico rect{fill:none;stroke:#fff;stroke-width:3.5;stroke-linecap:round;stroke-linejoin:round}
"""


def thumb(start, dur, left, top, w, h):
    vw, vh = int(w * 1.3), int(h * 1.3)
    return ('<div class="thumb" id="th" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">'
            '<video id="th-v" class="clip" src="assets/aroll_g.mp4" data-start="0" data-duration="%.2f" data-media-start="%.2f" muted playsinline '
            'style="left:%dpx;top:%dpx;width:%dpx;height:%dpx"></video></div>') % (left, top, w, h, dur, start, -(vw - w) // 2, -int((vh - h) * 0.25), vw, vh)


def build_broll(b):
    s0, d = b["start"], b["end"] - b["start"]
    bh, bjs = block(b["id"] + "-tx", b.get("lines", []), s0)
    ex, exjs = [], []
    for k, c in enumerate(b.get("chips", [])):  # [teks, ikon, x, y, t]
        ex.append('<div class="chip" id="%s-c%d" style="left:%dpx;top:%dpx"><i>%s</i>%s</div>' % (b["id"], k, c[2], c[3], html.escape(c[1]), html.escape(c[0])))
        exjs.append("POP('#%s-c%d',%.2f);" % (b["id"], k, c[4] - s0))
    for k, c in enumerate(b.get("keys", [])):  # [teks, x, y, t]
        ex.append('<div class="key" id="%s-k%d" style="left:%dpx;top:%dpx">%s</div>' % (b["id"], k, c[1], c[2], html.escape(c[0])))
        exjs.append("POP('#%s-k%d',%.2f);" % (b["id"], k, c[3] - s0))
    kb, pan = b.get("kb", [1.04, 1.16]), b.get("pan", [0, -30])
    body = ('<div class="kb" id="%s-kb"><img src="assets/broll/%s_g.jpg" style="object-position:%d%% 50%%" /></div>\n<div class="shade"></div>\n%s\n<div class="mid">%s</div>'
            % (b["id"], b["img"], b.get("pos", 50), "\n".join(ex), bh))
    js = ("tl.fromTo('#%s-kb',{scale:%.3f,x:%d},{scale:%.3f,x:%d,duration:%.2f,ease:'none'},0);\n" % (b["id"], kb[0], pan[0], kb[1], pan[1], d)) + bjs + "\n" + "".join(exjs)
    return scene(b["id"], BROLL_CSS, body, js)


def build_title(t):
    css = """
#root{background:radial-gradient(ellipse 85% 60% at 50% 48%,#1c1c1c,#050505 75%)}
.tc{position:absolute;left:0;width:1080px;top:0;height:1920px;display:flex;flex-direction:column;align-items:center;justify-content:center}
.ta{font-family:'Inter',sans-serif;font-weight:800;font-size:132px;letter-spacing:-0.035em;line-height:1;color:#fff;text-shadow:0 0 30px rgba(255,255,255,.3)}
.tb{position:relative;font-family:'Playfair Display',serif;font-style:italic;font-weight:600;font-size:150px;line-height:1;margin-top:-6px;color:#fff;text-shadow:0 0 30px rgba(255,255,255,.3)}
"""
    i = t["id"]
    stk = STRIKE.format(st="position:absolute;left:-4%;width:108%;top:40%;height:64px") if t.get("strike") else ""
    body = '<div class="tc"><div id="%s-a" class="ta">%s</div><div id="%s-b" class="tb">%s%s</div></div>' % (i, chars(t["top"]), i, chars(t["bottom"]), stk)
    js = "TYPE('#%s-a',.02,.22);TYPE('#%s-b',.18,.4);" % (i, i)
    if t.get("strike"):
        js += "DRAW('#%s-b .strike path',%.2f,.2);" % (i, t["strike"] - t["start"])
    return scene(i, css, body, js)


def build_glitch(g):
    d = g["end"] - g["start"]; i = g["id"]; txt = html.escape(g["text"])
    css = """
.kb{position:absolute;left:0;top:0;width:1080px;height:1920px}
.kb img{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover}
.tint{position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,20,60,.55),rgba(30,0,60,.55));mix-blend-mode:multiply}
.gw{position:absolute;left:0;top:0;width:1080px;height:1920px;display:flex;align-items:center;justify-content:center}
.gl{position:absolute;font-family:'Inter',sans-serif;font-weight:900;font-size:%dpx;letter-spacing:-0.05em;line-height:1;white-space:nowrap}
.gr{color:#ff2a4f;mix-blend-mode:screen}.gc{color:#22e6ff;mix-blend-mode:screen}.gwh{color:#fff;text-shadow:0 0 40px rgba(255,255,255,.45)}
.band{position:absolute;left:0;width:1080px;overflow:hidden;opacity:0}
.band .gl{color:#fff;left:0;width:1080px;text-align:center}
.scan2{position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,.28) 0 2px,transparent 2px 5px)}
""" % min(210, int(1700 / max(4, len(g["text"]))))
    body = ('<div class="kb" id="%s-kb"><img src="assets/broll/%s_g.jpg" style="object-position:%d%% 50%%"/></div><div class="tint"></div>'
            '<div class="gw" id="%s-gw"><div id="%s-c" class="gl gc">%s</div><div id="%s-r" class="gl gr">%s</div><div class="gl gwh">%s</div></div>'
            '<div class="band" id="%s-b1" style="top:870px;height:52px"><div class="gl" style="top:-15px">%s</div></div>'
            '<div class="band" id="%s-b2" style="top:960px;height:40px"><div class="gl" style="top:-105px">%s</div></div><div class="scan2"></div>'
            % (i, g["img"], g.get("pos", 50), i, i, txt, i, txt, txt, i, txt, i, txt))
    jit = [(-14, 12, 30, -40), (10, -8, -50, 26), (-22, 18, 44, -18), (6, -4, -20, 60), (0, 0, 0, 0)]
    js = ["tl.fromTo('#%s-kb',{scale:1.1},{scale:1.2,duration:%.2f,ease:'none'},0);" % (i, d),
          "tl.fromTo('#%s-gw',{opacity:0,scale:1.25},{opacity:1,scale:1,duration:.22,ease:'power4.out'},0.02);" % i]
    for b0 in (0.04, d - 0.32):
        for k, (r, c, x1, x2) in enumerate(jit):
            t = b0 + k * 0.055
            js.append("tl.set('#%s-r',{x:%d},%.3f);tl.set('#%s-c',{x:%d},%.3f);tl.set('#%s-b1',{opacity:%d,x:%d},%.3f);tl.set('#%s-b2',{opacity:%d,x:%d},%.3f);"
                      % (i, r, t, i, c, t, i, 1 if x1 else 0, x1, t, i, 1 if x2 else 0, x2, t))
    return scene(i, css, body, "\n".join(js))


def build_flow(g):
    """Diagram alur vertikal: chip judul → (opsional) 'bukan X' dicoret → node berpanah → loop balik."""
    s0, d, i = g["start"], g["end"] - g["start"], g["id"]
    L = lambda t: t - s0
    cx = 705
    body = ['<div class="bgd"></div><div class="scan"></div><div class="vig"></div>', thumb(s0, d, 44, 700, 300, 533)]
    js = ["POP('#th',.0,{scale:.85,y:0});"]
    body.append('<div class="chipo" id="%s-chip" style="left:380px;width:650px;text-align:center;top:430px;font-size:60px;border:none;box-shadow:none"><span style="display:inline-block;padding:10px 28px;border:3px solid #fff;border-radius:16px;box-shadow:0 0 18px rgba(255,255,255,.55),inset 0 0 12px rgba(255,255,255,.25)">%s</span></div>' % html.escape(g["chip"]))
    js.append("POP('#%s-chip',%.2f,{scale:.8,y:0});" % (i, L(g.get("chip_t", s0 + 0.1))))
    paths = ['<path id="%s-c0" d="M%d 516 V 572"/>' % (i, cx)]
    ny = 600
    st = g.get("struck")
    if st:  # {"pre":"bukan cuma","pre_t":..,"text":"bikin prompt","t":..,"strike_t":..,"post":"tapi","post_t":..}
        body.append('<div class="lab it" id="%s-pre" style="left:380px;width:650px;text-align:center;top:580px;font-size:56px">%s</div>' % (i, html.escape(st["pre"])))
        body.append('<div class="lab" id="%s-st" style="left:380px;width:650px;text-align:center;top:650px;font-size:62px"><span style="position:relative;display:inline-block">%s%s</span></div>'
                    % (i, html.escape(st["text"]), STRIKE.format(st="position:absolute;left:-4%;width:108%;top:36%;height:44px")))
        js += ["DRAW('#%s-c0',%.2f,.25);" % (i, L(st.get("pre_t", s0 + 0.4))),
               "POP('#%s-pre',%.2f,{scale:1,y:10});" % (i, L(st.get("pre_t", s0 + 0.4))),
               "POP('#%s-st',%.2f,{scale:1,y:10});" % (i, L(st["t"])),
               "DRAW('#%s-st .strike path',%.2f,.22);tl.to('#%s-st',{opacity:.45,duration:.3},%.2f);" % (i, L(st["strike_t"]), i, L(st["strike_t"]) + 0.3)]
        if st.get("post"):
            body.append('<div class="lab it" id="%s-post" style="left:380px;width:650px;text-align:center;top:755px;font-size:56px">%s</div>' % (i, html.escape(st["post"])))
            js.append("POP('#%s-post',%.2f,{scale:1,y:10});" % (i, L(st.get("post_t", st["strike_t"] + 0.15))))
        ny = 880
    else:
        js.append("DRAW('#%s-c0',%.2f,.25);" % (i, L(g.get("chip_t", s0 + 0.1)) + 0.3))
    nodes = g["nodes"]  # [[teks, t], ...]
    step = 180 if len(nodes) <= 3 else int((1300 - ny) / (len(nodes) - 1)) if len(nodes) > 1 else 180
    for k, (txt, t) in enumerate(nodes):
        y = ny + k * step
        body.append('<div class="lab" id="%s-n%d" style="left:380px;width:650px;text-align:center;top:%dpx;font-size:54px">%s</div>' % (i, k, y, html.escape(txt)))
        js.append("POP('#%s-n%d',%.2f,{scale:.9,y:14});" % (i, k, L(t) - 0.05))
        if k > 0:
            y0, y1 = ny + (k - 1) * step + 72, y - 18
            paths.append('<path id="%s-a%d" d="M%d %d V %d M%d %d L%d %d L%d %d"/>' % (i, k, cx, y0, y1, cx - 12, y1 - 14, cx, y1, cx + 12, y1 - 14))
            js.append("DRAW('#%s-a%d',%.2f,.3);" % (i, k, L(t) - 0.4))
    if g.get("loop_t") and len(nodes) > 1:
        ya, yb = ny + (len(nodes) - 1) * step + 35, ny + 35
        paths.append('<path id="%s-loop" d="M905 %d H 1010 V %d H 905 M921 %d L905 %d L921 %d"/>' % (i, ya, yb, yb - 12, yb, yb + 12))
        js.append("DRAW('#%s-loop',%.2f,.6);" % (i, L(g["loop_t"])))
    body.append('<svg class="ln2" viewBox="0 0 1080 1920">' + "".join(paths) + "</svg>")
    return scene(i, DIAG_CSS, "\n".join(body), "\n".join(js), bg="#151515")


def build_stairs(g):
    """Tangga langkah: judul di samping thumbnail, anak tangga digambar garis + ikon + label."""
    s0, d, i = g["start"], g["end"] - g["start"], g["id"]
    L = lambda t: t - s0
    body = ['<div class="bgd"></div><div class="scan"></div><div class="vig"></div>', thumb(s0, d, 50, 210, 260, 462)]
    hb, hjs = block(i + "-h", g.get("head", []), s0, style="position:absolute;left:340px;width:700px;top:300px;text-align:left")
    body.append(hb)
    js = ["POP('#th',.0,{scale:.85,y:0});", hjs]
    steps = g["steps"]  # [[ikon, "label<br>baris2", t], ...]
    n = len(steps); w = 960 / n; rise = 190 if n <= 3 else 150; fs = 38 if n <= 3 else 32
    paths = []
    for k, (ico, label, t) in enumerate(steps):
        x0, x1 = 60 + k * w, 60 + (k + 1) * w
        y = 1300 - k * rise
        tail = "V %d" % (y - rise) if k < n - 1 else "V %d" % (y - 60)
        paths.append('<path id="%s-s%d" d="M%d %d H %d %s"/>' % (i, k, x0, y, x1, tail))
        body.append('<svg class="ico" id="%s-i%d" viewBox="0 0 64 64" width="76" height="76" style="left:%dpx;top:%dpx">%s</svg>' % (i, k, x0 + 20, y - 204, ICONS.get(ico, ICONS["check"])))
        body.append('<div class="lab" id="%s-l%d" style="left:%dpx;top:%dpx;font-size:%dpx;line-height:1.12;white-space:nowrap">%s</div>' % (i, k, x0 + 20, y - 120, fs, label))
        js.append("DRAW('#%s-s%d',%.2f,.45);POP('#%s-i%d',%.2f,{scale:.7,y:10});POP('#%s-l%d',%.2f,{scale:.9,y:12});" % (i, k, L(t) - 0.35, i, k, L(t), i, k, L(t) + 0.08))
    body.insert(3, '<svg class="ln2" viewBox="0 0 1080 1920">' + "".join(paths) + "</svg>")
    return scene(i, DIAG_CSS, "\n".join(body), "\n".join(js), bg="#151515")


def build_kin(sp, dur):
    body, js = [], []
    for k in sp.get("kinetic", []):
        bh, bjs = block(k["id"], k["lines"], 0, style="position:absolute;left:60px;width:960px;bottom:470px", strike=k.get("strike"))
        body.append(bh); js.append(bjs)
        if k.get("out"):
            js.append("OUT('#%s',%.2f);" % (k["id"], k["out"]))
    return scene("kin", "", "\n".join(body), "\n".join(js), bg="transparent")


def build_fx(leaks, flashes):
    css = """
.lk{position:absolute;inset:-20%;mix-blend-mode:screen;opacity:0}
.lk .a{position:absolute;inset:0;background:radial-gradient(ellipse 45% 60% at 20% 50%,rgba(255,241,197,.95),transparent 55%),radial-gradient(ellipse 70% 90% at 30% 50%,rgba(255,126,57,.85),transparent 70%)}
.lk .b{position:absolute;inset:0;background:radial-gradient(ellipse 55% 70% at 78% 40%,rgba(255,60,60,.8),rgba(255,40,90,.3) 50%,transparent 78%)}
.fl{position:absolute;inset:0;background:radial-gradient(ellipse 70% 60% at 50% 50%,#fff,rgba(255,240,220,.9) 60%,rgba(255,220,180,.7));opacity:0}
"""
    body, js = [], []
    for k, t in enumerate(leaks):
        body.append('<div class="lk" id="lk%d"><div class="a"></div><div class="b"></div></div>' % k)
        js.append("tl.fromTo('#lk%d',{opacity:0,x:-160},{opacity:.95,x:0,duration:.22,ease:'sine.out'},%.2f);tl.to('#lk%d',{opacity:0,x:140,duration:.4,ease:'sine.in'},%.2f);" % (k, t - 0.22, k, t + 0.02))
    for k, t in enumerate(flashes):
        body.append('<div class="fl" id="fl%d"></div>' % k)
        js.append("tl.fromTo('#fl%d',{opacity:0},{opacity:.92,duration:.1,ease:'power2.out'},%.2f);tl.to('#fl%d',{opacity:0,duration:.3,ease:'power2.in'},%.2f);" % (k, t - 0.1, k, t))
    return scene("fx", css, "\n".join(body), "\n".join(js), bg="transparent")


def make_sfx(d, kind):
    out = d / "assets" / "sfx" / f"{kind}.wav"
    if out.exists():
        return out
    sys.path.insert(0, str(HERE))
    import numpy as np
    import mr  # synth() bawaan skill — tanpa file SFX luar
    sig = mr.synth(kind, np)
    sig = (sig / max(1e-6, np.abs(sig).max()) * 0.9 * 32767).astype("<i2")
    import wave
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(mr.SR); w.writeframes(sig.tobytes())
    return out


def cmd_build(a):
    d = Path(a.dir); sp = load(d)
    if not (d / "assets" / "aroll_g.mp4").exists():
        die("jalankan prep dulu")
    dur = float(sp.get("duration") or probe(d / "assets" / "aroll_g.mp4")["dur"])
    comp = d / "compositions"; comp.mkdir(exist_ok=True)
    for f in comp.glob("*.html"):
        f.unlink()
    scenes = []  # (id, start, dur, html)
    for b in sp.get("broll", []):
        scenes.append((b["id"], b["start"], b["end"] - b["start"], build_broll(b)))
    for t in sp.get("titles", []):
        scenes.append((t["id"], t["start"], t["end"] - t["start"], build_title(t)))
    for g in sp.get("glitch", []):
        scenes.append((g["id"], g["start"], g["end"] - g["start"], build_glitch(g)))
    for g in sp.get("diagrams", []):
        scenes.append((g["id"], g["start"], g["end"] - g["start"], build_flow(g) if g["type"] == "flow" else build_stairs(g)))
    scenes.sort(key=lambda s: s[1])
    for k in range(1, len(scenes)):
        if scenes[k][1] < scenes[k - 1][1] + scenes[k - 1][2] - 0.01:
            print(f"! {scenes[k][0]} mulai sebelum {scenes[k-1][0]} selesai — cek waktu di edit.json")
    leaks = sp.get("leaks") if "leaks" in sp else [b["start"] for b in sp.get("broll", [])]
    flashes = sp.get("flashes") if "flashes" in sp else [s["start"] for s in sp.get("titles", []) + sp.get("diagrams", [])]
    scenes.append(("kin", 0.0, dur, build_kin(sp, dur)))
    scenes.append(("fx", 0.0, dur, build_fx(leaks, flashes)))
    for sid, st, du, h in scenes:
        (comp / f"{sid}.html").write_text(h)
    # SFX: minimal & pelan (feedback: SFX rame = berisik). Default whoosh tiap B-roll (jarak ≥ 8 dtk) + glitch.
    if "sfx" in sp:
        sfx = sp["sfx"]
    else:
        sfx, last = [], -99
        for t in sorted(leaks):
            if t - last >= 8:
                sfx.append(["whoosh", t - 0.25, 0.12]); last = t
        sfx += [["glitch", g["start"], 0.10] for g in sp.get("glitch", [])]
    audio = []
    for k, (kind, t, vol) in enumerate(sfx):
        f = make_sfx(d, kind)
        du = min(1.0, dur - t)
        audio.append('<audio id="sfx%d" class="clip" src="assets/sfx/%s" data-start="%.2f" data-duration="%.2f" data-track-index="%d" data-volume="%.2f"></audio>'
                     % (k, f.name, t, du, 10 + k % 3, vol))
    z = {"kin": 4, "fx": 9}
    hosts = []
    for n, (sid, st, du, _) in enumerate(scenes):
        kind = "graphics"
        hosts.append('<div id="%s" data-composition-id="%s" data-composition-src="compositions/%s.html" data-start="%.2f" data-duration="%.2f" data-track-index="%d" '
                     'data-track-kind="%s" data-width="1080" data-height="1920" style="position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:%d"></div>'
                     % (sid, sid, sid, st, du, 2 + n % 2 if sid not in z else (4 if sid == "kin" else 5), kind, z.get(sid, 5)))
    fr = []
    for t0, t1, m in sp.get("framing", [[0, dur, "wide"]]):
        s, fy = (1.0, 720) if m == "wide" else (1.36, 950)
        fr.append("seg(%.2f,%.2f,%.3f,%d);" % (t0, t1, s, fy))
    gsap = "assets/gsap.min.js" if (d / "assets" / "gsap.min.js").exists() else "https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"
    index = INDEX.replace("@GSAP@", gsap).replace("@DUR@", "%.2f" % dur).replace("@HOSTS@", "\n      ".join(hosts)) \
        .replace("@AUDIO@", "\n      ".join(audio)).replace("@FR@", "\n      ".join(fr))
    (d / "index.html").write_text(index)
    print(f"✓ build: {len(scenes) - 2} scene + kinetic + fx, {len(audio)} SFX, durasi {dur:.2f}s → lanjut: check, snap")


INDEX = """<!doctype html>
<html lang="id" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="@GSAP@"></script>
    <style>
      *{margin:0;padding:0;box-sizing:border-box}
      html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:#000}
      #root{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}
      #aroll-wrap{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;z-index:2}
      #aroll{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover}
      #aroll-shade{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:3;pointer-events:none;
        background:linear-gradient(180deg,rgba(0,0,0,.25),rgba(0,0,0,0) 25%,rgba(0,0,0,0) 50%,rgba(0,0,0,.55) 78%,rgba(0,0,0,.7))}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="@DUR@" data-width="1080" data-height="1920">
      <div id="aroll-wrap">
        <video id="aroll" class="clip" src="assets/aroll_g.mp4" data-start="0" data-duration="@DUR@" data-track-index="0" playsinline data-has-audio="true"></video>
      </div>
      <div id="aroll-shade"></div>
      @HOSTS@
      @AUDIO@
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      const W = "#aroll-wrap";
      const F = (s, fy) => ({ scale: s, x: (1 - s) * 540, y: (1 - s) * fy });
      gsap.set(W, Object.assign({ transformOrigin: "0 0" }, F(1, 720)));
      const seg = (t0, t1, s, fy) => {           // jump-cut: framing berganti mendadak + drift pelan
        tl.set(W, F(s, fy), t0);
        tl.fromTo(W, F(s, fy), Object.assign(F(s + 0.035, fy), { duration: t1 - t0, ease: "none", immediateRender: false }), t0);
      };
      @FR@
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


# ================================================================ hyperframes wrappers / mix
def cmd_check(a):
    subprocess.run(HF + ["check"], cwd=a.dir)


def cmd_snap(a):
    out = Path(a.dir).resolve() / "build" / "snap"
    if out.exists():
        shutil.rmtree(out)
    run(HF + ["snapshot", "--at", a.at, "--no-end", "--timeout", "170000", "-o", str(out)], cwd=a.dir)
    print(f"✓ {out}/contact-sheet*.jpg — lihat: teks tidak menutup wajah, crop B-roll, diagram tidak mepet")


def cmd_render(a):
    d = Path(a.dir).resolve()
    if a.range:
        s, e = a.range.split(",")
        out = d / "build" / f"test_{s}-{e}.mp4"
        run(HF + ["render", "--sdr", "--start", s, "--end", e, "-o", str(out)], cwd=d)
    else:
        out = d / f"{d.name}.mp4"
        run(HF + ["render", "--sdr", "-o", str(out)], cwd=d)
    print(f"✓ {out}")


def cmd_mix(a):
    d = Path(a.dir).resolve(); vid = d / f"{d.name}.mp4"
    if not vid.exists():
        die("render dulu")
    out = d / f"{d.name}-tanpa-sfx.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(d / "assets" / "aroll_g.mp4"), "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)])
    print(f"✓ {out} (suara asli saja — buat tambah sound trending di aplikasi)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init"); p.add_argument("dir"); p.add_argument("--footage", required=True); p.add_argument("--rubrik"); p.set_defaults(fn=cmd_init)
    p = sp.add_parser("prep"); p.add_argument("dir"); p.set_defaults(fn=cmd_prep)
    p = sp.add_parser("words"); p.add_argument("dir"); p.add_argument("--model", default="small"); p.add_argument("--lang", default="id"); p.set_defaults(fn=cmd_words)
    p = sp.add_parser("stock"); p.add_argument("dir"); p.set_defaults(fn=cmd_stock)
    p = sp.add_parser("build"); p.add_argument("dir"); p.set_defaults(fn=cmd_build)
    p = sp.add_parser("check"); p.add_argument("dir"); p.set_defaults(fn=cmd_check)
    p = sp.add_parser("snap"); p.add_argument("dir"); p.add_argument("--at", required=True); p.set_defaults(fn=cmd_snap)
    p = sp.add_parser("render"); p.add_argument("dir"); p.add_argument("--range"); p.set_defaults(fn=cmd_render)
    p = sp.add_parser("mix"); p.add_argument("dir"); p.set_defaults(fn=cmd_mix)
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
