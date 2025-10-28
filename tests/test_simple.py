"""
Test simple para verificar que pytest funciona.
"""

def test_simple():
    """Test básico para verificar que pytest está funcionando."""
    assert 1 + 1 == 2
    
def test_python_version():
    """Test para verificar la versión de Python."""
    import sys
    assert sys.version_info.major >= 3
    
def test_imports_basicos():
    """Test para verificar que los imports básicos funcionan."""
    try:
        import os
        import sys
        assert True
    except ImportError:
        assert False, "No se pudieron importar módulos básicos"

def test_proyecto_structure():
    """Test para verificar la estructura del proyecto."""
    import os
    
    # Verificar que estamos en el directorio correcto
    current_dir = os.getcwd()
    expected_files = ['main.py', 'requirements.txt']
    
    for expected_file in expected_files:
        file_path = os.path.join(current_dir, expected_file)
        if not os.path.exists(file_path):
            # Intentar buscar en el directorio padre
            parent_dir = os.path.dirname(current_dir)
            file_path = os.path.join(parent_dir, expected_file)
            
        assert os.path.exists(file_path), f"No se encontró {expected_file}"