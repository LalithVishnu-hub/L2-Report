
import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'dashboard.db')

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def store_excel_data_to_db(df, table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create table if not exists (columns from df)
    columns = ', '.join([f'"{col}" TEXT' for col in df.columns])
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {columns}
        );
    """)
    # Insert data
    for _, row in df.iterrows():
        placeholders = ', '.join(['?'] * len(df.columns))
        col_names = ', '.join([f'"{col}"' for col in df.columns])
        sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})'
        cursor.execute(sql, tuple(str(x) if pd.notnull(x) else '' for x in row))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_data_from_db(table_name):
    conn = get_db_connection()
    df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
    conn.close()
    return df
