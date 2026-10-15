import os
import sqlite3
import pytest
from warehouse import init_db, seed_data, run_analytics

TEST_DB = "test_warehouse.db"


@pytest.fixture
def setup_test_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    init_db(db_path=TEST_DB, schema_path="schema.sql")
    seed_data(db_path=TEST_DB)

    yield TEST_DB

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_database_creation_and_seeding(setup_test_db):
    conn = sqlite3.connect(setup_test_db)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM customers")
    customer_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sales")
    sales_count = cursor.fetchone()[0]

    conn.close()

    assert customer_count == 4
    assert sales_count == 5


def test_analytics_query(setup_test_db):
    test_csv = "test_sales_report.csv"
    df_report = run_analytics(db_path=setup_test_db, output_csv=test_csv)

    assert not df_report.empty
    assert "total_revenue" in df_report.columns
    assert "rank_in_country" in df_report.columns
    assert os.path.exists(test_csv)

    if os.path.exists(test_csv):
        os.remove(test_csv)
