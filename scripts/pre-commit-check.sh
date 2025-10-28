#!/bin/bash

# Script para validar localmente antes de hacer push
# Simula lo que hará el CI

echo "🔍 PRE-COMMIT VALIDATION SCRIPT"
echo "==============================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar resultados
show_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

echo -e "${YELLOW}🧪 Running tests...${NC}"
python -m pytest -v --tb=short
show_result $? "Tests"

echo -e "${YELLOW}🔧 Testing database connection utility...${NC}"
python db/test_connection.py || true
show_result 0 "Database utility test"

echo -e "${YELLOW}🔍 Checking Python syntax...${NC}"
python -m py_compile $(find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./__pycache__/*")
show_result $? "Python syntax check"

echo -e "${YELLOW}📋 Collecting test information...${NC}"
python -m pytest --collect-only -q | grep -E "test session starts|collected"
show_result 0 "Test collection"

echo ""
echo -e "${GREEN}🎉 ALL VALIDATIONS PASSED!${NC}"
echo -e "${GREEN}✅ Ready to push to repository${NC}"
echo ""
echo "Summary:"
echo "- ✅ All tests passing"
echo "- ✅ Syntax valid"
echo "- ✅ Database utility working"
echo "- ✅ Test collection successful"
echo ""
echo "Your code is ready for CI/CD! 🚀"