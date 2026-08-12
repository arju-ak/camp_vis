import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="Campus Vision AI", layout="wide", initial_sidebar_state="expanded")

# Read the React HTML file we built
html_path = os.path.join(os.path.dirname(__file__), 'frontend', 'index.html')
try:
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
except Exception as e:
    st.error(f"Could not load frontend HTML: {e}")
    html_content = ""

st.sidebar.markdown("# 🌐 Backend Public URL Config")
backend_url = st.sidebar.text_input(
    "Flask API URL", 
    value=st.query_params.get("api", "http://localhost:5000"),
    help="Enter your ngrok or localtunnel HTTPS URL (e.g., https://xxx.ngrok-free.app or https://xxx.loca.lt)"
)

st.sidebar.info("""
### 🚀 How to Share over Internet:
1. Keep `python dashboard_api.py` running on your laptop.
2. In terminal, run a public tunnel:
   - **localtunnel**: `npx localtunnel --port 5000`
   - **ngrok**: `ngrok http 5000`
3. Paste the generated public `https://...` URL into the box above!
""")

# Inject the chosen API URL into HTML content
if html_content and backend_url:
    clean_url = backend_url.rstrip('/')
    injected_script = f"<script>window.CUSTOM_API_BASE = '{clean_url}';</script>"
    if "<head>" in html_content:
        html_content = html_content.replace("<head>", f"<head>{injected_script}")
    else:
        html_content = injected_script + html_content

st.markdown("<h2 style='text-align: center; color: #a1a1aa;'>Campus Vision AI Monitoring System</h2>", unsafe_allow_html=True)

if html_content:
    components.html(html_content, height=850, scrolling=True)
