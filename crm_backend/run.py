import os
import sys

# Add the workspace root to sys.path so that crm_backend is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn

if __name__ == "__main__":
    reload_flag = os.environ.get("AI_HCP_RELOAD", "0") == "1"
    uvicorn.run("crm_backend.app.main:app", host="0.0.0.0", port=8000, reload=reload_flag)
