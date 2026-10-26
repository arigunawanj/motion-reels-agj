#!/usr/bin/env bash
# Install skill motion-reels-agj ke agent yang terpasang.
#   ./install.sh            global (Claude Code, Codex, Antigravity, ~/.agents)
#   ./install.sh --project  ke project di folder saat ini (.claude/.agents/.codex)
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
NAME=motion-reels-agj
copy() { mkdir -p "$1"; rm -rf "$1/$NAME"; cp -R "$SRC" "$1/$NAME"; rm -rf "$1/$NAME/.git"; echo "✓ $1/$NAME"; }

if [ "$1" = "--project" ]; then
  for t in .claude/skills .agents/skills .codex/skills; do copy "$PWD/$t"; done
else
  copy "$HOME/.claude/skills"                                   # Claude Code
  [ -d "$HOME/.codex" ]  && copy "$HOME/.codex/skills"           # OpenAI Codex
  if [ -d "$HOME/.gemini" ]; then                                # Google Antigravity
    copy "$HOME/.gemini/config/skills"
    [ -d "$HOME/.gemini/antigravity" ] && copy "$HOME/.gemini/antigravity/skills"
  fi
  copy "$HOME/.agents/skills"                                    # standar lintas agent
fi

echo
echo "Cek dependensi:"
command -v ffmpeg >/dev/null && echo "  ✓ ffmpeg" || echo "  ! ffmpeg belum ada (brew install ffmpeg / apt install ffmpeg)"
python3 -c "import numpy" 2>/dev/null && echo "  ✓ numpy" || echo "  ! pip install numpy"
python3 -c "import playwright" 2>/dev/null && echo "  ✓ playwright" || echo "  ! pip install playwright && python3 -m playwright install chromium"
[ -n "$TTS_API_KEY" ] && echo "  ✓ TTS_API_KEY ter-set" || echo "  ! export TTS_API_KEY=...  (simpan di ~/.zshrc, jangan di repo)"
