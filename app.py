import os
import sys

import dashboard_api

if __name__ == "__main__":
    print("=" * 60)
    print("  CAMPUS VISION AI — HUGGING FACE BACKEND SERVER")
    print("=" * 60)

    # 1. Enable 24/7 simulation mode for cloud hosting
    dashboard_api.SIMULATE = True

    # 2. Initialize SQLite DB
    dashboard_api.db.init_db()

    # 3. Start simulation threads
    dashboard_api.start_modules_simulate()

    # 4. Run Flask + SocketIO server on main thread port 7860
    dashboard_api.socketio.run(
        dashboard_api.app,
        host="0.0.0.0",
        port=7860,
        debug=False,
        allow_unsafe_werkzeug=True
    )
