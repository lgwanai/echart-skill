import pytest
import os
import json
import tempfile
import logging_config


def test_configure_logging_creates_directory():
    """configure_logging should create log directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "subdir", "test.log")
        logging_config.configure_logging(log_path)
        assert os.path.exists(os.path.dirname(log_path))


def test_get_logger_returns_structlog():
    """get_logger should return a configured structlog logger."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "test.log")
        logging_config.configure_logging(log_path)
        logger = logging_config.get_logger("test_module")
        assert logger is not None
        logger.info("test message", key="value")

        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "test message" in content
            # Verify JSON structure
            log_entry = json.loads(content.strip())
            assert "event" in log_entry
            assert "level" in log_entry


def test_log_output_is_json():
    """Log output should be valid JSON with Chinese characters."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "test.log")
        logging_config.configure_logging(log_path)
        logger = logging_config.get_logger("test")
        logger.info("测试消息", 操作="导入", 文件="数据.xlsx")

        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            log_entry = json.loads(content.strip())
            assert log_entry["event"] == "测试消息"
            assert log_entry["操作"] == "导入"
            assert log_entry["文件"] == "数据.xlsx"
