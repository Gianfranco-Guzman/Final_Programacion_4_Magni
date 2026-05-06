@echo off
REM Script para setup rápido del backend en Windows

setlocal enabledelayedexpansion

echo 🚀 Food Store API - Setup Script
echo ==================================

REM 1. Crear virtualenv si no existe
if not exist "venv" (
    echo 📦 Creando virtualenv...
    python -m venv venv
)

REM 2. Activar virtualenv
echo 🔌 Activando virtualenv...
call venv\Scripts\activate.bat

REM 3. Instalar dependencias
echo 📚 Instalando dependencias...
pip install -q -r requirements.txt

REM 4. Crear base de datos
echo 🗄️ Creando tablas...
python -c "from app.db.base import create_all_tables; create_all_tables(); print('✓ Tablas creadas')"

REM 5. Poblar seed data
echo 🌱 Poblando datos iniciales...
python -c "from app.db.seed import populate_seed_data; populate_seed_data()"

REM 6. Iniciar servidor
echo ✅ Setup completado. Iniciando servidor...
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
