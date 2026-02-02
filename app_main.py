import customtkinter as ctk
import psycopg2
from PIL import Image
import io
import threading
import os
from config import DB_CONFIG

class AmazonApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Amazon Product Manager")
        self.geometry("1200x750")
        ctk.set_appearance_mode("Dark")
        
        icon_path = "Amazon.ico"
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass
        
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=3) 
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(2, weight=1) 

        self.logo_label = ctk.CTkLabel(
            self.left_frame, 
            text="📦 Мои Товары", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 15))

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_list) 
        
        self.search_entry = ctk.CTkEntry(
            self.left_frame, 
            placeholder_text="🔍 Поиск (ASIN, Имя)...",
            textvariable=self.search_var,
            height=35
        )
        self.search_entry.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        self.scroll_list = ctk.CTkScrollableFrame(self.left_frame, label_text="Список товаров")
        self.scroll_list.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        self.refresh_btn = ctk.CTkButton(
            self.left_frame, 
            text="🔄 Обновить базу", 
            command=self.start_loading,
            height=40,
            fg_color="#3B8ED0", 
            hover_color="#36719F"
        )
        self.refresh_btn.grid(row=3, column=0, padx=20, pady=25)

        self.right_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)
        
        # 1. Контейнер для фото
        self.image_container = ctk.CTkLabel(self.right_frame, text="", height=320)
        self.image_container.pack(pady=(0, 30), fill="x")

        # 2. Таблица характеристик 
        self.info_frame = ctk.CTkFrame(self.right_frame, fg_color="#232323", corner_radius=10)
        self.info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.fields = {}
        # Формат: (Метка, Ключ, Номер строки, Цвет текста)
        rows_config = [
            ("НАЗВАНИЕ:", "name_val", 0, "white"),
            ("ASIN:", "asin_val", 1, "white"),
            ("separator", "", 2, ""), # Разделитель
            ("КОЛИЧЕСТВО:", "qty_val", 3, "white"),
            ("РАЗМЕРЫ:", "dims_val", 4, "white"),
            ("separator", "", 5, ""),
            ("ЦЕНА ПРОДАЖИ:", "sell_val", 6, "#4CAF50"), 
            ("ЦЕНА ЗАКУПКИ:", "buy_val", 7, "#F44336"),  
            ("МАРЖА:", "margin_val", 8, "#FF9800"),      
            ("separator", "", 9, ""),
            ("РЫНОК:", "market_val", 10, "gray80")
        ]

        current_row = 0
        for label, key, _, color in rows_config:
            if label == "separator":
                sep = ctk.CTkFrame(self.info_frame, height=2, fg_color="gray30")
                sep.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=20, pady=5)
            else:
                self.create_info_row(label, key, current_row, color)
            current_row += 1

        self.all_products = [] 
        
        self.start_loading()

    def create_info_row(self, label_text, key, row_idx, color="white"):
        icons = {
            "НАЗВАНИЕ:": "📄", "ASIN:": "🆔", "КОЛИЧЕСТВО:": "📊", 
            "РАЗМЕРЫ:": "📏", "ЦЕНА ПРОДАЖИ:": "💰", "ЦЕНА ЗАКУПКИ:": "📉", 
            "МАРЖА:": "💵", "РЫНОК:": "🌍"
        }
        icon = icons.get(label_text, "🔹")
        
        lbl = ctk.CTkLabel(
            self.info_frame, 
            text=f"{icon} {label_text}", 
            font=("Consolas", 14, "bold"), 
            text_color="gray70"
        )
        lbl.grid(row=row_idx, column=0, sticky="w", padx=25, pady=6)
        
        val = ctk.CTkEntry(
            self.info_frame, 
            state="readonly", 
            fg_color="transparent", 
            border_width=0,
            text_color=color,
            font=("Consolas", 15, "bold"),
            width=450
        )
        val.grid(row=row_idx, column=1, sticky="w", padx=10, pady=6)
        self.fields[key] = val

    def start_loading(self):
        self.refresh_btn.configure(state="disabled", text="Загрузка...")
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def fetch_data(self):
        try:
            params = DB_CONFIG.copy()
            if "pool_mode" in params: del params["pool_mode"]
            
            conn = psycopg2.connect(**params, sslmode="require")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT asin, name, quantity, dimensions, price_buy, price_sell, marketplace, region, image_data 
                FROM amazon_products ORDER BY asin
            """)
            rows = cursor.fetchall()
            conn.close()
            
            self.after(0, self.save_and_update, rows)
            
        except Exception as e:
            print(f"Error: {e}")
            self.after(0, lambda: self.refresh_btn.configure(text="Ошибка!", state="normal"))

    def save_and_update(self, rows):
        self.all_products = rows
        self.update_list(rows)
        self.refresh_btn.configure(state="normal", text="🔄 Обновить базу")

    def filter_list(self, *args):
        search_text = self.search_var.get().lower()
        if not search_text:
            self.update_list(self.all_products)
            return

        filtered = []
        for row in self.all_products:
            asin = str(row[0]).lower()
            name = str(row[1]).lower()
            if search_text in asin or search_text in name:
                filtered.append(row)
        
        self.update_list(filtered)

    def update_list(self, rows):
        for widget in self.scroll_list.winfo_children():
            widget.destroy()

        for row in rows:
            asin = row[0]
            name = row[1]
            
            btn = ctk.CTkButton(
                self.scroll_list, 
                text=f"{asin}\n{name[:25]}...", 
                command=lambda r=row: self.show_details(r),
                fg_color="transparent", 
                border_width=1,
                border_color="#555555",
                hover_color="#3A3A3A",
                text_color=("gray10", "gray90"),
                anchor="w",
                height=55,
                font=("Arial", 12)
            )
            btn.pack(fill="x", pady=3)

    def show_details(self, row):
        asin, name, qty, dims, p_buy, p_sell, market, region, img_bytes = row
        
        margin = (p_sell or 0) - (p_buy or 0)
        
        self.set_field("asin_val", asin)
        self.set_field("name_val", name)
        self.set_field("qty_val", f"{qty} шт.")
        self.set_field("dims_val", dims)
        self.set_field("sell_val", f"${p_sell:.2f}")
        self.set_field("buy_val", f"${p_buy:.2f}")
        self.set_field("margin_val", f"${margin:.2f}")
        self.set_field("market_val", f"{market} ({region})")

        
        if img_bytes:
            try:
                image = Image.open(io.BytesIO(img_bytes))
                base_h = 320
                ratio = base_h / float(image.size[1])
                new_w = int(float(image.size[0]) * float(ratio))
                
                image = image.resize((new_w, base_h), Image.Resampling.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=image, dark_image=image, size=(new_w, base_h))
                
                self.image_container.configure(image=ctk_img, text="")
            except:
                self.image_container.configure(image=None, text="⚠️ Ошибка фото")
        else:
            self.image_container.configure(image=None, text="🚫 Нет фото")

    def set_field(self, key, value):
        widget = self.fields[key]
        widget.configure(state="normal")
        widget.delete(0, "end")
        widget.insert(0, str(value))
        widget.configure(state="readonly")

if __name__ == "__main__":
    app = AmazonApp()
    app.mainloop()
