#!/bin/bash

# Atualizar o Dockerfile para instalar bibliotecas geográficas
cat << 'EOF' > Dockerfile
FROM python:3.9-slim

# Instalar dependências para interface gráfica e processamento geográfico
RUN apt-get update && apt-get install -y \
    python3-tk \
    libx11-6 \
    xvfb \
    build-essential \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install geopandas descartes

COPY . .

CMD ["python", "main.py"]
EOF

# Reconstruir a imagem Docker
echo "Recriando a imagem Docker..."
docker-compose build

echo "Configuração concluída! Execute com:"
echo "docker-compose run route-finder python main_gui_maps.py"