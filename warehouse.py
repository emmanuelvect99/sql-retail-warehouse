import logging
import os
import sqlite3
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("warehouse.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

DB_NAME = "retail_warehouse.db"


def init_db(db_path: str = DB_NAME, schema_path: str = "schema.sql") -> bool:
    if not os.path.exists(schema_path):
        logging.error(f"Fichier de schéma introuvable : '{schema_path}'")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    logging.info("✅ Base de données et schéma initialisés avec succès.")
    return True


def seed_data(db_path: str = DB_NAME):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    customers = [
        ("Alice", "Martin", "alice@example.com", "France"),
        ("Bob", "Smith", "bob@example.com", "USA"),
        ("Charlie", "Dupont", "charlie@example.com", "France"),
        ("David", "Kowalski", "david@example.com", "Germany"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO customers (first_name, last_name, email, country) VALUES (?, ?, ?, ?)",
        customers,
    )

    products = [
        ("Laptop Pro 15", "Electronics", 1200.00),
        ("Wireless Mouse", "Electronics", 25.50),
        ("Mechanical Keyboard", "Electronics", 85.00),
        ("Ergonomic Chair", "Furniture", 250.00),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO products (product_name, category, price) VALUES (?, ?, ?)",
        products,
    )

    sales = [
        (1, 1, 1, "2026-10-01"),
        (1, 2, 2, "2026-10-02"),
        (2, 4, 1, "2026-10-03"),
        (3, 1, 1, "2026-10-04"),
        (4, 3, 3, "2026-10-05"),
    ]
    cursor.executemany(
        "INSERT INTO sales (customer_id, product_id, quantity, sale_date) VALUES (?, ?, ?, ?)",
        sales,
    )

    conn.commit()
    conn.close()
    logging.info("✅ Données de démonstration insérées.")


def run_analytics(db_path: str = DB_NAME, output_csv: str = "sales_report.csv") -> pd.DataFrame:
    conn = sqlite3.connect(db_path)

    query = """
    WITH sales_summary AS (
        SELECT 
            c.country,
            p.category,
            p.product_name,
            SUM(s.quantity) AS total_units_sold,
            ROUND(SUM(s.quantity * p.price), 2) AS total_revenue
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        JOIN products p ON s.product_id = p.product_id
        GROUP BY c.country, p.category, p.product_name
    )
    SELECT 
        country,
        category,
        product_name,
        total_units_sold,
        total_revenue,
        RANK() OVER (PARTITION BY country ORDER BY total_revenue DESC) AS rank_in_country
    FROM sales_summary
    ORDER BY country, rank_in_country;
    """

    df_report = pd.read_sql_query(query, conn)
    conn.close()

    df_report.to_csv(output_csv, index=False)
    logging.info(f"📊 Rapport analytique exporté vers : '{output_csv}'")
    return df_report


if __name__ == "__main__":
    init_db()
    seed_data()
    df = run_analytics()
    print("\n--- Résultat du Rapport Analytique (SQL Window Functions) ---")
    print(df.to_string(index=False))
