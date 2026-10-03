FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3939

# --chdir /app/src: muda para dentro de src antes de importar, resolvendo os imports relativos do main.py
CMD ["gunicorn", "--chdir", "/app/src", "--bind", "0.0.0.0:3939", "--workers", "2", "--worker-class", "gthread", "--threads", "2", "--timeout", "120", "main:app"]
