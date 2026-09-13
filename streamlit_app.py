import os
import sys
import tempfile
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("AI_NOTEBOOK_PATH", str(ROOT / "AI_Surveillance_Final_Notebook.ipynb"))
os.environ.setdefault("AI_WORKDIR", str(ROOT / "backend" / "outputs"))

st.set_page_config(page_title="AI Construction Site Surveillance", page_icon="🏗️", layout="wide")
st.title("🏗️ AI Construction Site Surveillance")

@st.cache_resource(show_spinner="Loading AI models...")
def load_pipeline():
    try:
        from backend.pipeline_adapter import run_pipeline
        return run_pipeline, None
    except Exception as exc:
        return None, str(exc)

run_pipeline, load_error = load_pipeline()

if load_error:
    st.error("Pipeline failed to load")
    st.code(load_error)
    st.stop()

st.success("Pipeline loaded")

uploaded = st.file_uploader(
    "Upload image or video",
    type=["jpg", "jpeg", "png", "webp", "mp4", "mov", "avi", "mkv"],
)

if uploaded is not None:
    suffix = Path(uploaded.name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        st.image(tmp_path, use_container_width=True)
    else:
        st.video(tmp_path)

    if st.button("Run AI Analysis", type="primary"):
        with st.spinner("Running inference..."):
            try:
                result = run_pipeline(tmp_path)
                st.success("Done")
                st.json(result if isinstance(result, dict) else {"result": str(result)})
            except Exception as exc:
                st.error("Analysis failed")
                st.exception(exc)