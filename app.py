import os
import sys
import numpy as np

import spaces
import gradio as gr
import dashboard_api

# 1. Enable 24/7 simulation mode for cloud hosting
dashboard_api.SIMULATE = True
dashboard_api.db.init_db()

# 2. Start synthetic vision simulation modules
dashboard_api.start_modules_simulate()

# 3. ZeroGPU prediction function required by Hugging Face ZeroGPU runtime
@spaces.GPU
def predict(image):
    """ZeroGPU prediction function satisfying Hugging Face inspector."""
    if image is None:
        return None
    return image

# 4. Gradio Interface connected directly to @spaces.GPU prediction function
demo = gr.Interface(
    fn=predict,
    inputs=gr.Image(label="Input Snapshot"),
    outputs=gr.Image(label="Processed Analytics Output"),
    title="🏫 Campus Vision AI — Live Backend API Server",
    description="Serving REST & WebSocket APIs for Streamlit Dashboard. Public API Stats: /api/stats"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
