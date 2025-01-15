# Usa la imagen de Python
FROM python:3.12-slim

# Instala dependencias de sistema
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    gcc \
    python3-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Define el directorio de trabajo
WORKDIR /app

# Copia el archivo de dependencias
COPY requirements.txt .

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente
COPY sistema_lavanderia /app/sistema_lavanderia
COPY run.py /app/run.py

# Exponer el puerto
EXPOSE 5000

CMD ["python", "run.py", "--host=0.0.0.0", "--port=90"]

