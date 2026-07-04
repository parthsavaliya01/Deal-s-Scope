# Deployment

Docker

```bash
docker build -t dealscope:latest .
docker run -e DISABLE_LLM=true -p 8501:8501 dealscope:latest
```

Docker Compose

```bash
docker-compose up --build
```

Cloud providers

See README for provider-specific tips (Render, Railway, Streamlit Cloud). Be sure to populate environment variables securely.
