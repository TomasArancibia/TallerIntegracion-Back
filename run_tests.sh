#!/bin/bash

# Script para ejecutar tests del backend
# Uso: ./run_tests.sh [opciones]

set -e  # Salir en caso de error

echo "🧪 Iniciando tests del backend TallerIntegracion..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  -h, --help              Mostrar esta ayuda"
    echo "  -a, --all               Ejecutar todos los tests (default)"
    echo "  -u, --unit              Ejecutar solo tests unitarios"
    echo "  -i, --integration       Ejecutar solo tests de integración"
    echo "  -c, --coverage          Ejecutar tests con reporte de cobertura"
    echo "  -f, --file FILE         Ejecutar tests de un archivo específico"
    echo "  -v, --verbose           Ejecutar con output verbose"
    echo "  -x, --exitfirst         Parar en el primer error"
    echo "  --install               Instalar dependencias de testing"
    echo ""
    echo "Ejemplos:"
    echo "  $0 --all                # Todos los tests"
    echo "  $0 --coverage           # Tests con cobertura"
    echo "  $0 --file test_solicitudes.py  # Solo tests de solicitudes"
    echo "  $0 --verbose --exitfirst        # Verbose y parar en primer error"
}

# Función para instalar dependencias
install_deps() {
    echo -e "${BLUE}📦 Instalando dependencias de testing...${NC}"
    
    if [ -f "requirements-test.txt" ]; then
        pip install -r requirements-test.txt
        echo -e "${GREEN}✅ Dependencias de testing instaladas${NC}"
    else
        echo -e "${YELLOW}⚠️  Archivo requirements-test.txt no encontrado${NC}"
        echo -e "${BLUE}Instalando dependencias básicas...${NC}"
        pip install pytest pytest-asyncio pytest-cov httpx pytest-mock
    fi
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Dependencias principales instaladas${NC}"
    fi
}

# Función para verificar instalación
check_deps() {
    if ! python -c "import pytest" 2>/dev/null; then
        echo -e "${RED}❌ pytest no está instalado${NC}"
        echo -e "${YELLOW}💡 Ejecuta: $0 --install${NC}"
        exit 1
    fi
}

# Función para ejecutar tests
run_tests() {
    local test_args="$1"
    local test_description="$2"
    
    echo -e "${BLUE}🏃 Ejecutando $test_description...${NC}"
    echo "Comando: pytest $test_args"
    echo ""
    
    if pytest $test_args; then
        echo ""
        echo -e "${GREEN}✅ $test_description completados exitosamente!${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}❌ $test_description fallaron${NC}"
        return 1
    fi
}

# Función para mostrar estadísticas
show_stats() {
    echo ""
    echo -e "${BLUE}📊 Estadísticas de archivos de test:${NC}"
    
    if [ -d "tests" ]; then
        echo "Archivos de test encontrados:"
        find tests -name "test_*.py" -exec basename {} \; | sort
        echo ""
        echo "Total de archivos: $(find tests -name "test_*.py" | wc -l)"
        echo "Total de funciones de test: $(grep -r "def test_" tests/ | wc -l)"
    else
        echo -e "${RED}❌ Directorio 'tests' no encontrado${NC}"
        exit 1
    fi
}

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ No se encontró main.py. Asegúrate de estar en el directorio del backend.${NC}"
    exit 1
fi

# Crear directorio tests si no existe
if [ ! -d "tests" ]; then
    echo -e "${YELLOW}⚠️  Directorio 'tests' no encontrado. Creándolo...${NC}"
    mkdir -p tests
fi

# Procesar argumentos
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    --install)
        install_deps
        exit 0
        ;;
    -a|--all|"")
        check_deps
        show_stats
        run_tests "tests/" "todos los tests"
        ;;
    -u|--unit)
        check_deps
        run_tests "tests/ -m 'not integration'" "tests unitarios"
        ;;
    -i|--integration)
        check_deps
        run_tests "tests/test_integration.py" "tests de integración"
        ;;
    -c|--coverage)
        check_deps
        run_tests "tests/ --cov=. --cov-report=html --cov-report=term-missing" "tests con cobertura"
        echo ""
        echo -e "${GREEN}📊 Reporte de cobertura generado en: htmlcov/index.html${NC}"
        ;;
    -f|--file)
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Debes especificar un archivo${NC}"
            echo "Uso: $0 --file test_solicitudes.py"
            exit 1
        fi
        check_deps
        run_tests "tests/$2" "tests del archivo $2"
        ;;
    -v|--verbose)
        check_deps
        run_tests "tests/ -v" "tests en modo verbose"
        ;;
    -x|--exitfirst)
        check_deps
        run_tests "tests/ -x" "tests (parar en primer error)"
        ;;
    *)
        echo -e "${RED}❌ Opción desconocida: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

# Si llegamos aquí, los tests fueron exitosos
echo ""
echo -e "${GREEN}🎉 ¡Testing completado!${NC}"

# Mostrar comandos útiles
echo ""
echo -e "${BLUE}💡 Comandos útiles:${NC}"
echo "  Ver cobertura HTML:     open htmlcov/index.html"
echo "  Tests específicos:      pytest tests/test_solicitudes.py::TestSolicitudesRouter::test_crear_solicitud"
echo "  Debug mode:             pytest tests/ -s --pdb"
echo "  Parallel execution:     pytest tests/ -n auto"
echo ""