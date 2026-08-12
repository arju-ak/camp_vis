import os
import subprocess
import time
import gradio as gr

# Start the Campus Vision AI Flask Backend in a background process
print("Starting Campus Vision AI Flask Backend Server...")
backend_process = subprocess.Popen([
    "python", "dashboard_api.py", "--simulate", "--port", "7860", "--host", "0.0.0.0"
])

# Lightweight Gradio wrapper for Hugging Face Space hosting
with gr.Blocks(title="Campus Vision AI — Backend API") as demo:
    gr.Markdown("""
    # 🏫 Campus Vision AI — Public Backend API
    **Status**: Active 🟢 (Serving REST & WebSocket APIs for Streamlit Dashboard)

    - **API Stats Endpoint**: `/api/stats`
    - **Mode**: Simulation Mode (24/7 AI Surveillance Feed)
    """)

if __name__ == "__main__":
    # Gradio launches on Hugging Face Space port 7860
    demo.launch(server_name="0.0.0.0", server_port=7860)
