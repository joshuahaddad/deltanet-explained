#!/usr/bin/env bash
# Render the Manim animations in animations/ to figures/<name>.gif.
# Needs Docker: Manim, LaTeX and the style's fonts live in the image built from ./Dockerfile.
#   ./make_animations.sh          # every scene
#   ./make_animations.sh lookup   # just animations/lookup.py
set -euo pipefail
cd "$(dirname "$0")"
IMAGE=deltanet-manim:style
# Build the image once; --network host because the default build network could not reach the TeX mirror.
docker image inspect "$IMAGE" >/dev/null 2>&1 || docker build --network host -t "$IMAGE" - < Dockerfile
names=("$@")
[ ${#names[@]} -eq 0 ] && names=($(cd animations && ls *.py | sed 's/\.py$//' | grep -vx style))
for n in "${names[@]}"; do
  # Render lossless PNG frames, then build the GIF ourselves (see frames_to_gif.py).
  rm -rf ".media/images/$n"
  docker run --rm --user "$(id -u):$(id -g)" -v "$PWD":/manim -w /manim/animations "$IMAGE" bash -c "
    manim -qm --format png --media_dir /manim/.media $n.py &&
    python /manim/frames_to_gif.py /manim/.media/images/$n /manim/figures/$n.gif"
  echo "wrote figures/$n.gif ($(du -h figures/$n.gif | cut -f1))"
done
