# 🏗️ AI-Based Construction Site Surveillance System

> **See. Detect. Respond.**
>
> An end-to-end, multi-model computer vision platform for construction-site safety monitoring, automated hazard detection, emergency alerting, worker tracking, and predictive risk analysis.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/Computer%20Vision-YOLOv8-111827)](https://github.com/ultralytics/ultralytics)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenCV](https://img.shields.io/badge/Vision-OpenCV-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![PyTorch](https://img.shields.io/badge/ML-PyTorch-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Hugging Face](https://img.shields.io/badge/Models-Hugging%20Face-FFD21E?logo=huggingface&logoColor=111827)](https://huggingface.co/)

---

## 📌 Overview

The **AI-Based Construction Site Surveillance System** is a practical, end-to-end computer vision solution designed to reduce the monitoring gap between a safety incident occurring and a human supervisor noticing it.

The system combines:

- Multiple pretrained YOLO-based detectors
- PPE compliance monitoring
- Fire and smoke detection
- Fight / physical altercation detection
- Fallen-worker detection
- ByteTrack-based worker tracking and headcount
- SSIM-based structural anomaly monitoring
- Annotated image/video generation
- Timestamped event logging
- Site risk scoring and analytics
- Visual and audible emergency alerts
- SMTP-based email notifications
- A professional web dashboard for non-technical site staff

The project was developed as two coordinated layers:

1. **AI inference pipeline** — developed and benchmarked in a GPU-enabled Kaggle/Jupyter environment.
2. **Web application** — a responsive monitoring dashboard with a FastAPI backend and frontend interface.

The system is designed around the principle:

> **Detect the event → classify its severity → preserve evidence → alert the responsible person → support human decision-making.**

---

## ✨ Key Capabilities

| Capability | Description | Implementation |
|---|---|---|
| 🦺 PPE Compliance | Detects worker PPE states such as helmet/vest compliance and violations | YOLOv8 |
| 🔥 Fire & Smoke | Detects visible fire and smoke events | YOLOv8n |
| 🥊 Fight / Violence | Detects physical altercation / fight classes | YOLOv8-nano |
| 🚑 Fallen Worker | Detects Fallen / Sitting / Standing worker states | YOLO-based pretrained model |
| 👷 Worker Headcount | Counts visible workers and tracks IDs across video | Worker class + ByteTrack |
| 🏗️ Structural Anomaly | Flags sudden large changes in scene structure | SSIM heuristic |
| 🚨 Emergency Alerts | Escalates critical events through UI, sound and email | Alert manager + SMTP |
| 📊 Risk Analytics | Aggregates recent safety events into a site risk view | Event-log analytics |
| 📁 Evidence | Produces annotated output and timestamped event records | OpenCV + Pandas |
| 🧪 Upload & Test | Lets users analyze images/videos from the dashboard | Frontend + FastAPI |

### Critical Event Types

The current emergency workflow treats the following as critical:

- Fire
- Fight / altercation
- Fallen or unresponsive worker
- Structural anomaly

Critical events can trigger:

1. A high-visibility dashboard alarm
2. An audible siren indicator
3. An email notification with an annotated screenshot and timestamp
4. Event-log entry for later analysis

Alert cooldown logic prevents a continuous incident from generating one notification per frame.

---

## 🖼️ Project Screenshots

### AI Processing Architecture

![AI Surveillance processing pipeline](docs/images/architecture-pipeline.png)

### AI Detection Lab

The dashboard provides an upload-and-test workflow where the original media can be compared with the AI-analyzed result, including detection confidence and severity information.

![AI Detection Lab](docs/images/dashboard-ai-detection-lab.png)

### Detection Output Examples

The current output visualization uses bounding boxes, labels, confidence scores, PPE status, and worker-count overlays.

![Detection outputs](docs/images/detection-outputs.png)

---

## 🧠 AI Detection Pipeline

The processing flow is approximately:

```text
Input Image / Video
        │
        ▼
FFmpeg Normalization
        │
        ▼
Frame Extraction
        │
        ├───────────────┬────────────────┬────────────────┬───────────────┐
        ▼               ▼                ▼                ▼               ▼
     PPE Model      Fire/Smoke       Fight Model      Fall Model      ByteTrack
        │               │                │                │               │
        └───────────────┴────────────────┴────────────────┴───────────────┘
                                      │
                                      ▼
                           Structural SSIM Monitor
                                      │
                                      ▼
                         Aggregation / Overlay Engine
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
             Annotated Output                    Event Log / Analytics
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      ▼
                            Alert / Notification Layercan use the notebook's current `event`, `detail`, `conf`, `frame`, and `time_s` fields; the API converts them to the frontend schema.

## Known limitation
🧩 Models & Data Sources

The project uses genuine pretrained checkpoints downloaded programmatically from Hugging Face.

Module	Model / Source	Notes
PPE	killuminati1/construction-ppe-yolov8	Construction PPE model with 19 classes; reported mAP50 ≈ 0.76
Fire / Smoke	rabahdev/fire-smoke-yolov8n	YOLOv8n fine-tuned on the D-Fire dataset; reported mAP50 ≈ 0.75
Fight / Violence	Musawer14/fight_detection_yolov8	Community-trained YOLOv8-nano model; no formally published benchmark
Fallen Worker	melihuzunoglu/human-fall-detection	Detects Fallen / Sitting / Standing; no formally published benchmark
Worker Tracking	ByteTrack using the PPE model's Worker class	Tracking/logic layer rather than a separate detector
Structural Anomaly	SSIM	Rule-based heuristic, not a trained collapse classifier
Transparency Note

The project deliberately distinguishes trained models from heuristic logic.

The structural/collapse detector is not a trained building-collapse model. It compares frames using Structural Similarity Index (SSIM) against a slowly adapting reference and flags large sudden drops.

This can also react to non-collapse changes such as a large vehicle moving through the scene. It should therefore be treated as a human-review tripwire, not a certified structural-collapse detector.

The fight and fallen-worker models are functional pretrained community models, but they do not have formally published benchmark metrics in the project documentation. They should be validated against site-specific footage before safety-critical deployment.

⚙️ System Architecture
1. Input

The current application accepts:

Image files
Video files

Live RTSP/IP-camera ingestion is identified as a future extension.

2. Video Normalization

FFmpeg is used to normalize uploaded footage and improve compatibility across different video codecs and containers.

Annotated video is encoded using H.264 for reliable browser/media-player playback.

3. Parallel AI Inference

The pipeline evaluates frames through the available detection modules:

PPE
Fire / smoke
Fight / violence
Fallen worker
Worker tracking
Structural anomaly heuristic
4. Aggregation

Detection results are combined into a common event representation.

The overlay engine can draw:

Bounding boxes
Detection labels
Confidence scores
PPE status
Worker-count HUD
Critical-event banners
5. Event Logging

Events are stored in a structured timestamped table/CSV with fields such as:

frame
time_s
event
detail
conf

The FastAPI layer can normalize these notebook events into the frontend's event schema.

6. Alerting

Critical events enter the alert workflow, which supports:

Dashboard alert
Audible alarm indicator
Email notification
Annotated screenshot evidence
Timestamped event record
Per-event cooldown
🖥️ Frontend Dashboard

The web application is organized into three main areas.

Monitor
Dashboard
Live Monitoring
Upload & Test / AI Detection Lab
Detection Events
Alerts
Insights
Workers
PPE Compliance
Reports
System
Settings
AI service connection status
System configuration

The interface uses consistent status indicators and is designed for site supervisors and safety officers rather than machine-learning specialists.

🔌 Backend & Notebook Integration

The repository separates the web API from the notebook inference logic.

Backend

The main API components are:

backend/
├── api.py
├── pipeline_adapter.py
├── requirements.txt
├── uploads/
└── outputs/

backend/api.py exposes the application service and normalizes inference results.

backend/pipeline_adapter.py is the explicit integration boundary between the web application and the notebook pipeline.

Notebook

The notebook contains the actual inference pipeline:

AI_Surveillance_Final_Notebook.ipynb

It defines the model-loading, configuration, detection, tracking, structural-anomaly, processing, visualization, and event-log workflow.

The notebook currently defines run_pipeline(path) inside its Jupyter/Kaggle runtime rather than as a normal importable production package.

The adapter can expose the notebook result in either of these forms:

(annotated_output_path, event_log_dataframe)

or:

{
    "output_path": "...",
    "event_log": ...
}

Event rows can use the notebook's existing:

event
detail
conf
frame
time_s

fields.

🚀 Quick Start
Prerequisites

Recommended environment:

Python 3.10+
FFmpeg
NVIDIA GPU recommended for faster inference
CUDA-compatible PyTorch environment when using GPU acceleration
Internet access for first-time model downloads

The notebook was developed/tested in a Kaggle GPU environment using NVIDIA T4/P100 acceleration.

1. Clone the Repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_REPOSITORY_FOLDER>
2. Install Backend Dependencies
python -m pip install -r backend/requirements.txt
3. Start the FastAPI Service
python -m uvicorn backend.api:app --reload
4. Open the Dashboard

Visit:

http://127.0.0.1:8000
5. Connect the AI Pipeline

Set the adapter module:

$env:AI_PIPELINE_MODULE = "your_adapter_module"
python -m uvicorn backend.api:app --reload

The frontend can still be navigated without a connected AI service. When the pipeline is not connected, upload requests return a service-unavailable state instead of inventing detections.

📓 Running the Notebook

The notebook was designed for a GPU-enabled Kaggle/Jupyter workflow.

Recommended Sequence
Enable Internet access so pretrained model weights can be downloaded.
Enable a GPU accelerator when available.
Run the notebook cells from top to bottom.
Use the interactive input section to:
Upload an image/video
Provide a /kaggle/input/... path
Use the demonstration clip
Run the master pipeline.
Preview the annotated result.
Review the generated analytics.
Save the event log and outputs.

The notebook includes safeguards for common execution problems such as invalid input paths, video codec compatibility, missing output variables, and cell-order issues.

📊 Analytics

The notebook generates analytics directly from real detection output, including:

Detection counts by event type
Event timelines
Model benchmark comparison charts
Worker-count trends
Structural SSIM traces
PPE/violation breakdowns
Timestamped event logs

The project intentionally avoids inventing benchmark results for models that do not have formally published metrics.

🚨 Alert & Notification System

The system separates normal informational detections from critical safety events.

Informational Events

Examples include individual PPE violations that require monitoring but do not necessarily represent an immediate emergency.

Critical Events

The critical alert workflow is activated for:

Fire
Fight / altercation
Fallen / unresponsive worker
Structural anomaly

When a critical event is detected, the system can:

AI Detection
     │
     ▼
Critical Event
     │
     ├──────────────► Dashboard Alert
     │
     ├──────────────► Audible Alarm
     │
     ├──────────────► Email Notification
     │                    │
     │                    ├── Timestamp
     │                    └── Annotated Screenshot
     │
     └──────────────► Event Log
Alert Cooldown

A cooldown mechanism is used per event type.

For example, if a fire remains visible for 30 seconds, the system should not send a new email for every processed frame. Instead, the event is rate-limited to avoid notification flooding.

👷 Worker Tracking

Worker tracking uses the detected Worker class together with ByteTrack-style tracking logic.

The system can provide:

Visible worker count
Persistent tracking IDs during a sequence
Worker-level PPE status
Worker activity states
Worker safety information

Tracking accuracy can be affected by:

Heavy occlusion
Workers leaving and re-entering the scene
Similar-looking workers
Camera angle
Poor lighting
Temporary loss of detections

A future Re-ID system could improve identity continuity across longer periods and multiple cameras.

🦺 PPE Compliance Monitoring

The PPE module is designed to identify construction workers and their protective-equipment status.

The system can identify classes related to:

Helmet / hard hat
No helmet
Vest
No vest
Worker

The frontend can represent PPE status using clear visual indicators so supervisors can quickly distinguish compliant workers from violations.

Example:

Worker ID: 01
Helmet: ✓
Vest:   ✓
Status: SAFE

or:

Worker ID: 02
Helmet: ✗
Vest:   ✓
Status: PPE VIOLATION
🔥 Fire & Smoke Detection

The fire/smoke module uses a pretrained YOLO-based model to detect visible fire and smoke.

When detected above the configured threshold, the event can be classified as critical.

Example workflow:

Frame
  │
  ▼
Fire/Smoke Model
  │
  ▼
Confidence Check
  │
  ▼
Fire / Smoke Event
  │
  ├── Bounding Box
  ├── Confidence Score
  ├── Critical Banner
  ├── Alarm
  └── Email Alert
🥊 Fight / Violence Detection

The system includes a pretrained community YOLO-based fight detection model.

It is intended to identify physical altercation/fight events in surveillance footage.

Because this model does not have a formal published benchmark included in the project documentation, deployment should include site-specific validation and threshold tuning.

🚑 Fallen Worker Detection

The fallen-worker module distinguishes between worker posture states such as:

Fallen
Sitting
Standing

A fallen/unresponsive worker event is treated as critical by the alerting workflow.

The distinction between normal sitting and an actual emergency should be validated using site-specific footage and operational rules.

🏗️ Structural Anomaly Detection

The current structural anomaly system is deliberately implemented as a heuristic.

It uses:

Structural Similarity Index (SSIM)

to compare the current frame against a slowly adapting reference frame.

Conceptually:

Reference Frame
       │
       ▼
Current Frame
       │
       ▼
SSIM Comparison
       │
       ▼
Large Sudden Difference?
       │
    ┌──┴──┐
   YES    NO
    │      │
    ▼      ▼
Possible   Normal
Structural Scene
Anomaly

This approach can help identify sudden large visual changes, but it is not equivalent to a trained structural-collapse detector.

Potential triggers include:

Structural collapse
Major scene change
Large object movement
Camera movement
Lighting changes
Other sudden visual changes

Therefore, the result should be treated as an alert for human investigation.

📈 Risk Analytics

The system includes an aggregated site-risk concept based on recent detection history.

Risk analysis can incorporate:

Critical incidents
PPE violations
Fire/smoke detections
Fight events
Fallen-worker events
Structural anomalies
Recent event frequency

The goal is to allow supervisors to identify increasing safety risk instead of only responding after an incident has already occurred.

📁 Event Logging

The detection engine produces structured event information that can be used for analytics and reporting.

Typical fields include:

frame
time_s
event
detail
conf

Example:

Frame: 142
Time: 5.68s
Event: No Helmet
Detail: Worker ID 02
Confidence: 0.91

This event information can be normalized by the API and displayed in the dashboard.

🧪 Upload & Test / AI Detection Lab

The AI Detection Lab provides a testing interface for the computer-vision pipeline.

Users can:

Upload an image or video.
Submit it for AI analysis.
View the original media.
View the AI-analyzed result.
Inspect detected events.
Review confidence scores.
Review severity information.

This makes it possible to test the system using representative construction-site footage before connecting it to live monitoring infrastructure.

🛡️ Safety & Deployment Considerations

This project is an AI-assisted monitoring system, not a certified replacement for trained safety personnel, emergency procedures, or regulatory compliance systems.

Before real-world safety-critical deployment:

Validate every detector on representative site footage.
Tune confidence thresholds per camera/site.
Review false positives and false negatives.
Validate camera placement, lighting, occlusion, and viewing angles.
Establish human-review procedures for structural anomalies.
Test notification delivery and cooldown behavior.
Protect uploaded footage and event records.
Add appropriate access control and audit logging.
Evaluate local privacy, workplace monitoring, and data-retention requirements.

The current project documentation specifically recommends site-specific validation for the community-trained fight/fall models and the structural anomaly heuristic.

⚠️ Current Limitations
Structural Anomaly Detection

The structural detector is currently an SSIM-based heuristic rather than a trained building-collapse classifier.

Fight / Fallen-Worker Models

These are real pretrained community models but lack formal published benchmark results in the project documentation.

Worker Counting

The current unique-worker estimate can be affected by:

Heavy occlusion
Workers leaving and re-entering the frame
New tracking IDs being assigned

A Re-ID model could improve long-term identity continuity.

Input Sources

The current pipeline supports uploaded image/video workflows.

Live RTSP camera ingestion is planned rather than presented as a completed feature.

Production Architecture

The notebook remains an interactive Kaggle/Jupyter artifact.

The backend integration layer provides a clean boundary for connecting it to the web application, but a fully productionized inference service would be a future engineering step.

🔮 Future Roadmap
AI & Computer Vision
 Fine-tune models using site-specific footage
 Improve worker Re-ID and long-term tracking
 Replace the SSIM tripwire with a validated structural anomaly model
 Expand PPE classes and site-specific hazards
 Add additional validated hazard detectors
 Improve confidence calibration
Real-Time Infrastructure
 RTSP/IP camera ingestion
 Multi-camera processing
 Camera health monitoring
 Distributed inference
 Queue-based video processing
Alerting
 SMS integration
 Slack/Teams notifications
 Escalation policies
 Incident acknowledgement workflow
 Human-review queue for uncertain alerts
Analytics
 Historical incident trends
 Site-to-site comparison
 Camera-level risk analysis
 Advanced risk forecasting
 Exportable compliance reports
🗂️ Repository Structure
.
├── AI_Surveillance_Final_Notebook.ipynb
├── README.md
├── .gitignore
│
├── backend/
│   ├── api.py
│   ├── pipeline_adapter.py
│   ├── requirements.txt
│   ├── uploads/
│   └── outputs/
│
├── frontend/
│   ├── assets/
│   │   └── Alarm sound.mp3
│   └── ...
│
└── docs/
    └── images/
        ├── architecture-pipeline.png
        ├── dashboard-ai-detection-lab.png
        └── detection-outputs.png

The project's .gitignore should exclude Python caches, virtual environments, Jupyter checkpoints, secrets, Node modules, logs, and runtime upload/output directories.

In particular:

backend/uploads/*
backend/outputs/*

should remain excluded so test media and generated outputs do not become repository clutter.

🧪 Example Event Flow
Camera / Uploaded Media
        │
        ▼
Frame Normalization
        │
        ▼
AI Inference
        │
        ├── PPE Violation ──────► Informational Event
        │
        ├── Fire / Smoke ───────► CRITICAL
        │
        ├── Fight ──────────────► CRITICAL
        │
        ├── Worker Down ────────► CRITICAL
        │
        └── Structural Anomaly ─► CRITICAL / HUMAN REVIEW
                                      │
                                      ▼
                              Alert Manager
                                      │
                         ┌────────────┼────────────┐
                         ▼            ▼            ▼
                      Dashboard     Sound        Email
                                      │
                                      ▼
                               Event + Evidence
🎯 Intended Users
Site Safety Officer

Monitor alerts, review incidents, acknowledge events, and inspect the daily risk state.

Site Supervisor / Manager

Review PPE compliance, worker trends, reports, and recurring safety issues.

Site Owner / Executive

Receive critical notifications and review high-level safety reporting.

System Administrator

Configure system behavior, thresholds, camera connections, and notification recipients.

🧰 Technology Stack
Layer	Technologies
AI / Computer Vision	Python, Ultralytics YOLOv8, OpenCV, PyTorch
Model Hosting	Hugging Face Hub
Video Processing	FFmpeg, H.264
Tracking	ByteTrack
Structural Analysis	scikit-image / SSIM
Data & Analytics	Pandas, Matplotlib, Seaborn
Experimentation	Kaggle Notebooks, NVIDIA T4/P100
Backend	FastAPI, Uvicorn
Frontend	Web Application
Notifications	SMTP Email + Attached Evidence
Runtime Integration	Notebook Adapter
📈 Project Success Metrics

The project's product requirements identify these practical success measures:

Reduction in mean time-to-notice for critical events
PPE compliance trend over time
Precision of critical alerts
Percentage of flagged incidents acknowledged and acted upon
Reliability of notification delivery
Usability for non-technical safety personnel
🔐 Data & Repository Hygiene

Do not commit:

API keys
SMTP passwords
.env files
Private camera credentials
Sensitive worker footage
Personally identifiable information
Large generated outputs
Temporary uploads

Use environment variables for secrets and keep private operational data outside the Git repository.

Example:

.env

should remain local and should never be committed.

For collaboration, provide a safe template such as:

.env.example

without real credentials.

📚 Project Documentation

The project documentation covers:

System motivation
Architecture
Application interface
Detection outputs
Model sources
Backend pipeline
Alert/email workflow
Frontend modules
Product requirements
Real-world usefulness
Technology stack
Limitations
Future scope
Glossary
🏁 Conclusion

The AI-Based Construction Site Surveillance System demonstrates how multiple computer-vision models, event processing, worker tracking, automated notifications, analytics, and a usable web interface can be combined into one coherent industrial-safety platform.

Rather than presenting isolated object detectors, the project connects the full workflow:

Input → AI Detection → Tracking → Event Aggregation → Risk Insight → Alert → Evidence → Human Response

The result is a strong foundation for a production-oriented construction safety platform, while clearly documenting the areas that still require additional validation and engineering before safety-critical deployment.

The notebook is designed for an interactive Kaggle/Jupyter kernel, so the first API request lazily executes its existing import, model-loading, configuration, detection-helper, and pipeline cells in a persistent Python namespace. Model weights may take time to download on the first request. The models are not duplicated in the browser and the notebook file is not rewritten.
