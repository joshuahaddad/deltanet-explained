"""8 keys, 300 random overwrites: the plain sum's readback error climbs, the delta rule's stays small (β = 1 lowest)."""
import sys

import numpy as np
from manim import *
import style

sys.path.insert(0, "/manim")
from deltanet import unit

# same setup and RNG order as make_figures.py:dict_test and interactive/make_dict_test_json.py
rng = np.random.default_rng(1)
d, n_keys, steps = 128, 8, 300
keys = unit(rng.normal(size=(n_keys, d)))
truth = np.zeros((n_keys, d))
S_sum, S_delta, S_half = np.zeros((d, d)), np.zeros((d, d)), np.zeros((d, d))
err_sum, err_delta, err_half, idx = [], [], [], []
rel = lambda S, seen: np.mean(np.linalg.norm((keys @ S - truth)[seen], axis=1) / np.linalg.norm(truth[seen], axis=1))
for _ in range(steps):
    i = rng.integers(n_keys)
    k, v = keys[i], rng.normal(size=d)
    truth[i] = v
    S_sum += np.outer(k, v)
    S_delta += np.outer(k, v - S_delta.T @ k)
    S_half += 0.5 * np.outer(k, v - S_half.T @ k)
    idx.append(i)
    seen = np.abs(truth).sum(1) > 0
    err_sum.append(rel(S_sum, seen))
    err_delta.append(rel(S_delta, seen))
    err_half.append(rel(S_half, seen))

# storyboard check values
assert f"{err_sum[-1]:.2f}" == "6.19" and f"{err_delta[-1]:.2f}" == "0.19", (err_sum[-1], err_delta[-1])
assert f"{err_half[-1]:.2f}" == "0.59", err_half[-1]  # matches the page's DICT.delta["0.5"]
assert idx[:8] == [4, 7, 7, 2, 7, 5, 3, 7]


class DictTest(Scene):
    def construct(self):
        t = ValueTracker(0)
        n = lambda: int(t.get_value() + 1e-6)

        title = Text("8 keys, 300 updates: read back each key's latest value", font_size=style.BODY, color=style.INK).set_y(3.45)
        strip = VGroup(*[VGroup(RoundedRectangle(width=1.1, height=0.6, corner_radius=0.1, color=style.MUTED,
                                                 stroke_width=style.STRUCTURE, fill_color=style.SURFACE, fill_opacity=1),
                                MathTex(f"k_{{{j + 1}}}", font_size=45, color=style.INK))
                         .move_to([-4.55 + 1.3 * j, 2.45, 0]) for j in range(n_keys)])
        dict_lab = Text("dict", font_size=style.SMALL, color=style.MUTED).move_to([-6.3, 2.45, 0])

        ax = Axes(x_range=[0, 300, 50], y_range=[0, 8, 1], x_length=7.8, y_length=4.2, tips=False,
                  axis_config={"color": style.MUTED, "stroke_width": style.STRUCTURE, "include_numbers": True, "font_size": 45})
        ax.shift([-5.6, -2.85, 0] - ax.c2p(0, 0))
        for axis in (ax.x_axis, ax.y_axis):
            axis.numbers.set_color(style.INK)
        x_lab = Text("updates written", font_size=style.SMALL, color=style.INK).next_to(ax.x_axis, DOWN, buff=0.15)
        y_lab = Text("error reading latest value", font_size=style.SMALL, color=style.INK).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.5)
        ref = DashedLine(ax.c2p(0, 1), ax.c2p(300, 1), color=style.MUTED, stroke_width=style.STRUCTURE)
        ref_lab = Text("1 = error as big as the value", font_size=style.SMALL, color=style.MUTED)
        ref_lab.next_to(ax.c2p(300, 1), UP, buff=0.12).align_to(ax.c2p(300, 1), RIGHT)

        def legend_row(color, name, y, line=Line):
            row = VGroup(line(ORIGIN, 0.6 * RIGHT, color=color, stroke_width=style.DATA),
                         Text(name, font_size=style.SMALL, color=style.INK)).arrange(RIGHT, buff=0.25)
            return row.next_to(ax.c2p(10, y), RIGHT, buff=0)
        legend = VGroup(legend_row(style.BLUE, "plain sum", 7.6), legend_row(style.ORANGE, "delta rule, β = 1", 6.6),
                        legend_row(style.ORANGE, "delta rule, β = 0.5", 5.6, DashedLine))
        counter = always_redraw(lambda: Text(f"update {n()}", font_size=style.SMALL, color=style.INK)
                                .next_to(ax.c2p(300, 8), DOWN, buff=0).align_to(ax.c2p(300, 8), RIGHT))

        def curve(err, color, dashed=False):
            def draw():
                pts = [ax.c2p(j + 1, err[j]) for j in range(n())]
                line = VMobject(stroke_color=color, stroke_width=style.DATA)
                if len(pts) < 2:
                    return line
                line.set_points_as_corners(pts)
                return DashedVMobject(line, num_dashes=max(1, int(line.get_arc_length() / 0.2))) if dashed else line
            return always_redraw(draw)
        blue = curve(err_sum, style.BLUE)
        orange = curve(err_delta, style.ORANGE)
        half = curve(err_half, style.ORANGE, dashed=True)

        def light_slot(group):
            for j, (box, lab) in enumerate(group):
                on = n() > 0 and j == idx[n() - 1]
                box.set_stroke(style.ORANGE if on else style.MUTED, width=style.EMPHASIS if on else style.STRUCTURE)
                lab.set_color(style.ORANGE if on else style.INK)
        strip.add_updater(light_slot)

        # beat 1: a readable empty chart
        self.add(title, strip, dict_lab, ax, x_lab, y_lab, ref, ref_lab, legend, counter, blue, half, orange)
        self.wait(1)

        # beat 2: the first 8 updates, slowly, lighting the written slot
        for s in range(1, 9):
            self.play(t.animate.set_value(s), run_time=0.35, rate_func=linear)
            self.wait(0.15)

        # beat 3: too fast to follow slots, so dim the strip; pause at 50 where the curves have split
        strip.clear_updaters()
        self.play(t.animate.set_value(50), *[box.animate.set_stroke(style.RULE, width=style.STRUCTURE) for box, _ in strip],
                  *style.dim(*[lab for _, lab in strip]), run_time=1, rate_func=linear)
        callout = Text("every overwrite piles on: old + new", font_size=style.SMALL, color=style.BLUE).next_to(ax.c2p(10, 4), RIGHT, buff=0)
        self.play(Indicate(blue, color=style.BLUE), FadeIn(callout), run_time=1)
        self.wait(0.5)
        self.play(FadeOut(callout), run_time=0.3)
        self.play(t.animate.set_value(300), run_time=5, rate_func=linear)

        # beat 4: call out the result
        end_sum = MathTex(f"{err_sum[-1]:.2f}", font_size=45, color=style.BLUE).next_to(ax.c2p(300, err_sum[-1]), RIGHT, buff=0.25)
        end_delta = MathTex(f"{err_delta[-1]:.2f}", font_size=45, color=style.ORANGE).next_to(ax.c2p(300, err_delta[-1]), RIGHT, buff=0.25).shift(0.05 * UP)
        end_half = MathTex(f"{err_half[-1]:.2f}", font_size=45, color=style.ORANGE).next_to(end_delta, UP, buff=0.12)
        brace = Brace(VGroup(end_delta, end_half), RIGHT, buff=0.1, color=style.MUTED)
        slower = Text("lower β =\nslower overwrite", font_size=style.SMALL, color=style.INK).next_to(brace, RIGHT, buff=0.15)
        self.play(Write(end_sum), Write(end_delta), Write(end_half), GrowFromCenter(brace), FadeIn(slower), run_time=1.5)

        # beat 5: held final frame
        self.wait(2.8)
