##"""Runtime adapter for the existing notebook pipeline."""

#import os
#from pathlib import Path

#from .notebook_runtime import create_runtime

#ROOT = Path(__file__).resolve().parent.parent
#NOTEBOOK = Path(os.getenv("AI_NOTEBOOK_PATH", ROOT / "AI Surveliance Final notbook.ipynb"))
#WORKDIR = Path(os.getenv("AI_WORKDIR", ROOT / "backend" / "outputs"))
#WORKDIR.mkdir(parents=True, exist_ok=True)
#RUNTIME = create_runtime(NOTEBOOK, WORKDIR)


#def run_pipeline(path: str):
  #  return RUNTIME.instance.run(path)
def run_pipeline(path):
    return run_pipeline(path) 
