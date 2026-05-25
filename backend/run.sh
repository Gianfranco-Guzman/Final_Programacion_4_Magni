#!/bin/bash

set -e

echo "Food Store API"
echo "=================================="

if [ ! -d "venv" ]; then
    echo "Creando virtualenv..."
    python3 -m venv venv
fi

echo "Activando virtualenv..."
source venv/bin/activate

echo "Instalando dependencias..."
pip install -q -r requirements.txt

echo "Creando tablas..."
python -c "from app.db.base import create_all_tables; create_all_tables(); print('✓ Tablas creadas')"

echo "Poblando datos iniciales..."
python -c "from app.db.seed import populate_seed_data; populate_seed_data()"

echo "Iniciando servidor..."
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
