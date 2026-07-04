FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
ENV STREAMLIT_SERVER_PORT=8501
EXPOSE 8501
CMD ["sh", "-c", "streamlit run main.py --server.headless true --server.port $STREAMLIT_SERVER_PORT"]