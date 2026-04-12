"""
Database CLI Module.

Provides command-line interface for database operations:
- query: Execute SQL/MongoDB queries
- list-tables: Discover tables/collections
- describe-table: Get table/collection schema
- import: Import query results to DuckDB

Usage:
    python scripts/db_cli.py query <profile> "SELECT * FROM users"
    python scripts/db_cli.py list-tables <profile>
    python scripts/db_cli.py describe-table <profile> <table>
    python scripts/db_cli.py import <profile> "SELECT * FROM orders" --table-name orders_import
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_config import get_logger
from scripts.db_config import load_config, ConnectionProfile
from scripts.db_connector import create_connector, SQLConnector, MongoDBConnector
from scripts.db_schema import (
    discover_tables, describe_table, format_schema_table,
    list_mongo_databases, list_mongo_collections, infer_mongo_schema, format_mongo_schema
)

logger = get_logger(__name__)


def format_table_output(data: List[Dict[str, Any]]) -> str:
    """Format data as markdown table.
    
    Args:
        data: List of row dictionaries
        
    Returns:
        Markdown table string
    """
    if not data:
        return "No results."
    
    df = pd.DataFrame(data)
    return df.to_markdown(index=False)


def format_json_output(data: List[Dict[str, Any]]) -> str:
    """Format data as JSON.
    
    Args:
        data: List of row dictionaries
        
    Returns:
        JSON string
    """
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def get_profile(config_path: Optional[str], profile_name: str) -> ConnectionProfile:
    """Load and validate connection profile.
    
    Args:
        config_path: Optional config file path
        profile_name: Profile name to load
        
    Returns:
        ConnectionProfile instance
        
    Raises:
        KeyError: If profile not found
        SystemExit: On error (for CLI)
    """
    try:
        config = load_config(config_path)
        if profile_name not in config.connections:
            available = list(config.connections.keys())
            print(f"Error: Profile '{profile_name}' not found.")
            print(f"Available profiles: {', '.join(available)}")
            sys.exit(1)
        return config.connections[profile_name]
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Create db_connections.json or specify --config path.")
        sys.exit(1)


def cmd_query(args: argparse.Namespace) -> None:
    """Execute database query command."""
    profile = get_profile(args.config, args.profile)
    connector = create_connector(profile)
    
    try:
        if args.file:
            query_text = Path(args.file).read_text()
        else:
            query_text = args.query
        
        if connector.config.type == "mongodb":
            if args.collection is None:
                print("Error: --collection required for MongoDB queries")
                sys.exit(1)
            results = connector.execute_query(query_text, collection=args.collection)
        else:
            results = connector.execute_query(query_text)
        
        if args.output == "json":
            print(format_json_output(results))
        else:
            print(format_table_output(results))
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        connector.close()


def cmd_list_tables(args: argparse.Namespace) -> None:
    """Execute list-tables command."""
    profile = get_profile(args.config, args.profile)
    connector = create_connector(profile)
    
    try:
        if connector.config.type == "mongodb":
            if args.show_databases:
                databases = list_mongo_databases(connector)
                data = [{"database": db} for db in databases]
            else:
                collections = list_mongo_collections(connector, args.database)
                data = [{"collection": c} for c in collections]
        else:
            tables = discover_tables(connector, args.schema)
            data = [{"table": t} for t in tables]
        
        if args.output == "json":
            print(format_json_output(data))
        else:
            print(format_table_output(data))
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        connector.close()


def cmd_describe_table(args: argparse.Namespace) -> None:
    """Execute describe-table command."""
    profile = get_profile(args.config, args.profile)
    connector = create_connector(profile)
    
    try:
        if connector.config.type == "mongodb":
            schema = infer_mongo_schema(connector, args.table, sample_size=args.sample_size)
            if args.output == "json":
                print(format_json_output([{"field": k, "type": v} for k, v in schema.items()]))
            else:
                print(format_mongo_schema(schema))
        else:
            columns = describe_table(connector, args.table, args.schema)
            if args.output == "json":
                print(format_json_output(columns))
            else:
                print(format_schema_table(columns))
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        connector.close()


def cmd_import(args: argparse.Namespace) -> None:
    """Execute import command to DuckDB."""
    profile = get_profile(args.config, args.profile)
    connector = create_connector(profile)
    
    try:
        if args.file:
            query_text = Path(args.file).read_text()
        else:
            query_text = args.query
        
        table_name = args.table_name or generate_table_name(query_text)
        db_path = args.duckdb or "workspace.duckdb"
        
        ensure_duckdb_meta_table(db_path)
        
        if connector.config.type == "mongodb":
            if args.collection is None:
                print("Error: --collection required for MongoDB import")
                sys.exit(1)
            row_count = connector.execute_query_to_duckdb(
                query_text,
                table_name=table_name,
                collection=args.collection,
                db_path=db_path
            )
        else:
            row_count = connector.execute_query_to_duckdb(
                query_text,
                table_name=table_name,
                db_path=db_path
            )
        
        print(f"Imported {row_count} rows to DuckDB table: {table_name}")
        print(f"Database: {db_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        connector.close()


def generate_table_name(query: str) -> str:
    """Generate default table name from query.
    
    Args:
        query: SQL query string
        
    Returns:
        Generated table name
    """
    import re
    
    match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
    if match:
        source_table = match.group(1)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{source_table}_{timestamp}"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"query_result_{timestamp}"


def ensure_duckdb_meta_table(db_path: str) -> None:
    """Ensure _data_skill_meta table exists in DuckDB.
    
    Args:
        db_path: Path to DuckDB database
    """
    import duckdb
    
    conn = duckdb.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS _data_skill_meta (
            table_name VARCHAR PRIMARY KEY,
            source_type VARCHAR,
            source_path VARCHAR,
            row_count INTEGER,
            created_at TIMESTAMP
        )
    """)
    conn.close()


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="db-cli",
        description="Database connection and query CLI"
    )
    
    parser.add_argument(
        "--config",
        help="Path to db_connections.json (auto-discovered if not specified)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Execute database query")
    query_parser.add_argument("profile", help="Connection profile name")
    query_parser.add_argument("query", nargs="?", help="SQL query string")
    query_parser.add_argument("--file", "-f", help="Query file path")
    query_parser.add_argument("--output", "-o", choices=["table", "json"], default="table",
                              help="Output format")
    query_parser.add_argument("--collection", "-c", help="MongoDB collection name")
    query_parser.set_defaults(func=cmd_query)
    
    # List tables command
    list_parser = subparsers.add_parser("list-tables", help="List tables/collections")
    list_parser.add_argument("profile", help="Connection profile name")
    list_parser.add_argument("--schema", "-s", help="Schema name (PostgreSQL)")
    list_parser.add_argument("--database", "-d", help="Database name (MongoDB)")
    list_parser.add_argument("--show-databases", action="store_true",
                             help="Show databases instead of collections (MongoDB)")
    list_parser.add_argument("--output", "-o", choices=["table", "json"], default="table",
                             help="Output format")
    list_parser.set_defaults(func=cmd_list_tables)
    
    # Describe table command
    describe_parser = subparsers.add_parser("describe-table", help="Describe table/collection")
    describe_parser.add_argument("profile", help="Connection profile name")
    describe_parser.add_argument("table", help="Table/collection name")
    describe_parser.add_argument("--schema", "-s", help="Schema name (PostgreSQL)")
    describe_parser.add_argument("--sample-size", type=int, default=100,
                                 help="Sample size for MongoDB schema inference")
    describe_parser.add_argument("--output", "-o", choices=["table", "json"], default="table",
                                 help="Output format")
    describe_parser.set_defaults(func=cmd_describe_table)
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import query results to DuckDB")
    import_parser.add_argument("profile", help="Connection profile name")
    import_parser.add_argument("query", nargs="?", help="SQL query string")
    import_parser.add_argument("--file", "-f", help="Query file path")
    import_parser.add_argument("--table-name", "-t", help="Target table name in DuckDB")
    import_parser.add_argument("--duckdb", help="DuckDB database path (default: workspace.duckdb)")
    import_parser.add_argument("--collection", "-c", help="MongoDB collection name")
    import_parser.set_defaults(func=cmd_import)
    
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    """Main entry point.
    
    Args:
        argv: Command-line arguments (defaults to sys.argv)
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == "__main__":
    main()