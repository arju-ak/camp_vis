import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="Campus Vision AI", layout="wide", initial_sidebar_state="collapsed")

# Read the React HTML file we built
html_path = os.path.join(os.path.dirname(__file__), 'frontend', 'index.html')
try:
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
except Exception as e:
    st.error(f"Could not load frontend HTML: {e}")
    html_content = ""

# Display important setup notes for Streamlit hosting
st.sidebar.markdown("""
# ⚠️ Cloud Deployment Note
If you upload this to Streamlit Community Cloud (internet server), the live camera feed will break because the cloud server does not have access to your laptop's physical webcam!

To share this over the internet while keeping your webcam active, use **ngrok** to tunnel your local Flask server instead.
""")

st.sidebar.success("""
### Local API running?
Ensure you have run `python dashboard_api.py` in the background for this frontend to fetch the stats properly!
""")

# Embed the raw React + Three.js application into Streamlit
# We use a large height to ensure the dashboard fits perfectly
st.markdown("<h2 style='text-align: center; color: #a1a1aa;'>Streamlit Dashboard Wrapper</h2>", unsafe_allow_html=True)

if html_content:
    # Setting scrolling=True just in case the screen splits
    components.html(html_content, height=850, scrolling=True)
