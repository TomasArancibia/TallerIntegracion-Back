# Configuración de CI/CD para TallerIntegracion-Back

## GitHub Actions Workflows

Este proyecto tiene 2 workflows de GitHub Actions:

### 1. `backend.yml` - CI/CD Principal
- **Trigger**: Push y PR a branch `main`
- **Funciones**:
  - Ejecuta tests en Python 3.11 y 3.12
  - Solo hace deploy si los tests pasan
  - Deploy automático a Render

### 2. `test.yml` - Tests Extensivos
- **Trigger**: Push y PR a cualquier branch
- **Funciones**:
  - Tests en múltiples versiones de Python
  - Análisis de calidad de código
  - Escaneo de seguridad
  - Reportes detallados

## Configuración de Secrets

Para que el CI/CD funcione, necesitas configurar estos secrets en GitHub:

1. Ve a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Agrega estos secrets:

```
RENDER_DEPLOY_HOOK: [URL del webhook de Render para deploy automático]
```

## Personalización

### Cambiar versiones de Python
Edita la matriz en los workflows:
```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]  # Agrega/quita versiones aquí
```

### Modificar triggers
Cambia las condiciones `on:` en los workflows:
```yaml
on:
  push:
    branches: [ main, develop ]  # Agrega más branches
  pull_request:
    branches: [ main ]
```

### Agregar más validaciones
En `test.yml` puedes agregar más pasos:
```yaml
- name: Nueva validación
  run: |
    echo "Ejecutar nueva validación..."
```

## Scripts Locales

### Windows
```cmd
scripts\pre-commit-check.bat
```

### Linux/Mac
```bash
chmod +x scripts/pre-commit-check.sh
./scripts/pre-commit-check.sh
```

## Monitoreo

- Los badges en README.md muestran el estado actual
- GitHub Actions tab muestra historial detallado
- Notificaciones automáticas en caso de fallos

## Troubleshooting

### Tests fallan en CI pero pasan localmente
1. Verificar versión de Python
2. Verificar dependencias en requirements.txt
3. Verificar variables de entorno

### Deploy falla
1. Verificar RENDER_DEPLOY_HOOK secret
2. Verificar que los tests pasen primero
3. Revisar logs en Render

### Workflows no se ejecutan
1. Verificar que los archivos estén en `.github/workflows/`
2. Verificar sintaxis YAML
3. Verificar permisos del repositorio