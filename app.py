import os
import sys

from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
import gradio as gr

import dashboard_api

# 1. Initialize simulation mode for Hugging Face Cloud backend
dashboard_api.SIMULATE = True
dashboard_api.db.init_db()
dashboard_api.start_modules_simulate()

# 2. Create FastAPI application
app = FastAPI(title="Campus Vision AI Server")

# 3. Mount Flask app to FastAPI so /api/stats and all routes work seamlessly
app.mount("/api", WSGIMiddleware(dashboard_api.app))

# 4. Create Gradio interface so Hugging Face Space watchdog marks it 100% HEALTHY
with gr.Blocks(title="Campus Vision AI — Backend API") as demo:
    gr.Markdown("""
    # 🏫 Campus Vision AI — Live Backend API
    **Status**: Active 🟢 (Serving REST & WebSocket APIs for Streamlit Dashboard)

    - **API Stats**: [/api/stats](/api/stats)
    - **Mode**: Simulation Mode (24/7 AI Monitoring Feed)
    """)

# 5. Combine Gradio + FastAPI app
app = gr.mount_gradio_app(app, demo, path="/")
