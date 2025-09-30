# TallerIntegracion-Back

# Para ejecutar back, siempre activar entorno virtual, ya que ahí se encuentran las dependencias
python3 -m venv ~/.venvs/tallerint && source ~/.venvs/tallerint/bin/activate

# Instalar dependencias si es primera vez que se ejecuta
pip install -r "/Users/cristobalmartin/Desktop/Universidad/2025/Segundo Semestre/Taller de Integración/Código/TallerIntegracion-Back/requirements.txt"

# Ejecutar Back
uvicorn main:app --reload --port 8000

--------------------------------------------------------------------------------------------------------------

# Para correr Docker, ejecutar este comando en la terminal desde el repositorio del Back
docker compose up -d

--------------------------------------------------------------------------------------------------------------
# Para ingresar a pgAdmin
http://localhost:5050

# Credenciales de pgAdmin
Email: admin@uc.cl
Password: admin123

# Credenciales del servidor Postgres
Username: ucuser
Password: ucpass
Database: uchospital
