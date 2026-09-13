from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from types import SimpleNamespace


_KAGGLE_PATHS = ("/kaggle/working", "/kaggle/input", "/kaggle")


class NotebookRuntime:
    """Load the notebook's existing model and pipeline cells into one namespace."""

    PIPELINE_CELLS = (4, 6, 10, 12, 18)

    def __init__(self, notebook_path: Path, workdir: Path):
        self.notebook_path = notebook_path
        self.workdir = workdir
        self.namespace: dict[str, object] = {}
        self.lock = threading.RLock()
        self.ready = False

    def _patch_kaggle_paths(self) -> None:
        workdir_str = str(self.workdir)
        real_makedirs = os.makedirs

        def safe_makedirs(name, *args, **kwargs):
            name_str = str(name)
            if name_str.startswith("/kaggle"):
                name_str = workdir_str
            return real_makedirs(name_str, *args, **kwargs)

        os.makedirs = safe_makedirs

        for kp in _KAGGLE_PATHS:
            try:
                real_makedirs(kp, exist_ok=True)
            except PermissionError:
                pass

    def start(self) -> None:
        with self.lock:
            if self.ready:
                return
            notebook = json.loads(self.notebook_path.read_text(encoding="utf-8"))
            cells = notebook.get("cells", [])
            self.namespace["__file__"] = str(self.notebook_path)
            self._patch_kaggle_paths()
            for index in self.PIPELINE_CELLS:
                source = "".join(cells[index].get("source", []))
                if index == 4:
                    source = source.replace("/kaggle/working", str(self.workdir))
                    source = source.replace("/kaggle/input", str(self.workdir))
                    source = source.replace("/kaggle", str(self.workdir))
                    exec(compile(source, f"{self.notebook_path}:cell-{index}", "exec"), self.namespace)
                    self.namespace["WORKDIR"] = str(self.workdir)
                else:
                    exec(compile(source, f"{self.notebook_path}:cell-{index}", "exec"), self.namespace)
            self.ready = True

    def run(self, path: str):
        with self.lock:
            self.start()
            return self.namespace["run_pipeline"](path)


def create_runtime(notebook_path: Path, workdir: Path) -> SimpleNamespace:
    return SimpleNamespace(instance=NotebookRuntime(notebook_path, workdir))