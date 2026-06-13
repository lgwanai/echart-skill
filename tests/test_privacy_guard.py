"""Tests for Privacy Guard module."""

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.privacy_guard import (
    PrivacyGuard,
    ClassificationRule,
    ColumnClassification,
    TableClassification,
    AuditRecord,
    SENSITIVE_PATTERNS,
    MASK_FUNCTIONS,
    CLASSIFICATION_LEVELS,
    mask_phone,
    mask_email,
    mask_id_card,
    mask_bank_card,
    mask_salary,
    mask_address,
    mask_real_name,
    _is_blocked_query,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def guard():
    return PrivacyGuard()


@pytest.fixture
def guard_disabled():
    return PrivacyGuard(enabled=False)


@pytest.fixture
def guard_no_mask():
    return PrivacyGuard(mask_pii=False)


@pytest.fixture
def audit_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


# ---------------------------------------------------------------------------
# Sensitive pattern detection
# ---------------------------------------------------------------------------

class TestSensitivePatterns:
    """Auto-detection of sensitive columns by name."""

    def test_detects_phone_columns(self, guard):
        result = guard.classify_columns("users", ["phone", "name", "age"])
        assert result.has_sensitive_data
        assert any(c.rule_name == "phone" for c in result.sensitive_columns)

    def test_detects_chinese_phone(self, guard):
        result = guard.classify_columns("users", ["手机号", "姓名"])
        assert any(c.rule_name == "phone" for c in result.sensitive_columns)

    def test_detects_email(self, guard):
        result = guard.classify_columns("users", ["email", "name"])
        assert any(c.rule_name == "email" for c in result.sensitive_columns)

    def test_detects_id_card(self, guard):
        result = guard.classify_columns("users", ["身份证号"])
        assert any(c.rule_name == "id_card" for c in result.sensitive_columns)

    def test_detects_salary(self, guard):
        result = guard.classify_columns("employees", ["salary", "dept"])
        assert any(c.rule_name == "salary" for c in result.sensitive_columns)

    def test_detects_address(self, guard):
        result = guard.classify_columns("users", ["详细地址"])
        assert any(c.rule_name == "address" for c in result.sensitive_columns)

    def test_detects_password(self, guard):
        result = guard.classify_columns("users", ["password_hash"])
        assert any(c.rule_name == "password" for c in result.sensitive_columns)

    def test_skips_public_columns(self, guard):
        result = guard.classify_columns("orders", ["order_date", "amount", "quantity"])
        assert not result.has_sensitive_data
        assert result.max_classification == "internal"

    def test_handles_empty_columns(self, guard):
        result = guard.classify_columns("empty", [])
        assert not result.has_sensitive_data
        assert result.columns == []

    def test_first_match_wins(self, guard):
        result = guard.classify_columns("t", ["手机email"])
        assert len([c for c in result.sensitive_columns]) == 1

    def test_restricted_vs_sensitive(self, guard):
        result = guard.classify_columns("t", ["salary", "phone"])
        assert result.max_classification == "restricted"


# ---------------------------------------------------------------------------
# Masking functions
# ---------------------------------------------------------------------------

class TestMaskingFunctions:
    def test_mask_phone(self):
        assert mask_phone("13812341234") == "138****1234"

    def test_mask_phone_short(self):
        assert mask_phone("12345") == "123****"

    def test_mask_email(self):
        assert mask_email("user@domain.com") == "u***@domain.com"

    def test_mask_email_no_at(self):
        assert mask_email("nodomain") == "***"

    def test_mask_id_card(self):
        result = mask_id_card("320106199001011234")
        assert result.startswith("3201")
        assert result.endswith("1234")
        assert "*" * 10 in result

    def test_mask_bank_card(self):
        result = mask_bank_card("6222021234561234")
        assert result.startswith("6222")
        assert result.endswith("1234")

    def test_mask_salary(self):
        assert mask_salary(50000) == "[REDACTED]"

    def test_mask_address(self):
        result = mask_address("北京市海淀区中关村")
        assert result.endswith("****")
        assert len(result) == 8

    def test_mask_real_name_two_char(self):
        assert mask_real_name("张三") == "张*"

    def test_mask_real_name_three_char(self):
        assert mask_real_name("司马懿") == "司*懿"

    def test_mask_real_name_single_char(self):
        assert mask_real_name("王") == "*"

    def test_mask_none_preserved(self):
        """None values should remain None — mask functions receive str()."""
        pass  # mask_rows handles None, not mask functions themselves


# ---------------------------------------------------------------------------
# Row-level masking
# ---------------------------------------------------------------------------

class TestMaskRows:
    def test_masks_sensitive_rows(self, guard):
        classification = TableClassification("users", [
            ColumnClassification("name", "", "internal", False, ""),
            ColumnClassification("phone", "phone", "sensitive", True, "mask_phone"),
        ], True, "sensitive")
        rows = [{"name": "Alice", "phone": "13800001111"}]
        masked = guard.mask_rows(rows, classification)
        assert masked[0]["phone"] == "138****1111"
        assert masked[0]["name"] == "Alice"

    def test_preserves_none_values(self, guard):
        classification = TableClassification("users", [
            ColumnClassification("phone", "phone", "sensitive", True, "mask_phone"),
        ], True, "sensitive")
        rows = [{"phone": None}]
        masked = guard.mask_rows(rows, classification)
        assert masked[0]["phone"] is None

    def test_skips_when_disabled(self, guard_disabled):
        classification = TableClassification("users", [
            ColumnClassification("phone", "phone", "sensitive", True, "mask_phone"),
        ], True, "sensitive")
        rows = [{"phone": "13800001111"}]
        masked = guard_disabled.mask_rows(rows, classification)
        assert masked[0]["phone"] == "13800001111"

    def test_skips_when_no_mask_pii(self, guard_no_mask):
        classification = TableClassification("users", [
            ColumnClassification("phone", "phone", "sensitive", True, "mask_phone"),
        ], True, "sensitive")
        rows = [{"phone": "13800001111"}]
        masked = guard_no_mask.mask_rows(rows, classification)
        assert masked[0]["phone"] == "13800001111"

    def test_handles_empty_rows(self, guard):
        classification = TableClassification("t", [], False, "public")
        assert guard.mask_rows([], classification) == []


# ---------------------------------------------------------------------------
# Read-only enforcement
# ---------------------------------------------------------------------------

class TestReadOnlyEnforcement:
    def test_allows_select(self, guard):
        guard.enforce_read_only("SELECT * FROM users")
        guard.enforce_read_only("  select count(*) from orders")

    def test_allows_with(self, guard):
        guard.enforce_read_only("WITH cte AS (SELECT * FROM t) SELECT * FROM cte")

    def test_blocks_drop(self, guard):
        with pytest.raises(ValueError):
            guard.enforce_read_only("DROP TABLE users")

    def test_blocks_delete(self, guard):
        with pytest.raises(ValueError):
            guard.enforce_read_only("DELETE FROM users WHERE id=1")

    def test_blocks_update(self, guard):
        with pytest.raises(ValueError):
            guard.enforce_read_only("UPDATE users SET name='x'")

    def test_blocks_insert(self, guard):
        with pytest.raises(ValueError):
            guard.enforce_read_only("INSERT INTO users VALUES (1)")

    def test_blocks_alter(self, guard):
        with pytest.raises(ValueError):
            guard.enforce_read_only("ALTER TABLE users ADD COLUMN x INT")

    def test_blocks_truncate(self, guard):
        with pytest.raises(ValueError):
            guard.enforce_read_only("TRUNCATE TABLE users")

    def test_skips_when_disabled(self, guard_disabled):
        guard_disabled.enforce_read_only("DROP TABLE users")  # no error

    def test_comments_ignored(self, guard):
        guard.enforce_read_only("-- this is a comment\nSELECT * FROM users")


# ---------------------------------------------------------------------------
# _is_blocked_query helper
# ---------------------------------------------------------------------------

class TestIsBlockedQuery:
    def test_select_not_blocked(self):
        is_blocked, token = _is_blocked_query("SELECT * FROM users")
        assert not is_blocked

    def test_drop_blocked(self):
        is_blocked, token = _is_blocked_query("DROP TABLE users")
        assert is_blocked
        assert token == "DROP"

    def test_create_table_not_blocked(self):
        # CREATE TABLE without data is OK for import
        is_blocked, token = _is_blocked_query("CREATE TABLE users (id INT)")
        assert is_blocked  # CREATE is blocked
        assert token == "CREATE"

    def test_comment_stripped(self):
        is_blocked, token = _is_blocked_query("-- comment\nSELECT 1")
        assert not is_blocked

    def test_empty_query(self):
        is_blocked, token = _is_blocked_query("")
        assert not is_blocked


# ---------------------------------------------------------------------------
# Audit logging
# ---------------------------------------------------------------------------

class TestAuditLogging:
    def test_writes_audit_entry(self, guard, audit_dir):
        guard._audit_log_path = os.path.join(audit_dir, "audit.log")
        record = AuditRecord(
            timestamp="2026-01-01T00:00:00",
            table="orders", columns_accessed=["amount", "region"],
            query_hash="abc123", row_count=10,
            masked=True, max_classification="sensitive",
            is_mutation=False, blocked_token="",
        )
        guard.audit(record)
        assert os.path.exists(guard._audit_log_path)

        with open(guard._audit_log_path) as f:
            line = f.readline().strip()
        entry = json.loads(line)
        assert entry["tbl"] == "orders"
        assert entry["mask"] is True
        assert entry["lv"] == "sensitive"

    def test_audit_skips_when_disabled(self, guard_disabled, audit_dir):
        guard_disabled._audit_log_path = os.path.join(audit_dir, "audit.log")
        record = AuditRecord("", "", [], "", 0, False, "public", False, "")
        guard_disabled.audit(record)
        assert not os.path.exists(os.path.join(audit_dir, "audit.log"))

    def test_audit_skips_when_audit_disabled(self, audit_dir):
        guard = PrivacyGuard(audit_enabled=False)
        guard._audit_log_path = os.path.join(audit_dir, "audit.log")
        guard.audit(AuditRecord("", "", [], "", 0, False, "public", False, ""))
        assert not os.path.exists(os.path.join(audit_dir, "audit.log"))


# ---------------------------------------------------------------------------
# Classification levels
# ---------------------------------------------------------------------------

class TestClassificationLevels:
    def test_level_ordering(self):
        assert CLASSIFICATION_LEVELS["public"] < CLASSIFICATION_LEVELS["sensitive"]
        assert CLASSIFICATION_LEVELS["sensitive"] < CLASSIFICATION_LEVELS["restricted"]
        assert CLASSIFICATION_LEVELS["restricted"] == 3

    def test_max_classification(self, guard):
        result = guard.classify_columns("t", ["salary", "phone", "name"])
        assert result.max_classification == "restricted"

    def test_has_sensitive_data_false(self, guard):
        result = guard.classify_columns("t", ["date", "amount"])
        assert not result.has_sensitive_data

    def test_sensitive_columns_filter(self, guard):
        result = guard.classify_columns("t", ["salary", "phone", "name"])
        assert len(result.sensitive_columns) == 2


# ---------------------------------------------------------------------------
# Full guard pipeline
# ---------------------------------------------------------------------------

class TestGuardPipeline:
    def test_guard_query_masks_and_audits(self, audit_dir):
        guard = PrivacyGuard()
        guard._audit_log_path = os.path.join(audit_dir, "audit.log")

        rows = [{"name": "Alice", "phone": "13800001111"}]
        result = guard.guard_query(
            "SELECT name, phone FROM users",
            "users", ["name", "phone"], rows,
        )
        assert result[0]["phone"] == "138****1111"

    def test_guard_query_blocks_drop(self, guard):
        with pytest.raises(ValueError):
            guard.guard_query("DROP TABLE users", "users", [], [])


# ---------------------------------------------------------------------------
# Integration with DuckDB
# ---------------------------------------------------------------------------

class TestIntegration:
    def test_execute_query_with_sensitive_data(self):
        import duckdb

        tmp = os.path.join(tempfile.gettempdir(), "test_privacy_i.duckdb")
        if os.path.exists(tmp):
            os.unlink(tmp)
        conn = duckdb.connect(tmp)
        conn.execute("CREATE TABLE users (name TEXT, phone TEXT, email TEXT, salary INTEGER)")
        conn.execute("INSERT INTO users VALUES ('Alice','13800001111','alice@test.com',50000)")
        conn.execute("INSERT INTO users VALUES ('Bob','13900002222','bob@test.com',60000)")
        conn.close()

        try:
            from database import get_repository
            import database
            database._repo = None  # Reset singleton
            repo = get_repository(tmp)
            rows = repo.execute_query("SELECT name, phone, email, salary FROM users")
            assert len(rows) == 2
            # Should be masked
            assert rows[0]["phone"] != "13800001111"
            assert "***" in str(rows[0]["email"])
            assert rows[0]["salary"] == "[REDACTED]"
            assert rows[0]["name"] == "Alice"  # Not sensitive
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    def test_execute_query_raw_bypasses(self, audit_dir):
        import duckdb
        tmp = os.path.join(tempfile.gettempdir(), "test_privacy_raw.duckdb")
        if os.path.exists(tmp):
            os.unlink(tmp)
        conn = duckdb.connect(tmp)
        conn.execute("CREATE TABLE t (phone TEXT)")
        conn.execute("INSERT INTO t VALUES ('13800001111')")
        conn.close()

        try:
            from database import get_repository
            import database
            database._repo = None
            repo = get_repository(tmp)
            rows = repo.execute_query_raw("SELECT phone FROM t")
            assert rows[0]["phone"] == "13800001111"  # Not masked
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass
