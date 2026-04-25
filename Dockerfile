# F1 Strategist server image.
# Starts the FastAPI app on port 8000.
FROM python:3.12-slim

WORKDIR /app

# Install runtime deps. Training/eval happen outside the container.
RUN pip install --no-cache-dir \
    "openenv-core>=0.2.3" \
    "fastapi>=0.104.0" \
    "uvicorn>=0.24.0" \
    "pydantic>=2.0.0" \
    "numpy>=1.26.0" \
    "pandas>=2.0.0" \
    "matplotlib>=3.8.0"

# Optional: include Gradio + imageio for the /web interactive panel and GIF rendering
RUN pip install --no-cache-dir "gradio>=4.0.0" "imageio>=2.31.0" "pillow>=10.0.0"

# Copy repo. Order matters: code that changes most last so docker caches well.
COPY models.py /app/models.py
COPY client.py /app/client.py
COPY server /app/server
COPY data /app/data

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENABLE_WEB_INTERFACE=1

EXPOSE 8000

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
