from session import engine
from sqlalchemy import text  # 👈 Importar text()

def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))  # 👈 envolver en text()
            print("✅ Conexión exitosa a Postgres:", result.scalar())
    except Exception as e:
        print("❌ Error de conexión:", e)

if __name__ == "__main__":
    test_connection()