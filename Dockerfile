FROM runpod/worker-comfyui:5.8.6-base

# Pin the exact ComfyUI version validated on the dev pod (2026-08-09).
# The MiniMax H3 nodes are core ComfyUI nodes and need >= 0.30.x.
RUN cd /comfyui && git fetch --depth 1 origin tag v0.30.1 && git checkout v0.30.1 && \
    pip install -r requirements.txt

# Only the custom node packs the minimaxH3_v2 workflow actually uses.
RUN cd /comfyui/custom_nodes && \
    git clone --depth 1 https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo.git && \
    git clone --depth 1 https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3.git && \
    git clone --depth 1 https://github.com/kijai/ComfyUI-KJNodes.git && \
    git clone --depth 1 https://github.com/Lightricks/ComfyUI-LTXVideo.git && \
    git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Impact-Pack.git

# Node requirements; torch stack excluded so the base image's CUDA torch stays intact.
RUN cd /comfyui/custom_nodes && \
    for d in */; do \
      if [ -f "$d/requirements.txt" ]; then \
        grep -viE '^(torch|torchvision|torchaudio|xformers)([=<>!~ ]|$)' "$d/requirements.txt" > /tmp/req.txt && \
        pip install --no-cache-dir -r /tmp/req.txt; \
      fi; \
    done

# Version pins discovered during pod validation:
#  - kornia 0.7.3: newest kornia removed `pad`, breaking ComfyUI-LTXVideo
#  - transformers < 5: v5 removed AutoImageProcessor, breaking ComfyUI-LTXVideo
RUN pip install --no-cache-dir "kornia==0.7.3" "transformers<5" \
    opencv-python-headless scikit-image lazy_loader

# Models are read from the attached network volume (mounted at /runpod-volume).
COPY extra_model_paths.yaml /comfyui/extra_model_paths.yaml
