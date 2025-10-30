"""
Tests para verificar la estructura del proyecto y archivos principales.
"""
import os
import sys


class TestProyectoEstructura:
    """Tests para verificar la estructura del proyecto."""

    def test_archivos_principales_existen(self):
        """Verificar que los archivos principales del proyecto existen."""
        archivos_esperados = [
            'main.py',
            'requirements.txt',
            'pytest.ini',
        ]

        for archivo in archivos_esperados:
            assert os.path.exists(archivo), f"El archivo {archivo} no existe"

    def test_directorios_principales_existen(self):
        """Verificar que los directorios principales existen."""
        directorios_esperados = [
            'routers',
            'models',
            'db',
            'auth',
            'tests',
        ]

        for directorio in directorios_esperados:
            assert os.path.isdir(directorio), f"El directorio {directorio} no existe"

    def test_archivos_router_existen(self):
        """Verificar que los archivos de routers existen."""
        routers_esperados = [
            'routers/solicitudes.py',
            'routers/qr.py',
            'routers/admin.py',
            'routers/chat.py',
        ]

        for router in routers_esperados:
            assert os.path.exists(router), f"El router {router} no existe"

    def test_modelos_existen(self):
        """Verificar que los archivos de modelos existen."""
        assert os.path.exists('models/models.py'), "El archivo models/models.py no existe"
        assert os.path.exists('models/__init__.py'), "El archivo models/__init__.py no existe"

    def test_db_session_existe(self):
        """Verificar que el archivo de sesión de BD existe."""
        assert os.path.exists('db/session.py'), "El archivo db/session.py no existe"

    def test_auth_dependencies_existe(self):
        """Verificar que las dependencias de auth existen."""
        assert os.path.exists('auth/dependencies.py'), "El archivo auth/dependencies.py no existe"

    def test_requirements_tiene_contenido(self):
        """Verificar que requirements.txt tiene contenido."""
        assert os.path.exists('requirements.txt'), "requirements.txt no existe"
        
        with open('requirements.txt', 'r') as f:
            contenido = f.read().strip()
            assert len(contenido) > 0, "requirements.txt está vacío"
            assert 'fastapi' in contenido.lower(), "FastAPI no está en requirements.txt"
            assert 'sqlalchemy' in contenido.lower(), "SQLAlchemy no está en requirements.txt"

    def test_main_py_tiene_contenido(self):
        """Verificar que main.py tiene contenido básico."""
        assert os.path.exists('main.py'), "main.py no existe"

        with open('main.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            assert 'FastAPI' in contenido, "main.py no importa FastAPI"
            assert 'app = FastAPI' in contenido, "main.py no crea una instancia de FastAPI"

    def test_pytest_ini_existe_y_valido(self):
        """Verificar que pytest.ini existe y es válido."""
        assert os.path.exists('pytest.ini'), "pytest.ini no existe"
        
        with open('pytest.ini', 'r') as f:
            contenido = f.read()
            assert '[pytest]' in contenido, "pytest.ini no tiene la sección [pytest]"
            assert 'testpaths' in contenido, "pytest.ini no especifica testpaths"


class TestImportacionesBasicas:
    """Tests para verificar importaciones básicas del proyecto."""

    def test_importar_modulos_python_estandar(self):
        """Verificar que podemos importar módulos estándar de Python."""
        import os
        import sys
        import json
        import datetime
        import uuid

        assert True  # Si llegamos aquí, las importaciones funcionaron

    def test_sys_path_incluye_proyecto(self):
        """Verificar que el directorio del proyecto está en sys.path."""
        proyecto_dir = os.getcwd()
        assert proyecto_dir in sys.path or any(proyecto_dir in path for path in sys.path)

    def test_python_version_compatible(self):
        """Verificar que estamos usando una versión compatible de Python."""
        assert sys.version_info.major == 3, "Debe usar Python 3"
        assert sys.version_info.minor >= 8, "Debe usar Python 3.8 o superior"


class TestArchivosTest:
    """Tests para verificar la estructura de archivos de test."""

    def test_directorio_tests_existe(self):
        """Verificar que el directorio tests existe."""
        assert os.path.isdir('tests'), "El directorio tests no existe"

    def test_archivos_test_existen(self):
        """Verificar que los archivos de test principales existen."""
        archivos_test_esperados = [
            'tests/test_simple.py',
            'tests/test_main.py',
            'tests/test_endpoints_solicitudes.py',
            'tests/test_endpoints_qr.py',
            'tests/test_endpoints_admin.py',
            'tests/test_endpoints_chat.py',
        ]

        for archivo_test in archivos_test_esperados:
            assert os.path.exists(archivo_test), f"El archivo de test {archivo_test} no existe"

    def test_archivos_test_tienen_contenido(self):
        """Verificar que los archivos de test tienen contenido."""
        archivo_test = 'tests/test_simple.py'
        assert os.path.exists(archivo_test), f"{archivo_test} no existe"
        
        with open(archivo_test, 'r', encoding='utf-8') as f:
            contenido = f.read()
            assert len(contenido) > 0, f"{archivo_test} está vacío"
            assert 'def test_' in contenido, f"{archivo_test} no tiene funciones de test"

    def test_conftest_existe(self):
        """Verificar que existe conftest.py."""
        assert os.path.exists('tests/conftest.py'), "No existe conftest.py"
        
        with open('tests/conftest.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            assert 'TestClient' in contenido, "conftest.py no define TestClient"
