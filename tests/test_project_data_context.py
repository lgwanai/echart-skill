import argparse
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.db_manager as db_manager
import scripts.project_data_context as context_module
from scripts.db_config import ConnectionProfile
from scripts.db_connector import SQLConnector


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    (root / ".git").mkdir()
    return root


def _write_csv(project: Path, name: str = "orders.csv") -> Path:
    path = project / name
    path.write_text(
        "order_date,region,amount\n2026-01-01,North,10\n2026-01-02,South,20\n",
        encoding="utf-8",
    )
    return path


def test_register_file_writes_project_owned_structure_without_values(project: Path):
    source, path = context_module.register_file_source(_write_csv(project), project_root=project)

    assert path == project / ".echart-skill" / "data_sources.json"
    assert source["path"] == "orders.csv"
    assert source["access"] == {"kind": "file", "path": "orders.csv"}
    assert source["assets"][0]["content_summary"] == {
        "time_fields": ["order_date"],
        "measure_fields": ["amount"],
        "dimension_fields": ["region"],
        "identifier_fields": [],
    }
    payload = path.read_text(encoding="utf-8")
    assert "North" not in payload
    assert "South" not in payload
    assert '"host"' not in payload
    assert '"password"' not in payload
    assert context_module._safe_description("例如：张三") == ""
    assert context_module._safe_description("订单状态及业务含义") == "订单状态及业务含义"


def test_resolver_prefers_table_and_column_matches(project: Path, monkeypatch):
    monkeypatch.setattr(context_module, "_configured_profile_sources", lambda root: [])
    context_module.register_file_source(_write_csv(project), project_root=project)
    other = project / "employees.csv"
    other.write_text("employee_id,department,salary\n1,Ops,100\n", encoding="utf-8")
    context_module.register_file_source(other, project_root=project)

    result = context_module.resolve_sources("分析 department 的 salary 分布", project)

    assert result["status"] == "resolved"
    assert result["selected"]["id"] == "file:employees.csv"
    assert "salary" in result["selected"]["matched_columns"]


def test_resolver_does_not_silently_choose_ambiguous_sources(project: Path, monkeypatch):
    monkeypatch.setattr(context_module, "_configured_profile_sources", lambda root: [])
    context_module.register_file_source(_write_csv(project, "one.csv"), project_root=project)
    context_module.register_file_source(_write_csv(project, "two.csv"), project_root=project)

    result = context_module.resolve_sources("做一下数据分析", project)

    assert result["status"] == "ambiguous"
    assert result["selected"] is None
    assert len(result["candidates"]) == 2


def test_unindexed_configured_profile_requires_refresh(project: Path, monkeypatch):
    monkeypatch.setattr(
        context_module,
        "_configured_profile_sources",
        lambda root: [{
            "id": "database:finance",
            "kind": "database",
            "profile": "finance",
            "database": "ledger",
            "status": "needs_refresh",
            "assets": [],
        }],
    )

    result = context_module.resolve_sources("分析 finance 数据", project)

    assert result["status"] == "needs_refresh"
    assert result["selected"]["profile"] == "finance"


def test_changed_file_is_marked_stale(project: Path, monkeypatch):
    monkeypatch.setattr(context_module, "_configured_profile_sources", lambda root: [])
    data_file = _write_csv(project)
    context_module.register_file_source(data_file, project_root=project)
    data_file.write_text(data_file.read_text() + "2026-01-03,West,30\n", encoding="utf-8")

    result = context_module.resolve_sources("orders amount", project)

    assert result["status"] == "needs_refresh"
    assert result["selected"]["status"] == "stale"
    assert context_module.validate_context(project)


def test_refresh_database_persists_schema_without_connection_secrets(project: Path, monkeypatch):
    profile = ConnectionProfile(
        type="postgresql",
        host="private.example",
        database="warehouse",
        username="reader",
        password="super-secret",
        db_schema="analytics",
    )

    class FakeSQLConnector(SQLConnector):
        def __init__(self, config):
            self.config = config

        def connect(self):
            return None

        def close(self):
            return None

    import scripts.db_config as db_config
    import scripts.db_connector as db_connector
    import scripts.db_schema as db_schema

    monkeypatch.setattr(db_config, "load_effective_config", lambda cwd=None: SimpleNamespace(connections={"analytics": profile}))
    monkeypatch.setattr(db_connector, "create_connector", lambda value: FakeSQLConnector(value))
    monkeypatch.setattr(db_schema, "discover_tables", lambda connector, schema=None: ["fact_sales"])
    monkeypatch.setattr(
        db_schema,
        "describe_table",
        lambda connector, table, schema=None: [
            {"name": "sale_date", "type": "DATE", "nullable": False},
            {"name": "revenue", "type": "DECIMAL", "nullable": True},
        ],
    )
    monkeypatch.setattr(db_schema, "get_table_row_count", lambda connector, table, schema=None: 1234)

    source, context_path = context_module.refresh_database_source("analytics", project_root=project)

    assert source["profile"] == "analytics"
    assert source["assets"][0]["row_count"] == 1234
    assert source["assets"][0]["content_summary"]["measure_fields"] == ["revenue"]
    payload = context_path.read_text(encoding="utf-8")
    assert "private.example" not in payload
    assert "reader" not in payload
    assert "super-secret" not in payload


def test_connection_test_cli_refreshes_project_index(monkeypatch, project: Path, capsys):
    monkeypatch.setattr(db_manager, "test_connection", lambda name, cwd=None: (True, "connected"))
    calls = []

    def fake_refresh(name, **kwargs):
        calls.append((name, kwargs))
        return ({"indexed_asset_count": 2, "asset_count": 2}, project / ".echart-skill" / "data_sources.json")

    monkeypatch.setattr(context_module, "refresh_database_source", fake_refresh)
    args = argparse.Namespace(
        name="analytics",
        cwd=str(project),
        no_index=False,
        max_assets=50,
        skip_row_counts=False,
    )

    db_manager._cmd_test(args)

    assert calls[0][0] == "analytics"
    assert calls[0][1]["project_root"] == str(project)
    assert "项目数据源索引已刷新" in capsys.readouterr().out


def test_documented_cli_runs_directly_and_returns_clean_json(project: Path):
    data_file = _write_csv(project)
    register = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/project_data_context.py"),
            "--project-root",
            str(project),
            "register-file",
            str(data_file),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(register.stdout)["source_id"] == "file:orders.csv"

    resolve = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/project_data_context.py"),
            "--project-root",
            str(project),
            "resolve",
            "--query",
            "orders amount trend",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(resolve.stdout)["status"] == "resolved"
