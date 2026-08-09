# MiniMax H3 serverless worker (ComfyUI)

Docker image for a RunPod serverless endpoint that renders MiniMax H3 videos
via the `minimaxH3_v2` ComfyUI workflow. Models are read from the attached
network volume (`/runpod-volume/ComfyUI/models`); nothing installs at runtime.

## Deploy

1. Push this repo to GitHub.
2. RunPod console → **Serverless** → **New Endpoint** → **Import Git Repository**
   → pick this repo/branch (Dockerfile at repo root). RunPod builds the image.
3. Endpoint settings:
   - **GPU**: RTX 5090 (32 GB) — the validated dev configuration
   - **Workers**: min 0, max 1
   - **Idle timeout**: 60–120 s (budget) — you pay for idle time after each job
   - **FlashBoot**: on
   - **Advanced → Network Volume**: attach the ComfyUI volume (same datacenter)

## Test from a local PC

1. RunPod console → Settings → API Keys → create a key.
2. Export the workflow from the ComfyUI UI via **Workflow → Export (API)**
   and save as `workflow_api.json` next to `test_endpoint.py`.
3. ```
   set RUNPOD_API_KEY=rpa_xxx
   set ENDPOINT_ID=<endpoint id>
   python test_endpoint.py workflow_api.json
   ```

## Baked-in fixes (from pod validation 2026-08-09)

- ComfyUI pinned to v0.30.1 (MiniMax H3 core nodes)
- kornia 0.7.3 (newer versions break ComfyUI-LTXVideo)
- transformers < 5 (v5 removed AutoImageProcessor)
- opencv-headless / scikit-image / lazy_loader (Impact-Pack + import chain)
- SageAttention: NOT included in v1 — bypass the "MiniMax H3 Mem Eff Sage
  Attention Patch" node in the API workflow, or bake sage in a v2 image
  (compile recipe in project memory).
