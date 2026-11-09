#!/usr/bin/env bash
# ./qa/shoot.sh [page]: run qa/shoot.py in the pinned Playwright image. Screenshots land in qa/shots/.
set -euo pipefail
cd "$(dirname "$0")/.."
docker run --rm --network host -u "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD":/work -w /work \
  mcr.microsoft.com/playwright/python:v1.49.1-noble \
  sh -c 'pip install -q --user --disable-pip-version-check --no-warn-script-location playwright==1.49.1 && python qa/shoot.py "$@"' shoot "$@"
# The image ships the browsers, not the Python package; the package version must match the image tag.
