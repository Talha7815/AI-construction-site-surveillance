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

    st.subheader("Original input")
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        st.image(tmp_path, use_container_width=True)
    else:
        st.video(tmp_path)

    if st.button("Run AI Analysis", type="primary"):
        with st.spinner("Running inference... this may take a minute."):
            try:
                result = run_pipeline(tmp_path)

                st.success("Analysis complete")

                # --- Extract the output file path from the pipeline result ---
                output_file = None

                # Case 1: result is a tuple like (path, dataframe)
                if isinstance(result, tuple) and len(result) > 0:
                    first = result[0]
                    if isinstance(first, str):
                        output_file = first
                    elif isinstance(first, (list, tuple)) and len(first) > 0:
                        output_file = str(first[0])

                # Case 2: result is a dict
                elif isinstance(result, dict):
                    for key in ("output_video", "output_image", "annotated", "video", "image", "path", "output"):
                        if key in result and result[key]:
                            output_file = str(result[key])
                            break

                # Case 3: result is a plain string
                elif isinstance(result, str):
                    output_file = result

                # --- Display the annotated output ---
                if output_file:
                    out_path = Path(output_file)
                    if not out_path.is_absolute():
                        out_path = ROOT / out_path

                    st.subheader("Annotated output (with detection boxes)")

                    if out_path.exists():
                        ext = out_path.suffix.lower()
                        if ext in {".mp4", ".mov", ".avi", ".mkv", ".webm"}:
                            st.video(str(out_path))
                            with open(out_path, "rb") as f:
                                st.download_button(
                                    "⬇ Download annotated video",
                                    f,
                                    file_name=out_path.name,
                                    mime="video/mp4",
                                )
                        else:
                            st.image(str(out_path), use_container_width=True)
                            with open(out_path, "rb") as f:
                                st.download_button(
                                    "⬇ Download annotated image",
                                    f,
                                    file_name=out_path.name,
                                    mime="image/jpeg",
                                )
                    else:
                        st.warning(f"Output file not found: {out_path}")
                else:
                    st.info("Could not find annotated output path in pipeline result.")

                # --- Show the raw result log ---
                with st.expander("Show raw pipeline result / event log"):
                    st.write(result)

            except Exception as exc:
                st.error("Analysis failed")
                st.exception(exc)