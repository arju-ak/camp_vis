import os
import sys
import threading
import gradio as gr

import dashboard_api

# 1. Initialize simulation mode
dashboard_api.SIMULATE = True
dashboard_api.db.init_db()

# 2. Start Flask backend server on port 5000 in a background daemon thread
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

# 4. Launch Gradio UI on port 7860 to satisfy Hugging Face Space health check
with gr.Blocks(title="Campus Vision AI — Server") as demo:
    gr.Markdown("""
    # 🏫 Campus Vision AI — Public Server
    **Status**: Active 🟢 (Serving REST & WebSocket APIs for Streamlit Dashboard)

    - **Mode**: Simulation Mode (24/7 AI Monitoring Feed)
    """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
