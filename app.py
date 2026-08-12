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

    # 3. Start synthetic vision simulation modules
    dashboard_api.start_modules_simulate()

    # 4. Run standard Flask app directly on main thread port 7860
    dashboard_api.app.run(
        host="0.0.0.0",
        port=7860,
        debug=False
    )
