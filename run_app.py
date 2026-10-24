"""Launcher script for ResearchPilot AI (FastAPI + React Full-Stack Application)."""

import os
import sys
import webbrowser
import uvicorn

def main():
    print("=" * 65)
    print("🔬 ResearchPilot AI — Gemma 4 Scientific Research Assistant")
    print("=" * 65)
    print("Starting FastAPI backend & serving React production build at:")
    print("👉 http://localhost:8000")
    print("=" * 65)

    # Automatically open the browser
    webbrowser.open("http://localhost:8000")

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

if __name__ == "__main__":
    main()
