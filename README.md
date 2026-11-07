# Orbital ASCII

A procedural monochrome particle artwork for an ANSI terminal. The scene is calculated at runtime from persistent parametric ring, crown, orbit, axis, and ambient-star particles. It uses NumPy for the vectorized particle field and emits Braille dot cells with truecolor ANSI by default. The default composition follows `reference/ChatGPT Image Nov 5, 2026, 09_39_30 PM.gif`: a vertically elongated glyph ring, faceted crown, faint crossing orbital traces, star grain, and compact HUD.

## Install on Arch Linux

```sh
sudo pacman -S python python-pip ffmpeg
cd orbital-ascii
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run.sh
```

Controls: Space pause/resume, R restart, `+` / `-` particle density, `[` / `]` speed, G geometry emphasis, P ASCII/Braille mode, O orbits, H HUD, C color fallback cycle, D debug, Q quit. The terminal is restored on exit and Ctrl+C.

Render a preview GIF with `python main.py --export output/rendered_preview.gif`; use `--duration 4` for a short preview. The export uses the live ring-first animation and keeps the reference's 432×384 frame size.

Adjust `config.toml` to change timing, particle count, geometry, render mode, brightness, seed, or HUD. The default dot renderer keeps the reference aspect ratio and centers the art in the terminal; press P to switch to Braille mode.

## Reference fidelity

The checked-in reference GIF is 432×384, 10 fps, and 20 seconds long. The live animation starts blank, draws the near-circular ring from the bottom in two arcs, builds the smaller downward-pointing diamond from its tip, then reveals “WILL YOU MARRY ME / ANISHU...?” in bold, centered text below it. The text stays visible during the two horizontal spins around the ring's bottom point, then fades with the sculpture for a seamless loop. The preview is generated from the live simulation; the reference file remains unchanged.

The terminal player requires a POSIX TTY. GIF export requires FFmpeg. The only Python runtime dependency is NumPy; Pillow and SciPy are not required.
