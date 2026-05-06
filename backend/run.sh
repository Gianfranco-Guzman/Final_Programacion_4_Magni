#!/bin/bash

# Script para setup rápido del backend

set -e

echo "🚀 Food Store API - Setup Script"
echo "=================================="

# 1. Crear virtualenv si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando virtualenv..."
    python3 -m venv venv
fi

# 2. Activar virtualenv
echo "🔌 Activando virtualenv..."
source venv/bin/activate

# 3. Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -q -r requirements.txt

# 4. Crear base de datos
echo "🗄️ Creando tablas..."
python -c "from app.db.base import create_all_tables; create_all_tables(); print('✓ Tablas creadas')"

# 5. Poblar seed data
echo "🌱 Poblando datos iniciales..."
python -c "from app.db.seed import populate_seed_data; populate_seed_data()"

# 6. Iniciar servidor
echo "✅ Setup completado. Iniciando servidor..."
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
