import os
import sys
import threading
import numpy as np

import gradio as gr
import dashboard_api

# 1. Enable simulation mode for cloud hosting
dashboard_api.SIMULATE = True
dashboard_api.db.init_db()

# 2. Start simulation modules
dashboard_api.start_modules_simulate()

# 3. Start Flask API server on port 5000 in background daemon thread
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

# 4. Prediction function
def predict(image):
    if image is None:
        return np.zeros((300, 300, 3), dtype=np.uint8)
    return image

# 5. Create Gradio Blocks UI on main thread
with gr.Blocks(title="Campus Vision AI Server") as demo:
    gr.Markdown("""
    # 🏫 Campus Vision AI — Live Backend API
    **Status**: Active 🟢 (Serving REST & WebSocket APIs for Streamlit Dashboard)

    - **Mode**: Simulation Mode
    """)
    with gr.Row():
        img_in = gr.Image(label="Camera Feed Snapshot")
        img_out = gr.Image(label="AI Detection Output")
    btn = gr.Button("⚡ Run Vision Analytics")
    btn.click(fn=predict, inputs=img_in, outputs=img_out)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
