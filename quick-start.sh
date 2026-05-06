#!/bin/bash
# FOOD STORE — Quick Start Helper
# Uso: bash quick-start.sh

set -e

echo "🍔 FOOD STORE — Inicializando Proyecto"
echo "======================================="

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detectar OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
    VENV_ACTIVATE="backend\\venv\\Scripts\\activate"
else
    OS="unix"
    VENV_ACTIVATE="backend/venv/bin/activate"
fi

echo -e "${BLUE}[1/4] Verificando Docker${NC}"
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Instalar desde https://www.docker.com/"
    exit 1
fi
echo -e "${GREEN}✅ Docker encontrado${NC}"

echo ""
echo -e "${BLUE}[2/4] Levantando PostgreSQL${NC}"
docker-compose up -d postgres
echo -e "${GREEN}✅ PostgreSQL corriendo en localhost:5432${NC}"

echo ""
echo -e "${BLUE}[3/4] Setup Backend${NC}"
mkdir -p backend
cd backend

if [ ! -d "venv" ]; then
    echo "Creando venv..."
    python -m venv venv
fi

# Activar venv
if [ "$OS" == "windows" ]; then
    source "venv/Scripts/activate"
else
    source venv/bin/activate
fi

# Instalar dependencias
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt no encontrado. Ejecutar primero la delegación del DÍA 1"
    exit 1
fi

echo "Instalando dependencias..."
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencias Backend instaladas${NC}"

cd ..

echo ""
echo -e "${BLUE}[4/4] Setup Frontend${NC}"
if [ ! -d "frontend" ]; then
    echo "Creando proyecto Vite..."
    npm create vite@latest frontend -- --template react-ts
fi

cd frontend

echo "Instalando dependencias..."
npm install -q --legacy-peer-deps

if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
VITE_API_BASE_URL=http://localhost:8000/api/v1
EOF
fi

cd ..

echo ""
echo "======================================="
echo -e "${GREEN}✅ Setup completado!${NC}"
echo ""
echo -e "${BLUE}Próximos pasos:${NC}"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
if [ "$OS" == "windows" ]; then
    echo "  venv\\Scripts\\activate"
else
    echo "  source venv/bin/activate"
fi
echo "  python -m alembic upgrade head"
echo "  uvicorn app.main:app --reload"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Accesos:"
echo "  Frontend: http://localhost:5173"
echo "  Backend: http://localhost:8000"
echo "  Swagger: http://localhost:8000/docs"
echo ""
echo -e "${GREEN}¡Listo para empezar!${NC}"
