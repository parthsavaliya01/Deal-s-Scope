# Project structure

Top-level layout and purpose of main folders/files:

- `main.py` — Streamlit UI entrypoint (existing app logic preserved).
- `scrape_flipkart_data.py`, `scrape_croma_data.py` — scrapers (existing).
- `extract_product_name.py`, `find_relevent_search_results.py`, `generate_response_from_relevent_results.py` — prompt handling and response generation (existing).
- `docs/` — documentation (this folder).
- `.env.example` — example environment variables.
- `requirements.txt`, `requirements-dev.txt` — runtime and dev dependencies.
- `tests/` — unit and smoke tests.
