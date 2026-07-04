"""Run helper for the DealScope application.

This small wrapper allows launching Streamlit via Python for common tooling.
"""
import os
import subprocess


def main():
    port = os.environ.get("STREAMLIT_SERVER_PORT", "8501")
    cmd = ["streamlit", "run", "main.py", "--server.headless", "true", "--server.port", port]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
