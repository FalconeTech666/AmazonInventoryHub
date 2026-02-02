import psycopg2
from config import DB_CONFIG

def create_table():
    print(f"🔌 Подключаюсь к базе {DB_CONFIG['host']}...")
    
    params = DB_CONFIG.copy()
    if "pool_mode" in params: del params["pool_mode"]

    try:
        conn = psycopg2.connect(**params, sslmode="require")
        cursor = conn.cursor()
        
        create_query = """
        CREATE TABLE IF NOT EXISTS amazon_products (
            asin TEXT PRIMARY KEY,
            name TEXT,
            quantity INTEGER,
            dimensions TEXT,
            price_buy NUMERIC(10, 2),
            price_sell NUMERIC(10, 2),
            marketplace TEXT,
            region TEXT,
            image_data BYTEA
        );
        """
        
        cursor.execute(create_query)
        conn.commit()
        
        print("✅ Таблица 'amazon_products' успешно создана!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    create_table()
