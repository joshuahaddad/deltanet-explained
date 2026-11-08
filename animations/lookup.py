"""Attention is a dict lookup where every key matches a little, over a KV cache that grows per token."""
import numpy as np
from manim import *
import style

TOKENS = ["my", "cat", "sat", "on", "a", "mat"]
K = np.array([[0, 1], [2, 1], [1, 0], [-1, 0], [0, -1], [1, 2]])
Q5, Q6 = np.array([1, 0.5]), np.array([0.5, 1])
YS = [1.85, 1.13, 0.41, -0.31, -1.03, -1.75]


def softmax(s):
    e = np.exp(s)
    return e / e.sum()


S5, S6 = K[:5] @ Q5, K @ Q6
W5, W6 = softmax(S5), softmax(S6)

# storyboard check values
assert np.allclose(S5, [0.5, 2.5, 1, -1, -0.5]) and np.allclose(S6, [1, 2, 0.5, -0.5, -1, 2.5])
assert [f"{w:.2f}" for w in W5] == ["0.09", "0.70", "0.16", "0.02", "0.03"]
assert [f"{w:.2f}" for w in W6] == ["0.11", "0.30", "0.07", "0.02", "0.01", "0.49"]
assert W5.argmax() == 1 and W6.argmax() == 5


M = 1.5 * style.SMALL  # MathTex draws about 1.5x smaller than Text at the same font_size


def tex(s, x, y, color=style.INK, size=M):
    return MathTex(s, font_size=size, color=color).move_to([x, y, 0])


def text(s, x, y, color=style.INK, size=style.SMALL):
    return Text(s, font_size=size, color=color).move_to([x, y, 0])


def left_at(mob, x, y):
    return mob.move_to([x, y, 0], aligned_edge=LEFT)


def title_text(s):  # BODY, not TITLE: at 48 the B3 title runs into the query
    return left_at(Text(s, font_size=style.BODY, color=style.INK), -6.5, 3.45)


def cache_box(last_y):
    return RoundedRectangle(corner_radius=0.15, width=4.1, height=2.95 - (last_y - 0.4), stroke_width=style.STRUCTURE,
                            color=style.MUTED, fill_color=style.SURFACE, fill_opacity=1
                            ).move_to([-4.35, (2.95 + last_y - 0.4) / 2, 0])


def bars(w):  # drawn from the unrounded weights; 4 units = weight 1
    return VGroup(*[left_at(Rectangle(width=max(4 * wi, 1e-3), height=0.42, stroke_width=0, fill_color=style.BLUE,
                                      fill_opacity=style.BAR_OPACITY if wi > 0 else 0), 0.2, y)
                    for wi, y in zip(w, YS)])


def weights(w):
    return VGroup(*[tex(f"{wi:.2f}"[1:], 5.0, y) for wi, y in zip(w, YS)])


def scores(s):
    return VGroup(*[tex(f"{si:g}", -1.2, y, style.BLUE) for si, y in zip(s, YS)])


def new_query(q):  # right-aligned so the long title fits
    return tex(rf"q = [{q[0]:g},\ {q[1]:g}]", 0, 3.45, style.BLUE).move_to([6.6, 3.45, 0], aligned_edge=RIGHT)


class Lookup(Scene):
    def construct(self):
        title = title_text("dict: exact match")
        query = Text('memory["cat"]', font_size=style.BODY, color=style.BLUE).move_to([6.6, 3.45, 0], aligned_edge=RIGHT)
        rows = [VGroup(text(TOKENS[i], -5.6, y), tex(rf"[{K[i, 0]},\ {K[i, 1]}]", -4.2, y),
                       tex(f"v_{i + 1}", -2.9, y)) for i, y in enumerate(YS)]
        heads = VGroup(text("token", -5.6, 2.65), tex("k", -4.2, 2.65), tex("v", -2.9, 2.65))
        box = cache_box(YS[4])
        label = text("KV cache: 5 tokens", 0, 0, style.MUTED).next_to(box, DOWN, buff=0.35)
        self.add(title, query, box, heads, label, *rows[:5])

        # B1: exact match
        self.wait(0.5)
        match = style.box(rows[1]).set_stroke(style.TARGET)  # the one exact hit, so target rather than plum
        others = [rows[i] for i in (0, 2, 3, 4)]
        self.play(Create(match), *style.dim(*others), run_time=0.6)
        w_head = tex("w", 2.2, 2.65)
        one_hot = np.eye(5)[1]
        b = bars(one_hot)
        nums = VGroup(*[tex("1" if h else "0", 5.0, y, style.INK if h else style.MUTED) for h, y in zip(one_hot, YS)])
        self.play(FadeIn(w_head), GrowFromEdge(b, LEFT), FadeIn(nums), run_time=0.8)
        out = VGroup(Text('memory["cat"]', font_size=style.SMALL, color=style.INK),
                     MathTex(r"\rightarrow v_2", font_size=M, color=style.INK)).arrange(RIGHT).move_to([2.35, -2.9, 0])
        self.play(Write(out), run_time=0.5)
        self.wait(1.5)

        # B2: the same lookup, made soft; the newest token "a" makes the query
        self.play(Transform(title, title_text("attention: soft match")), Transform(query, new_query(Q5)),
                  FadeOut(out), FadeOut(match), VGroup(rows[0], rows[2], rows[3], rows[4][1:]).animate.set_color(style.INK),
                  rows[4][0].animate.set_color(style.BLUE), run_time=0.8)
        s_head, sc = tex(r"q\cdot k", -1.2, 2.65, style.BLUE), scores(S5)
        self.play(FadeIn(s_head), LaggedStart(*[Write(s) for s in sc], lag_ratio=0.25), run_time=0.8)
        self.play(Indicate(rows[1][1], color=style.BLUE), Indicate(sc[1], color=style.BLUE), run_time=0.5)
        b5, n5 = bars(W5), weights(W5)
        self.play(ReplacementTransform(w_head, tex(r"w = \mathrm{softmax}(q\cdot k)", 2.2, 2.65)),
                  ReplacementTransform(b, b5), ReplacementTransform(nums, n5), run_time=1.5)
        note = text("all > 0, sum = 1", 2.6, -1.45, size=style.BODY)
        top3 = np.argsort(-W5)[:3]  # the three biggest terms carry the blend; dots stand for the rest
        out5 = tex("o = " + " + ".join(rf"{W5[i]:.2f}\,v_{i + 1}"[1:] for i in top3) + r" + \dots", 2.35, -2.9)
        self.play(FadeIn(note), run_time=0.4)
        self.play(Write(out5), run_time=0.7)
        self.wait(1.5)

        # B3: generation appends one key and value, and the newest token reads them all (snappy: speed is the point)
        snap = dict(run_time=0.5, rate_func=style.SNAPPY)
        self.play(FadeOut(VGroup(sc, b5, n5, note, out5)), **snap)
        rows[5][1:].set_color(style.ORANGE)
        box6 = cache_box(YS[5])
        label6 = text("KV cache: 6 tokens", 0, 0, style.MUTED).next_to(box6, DOWN, buff=0.35)
        plus = text("+1 k, v", -1.2, YS[5], style.ORANGE)
        # stretch the box with the new row so the row never sits on the old label
        self.play(FadeIn(rows[5], shift=UP * 0.3), Transform(box, box6), Transform(label, label6), FadeIn(plus), **snap)
        self.play(Indicate(label, color=style.ORANGE), run_time=0.5)
        self.play(Transform(title, title_text("generating: newest token reads the cache")), Transform(query, new_query(Q6)),
                  FadeOut(plus), rows[4][0].animate.set_color(style.INK), rows[5][0].animate.set_color(style.BLUE),
                  run_time=0.6)
        sc6, b6, n6 = scores(S6), bars(W6), weights(W6)
        self.play(LaggedStart(*[Write(s) for s in sc6], lag_ratio=0.25), run_time=0.8)
        self.play(GrowFromEdge(b6, LEFT), FadeIn(n6), **snap)
        self.play(Write(tex(r"o = \textstyle\sum_i w_i\, v_i", 2.35, -2.9)), **snap)
        self.wait(1.5)

        # B4: the bottleneck
        self.play(Write(text("Every new token adds a key and value, and reads them all.", 0, -3.55)), run_time=1.0)
        self.wait(3)
