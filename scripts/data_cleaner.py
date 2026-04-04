import sqlite3
import argparse
import sys
import os
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validators import validate_table_name

def clean_old_data(db_path, days=30):
    """
    Clean up tables and metadata that haven't been used in the specified number of days.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if metadata table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_data_skill_meta'")
    if not cursor.fetchone():
        print("No metadata table found. Nothing to clean.")
        conn.close()
        return

    # Calculate the cutoff date
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    
    # Find tables to drop
    cursor.execute('''
        SELECT table_name, file_name, last_used_time 
        FROM _data_skill_meta 
        WHERE last_used_time < ?
    ''', (cutoff_date,))
    
    stale_records = cursor.fetchall()
    
    if not stale_records:
        print(f"No data older than {days} days found. Clean up complete.")
        conn.close()
        return
        
    print(f"Found {len(stale_records)} tables older than {days} days. Starting cleanup...")
    
    for record in stale_records:
        table_name, file_name, last_used = record
        print(f"Dropping table '{table_name}' (imported from '{file_name}', last used: {last_used})")

        # Validate table name before using in SQL to prevent injection
        try:
            validated_name = validate_table_name(table_name)
        except ValueError as e:
            print(f"跳过无效表名 '{table_name}': {e}")
            continue

        # Drop the actual table
        cursor.execute(f"DROP TABLE IF EXISTS {validated_name}")

        # We should also try to drop any derived tables (views or _vX tables)
        # that might have been created from this, but this requires parsing the name
        # For safety, we only drop the original imported table for now

        # Remove from metadata
        cursor.execute("DELETE FROM _data_skill_meta WHERE table_name = ?", (table_name,))
        
    conn.commit()
    conn.close()
    print("Cleanup completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up old unused data from SQLite")
    parser.add_argument("--db", default="workspace.db", help="Path to SQLite database file")
    parser.add_argument("--days", type=int, default=30, help="Number of days of inactivity before cleaning")
    
    args = parser.parse_args()
    
    try:
        clean_old_data(args.db, args.days)
    except Exception as e:
        print(f"ERROR: {e}")
