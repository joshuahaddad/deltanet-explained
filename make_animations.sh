#!/usr/bin/env bash
# Render animations/<name>.py to figures/<name>.gif with figure-kit (style, fonts and GIF pipeline in one image).
#   ./make_animations.sh          # every scene
#   ./make_animations.sh lookup   # just animations/lookup.py
# Needs Docker. Set FIGURE_KIT=~/writing-repos/figure-kit to build from a local checkout.
set -euo pipefail
cd "$(dirname "$0")"
TAG=v0.1.0
KIT=${FIGURE_KIT:-https://github.com/joshuahaddad/figure-kit.git#$TAG}
IMAGE=figure-kit:$TAG
docker image inspect $IMAGE >/dev/null 2>&1 || docker build --network host -t $IMAGE "$KIT"
docker run --rm -u "$(id -u):$(id -g)" -v "$PWD":/work $IMAGE render "$@"
