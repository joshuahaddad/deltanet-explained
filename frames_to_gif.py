"""PNG frames -> framed GIF with one shared palette, no dithering, identical frames merged.
Manim's own GIF output dithers every frame, which shifts colours and bloats the file.
Runs inside the Manim image: python frames_to_gif.py <frames_dir> out.gif (or out.png for a still: the framed last frame)"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent / "animations"))
import style  # noqa: E402

src, out = Path(sys.argv[1]), sys.argv[2]
frames = [Image.open(p).convert("RGB") for p in sorted(src.glob("*.png"))]

# Framing: plate, then a MAT_PX band, then CORNER_PX corners. Outside the radius is mat, never page colour.
m, (w, h) = style.MAT_PX, frames[0].size
mask = Image.new("L", (w, h), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], style.CORNER_PX, fill=255)
framed = []
for im in frames:
    framed.append(Image.new("RGB", (w + 2 * m, h + 2 * m), style.MAT))
    framed[-1].paste(im, (m, m), mask)
frames = framed
if out.endswith(".png"):
    sys.exit(frames[-1].save(out))

# Palette: the style colours exactly, then anti-aliasing shades sampled from the clip.
pinned = [style.BG, style.MAT, style.SURFACE, style.RULE, style.MUTED, style.INK, style.PRIMARY, style.SECONDARY,
          style.ACCENT, style.TARGET, style.ERROR, "#FFFFFF"]  # white: scenes still use it
pinned = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in pinned]
sample = frames[:: max(1, len(frames) // 16)]
w, h = sample[0].size
strip = Image.new("RGB", (w, h * len(sample)))
for i, im in enumerate(sample):
    strip.paste(im, (0, i * h))
shades = strip.quantize(colors=256 - len(pinned), method=Image.Quantize.MEDIANCUT).getpalette()[: 3 * (256 - len(pinned))]
pal = Image.new("P", (1, 1))
pal.putpalette([v for c in pinned for v in c] + shades)

gif, durations = [], []

prev_end = 0
for i, im in enumerate(frames):
    # GIF stores times in 10 ms steps: round the running clock, not each frame, or 15 fps plays 10% fast.
    end = round((i + 1) * 100 / style.config.frame_rate) * 10
    ms, prev_end = end - prev_end, end
    q = im.quantize(palette=pal, dither=Image.Dither.NONE)
    if gif and q.tobytes() == gif[-1].tobytes():
        durations[-1] += ms  # held frame: stretch the previous one instead of storing it again
    else:
        gif.append(q)
        durations.append(ms)
gif[0].save(out, save_all=True, append_images=gif[1:], duration=durations, loop=0)
