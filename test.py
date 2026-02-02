import psycopg2
from config import DB_CONFIG  # Импортируем настройки из соседнего файла

try:
    print(f"🔌 Подключаюсь к {DB_CONFIG['host']}...")
    
    connection = psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        sslmode="require"
    )
    
    print("✅ УСПЕХ! База подключена.")
    
    cursor = connection.cursor()
    cursor.execute("SELECT NOW();")
    print("⏰ Время сервера:", cursor.fetchone()[0])
    
    cursor.close()
    connection.close()

except Exception as e:
    print(f"❌ Ошибка: {e}")
