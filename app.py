import os
import sys
import numpy as np

from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
import gradio as gr

import dashboard_api

# 1. Enable 24/7 simulation mode for cloud hosting
dashboard_api.SIMULATE = True
dashboard_api.db.init_db()

# 2. Start synthetic vision simulation modules
dashboard_api.start_modules_simulate()

# 3. Simple frame processing function
def process_frame(image):
    if image is None:
        return np.zeros((300, 300, 3), dtype=np.uint8)
    return image

# 4. Create standard Gradio Interface
demo = gr.Interface(
    fn=process_frame,
    inputs=gr.Image(label="Input Snapshot"),
    outputs=gr.Image(label="Processed Analytics Output"),
    title="🏫 Campus Vision AI — Live Backend API Server",
    description="Serving REST & WebSocket APIs for Streamlit Dashboard. Public API Stats: /api/stats"
)

# 5. Create FastAPI app
app = FastAPI(title="Campus Vision AI Server")

# 6. Mount Flask app under /api
app.mount("/api", WSGIMiddleware(dashboard_api.app))

# 7. Mount Gradio interface under /
app = gr.mount_gradio_app(app, demo, path="/")
