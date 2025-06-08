FROM python:3.9-slim

# Instalar dependências mínimas para GUI
RUN apt-get update && apt-get install -y \
    python3-tk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    xvfb \
    fonts-dejavu-core \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Configurar variáveis de ambiente para GUI
ENV DISPLAY=:0
ENV QT_X11_NO_MITSHM=1
ENV LIBGL_ALWAYS_INDIRECT=1

WORKDIR /app

# Copiar requirements.txt primeiro para cache de layers otimizado
COPY requirements.txt .

# Instalar dependências Python incluindo geopandas
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código
COPY . .

# Comando padrão atualizado para usar o GUI com mapas
CMD ["python", "run_map_gui.py"]
