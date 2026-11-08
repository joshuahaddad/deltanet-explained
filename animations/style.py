"""Shared look for every animation, so the post's visuals read as one set. The spec is STYLE.md."""
from manim import (Arrow, MarkupText, Paragraph, Scene, StealthTip, SurroundingRectangle, TexTemplate, Text, config,
                   rate_functions)

# Palette "ink + plum accent": Okabe-Ito orange and sky on a near-black plate.
BG = "#16141C"         # the plate
MAT = "#1B1922"        # band round the plate, added by frames_to_gif.py
SURFACE = "#211E29"    # cards, table bodies
RULE = "#2E2A38"       # gridlines, deliberately faint
MUTED = "#8A8696"      # context, dimmed items
INK = "#ECEAF0"        # text and outlines
PRIMARY = "#E69F00"    # warm: the stored key, the delta rule
SECONDARY = "#56B4E9"  # cool: the query, interference, the plain sum
ACCENT = "#CC79A7"     # plum: emphasis shapes only, never data next to blue
TARGET = "#8FE8BE"     # light mint: target / correct, light enough to read as a dashed outline over bars
ERROR = "#F2795A"      # coral: wrong; pair it with a glyph, it sits close to orange for colour-blind readers
ORANGE, BLUE, GREY, GREEN = PRIMARY, SECONDARY, MUTED, TARGET  # the names the scenes already use

MAT_PX, CORNER_PX = 6, 14  # framing, added to every frame by frames_to_gif.py
config.background_color = BG
config.frame_rate = 15

# Type: CMU Serif text, Euler maths. MathTex draws about 1.5x smaller than Text at the same font_size.
SMALL, BODY, TITLE = 30, 38, 48
for cls in (Text, Paragraph, MarkupText):
    cls.set_default(font="CMU Serif")
config.tex_template = TexTemplate()
config.tex_template.add_to_preamble(r"\usepackage[euler-digits]{eulervm}")

# Strokes: data / structure / emphasis. Bars stay near-solid.
DATA, STRUCTURE, EMPHASIS = 5, 2, 6
BAR_OPACITY = 1.0  # solid: below 1 the dark plate shows through and orange turns brown
Arrow.set_default(tip_shape=StealthTip)

# Emphasis: box the focus by default; in crowded diagrams, dim the rest by swapping to MUTED (not opacity).
box = lambda m: SurroundingRectangle(m, color=ACCENT, stroke_width=EMPHASIS, corner_radius=0.12, buff=0.1)
dim = lambda *ms: [m.animate.set_color(MUTED) for m in ms]

# Motion: Manim's defaults (run_time 1, smooth), then a 1.5 s hold. Go snappy (SNAPPY, 0.5 s) when a clip
# runs long or the speed-up is the point, e.g. the KV cache growing.
RUN_TIME, EASE, SNAPPY = 1.0, rate_functions.smooth, rate_functions.ease_out_cubic

# We render PNG frames, and Manim writes a still wait() as ONE frame there, which deletes every hold.
_wait = Scene.wait
Scene.wait = lambda self, duration=1.0, stop_condition=None, frozen_frame=None: _wait(self, duration, stop_condition, frozen_frame=False)
