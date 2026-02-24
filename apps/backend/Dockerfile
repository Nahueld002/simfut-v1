FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes (ej. asyncpg)
RUN apt-get update && apt-get install -y gcc build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
