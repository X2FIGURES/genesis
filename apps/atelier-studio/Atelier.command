#!/usr/bin/env bash
# Double-click on macOS Finder to open Atelier Studio locally.
cd "$(dirname "$0")"
./scripts/setup-local.sh
exec ./scripts/run-atelier.sh
