import os
import sys

# Import dashboard_api directly and run Flask on Hugging Face port 7860
import dashboard_api

if __name__ == "__main__":
    print("=" * 60)
    print("  CAMPUS VISION AI — HUGGING FACE BACKEND SERVER")
    print("=" * 60)
    
    # Enable simulation mode for 24/7 cloud hosting
    dashboard_api.SIMULATE = True
    
    # Initialize database
    dashboard_api.db.init_db()
    
    # Start synthetic vision simulation modules
    dashboard_api.start_modules_simulate()
    
    # Run Flask + SocketIO app directly on Hugging Face default port 7860
    dashboard_api.socketio.run(
        dashboard_api.app, 
        host="0.0.0.0", 
        port=7860, 
        debug=False, 
        allow_unsafe_werkzeug=True
    )
