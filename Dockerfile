# ---- Build Stage ----
FROM python:3.10-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Final Stage ----
FROM python:3.10-slim
WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY app ./app
COPY data ./data
COPY vector_store ./vector_store
COPY .env .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
