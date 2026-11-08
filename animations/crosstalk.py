"""Two pairs in one matrix: reading with k1 leaks (k1·k2)·v2 as k2 tilts toward k1."""
import numpy as np
from manim import *
import style

V1 = np.array([3.0, 1.0, 2.0, 1.5])
V2 = np.array([1.0, 3.0, 1.5, 2.5])
K1 = np.array([1.0, 0.0])
SCALE, BASE, O = 0.75, -2.6, np.array([-5.2, -2.15, 0])


def read_out(deg):
    k2 = np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg))])
    S = np.outer(K1, V1) + np.outer(k2, V2)
    return S.T @ K1, K1 @ k2


# storyboard check values
r, c = read_out(90)
assert abs(c) < 1e-9 and np.allclose(r, V1)
r, c = read_out(45)
assert f"{c:.2f}" == "0.71" and np.allclose(r.round(2), [3.71, 3.12, 3.06, 3.27])


class Crosstalk(Scene):
    def construct(self):
        theta = ValueTracker(90)
        c = lambda: read_out(theta.get_value())[1]

        eq = MathTex(r"S", "=", r"k_1 v_1^\top", "+", r"k_2 v_2^\top", font_size=style.BODY * 1.5, color=style.INK).move_to(UP * 3.25)
        eq[2].set_color(style.ORANGE)
        eq[4].set_color(style.BLUE)
        rd = MathTex(r"S^\top k_1", "=", r"v_1", r"(k_1\cdot k_1)", "+", r"v_2", r"(k_1\cdot k_2)",
                     font_size=style.BODY * 1.5, color=style.INK).move_to(UP * 2.15)
        fit = min(1, 12 / rd.width)  # keep the read line inside 12 units; summary uses the same scale
        rd.scale(fit)
        rd[2:4].set_color(style.ORANGE)
        rd[5:7].set_color(style.BLUE)

        # keys panel
        k1 = Arrow(O, O + 3 * RIGHT, buff=0, color=style.ORANGE)
        k1_lab = MathTex("k_1", font_size=style.SMALL * 1.5, color=style.ORANGE).next_to(k1.get_end(), DOWN, buff=0.15)
        tip = lambda: O + 3 * np.array([np.cos(np.radians(theta.get_value())), np.sin(np.radians(theta.get_value())), 0])
        k2 = always_redraw(lambda: Arrow(O, tip(), buff=0, color=style.BLUE))
        k2_lab = always_redraw(lambda: MathTex("k_2", font_size=style.SMALL * 1.5, color=style.BLUE)
                               .move_to(tip() + 0.35 * (tip() - O) / 3))
        right = RightAngle(Line(O, O + RIGHT), Line(O, O + UP), length=0.35, color=style.GREY)
        P = O + 0.22 * DOWN  # projection sits just under the k1 axis so k1 stays orange
        drop = always_redraw(lambda: DashedLine(tip(), [tip()[0], P[1], 0], color=style.GREY))
        proj = always_redraw(lambda: Line(P, P + (3 * c() + 1e-4) * RIGHT, color=style.BLUE, stroke_width=style.DATA))
        dot_lab = MathTex(r"k_1\cdot k_2 =", font_size=style.SMALL * 1.5, color=style.BLUE)
        dot_num = DecimalNumber(0, num_decimal_places=2, font_size=style.SMALL * 1.5, color=style.BLUE)
        k2_line = VGroup(dot_lab, dot_num).arrange(RIGHT, buff=0.15)
        k1_line = MathTex(r"k_1\cdot k_1 = 1", font_size=style.SMALL * 1.5, color=style.ORANGE)
        VGroup(k1_line, k2_line).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([-4.0, -3.3, 0])
        dot_num.add_updater(lambda m: m.set_value(c()))

        # read panel
        orange = VGroup(*[Rectangle(width=0.6, height=SCALE * v, color=style.ORANGE, fill_opacity=style.BAR_OPACITY,
                                    stroke_width=0).move_to([i, BASE + SCALE * v / 2, 0]) for i, v in enumerate(V1)])
        blue = always_redraw(lambda: VGroup(*[
            Rectangle(width=0.6, height=max(SCALE * c() * v, 1e-3), color=style.BLUE,
                      fill_opacity=style.BAR_OPACITY, stroke_width=0)
            .next_to(orange[i], UP, buff=0) for i, v in enumerate(V2)]))
        v1_lab = MathTex("v_1", font_size=style.SMALL * 1.5, color=style.ORANGE).next_to(orange[0], LEFT, buff=0.15)
        baseline = Line([-0.5, BASE, 0], [3.5, BASE, 0], color=style.GREY, stroke_width=style.STRUCTURE)
        read_lab = Tex(r"read with $k_1$", font_size=style.SMALL * 1.5, color=style.INK).move_to([1.5, -3.25, 0])

        # beat 1: full first frame
        self.add(eq, rd, k1, k1_lab, right, k1_line, k2_line, v1_lab, baseline, orange, read_lab, drop, proj, k2, k2_lab, blue)
        self.wait(1.5)

        # beat 2: the two terms
        obox = style.box(rd[2:4])
        bbox = style.box(rd[5:7])
        self.play(Create(obox), Indicate(orange, color=style.ORANGE, scale_factor=1.05),
                  Indicate(k1_line, color=style.ORANGE), run_time=0.8)
        self.play(Create(bbox), Indicate(k2_line, color=style.BLUE), run_time=0.8)

        # beat 3: tilt k2 toward k1
        eq.save_state()
        rd.save_state()
        self.play(FadeOut(obox), FadeOut(right), *style.dim(eq, rd[2:5]), run_time=0.5)
        self.play(theta.animate.set_value(45), run_time=6, rate_func=smooth)
        self.wait(0.5)
        r, cv = read_out(theta.get_value())
        assert f"{cv:.2f}" == "0.71" and np.allclose(r, V1 + cv * V2)

        # beat 4: name the leak
        label = Text("crosstalk", font_size=style.BODY, color=style.BLUE).set_y(blue[3].get_center()[1]).to_edge(RIGHT, buff=0.6)
        arrow = Arrow(label.get_left(), blue[3].get_right(), buff=0.1, color=style.BLUE, stroke_width=style.DATA)
        self.play(Write(label), GrowArrow(arrow), run_time=0.6)
        self.play(Indicate(blue, color=style.BLUE, scale_factor=1.05), Indicate(proj, color=style.BLUE), run_time=0.8)

        # beat 5: summary
        summary = MathTex("=", r"v_1", "+", f"{cv:.2f}", r"\,v_2", font_size=style.BODY * 1.5, color=style.INK).scale(fit)
        summary.align_to(rd[1], LEFT).set_y(1.1)
        summary[1].set_color(style.ORANGE)
        summary[3:5].set_color(style.BLUE)
        self.play(Restore(eq), Restore(rd), Write(summary), Transform(bbox, style.box(summary[3:5])),
                  run_time=1)
        self.wait(2)
