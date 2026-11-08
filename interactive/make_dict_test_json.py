# Writes the dict_test data inlined in index.html as `const DICT` (paste its stdout there).
"""Precompute dict_test curves with the scene's exact RNG order (seed 1), for several beta. Run from the repo root."""
import json, sys
import numpy as np
from deltanet import unit

BETAS = [0.1, 0.25, 0.5, 0.75, 1.0]
rng = np.random.default_rng(1)
d, n_keys, steps = 128, 8, 300
keys = unit(rng.normal(size=(n_keys, d)))
truth = np.zeros((n_keys, d))
S_sum, S_d = np.zeros((d, d)), {b: np.zeros((d, d)) for b in BETAS}
out = {"idx": [], "sum": [], "delta": {str(b): [] for b in BETAS}}
rel = lambda S, seen: np.mean(np.linalg.norm((keys @ S - truth)[seen], axis=1) / np.linalg.norm(truth[seen], axis=1))
for _ in range(steps):
    i = rng.integers(n_keys)
    k, v = keys[i], rng.normal(size=d)
    truth[i] = v
    S_sum += np.outer(k, v)
    for b in BETAS:
        S_d[b] += b * np.outer(k, v - S_d[b].T @ k)
    out["idx"].append(int(i))
    seen = np.abs(truth).sum(1) > 0
    out["sum"].append(round(float(rel(S_sum, seen)), 3))
    for b in BETAS:
        out["delta"][str(b)].append(round(float(rel(S_d[b], seen)), 3))
assert f"{out['sum'][-1]:.2f}" == "6.19" and f"{out['delta']['1.0'][-1]:.2f}" == "0.19"
assert out["idx"][:8] == [4, 7, 7, 2, 7, 5, 3, 7]
json.dump(out, sys.stdout, separators=(",", ":"))
