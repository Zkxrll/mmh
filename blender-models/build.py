"""
Build one or more model scripts into Roblox-ready files.

    python3 build.py models/tree.py            # -> out/tree/
    python3 build.py models/*.py               # build everything
    python3 build.py models/tree.py --no-render

Each model script defines   build(rbx)   and optionally
    NAME = "tree"        (defaults to the file name)
    JOIN = True          (False = keep parts as separate MeshParts)
"""

import importlib.util
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import rbx  # noqa: E402


def build_one(path, render=True):
    spec = importlib.util.spec_from_file_location("model", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    name = getattr(mod, "NAME", os.path.splitext(os.path.basename(path))[0])
    outdir = os.path.join(HERE, "out", name)
    t = time.time()
    rbx.reset()
    mod.build(rbx)
    rbx.export(name, outdir, join_all=getattr(mod, "JOIN", True), render=render)
    print(f"built {name} in {time.time() - t:.1f}s -> {os.path.relpath(outdir, HERE)}\n")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    for p in args:
        build_one(p, render="--no-render" not in sys.argv)
