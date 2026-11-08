"""The series' eight questions as one still: what builds on what.
Part 1 (this post) is orange, Part 2 (next post) muted; the destination is ink."""
from manim import *
import style

# key: (label, sub-label, part)
NODES = {
    "rnn": ("RNN form", "no softmax", 1),
    "delta": ("Delta rule", "overwrites", 1),
    "grad": ("Gradient step", "write = learn", 1),
    "forget": ("Forget gate", "state decays", 2),
    "channel": ("Per-channel\ndecay", "Kimi Linear", 2),
    "split": ("Split erase\nand write", "Gated\nDeltaNet-2", 2),
    "chunk": ("Chunkwise\ntraining", "fast on GPUs", 2),
    "nope": ("No positional\nencoding", "recency\nfor free", 2),
}
EDGES = [("rnn", "delta"), ("delta", "grad"), ("delta", "forget"), ("forget", "channel"),
         ("channel", "split"), ("delta", "chunk"), ("forget", "nope")]
# 4 columns x 3 rows (row 0 at the top); the empty top-left cell holds the legend
X, Y = [-5.175, -1.725, 1.725, 5.175], [2.0, -0.3, -2.6]
GRID = {"rnn": (0, 1), "delta": (1, 1), "grad": (1, 0), "forget": (2, 1), "channel": (2, 0),
        "split": (3, 0), "chunk": (1, 2), "nope": (3, 1)}


def colour(k):
    return style.INK if k == "nope" else style.ORANGE if NODES[k][2] == 1 else style.MUTED


def card(k):
    name, sub, _ = NODES[k]
    lab = VGroup(Paragraph(*name.split("\n"), font_size=style.SMALL, color=style.INK, alignment="center"),
                 Paragraph(*sub.split("\n"), font_size=style.SMALL, color=style.ORANGE if NODES[k][2] == 1 else style.MUTED, alignment="center")).arrange(DOWN, buff=0.12)
    box = RoundedRectangle(width=3.1, height=lab.height + 0.45, corner_radius=0.12, fill_color=style.SURFACE, fill_opacity=1,
                           stroke_color=colour(k), stroke_width=style.DATA if k == "nope" else style.STRUCTURE)
    return VGroup(box, lab)


def direction(a, b):
    (ca, ra), (cb, rb) = GRID[a], GRID[b]
    return np.array([np.sign(cb - ca), np.sign(ra - rb), 0])


class MentalMap(Scene):
    def construct(self):
        cards = {k: card(k).move_to([X[c], Y[r], 0]) for k, (c, r) in GRID.items()}
        arrows = [Arrow(cards[a][0].get_edge_center(d := direction(a, b)), cards[b][0].get_edge_center(-d), buff=0.05,
                        stroke_width=style.STRUCTURE + 1, color=colour(b) if NODES[b][2] == 1 else style.MUTED,
                        tip_length=0.2, max_tip_length_to_length_ratio=0.6) for a, b in EDGES]
        legend = VGroup(Text("this post", font_size=style.SMALL, color=style.ORANGE),
                        Text("next post", font_size=style.SMALL, color=style.MUTED)).arrange(DOWN, buff=0.2).move_to([X[0], Y[0], 0])
        self.add(*arrows, *cards.values(), legend)
