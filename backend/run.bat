@echo off
setlocal enabledelayedexpansion

echo Food Store API
echo ==================================

if not exist "venv" (
    echo Creando virtualenv...
    python -m venv venv
)

echo Activando virtualenv...
call venv\Scripts\activate.bat

echo Instalando dependencias...
pip install -q -r requirements.txt

echo Creando tablas...
python -c "from app.db.base import create_all_tables; create_all_tables(); print('✓ Tablas creadas')"

echo Poblando datos iniciales...
python -c "from app.db.seed import populate_seed_data; populate_seed_data()"

echo Iniciando servidor...
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
