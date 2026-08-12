import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="Campus Vision AI", layout="wide", initial_sidebar_state="expanded")

# Read the React HTML file
html_path = os.path.join(os.path.dirname(__file__), 'frontend', 'index.html')
try:
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
except Exception as e:
    st.error(f"Could not load frontend HTML: {e}")
    html_content = ""

st.sidebar.markdown("# 🌐 Backend Public Server")
default_api = "https://arjunanidil-camp-vis.hf.space"

if "backend_url" not in st.session_state:
    st.session_state["backend_url"] = default_api

with st.sidebar.form(key="api_connect_form"):
    url_input = st.text_input(
        "Flask API Server URL", 
        value=st.session_state["backend_url"],
        help="Default is set to your free Hugging Face Space backend (https://arjunanidil-camp-vis.hf.space)"
    )
    submit_btn = st.form_submit_button("🔌 Connect to Backend", type="primary", use_container_width=True)

if submit_btn:
    st.session_state["backend_url"] = url_input.strip()

active_backend_url = st.session_state.get("backend_url", default_api)

# Inject the chosen API URL into HTML content
if html_content and active_backend_url:
    clean_url = active_backend_url.rstrip('/')
    injected_script = f"<script>window.CUSTOM_API_BASE = '{clean_url}';</script>"
    if "<head>" in html_content:
        html_content = html_content.replace("<head>", f"<head>{injected_script}")
    else:
        html_content = injected_script + html_content

st.markdown("<h2 style='text-align: center; color: #a1a1aa;'>Campus Vision AI Monitoring System</h2>", unsafe_allow_html=True)

if html_content:
    components.html(html_content, height=850, scrolling=True)
