import pandas as pd
import psycopg2
from PIL import Image
import io
import os
import re
from config import DB_CONFIG  

EXCEL_FILE = "products.xlsx"

def clean_currency(value):
    """Превращает '$40.00' или '40,00' в число 40.0"""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        clean = re.sub(r'[^\d.,]', '', value) 
        return float(clean.replace(',', '.')) if clean else 0.0
    return 0.0

def clean_path(path):
    """Убирает кавычки и лишние пробелы из пути"""
    if not isinstance(path, str): return ""
    return path.strip().strip('"').strip("'")

def process_image(path):
    path = clean_path(path)
    if not path or not os.path.exists(path):
        if path: print(f"⚠️ Файл не найден: {path}")
        return None
    
    try:
        with Image.open(path) as img:
            img = img.convert('RGB')
            img.thumbnail((1024, 1024))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=95)
            return buffer.getvalue()
    except Exception as e:
        print(f"⚠️ Ошибка фото {path}: {e}")
        return None

def upload_data():
    print("📂 Читаю Excel файл...")
    try:
        df = pd.read_excel(EXCEL_FILE)
        df.columns = df.columns.str.strip() 
    except Exception as e:
        print(f"❌ Ошибка чтения Excel: {e}")
        return

    print(f"🔌 Подключаюсь к базе {DB_CONFIG['host']}...")
    try:
        conn_params = DB_CONFIG.copy()
        if "pool_mode" in conn_params: 
            del conn_params["pool_mode"]
            
        conn = psycopg2.connect(**conn_params, sslmode="require")
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return

    print(f"🚀 Начинаю загрузку {len(df)} товаров...")

    for index, row in df.iterrows():
        img_bytes = process_image(row.get('image_path'))
        
        p_buy = clean_currency(row.get('price_buy'))
        p_sell = clean_currency(row.get('price_sell'))
        
        asin = str(row['asin']).strip()
        name = str(row['name']).strip()
        
        sql = """
            INSERT INTO amazon_products 
            (asin, name, quantity, dimensions, price_buy, price_sell, marketplace, region, image_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (asin) DO UPDATE SET
            name = EXCLUDED.name,
            quantity = EXCLUDED.quantity,
            price_sell = EXCLUDED.price_sell,
            price_buy = EXCLUDED.price_buy,
            image_data = COALESCE(EXCLUDED.image_data, amazon_products.image_data);
        """
        
        try:
            cursor.execute(sql, (
                asin, 
                name, 
                int(row.get('quantity', 0)), 
                str(row.get('dimensions', '')).strip(), 
                p_buy, 
                p_sell, 
                str(row.get('marketplace', '')).strip(), 
                str(row.get('region', '')).strip(),
                img_bytes
            ))
            print(f"✅ Загружен: {asin}")
        except Exception as e:
            print(f"❌ Ошибка на товаре {asin}: {e}")
            conn.rollback() 

    conn.commit()
    cursor.close()
    conn.close()
    print("\n🎉 Все готово! Данные в Supabase.")

if __name__ == "__main__":
    upload_data()
