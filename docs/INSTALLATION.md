# Installation

Instructions for Windows, macOS, and Linux

Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env as needed
```

Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env
```

Troubleshooting
- If scrapers fail, ensure Chrome and chromedriver are installed and compatible or set `CHROMEDRIVER_PATH` in `.env`.
