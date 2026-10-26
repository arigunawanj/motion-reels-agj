# Contoh: 5 Tips Vibe Coding (desain default AGJ Labs)

Project lengkap hasil skill ini: naskah (`script.json`), scene & kamera (`scenes.js`), tema (`style.css`), dokumen produksi (`production/`), dan paket caption dari skill [social-caption-publish](https://github.com/arigunawanj/social-caption-publish) (`publishing/`).

Render ulang contoh ini (folder contoh tidak menyertakan `engine/` agar tidak dobel):
```bash
cd examples/vibe-coding-agj
cp -r ../../engine . && cp ../../templates/project/index.html .
python3 ../../scripts/mr.py tts . --draft     # atau tanpa --draft + TTS_API_KEY untuk VO asli
python3 ../../scripts/mr.py stills .
```
