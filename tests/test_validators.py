import pytest
import validators


def test_validate_table_name_valid():
    """Valid table names should pass."""
    assert validators.validate_table_name("users") == "users"
    assert validators.validate_table_name("order_items") == "order_items"
    assert validators.validate_table_name("Table1") == "Table1"
    assert validators.validate_table_name("a") == "a"


def test_validate_table_name_empty():
    """Empty table name should raise error."""
    with pytest.raises(ValueError, match="表名不能为空"):
        validators.validate_table_name("")


def test_validate_table_name_invalid_characters():
    """Table names with invalid characters should raise error."""
    invalid_names = [
        "'; DROP TABLE users;--",
        "table-name",
        "table.name",
        "table name",
        "table;drop",
    ]
    for name in invalid_names:
        with pytest.raises(ValueError, match="无效的表名"):
            validators.validate_table_name(name)


def test_validate_table_name_starts_with_number():
    """Table names starting with number should raise error."""
    with pytest.raises(ValueError, match="必须以字母开头"):
        validators.validate_table_name("123table")


def test_validate_table_name_reserved_word():
    """SQL reserved words should be rejected."""
    reserved = ["select", "DROP", "table", "DELETE", "insert"]
    for word in reserved:
        with pytest.raises(ValueError, match="SQL 保留字"):
            validators.validate_table_name(word)


def test_validate_table_name_too_long():
    """Table name exceeding max length should raise error."""
    long_name = "a" * 129
    with pytest.raises(ValueError, match="表名过长"):
        validators.validate_table_name(long_name)
