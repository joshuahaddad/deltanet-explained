"""Linear attention and DeltaNet in a few lines of NumPy.

One head, one sequence, no batching: the point is the update rule, not speed.
Run this file to check the claims the article makes.
"""
import numpy as np


def linear_attention(q, k, v):
    """Running sum: S_t = S_{t-1} + k_t v_tᵀ, read with o_t = S_tᵀ q_t."""
    S = np.zeros((k.shape[1], v.shape[1]))
    out = []
    for q_t, k_t, v_t in zip(q, k, v):
        S = S + np.outer(k_t, v_t)
        out.append(S.T @ q_t)
    return np.array(out), S


def linear_attention_parallel(q, k, v):
    """The same outputs as one masked matrix product, which is how it trains in parallel."""
    return np.tril(q @ k.T) @ v


def deltanet(q, k, v, beta):
    """Delta rule: read what k currently returns, then write only the difference.

    S_t = S_{t-1} + β_t k_t (v_t − S_{t-1}ᵀ k_t)ᵀ
    """
    S = np.zeros((k.shape[1], v.shape[1]))
    out = []
    for q_t, k_t, v_t, b_t in zip(q, k, v, beta):
        S = S + b_t * np.outer(k_t, v_t - S.T @ k_t)
        out.append(S.T @ q_t)
    return np.array(out), S


def unit(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


def check():
    rng = np.random.default_rng(0)
    T, d = 12, 8
    q, k, v = rng.normal(size=(3, T, d))
    k = unit(k)

    # 1. Linear attention: the RNN form and the parallel form give the same outputs.
    rec, _ = linear_attention(q, k, v)
    assert np.allclose(rec, linear_attention_parallel(q, k, v))

    # 2. Write the same pair n times: the sum returns n·v, the delta rule returns v.
    n, key, val = 50, k[:1].repeat(50, 0), v[:1].repeat(50, 0)
    _, S_sum = linear_attention(q[:1].repeat(n, 0), key, val)
    _, S_delta = deltanet(q[:1].repeat(n, 0), key, val, np.ones(n))
    assert np.allclose(S_sum.T @ k[0], n * v[0])
    assert np.allclose(S_delta.T @ k[0], v[0])

    # 3. A delta-rule write is one gradient step on L(S) = ½‖Sᵀk − v‖² with learning rate β.
    S, beta = rng.normal(size=(d, d)), 0.3
    loss = lambda S: 0.5 * np.sum((S.T @ k[0] - v[0]) ** 2)
    eps, grad = 1e-6, np.zeros_like(S)
    for i in range(d):
        for j in range(d):
            E = np.zeros_like(S)
            E[i, j] = eps
            grad[i, j] = (loss(S + E) - loss(S - E)) / (2 * eps)
    delta_write = S + beta * np.outer(k[0], v[0] - S.T @ k[0])
    assert np.allclose(delta_write, S - beta * grad, atol=1e-6)

    print("ok: parallel == recurrent, sum gives n·v, delta gives v, delta write == gradient step")


if __name__ == "__main__":
    check()
