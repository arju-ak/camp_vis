import os
import sys
import threading
import numpy as np

# Safe ZeroGPU decorator fallback
try:
    import spaces
    gpu_decorator = spaces.GPU
except Exception:
    def gpu_decorator(func=None, **kwargs):
        if func is None:
            return lambda f: f
        return func

import gradio as gr
import dashboard_api

# 1. Initialize simulation mode for cloud hosting
dashboard_api.SIMULATE = True
dashboard_api.db.init_db()

# 2. Start Flask backend server in background daemon thread
def run_flask():
    dashboard_api.socketio.run(
        dashboard_api.app, 
        host="0.0.0.0", 
        port=5000, 
        debug=False, 
        allow_unsafe_werkzeug=True
    )

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# 3. Start synthetic vision simulation modules
dashboard_api.start_modules_simulate()

# 4. ZeroGPU prediction function using safe decorator
@gpu_decorator
def predict(image):
    """Prediction function with safe ZeroGPU compatibility."""
    if image is None:
        return np.zeros((300, 300, 3), dtype=np.uint8)
    return image

# 5. Build Gradio UI
with gr.Blocks(title="Campus Vision AI — Public Server") as demo:
    gr.Markdown("""
    # 🏫 Campus Vision AI — Live Backend Server
    **Status**: Active 🟢 (Serving REST & WebSocket APIs for Streamlit Dashboard)

    - **Mode**: Simulation Mode (24/7 AI Monitoring Feed)
    """)
    with gr.Row():
        img_input = gr.Image(label="Input Snapshot (Optional)")
        img_output = gr.Image(label="Vision Processing Output")
    btn = gr.Button("⚡ Analyze Image with AI")
    btn.click(fn=predict, inputs=img_input, outputs=img_output)

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860)
