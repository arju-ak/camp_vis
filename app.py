import os
import sys
import numpy as np

from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
import gradio as gr

import dashboard_api

# 1. Initialize simulation mode
dashboard_api.SIMULATE = True
dashboard_api.db.init_db()

# 2. Start simulation modules
dashboard_api.start_modules_simulate()

# 3. Create root FastAPI application
app = FastAPI(title="Campus Vision AI Server")

# 4. Mount Flask WSGI app at /api
app.mount("/api", WSGIMiddleware(dashboard_api.app))

# 5. Create Gradio UI
def predict(image):
    if image is None:
        return np.zeros((300, 300, 3), dtype=np.uint8)
    return image

with gr.Blocks(title="Campus Vision AI Server") as demo:
    gr.Markdown("""
    # 🏫 Campus Vision AI — Live Backend Server
    **Status**: Active 🟢 (Serving REST & WebSocket APIs for Streamlit Dashboard)

    - **API Stats Endpoint**: [/api/stats](/api/stats)
    - **Mode**: Simulation Mode
    """)
    with gr.Row():
        img_in = gr.Image(label="Camera Feed Snapshot")
        img_out = gr.Image(label="AI Detection Output")
    btn = gr.Button("⚡ Run Vision Analytics")
    btn.click(fn=predict, inputs=img_in, outputs=img_out)

# 6. Mount Gradio interface under /
app = gr.mount_gradio_app(app, demo, path="/")
