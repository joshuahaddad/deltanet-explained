# DeltaNet, explained

The companion repo for the post *DeltaNet: Attention That Overwrites Instead of Piling Up*.

- `deltanet.py`: linear attention and DeltaNet in about 30 lines of NumPy, with checks for the post's claims.
- `animations/`: the post's figures, one [Manim](https://www.manim.community/) scene per file. `style.py` holds the shared look, and `STYLE.md` describes it.
- `figures/`: the rendered GIFs.
- `interactive/index.html`: an interactive version you can play with in the browser ([live page](https://joshuahaddad.github.io/deltanet-explained/interactive/)).

## Run

Check the math (needs [uv](https://docs.astral.sh/uv/)):

```bash
uv run deltanet.py
```

This checks that:

- the RNN form and the parallel form of linear attention give the same outputs;
- writing the same pair n times returns n·v from the plain sum and v from the delta rule;
- one delta-rule write is one gradient step on ½‖Sᵀk − v‖².

Render the figures (needs Docker). The first run builds the image from `Dockerfile`: pinned Manim plus the style's fonts.

```bash
./make_animations.sh            # all of them
./make_animations.sh crosstalk  # just one
```

Each scene computes its numbers with NumPy and asserts them. The dict test, for example, checks the final errors of 6.19 for the plain sum and 0.19 for the delta rule.

## The two update rules

```python
S = S + np.outer(k, v)                       # linear attention: add
S = S + beta * np.outer(k, v - S.T @ k)      # DeltaNet: read, then write the difference
```

## Papers

- Kimi Linear: An Expressive, Efficient Attention Architecture. [arXiv:2510.26692](https://arxiv.org/abs/2510.26692)
- Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention. [arXiv:2605.22791](https://arxiv.org/abs/2605.22791)
