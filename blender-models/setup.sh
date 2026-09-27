#!/usr/bin/env bash
# Installs Blender as a Python module (bpy) plus mesh helpers.
# bpy 5.x wheels need Python 3.11.
set -e
PY=${PYTHON:-python3.11}
"$PY" -m pip install "bpy>=5.0,<6" trimesh numpy
"$PY" -c "import bpy; print('Blender', bpy.app.version_string, 'ready')"
