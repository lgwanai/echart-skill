from types import SimpleNamespace


class FakeSQLConnector:
    def __init__(self):
        self.config = SimpleNamespace(type="postgresql")
        self.closed = False

    def execute_query(self, query):
        return [{"name": "张三", "phone": "13800001111"}]

    def close(self):
        self.closed = True


def _privacy_config(tmp_path, mask_pii=True):
    return SimpleNamespace(
        privacy=SimpleNamespace(
            enabled=True,
            read_only=True,
            audit_enabled=True,
            mask_pii=mask_pii,
            audit_log_path=str(tmp_path / "audit.log"),
        )
    )


def test_db_cli_execute_with_audit_uses_table_classification_object(monkeypatch, tmp_path):
    import scripts.config_manager as config_manager
    from scripts.db_cli import _execute_with_audit

    monkeypatch.setattr(config_manager, "get_config", lambda: _privacy_config(tmp_path))

    rows = _execute_with_audit(
        connector=FakeSQLConnector(),
        query="SELECT name, phone FROM users",
        profile_name="analytics",
    )

    assert rows == [{"name": "张三", "phone": "138****1111"}]


def test_db_connector_execute_query_uses_table_classification_object(monkeypatch, tmp_path):
    import scripts.config_manager as config_manager
    import scripts.db_config as db_config
    import scripts.db_connector as db_connector

    fake_profile = SimpleNamespace(type="postgresql")
    fake_config = SimpleNamespace(connections={"analytics": fake_profile})
    connector = FakeSQLConnector()

    monkeypatch.setattr(config_manager, "get_config", lambda: _privacy_config(tmp_path))
    monkeypatch.setattr(db_config, "load_effective_config", lambda: fake_config)
    monkeypatch.setattr(db_connector, "create_connector", lambda profile: connector)

    rows = db_connector.execute_query("analytics", "SELECT name, phone FROM users")

    assert rows == [{"name": "张三", "phone": "138****1111"}]
    assert connector.closed is True
