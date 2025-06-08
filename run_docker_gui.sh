#!/bin/bash

echo "🐳 Executando GUI dos Mapas no Docker"
echo "====================================="

# Verifica se o Docker está rodando
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Verifica se o DISPLAY está configurado
if [ -z "$DISPLAY" ]; then
    echo "❌ Variável DISPLAY não configurada. Configure com: export DISPLAY=:0"
    exit 1
fi

# Permite acesso X11 temporariamente
echo "🔓 Permitindo acesso X11..."
xhost +local:docker

# Para e remove container anterior se existir
echo "🧹 Limpando containers anteriores..."
docker stop rotas-capitais-gui 2>/dev/null || true
docker rm rotas-capitais-gui 2>/dev/null || true

# Obtém UID e GID do usuário atual
USER_UID=$(id -u)
USER_GID=$(id -g)

echo "🚀 Iniciando container com GUI..."
echo "   Display: $DISPLAY"
echo "   UID:GID: $USER_UID:$USER_GID"

# Executa o container com GUI melhorada
docker run --rm \
    -e DISPLAY=$DISPLAY \
    -e MPLCONFIGDIR=/tmp/matplotlib \
    -e HOME=/tmp \
    -e PYTHONUNBUFFERED=1 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v "$(pwd)":/app \
    -w /app \
    --net=host \
    --name rotas-capitais-gui \
    python:3.9-slim \
    bash -c "
        echo '🔧 Instalando dependências...' &&
        apt-get update -qq && apt-get install -y -qq python3-tk libx11-6 libxext6 libxrender1 fonts-dejavu-core &&
        pip install -q matplotlib networkx numpy requests tabulate geopandas shapely &&
        echo '🚀 Iniciando aplicação...' &&
        python run_map_gui.py
    "

# Revoga acesso X11
echo "🔒 Revogando acesso X11..."
xhost -local:docker

echo "✅ Execução finalizada."