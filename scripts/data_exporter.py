import argparse
import sqlite3
import pandas as pd
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validators import validate_table_name

def export_data(db_path, output_path, table_name=None, query=None):
    """
    Export data from SQLite to a CSV or Excel file.
    Either table_name or query must be provided.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")

    if not table_name and not query:
        raise ValueError("Either table_name or query must be provided.")

    conn = sqlite3.connect(db_path)

    try:
        if query:
            print(f"Executing query: {query}")
            df = pd.read_sql_query(query, conn)
        else:
            # Validate table name to prevent SQL injection
            table_name = validate_table_name(table_name)
            print(f"Reading table: {table_name}")
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

        # Determine export format based on file extension
        ext = os.path.splitext(output_path)[1].lower()

        # Ensure output directory exists
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        if ext == '.csv':
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"Successfully exported {len(df)} rows to CSV: {output_path}")
        elif ext in ['.xlsx', '.xls']:
            df.to_excel(output_path, index=False)
            print(f"Successfully exported {len(df)} rows to Excel: {output_path}")
        else:
            raise ValueError(f"Unsupported output format: {ext}. Please use .csv or .xlsx")

    except ValueError:
        # Re-raise validation errors (e.g., invalid table name)
        raise
    except Exception as e:
        print(f"Error during export: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export data from SQLite to CSV or Excel")
    parser.add_argument("output_path", help="Path to save the output file (.csv or .xlsx)")
    parser.add_argument("--db", default="workspace.db", help="Path to SQLite database file")
    parser.add_argument("--table", help="Name of the table to export")
    parser.add_argument("--query", help="SQL query to execute and export")

    args = parser.parse_args()
    export_data(args.db, args.output_path, args.table, args.query)
