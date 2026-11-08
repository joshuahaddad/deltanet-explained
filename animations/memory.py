"""KV cache vs state S, as areas: every token adds a sliver, S stays one square; at 100k the cache is ~1,500 S-tiles."""
import numpy as np
from manim import *
import style

d = 128
per_token = 2 * d                  # 256
state = d * d                      # 16,384
tok_per_tile = state // per_token  # 64
T = 100_000
cache = per_token * T              # 25,600,000
ratio = cache / state              # 1562.5, also the number of tiles
assert (per_token, state, tok_per_tile) == (256, 16_384, 64) and tok_per_tile * per_token == state
assert ratio == 1562.5 and 1400 < ratio < 1600 and f"{cache / 1e6:.1f}M" == "25.6M"

BG, INK, MUTED, ORANGE, BLUE, GREEN = style.BG, style.INK, style.MUTED, style.ORANGE, style.BLUE, style.GREEN
TILE, COLS = 16 / 90, 50  # 16 px at 720p; whole-pixel tiles keep the GIF small
GRID_TL = np.array([-3.3, 2.5 + 5 / 90, 0])  # on a pixel corner; 50 x 32 rows spans x -3.3..5.6, y 2.56..-3.13


class Memory(Scene):
    def construct(self):
        tok = ValueTracker(0)
        title = Text("Numbers stored per head (d = 128)", font_size=style.TITLE, color=INK).move_to(UP * 3.5)
        S = Square(2.0, fill_color=ORANGE, fill_opacity=style.BAR_OPACITY, stroke_width=0).move_to(LEFT * 4.6)
        S_lab = MathTex(r"S:\ 128 \times 128 = 16{,}384", font_size=45, color=INK).move_to([-4.6, -1.5, 0])
        box = DashedVMobject(Square(2.0, stroke_color=MUTED, stroke_width=style.STRUCTURE), num_dashes=40).move_to(RIGHT * 0.6)
        box_lab = Text("KV cache", font_size=style.BODY, color=INK).move_to([0.6, -1.5, 0])
        note = MathTex("+256", r"\ \text{per token}", font_size=45, color=INK).move_to([3.6, 0, 0])
        note[0].set_color(BLUE)
        tokens = always_redraw(lambda: Text(f"tokens: {round(tok.get_value()):,}", font_size=style.BODY, color=INK)
                               .move_to([3.3, 2.85, 0], aligned_edge=LEFT))
        self.add(title, S, S_lab, box, box_lab, tokens)
        self.wait(0.2)

        # B1: eight tokens, one at a time; S pulses but never grows
        w = 2.0 / tok_per_tile
        slivers = [Rectangle(width=w, height=2.0, fill_color=BLUE, fill_opacity=style.BAR_OPACITY, stroke_width=0)
                   .move_to([-0.4 + (i + 0.5) * w, 0, 0]) for i in range(tok_per_tile)]
        for i in range(8):
            self.play(FadeIn(slivers[i], shift=0.6 * DOWN), Indicate(S, scale_factor=1.0, color=ORANGE),
                      tok.animate.set_value(i + 1), run_time=0.42)
            if i == 0:
                self.play(Write(note), run_time=0.4)

        # B2: the other 56, two per frame, hard edges
        for i in range(8, tok_per_tile, 2):
            self.add(*slivers[i:i + 2])
            tok.set_value(i + 2)
            self.wait(1 / config.frame_rate)

        # B3: 64 tokens fill exactly one S
        cross = MathTex(r"64 \text{ tokens} \times 256 = 16{,}384", font_size=57, color=INK).move_to([-2.0, -2.4, 0])
        eq = MathTex("=", font_size=72, color=GREEN).move_to([-2.0, 0, 0])
        filled = VGroup(*slivers)
        self.play(Write(cross), Write(eq), run_time=0.5)
        self.play(Indicate(S, color=ORANGE), Indicate(filled, color=BLUE), run_time=0.6)
        self.wait(1.2)

        # B4: clear the text, then S and the filled cache each shrink to one tile
        tiles = [Square(TILE, fill_color=BLUE, fill_opacity=style.BAR_OPACITY, stroke_color=BG, stroke_width=0.6)  # BG strokes read as gaps
                 .move_to(GRID_TL + [(i % COLS + 0.5) * TILE, -(i // COLS + 0.5) * TILE, 0])
                 for i in range(int(ratio) + 1)]
        tiles[-1].stretch_to_fit_width(TILE / 2, about_edge=LEFT)  # the half tile
        S_spot = [-5.6, GRID_TL[1] - TILE / 2, 0]
        S_small = MathTex("S", font_size=45, color=ORANGE).next_to(S_spot, LEFT, buff=0.35)
        legend = Paragraph("1 tile =", "16,384 numbers", font_size=style.SMALL, color=MUTED).move_to([-6.9, -2.85, 0], aligned_edge=LEFT)
        self.play(FadeOut(S_lab, note, box_lab, box, cross, eq), run_time=0.4)
        self.play(ReplacementTransform(filled, tiles[0]),
                  S.animate.scale(TILE / 2.0).move_to(S_spot), run_time=0.8)
        self.play(FadeIn(S_small, legend), run_time=0.3)

        # B5: 1 -> 1562.5 tiles; S never changes
        n = ValueTracker(1)
        grid = VGroup(*tiles[:1])
        grid.add_updater(lambda g: g.set_submobjects(tiles[:int(np.ceil(n.get_value()))]))
        self.remove(tiles[0])
        tok.add_updater(lambda m: m.set_value(round(tok_per_tile * n.get_value())))
        cache_num = always_redraw(lambda: Text(f"cache: {per_token * round(tok.get_value()):,}", font_size=style.BODY, color=BLUE)
                                  .move_to([-3.3, 2.85, 0], aligned_edge=LEFT))
        self.add(grid, tok, cache_num)
        self.play(n.animate.set_value(ratio), rate_func=linear, run_time=5.0)
        tok.clear_updaters()
        assert round(tok.get_value()) == T and per_token * round(tok.get_value()) == cache and len(grid) == 1563

        # B6: name the gap, as one block under S
        ring = style.box(S)
        S_note = Paragraph("16,384 numbers,", "at any length", font_size=style.SMALL, color=ORANGE).move_to([-6.9, 1.6, 0], aligned_edge=LEFT)
        head = Text("about 1,500×\nsmaller", font_size=style.BODY, color=ORANGE).next_to(S_note, DOWN, buff=0.15, aligned_edge=LEFT)
        cache_note = Paragraph("KV cache at 100k:", f"{cache / 1e6:.1f}M numbers", font_size=style.SMALL, color=BLUE) \
            .move_to([-6.9, head.get_bottom()[1] - 0.75, 0], aligned_edge=LEFT)
        self.play(Create(ring), FadeIn(S_note), run_time=0.4)
        self.play(FadeIn(cache_note), run_time=0.4)
        self.play(Write(head), run_time=0.6)

        # B7: hold
        self.wait(2.8)
