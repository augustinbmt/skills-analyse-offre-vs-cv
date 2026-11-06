#!/usr/bin/env bash
set -euo pipefail
FIX="$(cd "$(dirname "$0")/../fixtures" && pwd)"
cp "$FIX/cv-piege.pdf" ./
