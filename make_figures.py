"""Make the article's figures into figures/. Run: uv run make_figures.py"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

from deltanet import check, unit

OUT = Path(__file__).parent / "figures"
ORANGE, BLUE, GREY = "#E0A030", "#4678E6", "#888888"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})


V1 = np.array([3.0, 1.0, 2.0, 1.5])  # a toy 4-number value for k₁ (orange)
V2 = np.array([1.0, 3.0, 1.5, 2.5])  # and one for k₂ (blue)
DIMS = np.arange(4)


def memory():
    """KV cache per head grows with tokens; the linear-attention state does not."""
    n = np.logspace(2, 6, 200)
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.loglog(n, 256 * n, color=BLUE, lw=2.5, label="softmax attention: KV cache (256 numbers per token)")
    ax.loglog(n, np.full_like(n, 128 * 128), color=ORANGE, lw=2.5, label="linear attention / DeltaNet: one 128×128 state")
    ax.set(xlabel="tokens in context", ylabel="numbers stored per head")
    ax.annotate("25.6M at 100k tokens", (1e5, 2.56e7), (1.5e3, 4e7), arrowprops={"arrowstyle": "->", "color": GREY})
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "memory.png", dpi=150)
    plt.close(fig)


def crosstalk():
    """Store k1→v1 and k2→v2 in one matrix, read with k1, rotate k2 toward k1."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.4, 3.2), gridspec_kw={"width_ratios": [1, 1.3]})
    angles = np.r_[np.linspace(90, 0, 30), np.zeros(8)]

    def frame(i):
        a = np.radians(angles[i])
        c = np.cos(a)
        ax1.clear()
        ax1.set_axis_off()
        ax1.set(xlim=(-1.2, 1.2), ylim=(-0.3, 1.2), aspect="equal")
        ax1.arrow(0, 0, 1, 0, color=ORANGE, width=0.03, length_includes_head=True)
        ax1.arrow(0, 0, np.cos(a), np.sin(a), color=BLUE, width=0.03, length_includes_head=True)
        ax1.text(1.02, -0.15, "k₁", color=ORANGE)
        ax1.text(np.cos(a) - 0.25, np.sin(a) + 0.05, "k₂", color=BLUE)
        ax1.set_title(f"k₁·k₂ = {c:.2f}")
        ax2.clear()
        ax2.bar(DIMS - 0.2, V1, 0.35, color=ORANGE, label="stored for k₁ (v₁)")
        ax2.bar(DIMS + 0.2, V1, 0.35, color=ORANGE, alpha=0.55)
        ax2.bar(DIMS + 0.2, c * V2, 0.35, bottom=V1, color=BLUE, label="crosstalk from k₂")
        ax2.set(ylim=(0, 6.5), xticks=[], title="what reading with k₁ returns (right bars)")
        ax2.legend(frameon=False, fontsize=9, loc="upper left")

    FuncAnimation(fig, frame, frames=len(angles)).save(OUT / "crosstalk.gif", writer=PillowWriter(fps=8))
    plt.close(fig)


def sum_vs_delta():
    """k stores v1; write 'k → v2' again and again into both memories."""
    beta, n = 0.5, 10
    plain, delta = [V1], [V1]
    for _ in range(n):
        plain.append(plain[-1] + V2)                       # S += k vᵀ
        delta.append(delta[-1] + beta * (V2 - delta[-1]))  # S += β k (v − Sᵀk)ᵀ
    size = lambda rs: [np.linalg.norm(r) / np.linalg.norm(V2) for r in rs]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.4, 3.2))

    def frame(i):
        ax1.clear()
        ax1.bar(DIMS, delta[i], 0.6, color=ORANGE, label="delta rule reads")
        ax1.bar(DIMS, V2, 0.6, fill=False, edgecolor="black", lw=1.5, label="new value (target)")
        ax1.set(ylim=(0, 4.5), xticks=[], title=f"after {i} writes (β = {beta})")
        ax1.legend(frameon=False, fontsize=9, loc="upper left")
        ax2.clear()
        ax2.plot(size(plain[: i + 1]), "o-", color=BLUE, label="plain sum")
        ax2.plot(size(delta[: i + 1]), "o-", color=ORANGE, label="delta rule")
        ax2.set(xlim=(-0.5, n + 0.5), ylim=(0, 12), xticks=range(0, n + 1, 2), xlabel="writes", title="size of what k reads\n(1.0 = the new value)")
        ax2.legend(frameon=False, fontsize=9, loc="upper left")
        fig.tight_layout()

    frames = list(range(n + 1)) + [n] * 6
    FuncAnimation(fig, lambda j: frame(frames[j]), frames=len(frames)).save(
        OUT / "sum_vs_delta.gif", writer=PillowWriter(fps=2))
    plt.close(fig)


def dict_test():
    """A dict with 8 keys gets 300 random updates. Can each memory return every key's latest value?"""
    rng = np.random.default_rng(1)
    d, n_keys, steps = 128, 8, 300  # 128 = the head size used in Kimi Linear
    keys = unit(rng.normal(size=(n_keys, d)))
    truth = np.zeros((n_keys, d))
    S_sum, S_delta = np.zeros((d, d)), np.zeros((d, d))
    err_sum, err_delta = [], []
    rel = lambda S, seen: np.mean(np.linalg.norm((keys @ S - truth)[seen], axis=1) / np.linalg.norm(truth[seen], axis=1))
    for _ in range(steps):
        i = rng.integers(n_keys)
        k, v = keys[i], rng.normal(size=d)
        truth[i] = v
        S_sum += np.outer(k, v)
        S_delta += np.outer(k, v - S_delta.T @ k)  # β = 1: full overwrite
        seen = np.abs(truth).sum(1) > 0  # only score keys written so far
        err_sum.append(rel(S_sum, seen))
        err_delta.append(rel(S_delta, seen))
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.plot(err_sum, color=BLUE, lw=2, label="plain sum (linear attention)")
    ax.plot(err_delta, color=ORANGE, lw=2, label="delta rule (DeltaNet, β = 1)")
    ax.set(xlabel="updates written", ylabel="error reading latest values\n(1.0 = as big as the value)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "dict_test.png", dpi=150)
    plt.close(fig)
    return err_sum[-1], err_delta[-1]


if __name__ == "__main__":
    check()
    OUT.mkdir(exist_ok=True)
    memory()
    crosstalk()
    sum_vs_delta()
    e_sum, e_delta = dict_test()
    # the figure's claim, checked: the sum blows up, the delta rule stays small (leftover = crosstalk between keys)
    assert e_delta < 0.3 and e_sum > 3, (e_sum, e_delta)
    print(f"dict test final error: plain sum {e_sum:.2f}, delta rule {e_delta:.2f}")
    print("wrote", ", ".join(sorted(p.name for p in OUT.iterdir())))
