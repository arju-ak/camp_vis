import os
import sys
import numpy as np

import gradio as gr
import dashboard_api

# 1. Enable 24/7 simulation mode for cloud hosting
dashboard_api.SIMULATE = True
dashboard_api.db.init_db()

# 2. Start synthetic vision simulation modules
dashboard_api.start_modules_simulate()

# 3. Frame processing function
def process_frame(image):
    if image is None:
        return np.zeros((300, 300, 3), dtype=np.uint8)
    return image

# 4. Create standard Gradio Blocks UI
with gr.Blocks(title="Campus Vision AI Server") as demo:
    gr.Markdown("""
    # 🏫 Campus Vision AI — Live Backend API Server
    **Status**: Active 🟢 (Serving REST & WebSocket APIs for Streamlit Dashboard)

    - **Mode**: Simulation Mode
    """)
    with gr.Row():
        img_in = gr.Image(label="Input Snapshot")
        img_out = gr.Image(label="Processed Analytics Output")
    btn = gr.Button("⚡ Run Vision Analytics")
    btn.click(fn=process_frame, inputs=img_in, outputs=img_out)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
