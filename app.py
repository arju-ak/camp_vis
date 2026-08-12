import os
import sys

import dashboard_api

if __name__ == "__main__":
    print("=" * 60)
    print("  CAMPUS VISION AI — BACKEND SERVER")
    print("=" * 60)

    dashboard_api.SIMULATE = True
    dashboard_api.db.init_db()
    dashboard_api.start_modules_simulate()

    dashboard_api.socketio.run(
        dashboard_api.app,
        host="0.0.0.0",
        port=7860,
        debug=False,
        allow_unsafe_werkzeug=True
    )
