import os
import sys
import numpy as np

import gradio as gr
from fastapi.middleware.wsgi import WSGIMiddleware

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

# 5. Mount Flask app to Gradio's FastAPI backend under /api
demo.app.mount("/api", WSGIMiddleware(dashboard_api.app))

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
