#!/bin/bash
# FOOD STORE — Setup Inicial
# Ejecutar: bash setup.sh

set -e

echo "🍔 FOOD STORE — Inicialización del Proyecto"
echo "==========================================="

# Backend
echo ""
echo "📦 Configurando Backend (Python)..."
mkdir -p backend
cd backend

# Python venv
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✅ venv creado"
fi

source venv/bin/activate

# Dependencias
cat > requirements.txt << 'EOF'
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlmodel==0.0.19
alembic==1.13.0
psycopg2-binary==2.9.9
pydantic-settings==2.2.1
pyjwt==2.8.1
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
mercadopago==2.3.0
slowapi==0.1.9
python-dotenv==1.0.0
EOF

pip install -r requirements.txt
echo "✅ Dependencias Backend instaladas"

# .env backend
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/foodstore

# JWT
JWT_SECRET=tu-super-secret-key-cambiar-en-produccion-1234567890
JWT_ALGORITHM=HS256

# API
API_TITLE=FOOD STORE API
API_VERSION=1.0.0
EOF
    echo "✅ .env Backend creado (⚠️ CAMBIAR JWT_SECRET en prod)"
fi

cd ..

# Frontend
echo ""
echo "📦 Configurando Frontend (React + Vite)..."

if [ ! -d "frontend" ]; then
    npm create vite@latest frontend -- --template react-ts
    cd frontend
    npm install
    echo "✅ Frontend scaffolding + dependencias"
else
    cd frontend
    npm install
    echo "✅ Dependencias Frontend actualizadas"
fi

# .env frontend
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
VITE_API_BASE_URL=http://localhost:8000/api/v1
EOF
    echo "✅ .env Frontend creado"
fi

# Dependencias extras
npm install \
    zustand \
    @tanstack/react-query \
    @tanstack/react-form \
    axios \
    recharts \
    --save

echo "✅ Dependencias Frontend instaladas"

cd ..

# .gitignore
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
venv/
.pytest_cache/

# Node
node_modules/
dist/
.vite/

# Env
.env
.env.local

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Local
ROADMAP.LOCAL.md
*.local.md
EOF
    echo "✅ .gitignore creado"
fi

echo ""
echo "==========================================="
echo "✅ Setup completado!"
echo ""
echo "Próximos pasos:"
echo ""
echo "1️⃣  Backend:"
echo "   cd backend"
echo "   source venv/bin/activate  (o venv\\Scripts\\activate en Windows)"
echo "   python -m alembic upgrade head  (cuando tengas modelos)"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2️⃣  Frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3️⃣  Abre:"
echo "   - http://localhost:5173 (Frontend)"
echo "   - http://localhost:8000/docs (Backend Swagger)"
echo ""
echo "📖 Lee ROADMAP.LOCAL.md para la guía día a día"
echo ""
