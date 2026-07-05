# AmazonInventoryHub

Desktop inventory manager for Amazon products. The application loads product
data from a PostgreSQL database, displays product details in a dark desktop UI,
supports search by ASIN/name, and stores product images as binary data.

## Stack

- Python
- CustomTkinter
- PostgreSQL / Supabase
- psycopg2
- pandas
- Pillow

## Features

- Desktop interface for product inventory review.
- Product search by ASIN or name.
- Product detail panel with quantity, dimensions, prices and margin.
- Image loading from PostgreSQL byte data.
- Excel import helper for loading product data into the database.
- Separate table-creation and connection-test scripts.

## Configuration

Create environment variables based on `.env.example`:

```bash
AMAZON_DB_HOST=
AMAZON_DB_PORT=5432
AMAZON_DB_NAME=postgres
AMAZON_DB_USER=
AMAZON_DB_PASSWORD=
AMAZON_DB_POOL_MODE=session
```

Do not store database credentials in the repository.

## Local Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app_main.py
```

Optional helpers:

```bash
python test.py
python create_table.py
python import_excel.py
```

## Project Status

Portfolio pet project. Good example of Python desktop UI, PostgreSQL
integration, image processing and inventory data management.
