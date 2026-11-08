# Manim v0.19.0 plus the style's fonts: Euler maths (eulervm) and CMU Serif text.
# Build: docker build --network host -t deltanet-manim:style - < Dockerfile (make_animations.sh does this once)
FROM manimcommunity/manim:v0.19.0
USER root
# TeX Live 2024 is frozen, so tlmgr must use the historic repo.
RUN tlmgr option repository https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/2024/tlnet-final \
 && tlmgr install eulervm \
 && apt-get update && apt-get install -y --no-install-recommends fonts-cmu && rm -rf /var/lib/apt/lists/* \
 && fc-cache -f
USER manimuser
