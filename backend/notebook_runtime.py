from __future__ import annotations

import json
import threading
from pathlib import Path
from types import SimpleNamespace


class NotebookRuntime:
    """Load the notebook's existing model and pipeline cells into one namespace."""

    # Notebook cells: imports, model loading, configuration, detection helpers, pipeline.
    PIPELINE_CELLS = (4, 6, 10, 12, 18)

    def __init__(self, notebook_path: Path, workdir: Path):
        self.notebook_path = notebook_path
        self.workdir = workdir
        self.namespace: dict[str, object] = {}
        self.lock = threading.RLock()
        self.ready = False

    def start(self) -> None:
        with self.lock:
            if self.ready:
                return
            notebook = json.loads(self.notebook_path.read_text(encoding="utf-8"))
            cells = notebook.get("cells", [])
            self.namespace["__file__"] = str(self.notebook_path)
            for index in self.PIPELINE_CELLS:
                source = "".join(cells[index].get("source", []))
                if index == 4:
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