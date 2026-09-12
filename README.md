# AI Surveillance

Professional construction-site safety dashboard around the supplied notebook.

## What the project contains

- `AI Surveliance Final notbook.ipynb`: the existing inference pipeline.
- `frontend/`: responsive dashboard, upload lab, result view, theme switcher, event history, and emergency UI.
- `backend/api.py`: FastAPI service and result normalizer.
- `backend/pipeline_adapter.py`: explicit integration point for the notebook pipeline.
- `frontend/assets/Alarm sound.mp3`: the supplied alarm audio, used by one centralized alarm manager.

The UI only represents the notebook-supported capabilities: PPE classes, fire/smoke, fight/violence, fallen/sitting/standing, ByteTrack worker tracking, and the SSIM structural heuristic. Explosion, blast, and gas-leak events are intentionally not claimed.

## Run the dashboard

From this folder:

```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.api:app --reload
```

Open `http://127.0.0.1:8000`.

The dashboard is fully navigable without the AI service. Until `AI_PIPELINE_MODULE` points at a real adapter, upload requests return a clear service-unavailable state rather than fake detections.

## Connect the notebook

The notebook currently defines `run_pipeline(path)` inside its kernel and is not an importable production service. Create a small Python module that loads the existing model/configuration functions and exposes that function, then run:

```powershell
$env:AI_PIPELINE_MODULE = "your_adapter_module"
python -m uvicorn backend.api:app --reload
```

The adapter may return the notebook's existing tuple `(annotated_output_path, event_log_dataframe)` or a dictionary with `output_path` and `event_log`. Event rows can use the notebook's current `event`, `detail`, `conf`, `frame`, and `time_s` fields; the API converts them to the frontend schema.

## Known limitation

The notebook is designed for an interactive Kaggle/Jupyter kernel, so the first API request lazily executes its existing import, model-loading, configuration, detection-helper, and pipeline cells in a persistent Python namespace. Model weights may take time to download on the first request. The models are not duplicated in the browser and the notebook file is not rewritten.