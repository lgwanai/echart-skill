import argparse
import sqlite3
import pandas as pd
import os
import re
import warnings
import hashlib
from datetime import datetime

# Suppress openpyxl warnings about data validation
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

def calculate_md5(file_path):
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def init_meta_table(conn):
    """Initialize metadata table for tracking file imports and usage."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS _data_skill_meta (
            file_name TEXT,
            table_name TEXT PRIMARY KEY,
            md5_hash TEXT,
            import_time DATETIME,
            last_used_time DATETIME
        )
    ''')
    conn.commit()

def check_duplicate_import(conn, md5_hash):
    """Check if the file has already been imported with the same MD5. Returns a list of table names."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT table_name FROM _data_skill_meta 
        WHERE md5_hash = ?
    ''', (md5_hash,))
    results = cursor.fetchall()
    if results:
        tables = [r[0] for r in results]
        # Update last_used_time since we accessed it
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for t in tables:
            cursor.execute('''
                UPDATE _data_skill_meta 
                SET last_used_time = ? 
                WHERE table_name = ?
            ''', (now, t))
        conn.commit()
        return tables
    return None

def record_import(conn, file_name, table_name, md5_hash):
    """Record import metadata."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO _data_skill_meta 
        (file_name, table_name, md5_hash, import_time, last_used_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (file_name, table_name, md5_hash, now, now))
    conn.commit()

def clean_column_names(columns):
    """Clean column names to be valid SQLite identifiers."""
    cleaned = []
    seen = set()
    for col in columns:
        if pd.isna(col):
            col = "Unnamed"
        
        # Convert to string and clean
        col_str = str(col).strip()
        # Replace non-alphanumeric with underscore
        col_str = re.sub(r'\W+', '_', col_str)
        # Remove leading/trailing underscores
        col_str = col_str.strip('_')
        
        if not col_str or col_str.isdigit():
            col_str = f"col_{col_str}"
            
        # Ensure unique
        final_col = col_str
        counter = 1
        while final_col.lower() in [s.lower() for s in seen]:
            final_col = f"{col_str}_{counter}"
            counter += 1
            
        seen.add(final_col)
        cleaned.append(final_col)
    return cleaned

def find_header_row(df, max_rows=10):
    """Find the most likely header row by looking for the row with the most non-null values."""
    best_row_idx = 0
    max_non_nulls = 0
    
    for i in range(min(max_rows, len(df))):
        non_null_count = df.iloc[i].count()
        if non_null_count > max_non_nulls:
            max_non_nulls = non_null_count
            best_row_idx = i
            
    return best_row_idx

def unmerge_and_fill_excel(file_path, sheet_name=None):
    """
    Reads an Excel file, unmerges any merged cells, and fills them with the top-left value.
    Returns a pandas DataFrame.
    """
    import openpyxl
    wb = openpyxl.load_workbook(file_path, data_only=False)
    if sheet_name and sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
    else:
        sheet = wb.active
    
    # Extract merged cells ranges
    merged_ranges = list(sheet.merged_cells.ranges)
    
    # Iterate over merged cells and fill them with the top-left value
    for merged_cell in merged_ranges:
        min_col, min_row, max_col, max_row = merged_cell.bounds
        top_left_cell_value = sheet.cell(row=min_row, column=min_col).value
        
        # Unmerge the cells (optional, but good for clean structure)
        sheet.unmerge_cells(str(merged_cell))
        
        # Fill the unmerged cells with the top-left value
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                sheet.cell(row=row, column=col, value=top_left_cell_value)
                
    # Read into pandas
    data = sheet.values
    cols = next(data)
    df = pd.DataFrame(data, columns=cols)
    return df

def import_to_sqlite(file_path, db_path, table_name=None):
    """Import CSV/XLSX into SQLite, handling complex headers and merged cells."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    ext = os.path.splitext(file_path)[1].lower()
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    if not table_name:
        # Clean base name for table name
        table_name = re.sub(r'\W+', '_', base_name).strip('_')
        
    conn = sqlite3.connect(db_path)
    
    # Initialize metadata table
    init_meta_table(conn)
    
    # Calculate MD5
    file_md5 = calculate_md5(file_path)
    file_name = os.path.basename(file_path)
    
    # Check for duplicate import
    existing_tables = check_duplicate_import(conn, file_md5)
    if existing_tables:
        print(f"File '{file_name}' with identical content already imported as tables: {', '.join(existing_tables)}. Skipping import.")
        conn.close()
        return existing_tables

    cursor = conn.cursor()
    
    def get_unique_table_name(base_name):
        t_name = base_name
        counter = 1
        while True:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t_name,))
            if not cursor.fetchone():
                return t_name
            t_name = f"{base_name}_v{counter}"
            counter += 1

    imported_tables = []
    
    if ext == '.csv':
        target_table = get_unique_table_name(table_name)
        print(f"Importing {file_path} to table '{target_table}' in {db_path}...")
        
        chunk_size = 50000
        first_chunk = True
        sample_df = pd.read_csv(file_path, nrows=20, header=None)
        header_idx = find_header_row(sample_df)
        
        for chunk in pd.read_csv(file_path, skiprows=header_idx, chunksize=chunk_size):
            if first_chunk:
                chunk.columns = clean_column_names(chunk.columns)
                final_cols = chunk.columns
                chunk.to_sql(target_table, conn, index=False, if_exists='replace')
                first_chunk = False
            else:
                chunk.columns = final_cols
                chunk.to_sql(target_table, conn, index=False, if_exists='append')
                
        print(f"CSV import completed successfully.")
        record_import(conn, file_name, target_table, file_md5)
        imported_tables.append(target_table)
        
    elif ext in ['.xlsx', '.xls', '.et']:
        try:
            xl = pd.ExcelFile(file_path)
            sheet_names = xl.sheet_names
        except Exception:
            sheet_names = [0]
            
        for sheet_name in sheet_names:
            if len(sheet_names) > 1:
                safe_sheet_name = str(sheet_name).strip()
                safe_sheet_name = re.sub(r'\W+', '_', safe_sheet_name).strip('_')
                base_sheet_table = f"{table_name}_{safe_sheet_name}"
            else:
                base_sheet_table = table_name
                
            target_table = get_unique_table_name(base_sheet_table)
            print(f"Processing Excel sheet '{sheet_name}' to table '{target_table}'...")
            
            try:
                if ext == '.et':
                    raise ValueError("Skip unmerge for .et, fallback to pandas directly")
                df = unmerge_and_fill_excel(file_path, sheet_name=sheet_name if isinstance(sheet_name, str) else None)
                header_idx = find_header_row(df)
                if header_idx > 0:
                    new_header = df.iloc[header_idx]
                    df = df[header_idx+1:]
                    df.columns = new_header
            except Exception as e:
                print(f"Fallback to standard pandas read due to: {e}")
                sample_df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=20, header=None)
                header_idx = find_header_row(sample_df)
                df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=header_idx)
                
            df.dropna(how='all', inplace=True)
            df.dropna(axis=1, how='all', inplace=True)
            df.columns = clean_column_names(df.columns)
            df.to_sql(target_table, conn, index=False, if_exists='replace')
            print(f"Sheet '{sheet_name}' import completed. Loaded {len(df)} rows.")
            
            sheet_file_name = f"{file_name}::{sheet_name}" if len(sheet_names) > 1 else file_name
            record_import(conn, sheet_file_name, target_table, file_md5)
            imported_tables.append(target_table)

    elif ext == '.numbers':  # pragma: no cover - requires optional dependency
        try:
            from numbers_parser import Document
        except ImportError:
            raise ImportError("Please install 'numbers-parser' package to read .numbers files: pip install numbers-parser")

        print("Processing Mac Numbers file...")
        doc = Document(file_path)
        sheets = doc.sheets
        if not sheets:
            raise ValueError("No sheets found in the .numbers file.")

        for sheet in sheets:
            sheet_name = sheet.name
            if len(sheets) > 1:
                safe_sheet_name = str(sheet_name).strip()
                safe_sheet_name = re.sub(r'\W+', '_', safe_sheet_name).strip('_')
                base_sheet_table = f"{table_name}_{safe_sheet_name}"
            else:
                base_sheet_table = table_name

            target_table = get_unique_table_name(base_sheet_table)
            print(f"Processing Numbers sheet '{sheet_name}' to table '{target_table}'...")

            tables = sheet.tables
            if not tables:
                print(f"No tables found in sheet '{sheet_name}', skipping.")
                continue

            data = tables[0].rows(values_only=True)
            df = pd.DataFrame(data)

            df.dropna(how='all', inplace=True)
            df.dropna(axis=1, how='all', inplace=True)

            header_idx = find_header_row(df)
            if header_idx > 0:
                new_header = df.iloc[header_idx]
                df = df[header_idx+1:]
                df.columns = new_header
            elif len(df) > 0:
                df.columns = df.iloc[0]
                df = df[1:]

            df.columns = clean_column_names(df.columns)
            df.to_sql(target_table, conn, index=False, if_exists='replace')
            print(f"Sheet '{sheet_name}' import completed. Loaded {len(df)} rows.")

            sheet_file_name = f"{file_name}::{sheet_name}" if len(sheets) > 1 else file_name
            record_import(conn, sheet_file_name, target_table, file_md5)
            imported_tables.append(target_table)

    else:
        raise ValueError(f"Unsupported file format: {ext}")

    conn.close()
    return imported_tables

if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(description="Import Excel/CSV to SQLite")
    parser.add_argument("input_file", help="Path to the input Excel or CSV file")
    parser.add_argument("--db", default="workspace.db", help="Path to SQLite database file")
    parser.add_argument("--table", default=None, help="Target table name (auto-generated if not provided)")

    args = parser.parse_args()

    try:
        final_tables = import_to_sqlite(args.input_file, args.db, args.table)
        if isinstance(final_tables, list):
            print(f"SUCCESS: Data imported into tables: {', '.join(final_tables)}")
        else:
            print(f"SUCCESS: Data imported into table '{final_tables}'")
    except Exception as e:
        print(f"ERROR: {e}")
