#!/bin/bash

# Script para simular CI localmente con variables de entorno de testing

echo "🧪 SIMULACIÓN DE ENTORNO CI - TESTING LOCAL"
echo "==========================================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurar variables de entorno para testing
export DATABASE_URL="sqlite:///./test_ci.db"
export SUPABASE_URL="https://fake-supabase-url.supabase.co"
export SUPABASE_ANON_KEY="fake-anon-key-for-testing"
export SUPABASE_SERVICE_ROLE_KEY="fake-service-role-key-for-testing"
export OPENAI_API_KEY="sk-fake-openai-key-for-testing"

echo -e "${BLUE}🔧 Variables de entorno configuradas:${NC}"
echo "  DATABASE_URL: $DATABASE_URL"
echo "  SUPABASE_URL: $SUPABASE_URL"
echo "  SUPABASE_ANON_KEY: [OCULTO]"
echo "  SUPABASE_SERVICE_ROLE_KEY: [OCULTO]"
echo "  OPENAI_API_KEY: [OCULTO]"
echo

# Función para mostrar resultados
show_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

echo -e "${YELLOW}🐍 Verificando Python y dependencias...${NC}"
python --version
show_result $? "Python version check"

echo -e "${YELLOW}📦 Instalando dependencias de test...${NC}"
pip install pytest pytest-asyncio pytest-mock httpx pytest-cov > /dev/null 2>&1
show_result $? "Test dependencies installation"

echo -e "${YELLOW}🔗 Probando conexión a base de datos...${NC}"
python -c "
import os
from sqlalchemy import create_engine, text
try:
    engine = create_engine(os.environ['DATABASE_URL'])
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1 as test'))
        print('✅ Database connection successful!')
except Exception as e:
    print(f'⚠️ Database connection: {e}')
"

echo -e "${YELLOW}🧪 Ejecutando tests (como en CI)...${NC}"
python -m pytest -v --tb=short
test_result=$?
show_result $test_result "Tests execution"

echo -e "${YELLOW}🔍 Ejecutando análisis de código...${NC}"
python -c "
import py_compile
import glob
try:
    for file in glob.glob('**/*.py', recursive=True):
        if not any(x in file for x in ['venv', '.venv', '__pycache__', 'test_ci.db']):
            py_compile.compile(file, doraise=True)
    print('✅ Syntax check passed')
except Exception as e:
    print(f'❌ Syntax error: {e}')
"

echo -e "${YELLOW}📊 Recolectando información de tests...${NC}"
python -m pytest --collect-only -q | head -5

# Limpiar archivo de base de datos temporal
rm -f test_ci.db

echo
echo "=" * 50
echo -e "${BLUE}📊 RESUMEN DE SIMULACIÓN CI${NC}"
echo "=" * 50

if [ $test_result -eq 0 ]; then
    echo -e "${GREEN}🎉 ¡SIMULACIÓN EXITOSA!${NC}"
    echo -e "${GREEN}✅ Los tests pasarían en CI${NC}"
    echo -e "${GREEN}✅ Listo para push al repositorio${NC}"
    echo
    echo "Próximos pasos:"
    echo "1. git add ."
    echo "2. git commit -m 'Update: Fixed CI tests'"
    echo "3. git push"
    exit 0
else
    echo -e "${RED}⚠️ SIMULACIÓN FALLÓ${NC}"
    echo -e "${RED}❌ Los tests fallarían en CI${NC}"
    echo -e "${RED}❌ Revisar errores antes de push${NC}"
    echo
    echo "Acciones recomendadas:"
    echo "1. Revisar errores de tests arriba"
    echo "2. Corregir problemas encontrados"
    echo "3. Ejecutar este script nuevamente"
    exit 1
fi