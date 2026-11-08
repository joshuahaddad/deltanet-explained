# Animation style

The series look, picked over three rounds of side-by-side comparisons. To reuse it, copy `animations/style.py`,
`frames_to_gif.py`, `make_animations.sh` and `Dockerfile`, then `import style` in each scene.

## Palette ("ink + plum accent")

| Role | Constant | Hex | Use |
|---|---|---|---|
| Background | `BG` | `#16141C` | the plate |
| Mat | `MAT` | `#1B1922` | 6 px band round the plate (added by `frames_to_gif.py`) |
| Surface | `SURFACE` | `#211E29` | cards, table bodies |
| Rule | `RULE` | `#2E2A38` | gridlines (deliberately faint) |
| Muted | `MUTED` (`GREY`) | `#8A8696` | context, dimmed items (5.2:1) |
| Ink | `INK` | `#ECEAF0` | text, outlines (15.3:1) |
| Primary, warm | `PRIMARY` (`ORANGE`) | `#E69F00` | the stored key, the delta rule (8.1:1) |
| Secondary, cool | `SECONDARY` (`BLUE`) | `#56B4E9` | the query, interference, the plain sum (7.9:1) |
| Accent, plum | `ACCENT` | `#CC79A7` | emphasis shapes only (6.0:1) |
| Target | `TARGET` (`GREEN`) | `#8FE8BE` | target / correct, usually dashed |
| Error | `ERROR` | `#F2795A` | wrong; always with a ✗ or a shape |

Ratios are against `BG`. Orange and sky are Okabe-Ito, so they survive colour blindness.

Rules:

- **Plum never carries data next to blue.** Lilac and plum against sky are nearly identical (ΔE about 2) for deuteranopes. Plum may draw a box, never a category.
- At most 2 meaning hues per frame, plus target or error.
- Pick fills from the palette, never `WHITE`. The plate is dark, so a white veil or gap shows up as a grey slab.
- Dim by swapping to `MUTED`, not with `set_opacity`. Opacity on dark turns orange brown and adds GIF shades.

## Type

- Text is CMU Serif (`Text`, `Paragraph`, `MarkupText` default to it). Maths is Euler (`eulervm` with Euler digits) through the default TeX template.
- Scale: `SMALL` 30, `BODY` 38, `TITLE` 48. Nothing under 30, since the GIF shrinks to about a third of its size on a phone.
- `MathTex` draws about 1.5× smaller than `Text` at the same `font_size`, so set maths at about 1.5× the text step.
- Set symbols in maths, even inside labels: CMU Serif has no subscript digits.

## Strokes and shapes

- Weights: data `DATA` 5, structure `STRUCTURE` 2, emphasis `EMPHASIS` 6.
- Arrows use stealth tips by default.
- Bars are solid (`BAR_OPACITY` 1.0; lower lets the plate darken orange to brown) with no outline. Dashed means target or "not yet".

## Emphasis

- Default: `style.box(m)`, a plum box with 6 px stroke and rounded corners.
- In crowded diagrams: `self.play(*style.dim(a, b, c))`, which swaps everything else to `MUTED`.
- No glows. Keep colour flashes to 3 or fewer per second.

## Motion

- Default: Manim's run_time 1 with `smooth`, then hold 1.5 s after each step.
- Go snappy (`style.SNAPPY` = `ease_out_cubic`, about 0.5 s) when a clip runs long, or when the speed-up is the point, for example the KV cache growing.
- 15 fps. Keep the total to 8–20 s, and make the last 2–3 s work as a still.

## Framing

`frames_to_gif.py` adds the frame to every GIF:

1. the 1280×720 plate;
2. a 6 px `MAT` band;
3. 14 px rounded corners.

Outside the radius is mat, never page colour, so the GIF reads as a card on both white and dark Substack pages. Scenes don't draw a frame.

## Build

`make_animations.sh` builds `deltanet-manim:style` from `Dockerfile` once. The image is Manim v0.19.0 plus `eulervm` and `fonts-cmu`. It renders PNG frames, and `frames_to_gif.py` turns them into a GIF with one shared palette, no dithering and the frame above.
