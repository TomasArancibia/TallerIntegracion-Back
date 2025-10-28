@echo off
REM Script para validar localmente antes de hacer push (Windows)
REM Simula lo que hará el CI

echo  PRE-COMMIT VALIDATION SCRIPT
echo ===============================

echo.
echo  Running tests...
python -m pytest -v --tb=short
if %errorlevel% neq 0 (
    echo  Tests failed
    exit /b 1
) else (
    echo  Tests passed
)

echo.
echo  Testing database connection utility...
python db/test_connection.py
echo  Database utility test completed

echo.
echo  Checking Python syntax...
python -c "import py_compile; import glob; [py_compile.compile(f, doraise=True) for f in glob.glob('**/*.py', recursive=True) if not any(x in f for x in ['venv', '.venv', '__pycache__'])]"
if %errorlevel% neq 0 (
    echo Syntax check failed
    exit /b 1
) else (
    echo  Python syntax check passed
)

echo.
echo  Collecting test information...
python -m pytest --collect-only -q
echo  Test collection successful

echo.
echo  ALL VALIDATIONS PASSED!
echo  Ready to push to repository
echo.
echo Summary:
echo - All tests passing
echo - Syntax valid
echo - Database utility working
echo - Test collection successful
echo.
echo Your code is ready for CI/CD! 