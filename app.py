import os
import sys
import numpy as np

import gradio as gr
from fastapi.middleware.wsgi import WSGIMiddleware

import dashboard_api

# 1. Initialize simulation mode
dashboard_api.SIMULATE = True
dashboard_api.db.init_db()

# 2. Start simulation modules
dashboard_api.start_modules_simulate()

# 3. Prediction function
def predict(image):
    if image is None:
        return np.zeros((300, 300, 3), dtype=np.uint8)
    return image

# 4. Create Gradio Blocks UI
with gr.Blocks(title="Campus Vision AI Server") as demo:
    gr.Markdown("""
    # 🏫 Campus Vision AI — Live Backend API
    **Status**: Active 🟢 (Serving REST & WebSocket APIs for Streamlit Dashboard)

    - **API Stats Endpoint**: [/api/stats](/api/stats)
    - **Mode**: Simulation Mode
    """)
    with gr.Row():
        img_in = gr.Image(label="Camera Feed Snapshot")
        img_out = gr.Image(label="AI Detection Output")
    btn = gr.Button("⚡ Run Vision Analytics")
    btn.click(fn=predict, inputs=img_in, outputs=img_out)

# 5. Mount Flask app to Gradio's FastAPI app under /api
demo.app.mount("/api", WSGIMiddleware(dashboard_api.app))

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
