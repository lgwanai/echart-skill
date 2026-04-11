import argparse
import sys
import os
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_repository
from validators import validate_table_name
from logging_config import get_logger, configure_logging

# Initialize logging
configure_logging()
logger = get_logger(__name__)

def clean_old_data(db_path, days=30):
    """
    Clean up tables and metadata that haven't been used in the specified number of days.
    """
    repo = get_repository(db_path)

    with repo.connection() as conn:
        # Check if metadata table exists
        exists_result = conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_name = '_data_skill_meta'"
        ).fetchone()
        if not exists_result:
            logger.info("未找到元数据表，无需清理")
            return

        # Calculate the cutoff date
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

        # Find tables to drop
        stale_records = conn.execute('''
            SELECT table_name, file_name, last_used_time
            FROM _data_skill_meta
            WHERE last_used_time < ?
        ''', [cutoff_date]).fetchall()

        if not stale_records:
            logger.info("未找到过期数据", days=days)
            return

        logger.info("开始清理过期数据", count=len(stale_records), days=days)

        for record in stale_records:
            table_name, file_name, last_used = record
            logger.info("删除过期表", table_name=table_name, file_name=file_name, last_used=last_used)

            # Validate table name before using in SQL to prevent injection
            try:
                validated_name = validate_table_name(table_name)
            except ValueError as e:
                logger.warning("跳过无效表名", table_name=table_name, reason=str(e))
                continue

            # Drop the actual table
            conn.execute(f"DROP TABLE IF EXISTS {validated_name}")

            # Remove from metadata
            conn.execute("DELETE FROM _data_skill_meta WHERE table_name = ?", [table_name])

        conn.commit()
        logger.info("清理完成", deleted_count=len(stale_records))

if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(description="Clean up old unused data from DuckDB")
    parser.add_argument("--db", default="workspace.duckdb", help="Path to DuckDB database file")
    parser.add_argument("--days", type=int, default=30, help="Number of days of inactivity before cleaning")

    args = parser.parse_args()

    try:
        clean_old_data(args.db, args.days)
    except Exception as e:
        logger.error("清理失败", error=str(e))
