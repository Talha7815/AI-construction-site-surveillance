from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from types import SimpleNamespace


# Map every Kaggle path to our writable workdir
KAGGLE_MAP = {
    "/kaggle/working": None,   # filled in at runtime with self.workdir
    "/kaggle/input": None,
    "/kaggle": None,
}


def _rewrite_source(source: str, workdir: str) -> str:
    """Replace any /kaggle... path in notebook source with the workdir."""
    for kp in ("/kaggle/working", "/kaggle/input", "/kaggle"):
        source = source.replace(kp, workdir)
    return source


class NotebookRuntime:
    """Load the notebook's existing model and pipeline cells into one namespace."""

    PIPELINE_CELLS = (4, 6, 10, 12, 18)

    def __init__(self, notebook_path: Path, workdir: Path):
        self.notebook_path = notebook_path
        self.workdir = workdir
        self.namespace: dict[str, object] = {}
        self.lock = threading.RLock()
        self.ready = False

    def _patch_os(self) -> None:
        """Monkey-patch os.makedirs / os.path.exists to redirect /kaggle paths."""
        workdir_str = str(self.workdir)
        real_makedirs = os.makedirs
        real_exists = os.path.exists

        def safe_makedirs(name, *args, **kwargs):
            name_str = str(name)
            if name_str.startswith("/kaggle"):
                name_str = workdir_str
            return real_makedirs(name_str, *args, **kwargs)

        def safe_exists(path):
            path_str = str(path)
            if path_str.startswith("/kaggle"):
                path_str = workdir_str
            return real_exists(path_str)

        os.makedirs = safe_makedirs
        os.path.exists = safe_exists

        # Make sure the workdir itself exists
        real_makedirs(workdir_str, exist_ok=True)

    def start(self) -> None:
        with self.lock:
            if self.ready:
                return

            notebook = json.loads(self.notebook_path.read_text(encoding="utf-8"))
            cells = notebook.get("cells", [])
            workdir_str = str(self.workdir)

            self.namespace["__file__"] = str(self.notebook_path)
            self._patch_os()

            for index in self.PIPELINE_CELLS:
                source = "".join(cells[index].get("source", []))

                # Rewrite any hardcoded /kaggle path in the source itself
                source = _rewrite_source(source, workdir_str)

                exec(
                    compile(source, f"{self.notebook_path}:cell-{index}", "exec"),
                    self.namespace,
                )

                if index == 4:
                    self.namespace["WORKDIR"] = workdir_str

            self.ready = True

    def run(self, path: str):
        with self.lock:
            self.start()
            return self.namespace["run_pipeline"](path)


def create_runtime(notebook_path: Path, workdir: Path) -> SimpleNamespace:
    return SimpleNamespace(instance=NotebookRuntime(notebook_path, workdir))