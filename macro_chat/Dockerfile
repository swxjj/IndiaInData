FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    PYTHONPATH=/app

WORKDIR /app

# Dependencias mínimas del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY macro_chat/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY macro_chat /app/macro_chat

# Directorio para archivos generados
RUN mkdir -p /app/macro_chat/output

EXPOSE 8080

CMD ["sh", "-c", "uvicorn macro_chat.app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
