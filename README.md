# DeltaNet, explained

Companion to the post *DeltaNet: Attention That Overwrites Instead of Piling Up*.

- `deltanet.py`: linear attention and DeltaNet in about 30 lines of NumPy, plus checks for the post's claims.
- `make_figures.py`: makes the figures in `figures/`.
- `interactive/index.html`: the interactive version of the figures. Open it in a browser.

## Run

Needs [uv](https://docs.astral.sh/uv/).

```bash
uv run make_figures.py
```

This checks the claims, then writes the figures:

- the RNN form and the parallel form of linear attention give the same outputs
- writing the same pair n times: the plain sum returns n·v, the delta rule returns v
- one delta-rule write equals one gradient step on ½‖Sᵀk − v‖²
- the dict test: the plain sum's error keeps growing, the delta rule's stays small

## The two update rules

```python
S = S + np.outer(k, v)                       # linear attention: add
S = S + beta * np.outer(k, v - S.T @ k)      # DeltaNet: read, then write the difference
```

## Papers

- Kimi Linear: An Expressive, Efficient Attention Architecture. [arXiv:2510.26692](https://arxiv.org/abs/2510.26692)
- Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention. [arXiv:2605.22791](https://arxiv.org/abs/2605.22791)
