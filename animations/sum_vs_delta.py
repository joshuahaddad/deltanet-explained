"""k holds v1; write k -> v2 ten times: the plain sum's error grows, the delta rule halves it every write."""
import numpy as np
from manim import *
import style

for cls in (Text, MathTex, DecimalNumber):
    cls.set_default(color=style.INK)
MATH = round(1.5 * style.SMALL)  # MathTex draws ~1.5x smaller than Text

V1 = np.array([3.0, 1.0, 2.0, 1.5])
V2 = np.array([1.0, 3.0, 1.5, 2.5])
K = np.array([1.0, 0.0, 0.0, 0.0])
BETA, N = 0.5, 10

S_sum, S_delta = np.outer(K, V1), np.outer(K, V1)
read_sum, read_delta = [S_sum.T @ K], [S_delta.T @ K]
for _ in range(N):
    S_sum = S_sum + np.outer(K, V2)
    S_delta = S_delta + BETA * np.outer(K, V2 - S_delta.T @ K)
    read_sum.append(S_sum.T @ K)
    read_delta.append(S_delta.T @ K)
err_sum = [np.linalg.norm(V2 - r) for r in read_sum]
err = [np.linalg.norm(V2 - r) for r in read_delta]

# storyboard check values
for i in range(N + 1):
    assert np.allclose(read_sum[i], V1 + i * V2)
    assert i == 0 or np.isclose(err_sum[i], np.linalg.norm(V1 + (i - 1) * V2))
for i in range(N):
    assert np.isclose(err[i + 1], err[i] / 2)
assert [f"{e:.2f}" for e in err_sum[:4]] == ["3.04", "4.03", "7.76", "11.88"] and f"{err_sum[N]:.1f}" == "41.8"
assert f"{err[N]:.3f}" == "0.003"
assert np.allclose(read_delta[1], [2, 2, 1.75, 2]) and np.allclose(read_delta[2], [1.5, 2.5, 1.625, 2.25])
assert np.allclose(read_delta[3], [1.25, 2.75, 1.5625, 2.375])
assert [f"{e:.2f}" for e in err] == ["3.04", "1.52", "0.76", "0.38", "0.19", "0.10", "0.05", "0.02", "0.01", "0.01", "0.00"]

BASE, H, XS = -2.3, 1.1, [1.9, 3.1, 4.3, 5.5]


def bars(r):
    """Solid orange where the read and v2 agree; the error still to close is an orange outline, above or below."""
    fill = VGroup(*[Rectangle(width=0.8, height=H * min(v, t), color=style.ORANGE, fill_opacity=style.BAR_OPACITY, stroke_width=0)
                    .move_to([x, BASE + H * min(v, t) / 2, 0]) for x, v, t in zip(XS, r, V2)])
    gap = VGroup(*[Rectangle(width=0.8, height=max(H * abs(t - v), 1e-3), color=style.ORANGE, stroke_width=3)
                   .move_to([x, BASE + H * (t + v) / 2, 0]) for x, v, t in zip(XS, r, V2)])
    return VGroup(fill, gap)


class SumVsDelta(Scene):
    def construct(self):
        plain = MathTex(r"\text{plain sum: }", r"S \leftarrow S + k\,v^\top", font_size=MATH, color=style.BLUE).move_to([-3.6, 3.3, 0])
        delta = MathTex(r"\text{delta rule: }S \leftarrow S + ", r"\beta", r"\,k\,", r"(v - S^\top k)", r"^\top",
                        font_size=MATH, color=style.ORANGE).move_to([3.6, 3.3, 0])
        if delta.width > 6.4:
            delta.scale_to_fit_width(6.4)

        # left panel: the error of the read, both methods, on a log axis
        axes = Axes(x_range=[0, 10, 2], y_range=[-3, 2, 1], x_length=5.2, y_length=4.2, tips=False,
                    x_axis_config={"include_numbers": True, "font_size": 44},
                    y_axis_config={"scaling": LogBase()}).move_to([-3.0, -0.4, 0]).set_color(style.INK)
        axes.y_axis.add_labels({v: MathTex(f"{v:g}", font_size=MATH) for v in (0.01, 0.1, 1, 10, 100)})
        xlab = Text("writes", font_size=style.SMALL).next_to(axes.x_axis, DOWN, buff=0.15)
        ylab = MathTex(r"\|v - S^\top k\|\ \text{(log scale)}", font_size=MATH).next_to(axes.y_axis.get_top(), UP, buff=0.2)
        ylab.align_to(axes.y_axis.labels, LEFT)
        sum_lab = MathTex(r"v_1 + n\,v_2", color=style.BLUE, font_size=MATH).move_to(axes.c2p(3.6, 60))
        z = lambda c: 1 if c == style.ORANGE else 0  # orange sits on top of blue
        dot = lambda n, s, c: Dot(axes.c2p(n, s[n]), radius=0.07, color=c, z_index=z(c))
        seg = lambda n, s, c: Line(axes.c2p(n - 1, s[n - 1]), axes.c2p(n, s[n]), color=c, stroke_width=style.DATA, z_index=z(c))
        blue = VGroup(dot(0, err_sum, style.BLUE))
        orange = VGroup(dot(0, err, style.ORANGE))

        # right panel: the delta rule's read
        read = bars(read_delta[0])
        goal = VGroup(*[DashedVMobject(Rectangle(width=0.8, height=H * t, color=style.TARGET, stroke_width=4))
                        .move_to([x, BASE + H * t / 2, 0]) for x, t in zip(XS, V2)])
        baseline = Line([1.3, BASE, 0], [6.1, BASE, 0], color=style.INK, stroke_width=style.STRUCTURE)
        legend = VGroup(Square(0.25, color=style.ORANGE, fill_opacity=style.BAR_OPACITY, stroke_width=0), MathTex(r"S^\top k", font_size=MATH),
                        DashedVMobject(Square(0.25, color=style.TARGET, stroke_width=4), num_dashes=8), MathTex("v_2", font_size=MATH),
                        Square(0.25, color=style.ORANGE, stroke_width=3), MathTex(r"v - S^\top k", font_size=MATH))
        legend.arrange(RIGHT, buff=0.15).move_to([3.7, -2.85, 0])
        legend[2:].shift(0.3 * RIGHT)
        legend[4:].shift(0.3 * RIGHT)
        num = DecimalNumber(err[0], num_decimal_places=2, font_size=MATH, color=style.ORANGE)
        readout = VGroup(MathTex(r"\|v - S^\top k\| =", font_size=MATH, color=style.ORANGE), num).arrange(RIGHT, buff=0.15).move_to([3.7, -3.55, 0])
        caption = lambda n: (Text(f"after {n} write" + "s" * (n > 1), font_size=style.BODY) if n else
                             MathTex(r"k \text{ holds } v_1.\ \text{Write } k \to v_2", font_size=round(1.5 * style.BODY))
                             .scale_to_fit_width(6.0)).move_to([3.7, 1.75, 0])
        counter = caption(0)
        veil = Rectangle(width=6.2, height=5.9, fill_color=style.BG, fill_opacity=0.75, stroke_width=0, z_index=5).move_to([3.7, -1.0, 0])

        self.add(plain, delta, axes, xlab, ylab, sum_lab, blue, orange, baseline, read, goal, legend, readout, counter)
        self.wait(1.0)

        def write(n, t, hold, do_sum, do_delta, *extra):
            anims = list(extra)
            if do_sum:
                blue.add(piece := VGroup(seg(n, err_sum, style.BLUE), dot(n, err_sum, style.BLUE)))
                anims.append(Create(piece))
            if do_delta:
                orange.add(piece := VGroup(seg(n, err, style.ORANGE), dot(n, err, style.ORANGE)))
                num.set_value(err[n])  # numbers jump at the write's first frame, so any still frame pairs them right
                counter.become(caption(n))
                anims += [Create(piece), Transform(read, bars(read_delta[n]))]
            self.play(*anims, run_time=t)
            self.wait(hold)

        # 1. plain sum
        self.play(FadeIn(veil), *style.dim(delta, orange), run_time=0.4)
        box = style.box(plain[1])
        self.play(Create(box), run_time=0.3)
        write(1, 0.6, 0.2, True, False)
        write(2, 0.6, 0.2, True, False)
        write(3, 0.6, 0.2, True, False, Indicate(sum_lab, color=style.BLUE))
        self.play(FadeOut(box), run_time=0.3)

        # 2. delta rule
        self.play(FadeOut(veil), delta.animate.set_color(style.ORANGE), orange.animate.set_color(style.ORANGE),
                  *style.dim(plain, blue), run_time=0.4)
        box = style.box(delta[3])
        self.play(Create(box), read[1].animate(rate_func=there_and_back).set_stroke(width=8), run_time=0.8)
        write(1, 1.0, 0.5, False, True)
        for n in (2, 3):
            write(n, 0.6, 0.3, False, True)
        self.play(FadeOut(box), run_time=0.3)

        # 3. both together
        self.play(plain.animate.set_color(style.BLUE), blue.animate.set_color(style.BLUE), run_time=0.3)
        for n in range(4, N + 1):
            write(n, 0.3, 0.15, True, True)
        ends = VGroup(MathTex(f"{err_sum[N]:.1f}", font_size=MATH, color=style.BLUE).next_to(blue[-1][1], RIGHT, buff=0.12),
                      MathTex(f"{err[N]:.3f}", font_size=MATH, color=style.ORANGE).next_to(orange[-1][1], RIGHT, buff=0.12))

        # 4. the gradient
        grad = MathTex(r"= S - ", r"\beta", r"\,\nabla_S L,\quad L = \tfrac12\|S^\top k - v\|^2", font_size=MATH).move_to([3.6, 2.5, 0])
        if grad.width > 6.6:
            grad.scale_to_fit_width(6.6)
        self.play(FadeIn(ends), Write(grad), run_time=0.8)
        self.play(Indicate(delta[1], color=style.ORANGE), Indicate(grad[1], color=style.ORANGE), run_time=0.5)

        # 5. hold
        self.wait(3.0)
