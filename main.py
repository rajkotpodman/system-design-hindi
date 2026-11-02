"""
System Design Implementations Entrypoint
Run this script to start the live interactive web dashboard and API server:
    python main.py
Or with uvicorn:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import sys
import uvicorn

if sys.platform == "win32":
    try:
        if sys.stdout and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from implementations.api.app import app

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  🚀 SYSTEM DESIGN IMPLEMENTATION SERVER STARTING")
    print("  Interactive Web Dashboard: http://localhost:8000/")
    print("  Interactive Swagger Docs:  http://localhost:8000/docs")
    print("  ReDoc Documentation:       http://localhost:8000/redoc")
    print("=" * 70 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

