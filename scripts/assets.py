#!/usr/bin/env python3
"""assets.py — struktur folder aset standar untuk semua tipe konten (vlog, motion, ngobrol).

Setiap proyek punya 3 folder:
  sound/    suara milik konten ini: backsound pilihan, VO rekaman, SFX tambahan
  konten/   aset konten sendiri: preferensi gambar, logo, foto produk, screenshot, brand
  footage/  klip video: bahan utama (vlog, ngobrol) atau sisipan selang-seling (motion)
Dipakai oleh vlog.py, mr.py, aroll.py (init membuat folder; build mencari file di sini dulu).
"""
import os
from pathlib import Path

PERAN_FOOTAGE = {
    "vlog": "BAHAN UTAMA. Semua klip perjalanan/aktivitas taruh di sini (nama asli dari HP tidak apa-apa).",
    "ngobrol": "BAHAN UTAMA (A-roll rekaman bicara) + klip tambahan untuk B-roll.",
    "motion": "JARANG DIPAKAI. Motion grafik murni jalan tanpa footage; taruh klip di sini hanya kalau mau disisipkan selang-seling.",
}
README = {
    "sound": "Backsound/VO/SFX untuk konten ini.\nBackground music: boleh nama file saja di \"bgm\"; dicari di sini dulu, lalu di $BACKSOUND_DIR (folder backsound kantor).\n",
    "konten": "Aset konten sendiri: preferensi gambar, logo, foto produk, screenshot, referensi gaya.\nSkill memakai ini sebagai acuan visual sebelum mencari gambar dari luar.\n",
    "footage": "",
}


def scaffold(d, tipe):
    d = Path(d)
    for kind in ("sound", "konten", "footage"):
        p = d / kind
        p.mkdir(parents=True, exist_ok=True)
        r = p / "README.txt"
        txt = README[kind] or (PERAN_FOOTAGE[tipe] + "\n")
        if not r.exists():
            r.write_text(txt)
    return [d / k for k in ("sound", "konten", "footage")]


def find_sound(d, name):
    """Cari file suara: path langsung → <proyek>/sound → <proyek>/audio → <proyek> → $BACKSOUND_DIR (rekursif)."""
    d = Path(d)
    for c in (Path(name).expanduser(), d / "sound" / name, d / "audio" / name, d / name):
        if c.is_file():
            return c
    root = os.environ.get("BACKSOUND_DIR")
    if root and Path(root).expanduser().is_dir():
        want = Path(name).name.lower()
        for c in Path(root).expanduser().rglob("*"):
            if c.is_file() and c.name.lower() == want:
                return c
    return None


def list_konten(d):
    """Daftar gambar di konten/ (untuk dibaca agent sebagai preferensi visual)."""
    p = Path(d) / "konten"
    ext = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
    return sorted(f for f in p.rglob("*") if f.suffix.lower() in ext) if p.is_dir() else []
