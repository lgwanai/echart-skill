"""Tests for database connection manager (scripts/db_manager.py)."""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import module (not individual constants to avoid capturing pre-patch values)
import scripts.db_manager as dbm
import scripts.db_config as dbcfg


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_skill_root(tmp_path, monkeypatch):
    """Override skill root constants in both db_manager and db_config to use temp dir."""
    global_path = tmp_path / "references" / "db_connections.txt"
    index_path = tmp_path / "references" / "project_db_index.json"

    # Patch db_manager globals
    monkeypatch.setattr(dbm, "GLOBAL_DB_CONFIG_PATH", global_path)
    monkeypatch.setattr(dbm, "PROJECT_INDEX_PATH", index_path)
    monkeypatch.setattr(dbm, "PROJECT_ROOT", tmp_path)

    # Patch db_config globals so load_global_config / load_effective_config use temp
    monkeypatch.setattr(dbcfg, "GLOBAL_CONFIG_PATH", global_path)
    monkeypatch.setattr(dbcfg, "SKILL_ROOT", tmp_path)

    # Create references directory
    (tmp_path / "references").mkdir(parents=True, exist_ok=True)

    return tmp_path


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory with .echart-skill/."""
    proj = tmp_path / "my_project"
    proj.mkdir(parents=True)
    (proj / dbm.PROJECT_DB_DIRNAME).mkdir(parents=True, exist_ok=True)
    return proj


# ---------------------------------------------------------------------------
# Tests: config path helpers
# ---------------------------------------------------------------------------

class TestConfigFileInit:
    """Tests for _init_db_config_file."""

    def test_creates_file_if_missing(self, tmp_path):
        path = tmp_path / "test_config.txt"
        dbm._init_db_config_file(path)
        assert path.exists()

    def test_does_not_overwrite_existing(self, tmp_path):
        path = tmp_path / "test_config.txt"
        path.write_text("existing content")
        dbm._init_db_config_file(path)
        assert path.read_text() == "existing content"

    def test_creates_parent_dirs(self, tmp_path):
        path = tmp_path / "deep" / "nested" / "test_config.txt"
        dbm._init_db_config_file(path)
        assert path.exists()


class TestParseAndFormat:
    """Tests for _parse_connection_config and _format_connection_config."""

    def test_parse_empty_file(self, tmp_path):
        path = tmp_path / "empty.txt"
        path.write_text("")
        result = dbm._parse_connection_config(path)
        assert result == {}

    def test_parse_nonexistent_file(self, tmp_path):
        path = tmp_path / "nonexistent.txt"
        result = dbm._parse_connection_config(path)
        assert result == {}

    def test_parse_valid_config(self, tmp_path):
        path = tmp_path / "config.txt"
        path.write_text(
            "[connections.my_pg]\n"
            "type=postgresql\n"
            "host=localhost\n"
            "port=5432\n"
            "database=analytics\n"
            "username=reader\n"
            "password=${PG_PASS}\n"
        )
        result = dbm._parse_connection_config(path)
        assert "my_pg" in result
        assert result["my_pg"]["type"] == "postgresql"
        assert result["my_pg"]["host"] == "localhost"
        assert result["my_pg"]["port"] == 5432

    def test_parse_multiple_connections(self, tmp_path):
        path = tmp_path / "config.txt"
        path.write_text(
            "[connections.pg1]\n"
            "type=postgresql\n"
            "host=host1\n"
            "\n"
            "[connections.pg2]\n"
            "type=mysql\n"
            "host=host2\n"
        )
        result = dbm._parse_connection_config(path)
        assert len(result) == 2
        assert "pg1" in result
        assert "pg2" in result

    def test_format_and_parse_roundtrip(self, tmp_path):
        """Written config can be parsed back."""
        connections = {
            "test_db": {
                "type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "test",
            }
        }
        formatted = dbm._format_connection_config(connections)
        path = tmp_path / "roundtrip.txt"
        path.write_text(formatted)
        parsed = dbm._parse_connection_config(path)
        assert "test_db" in parsed
        assert parsed["test_db"]["type"] == "postgresql"


class TestConnectionInfo:
    """Tests for _connection_to_info."""

    def test_basic_conversion(self):
        profile = {"type": "postgresql", "host": "localhost", "port": 5432, "database": "test"}
        info = dbm._connection_to_info("test", profile, "global")
        assert info.name == "test"
        assert info.type == "postgresql"
        assert info.host == "localhost"
        assert info.port == 5432
        assert info.database == "test"
        assert info.level == "global"
        assert not info.has_password

    def test_default_port(self):
        profile = {"type": "postgresql"}
        info = dbm._connection_to_info("test", profile)
        assert info.port == 5432

        profile2 = {"type": "mysql"}
        info2 = dbm._connection_to_info("test2", profile2)
        assert info2.port == 3306

    def test_has_password_true(self):
        profile = {"type": "postgresql", "password": "${PG_PASS}"}
        info = dbm._connection_to_info("test", profile)
        assert info.has_password


# ---------------------------------------------------------------------------
# Tests: Project index
# ---------------------------------------------------------------------------

class TestProjectIndex:
    """Tests for project index operations."""

    def test_load_empty_index(self, temp_skill_root):
        items = dbm._load_project_index()
        assert items == []

    def test_save_and_load(self, temp_skill_root):
        items = [{"project_dir": "/test", "config_path": "/test/config.txt"}]
        dbm._save_project_index(items)
        loaded = dbm._load_project_index()
        assert len(loaded) == 1

    def test_record_project(self, temp_skill_root, temp_project):
        config_path = temp_project / dbm.PROJECT_DB_DIRNAME / dbm.PROJECT_DB_FILENAME
        config_path.write_text("[connections.test]\ntype=postgresql\n")
        dbm._record_project(temp_project, config_path)

        items = dbm._load_project_index()
        assert len(items) == 1
        assert items[0]["project_dir"] == str(temp_project.resolve())
        assert items[0]["config_path"] == str(config_path.resolve())

    def test_active_project_records(self, temp_skill_root, temp_project, monkeypatch):
        """Active records only include projects containing cwd."""
        config_path = temp_project / dbm.PROJECT_DB_DIRNAME / dbm.PROJECT_DB_FILENAME
        config_path.write_text("[connections.test]\ntype=postgresql\n")
        dbm._record_project(temp_project, config_path)

        # When cwd is inside the project, it should be active
        monkeypatch.chdir(temp_project)
        active = dbm._active_project_records(str(temp_project))
        assert len(active) == 1

        # When cwd is unrelated, no active records
        unrelated = temp_project.parent / "other"
        unrelated.mkdir(exist_ok=True)
        active2 = dbm._active_project_records(str(unrelated))
        assert len(active2) == 0


# ---------------------------------------------------------------------------
# Tests: add_connection
# ---------------------------------------------------------------------------

class TestAddConnection:
    """Tests for add_connection function."""

    def _global_config_path(self):
        """Get current (possibly monkeypatched) global config path."""
        return dbm.GLOBAL_DB_CONFIG_PATH

    def test_add_global_postgresql(self, temp_skill_root):
        info = dbm.add_connection(
            name="analytics",
            db_type="postgresql",
            host="localhost",
            port=5432,
            database="analytics_db",
            username="reader",
            password="${PG_PASS}",
            level="global",
        )
        assert info.name == "analytics"
        assert info.type == "postgresql"
        assert info.level == "global"
        assert self._global_config_path().exists()

        # Verify file content
        content = self._global_config_path().read_text()
        assert "analytics" in content
        assert "postgresql" in content

    def test_add_global_with_connection_string(self, temp_skill_root):
        info = dbm.add_connection(
            name="mongo",
            db_type="mongodb",
            connection_string="mongodb://localhost:27017/test",
            level="global",
        )
        assert info.type == "mongodb"
        content = self._global_config_path().read_text()
        assert "connection_string" in content

    def test_add_project_level(self, temp_skill_root, temp_project, monkeypatch):
        monkeypatch.chdir(temp_project)
        info = dbm.add_connection(
            name="proj_db",
            db_type="mysql",
            host="db.internal",
            database="production",
            level="project",
            project_dir=str(temp_project),
        )
        assert info.level == "project"
        config_path = temp_project / dbm.PROJECT_DB_DIRNAME / dbm.PROJECT_DB_FILENAME
        assert config_path.exists()
        content = config_path.read_text()
        assert "proj_db" in content

    def test_add_default_port_postgresql(self, temp_skill_root):
        info = dbm.add_connection(
            name="pg_default",
            db_type="postgresql",
            host="localhost",
            database="test",
            level="global",
        )
        assert info.port == 5432  # PostgreSQL default

    def test_add_default_port_mysql(self, temp_skill_root):
        info = dbm.add_connection(
            name="mysql_default",
            db_type="mysql",
            host="localhost",
            database="test",
            level="global",
        )
        assert info.port == 3306  # MySQL default

    def test_add_duplicate_name_fails(self, temp_skill_root):
        dbm.add_connection(name="unique", db_type="postgresql", host="h1", level="global")
        with pytest.raises(ValueError, match="already exists"):
            dbm.add_connection(name="unique", db_type="mysql", host="h2", level="global")

    def test_add_unsupported_type_fails(self, temp_skill_root):
        with pytest.raises(ValueError, match="Unsupported database type"):
            dbm.add_connection(name="bad", db_type="oracle", host="h", level="global")

    def test_add_invalid_level_fails(self, temp_skill_root):
        with pytest.raises(ValueError, match="level must be"):
            dbm.add_connection(name="bad", db_type="postgresql", level="invalid")


# ---------------------------------------------------------------------------
# Tests: remove_connection
# ---------------------------------------------------------------------------

class TestRemoveConnection:
    """Tests for remove_connection function."""

    def test_remove_existing(self, temp_skill_root):
        dbm.add_connection(name="to_remove", db_type="postgresql", host="localhost", level="global")
        ok = dbm.remove_connection("to_remove", level="global")
        assert ok is True
        # Verify removed from file
        remaining = dbm._parse_connection_config(dbm.GLOBAL_DB_CONFIG_PATH)
        assert "to_remove" not in remaining

    def test_remove_nonexistent(self, temp_skill_root):
        ok = dbm.remove_connection("nonexistent", level="global")
        assert ok is False

    def test_remove_project_level(self, temp_skill_root, temp_project, monkeypatch):
        monkeypatch.chdir(temp_project)
        dbm.add_connection(
            name="proj_db", db_type="mysql", host="h", level="project",
            project_dir=str(temp_project)
        )
        ok = dbm.remove_connection("proj_db", level="project", project_dir=str(temp_project))
        assert ok is True


# ---------------------------------------------------------------------------
# Tests: get_effective_connections
# ---------------------------------------------------------------------------

class TestEffectiveConnections:
    """Tests for effective connection resolution."""

    def test_global_only(self, temp_skill_root):
        dbm.add_connection(name="g1", db_type="postgresql", host="ghost1", level="global")
        dbm.add_connection(name="g2", db_type="mysql", host="ghost2", level="global")
        effective = dbm.get_effective_connections()
        assert len(effective) == 2
        assert "g1" in effective
        assert "g2" in effective

    def test_project_overrides_global(self, temp_skill_root, temp_project, monkeypatch):
        """Project connection with same name overrides global."""
        dbm.add_connection(
            name="shared", db_type="postgresql", host="global_host",
            database="global_db", level="global"
        )

        monkeypatch.chdir(temp_project)
        dbm.add_connection(
            name="shared", db_type="mysql", host="project_host",
            database="project_db", level="project",
            project_dir=str(temp_project)
        )

        effective = dbm.get_effective_connections(str(temp_project))
        assert effective["shared"]["type"] == "mysql"
        assert effective["shared"]["host"] == "project_host"
        assert effective["shared"]["database"] == "project_db"

    def test_project_not_active_outside_dir(self, temp_skill_root, temp_project, monkeypatch):
        """Project connections shouldn't be active outside project dir."""
        monkeypatch.chdir(temp_project)
        dbm.add_connection(
            name="proj_only", db_type="postgresql", host="proj_host",
            level="project", project_dir=str(temp_project)
        )

        unrelated = temp_project.parent / "other"
        unrelated.mkdir(exist_ok=True)
        effective = dbm.get_effective_connections(str(unrelated))
        assert "proj_only" not in effective

    def test_empty_when_no_configs(self, temp_skill_root):
        effective = dbm.get_effective_connections()
        assert effective == {}


# ---------------------------------------------------------------------------
# Tests: list_connections
# ---------------------------------------------------------------------------

class TestListConnections:
    """Tests for list_connections function."""

    def test_list_global(self, temp_skill_root):
        dbm.add_connection(name="g1", db_type="postgresql", host="h1", level="global")
        dbm.add_connection(name="g2", db_type="mysql", host="h2", level="global")
        result = dbm.list_connections(level="global")
        assert len(result) == 2
        assert all(r.level == "global" for r in result)

    def test_list_effective_deduplicated(self, temp_skill_root, temp_project, monkeypatch):
        """Effective list should deduplicate (project wins over global)."""
        dbm.add_connection(name="shared", db_type="postgresql", host="g_host", level="global")

        monkeypatch.chdir(temp_project)
        dbm.add_connection(
            name="shared", db_type="mysql", host="p_host",
            level="project", project_dir=str(temp_project)
        )

        result = dbm.list_connections(level="effective", cwd=str(temp_project))
        # Should only have one "shared" entry
        shared_entries = [r for r in result if r.name == "shared"]
        assert len(shared_entries) == 1
        # The project definition should win
        assert shared_entries[0].level == "project"
        assert shared_entries[0].type == "mysql"

    def test_list_empty(self, temp_skill_root):
        result = dbm.list_connections(level="effective")
        assert result == []


# ---------------------------------------------------------------------------
# Tests: show_connection
# ---------------------------------------------------------------------------

class TestShowConnection:
    """Tests for show_connection function."""

    def test_show_masks_password(self, temp_skill_root):
        dbm.add_connection(
            name="secure", db_type="postgresql", host="localhost",
            password="secret123", level="global"
        )
        result = dbm.show_connection("secure")
        assert result is not None
        assert result.get("password") == "***"

    def test_show_nonexistent(self, temp_skill_root):
        result = dbm.show_connection("nonexistent")
        assert result is None


# ---------------------------------------------------------------------------
# Tests: get_connection
# ---------------------------------------------------------------------------

class TestGetConnection:
    """Tests for get_connection function."""

    def test_get_existing(self, temp_skill_root):
        dbm.add_connection(
            name="test_pg", db_type="postgresql", host="localhost",
            database="test", level="global"
        )
        profile = dbm.get_connection("test_pg")
        assert profile is not None
        assert profile["type"] == "postgresql"
        assert profile["host"] == "localhost"

    def test_get_nonexistent(self, temp_skill_root):
        profile = dbm.get_connection("nonexistent")
        assert profile is None


# ---------------------------------------------------------------------------
# Tests: test_connection (integration)
# ---------------------------------------------------------------------------

class TestConnectionTesting:
    """Tests for test_connection function (db_manager.test_connection)."""

    def test_nonexistent_connection(self, temp_skill_root):
        success, msg = dbm.test_connection("nonexistent")
        assert not success
        assert "not found" in msg

    def test_connection_with_bad_host(self, temp_skill_root):
        dbm.add_connection(
            name="bad_host", db_type="postgresql",
            host="192.0.2.1",  # TEST-NET (unroutable)
            database="test",
            timeout=2,
            level="global",
        )
        success, msg = dbm.test_connection("bad_host")
        assert not success  # Should fail on unreachable host


# ---------------------------------------------------------------------------
# Tests: CLI integration
# ---------------------------------------------------------------------------

class TestCLI:
    """Tests for db_manager CLI entry point."""

    def test_help_output(self, capsys):
        """Verify --help returns cleanly."""
        with pytest.raises(SystemExit) as exc_info:
            dbm.main(["--help"])
        assert exc_info.value.code == 0

    def test_list_empty(self, temp_skill_root, capsys):
        dbm.main(["list"])
        captured = capsys.readouterr()
        assert "暂无" in captured.out

    def test_add_and_list(self, temp_skill_root, capsys):
        dbm.main([
            "add", "--name", "cli_test", "--type", "postgresql",
            "--host", "localhost", "--database", "test",
        ])
        captured = capsys.readouterr()
        assert "成功" in captured.out

        dbm.main(["list"])
        captured2 = capsys.readouterr()
        assert "cli_test" in captured2.out

    def test_add_and_show(self, temp_skill_root, capsys):
        dbm.main([
            "add", "--name", "show_test", "--type", "postgresql",
            "--host", "localhost", "--password", "secret",
        ])
        dbm.main(["show", "show_test"])
        captured = capsys.readouterr()
        assert "show_test" in captured.out
        assert "secret" not in captured.out  # Password masked

    def test_add_and_remove(self, temp_skill_root, capsys):
        dbm.main([
            "add", "--name", "rm_test", "--type", "mysql",
            "--host", "localhost",
        ])
        dbm.main(["remove", "rm_test"])
        captured = capsys.readouterr()
        assert "成功删除" in captured.out

    def test_effective_empty(self, temp_skill_root, capsys):
        dbm.main(["effective"])
        captured = capsys.readouterr()
        assert "暂无" in captured.out


# ---------------------------------------------------------------------------
# Tests: db_cli management commands
# ---------------------------------------------------------------------------

class TestDbCliManagement:
    """Tests for db_cli.py connection management subcommands."""

    def test_cli_help_includes_management(self):
        """Verify db_cli help shows management commands."""
        from scripts.db_cli import create_parser
        parser = create_parser()
        # Check that add subcommand exists
        assert "add" in [c for c in parser._subparsers._group_actions[0].choices]


# ---------------------------------------------------------------------------
# Tests: db_config effective loading
# ---------------------------------------------------------------------------

class TestDbConfigEffective:
    """Tests for effective config loading in db_config.py."""

    def test_load_effective_config_empty(self, temp_skill_root):
        from scripts.db_config import load_effective_config
        config = load_effective_config()
        assert config.connections == {}

    def test_load_global_config(self, temp_skill_root):
        from scripts.db_config import load_global_config
        dbm.add_connection(
            name="global_test", db_type="postgresql",
            host="localhost", level="global"
        )
        config = load_global_config()
        assert "global_test" in config.connections
        assert config.connections["global_test"].type == "postgresql"

    def test_load_local_config(self, temp_skill_root, temp_project, monkeypatch):
        monkeypatch.chdir(temp_project)
        dbm.add_connection(
            name="local_test", db_type="mysql",
            host="local_host", level="project",
            project_dir=str(temp_project)
        )
        from scripts.db_config import load_local_config
        config = load_local_config(str(temp_project))
        assert "local_test" in config.connections

    def test_effective_merges_correctly(self, temp_skill_root, temp_project, monkeypatch):
        """Effective config merges project over global."""
        dbm.add_connection(
            name="shared", db_type="postgresql", host="global_h", level="global"
        )
        dbm.add_connection(
            name="global_only", db_type="mysql", host="g_h", level="global"
        )

        monkeypatch.chdir(temp_project)
        dbm.add_connection(
            name="shared", db_type="mysql", host="project_h",
            level="project", project_dir=str(temp_project)
        )

        from scripts.db_config import load_effective_config
        config = load_effective_config(str(temp_project))

        # shared should be mysql (project override)
        assert config.connections["shared"].type == "mysql"
        assert config.connections["shared"].host == "project_h"
        # global_only should still be present
        assert "global_only" in config.connections
        assert config.connections["global_only"].type == "mysql"


# ---------------------------------------------------------------------------
# Tests: db_manager integration through db_cli
# ---------------------------------------------------------------------------

class TestDbCliQueryIntegration:
    """Verify db_cli.py query still works with effective config."""

    def test_profile_not_found_message(self, capsys):
        """When profile not found, suggest creating connections."""
        from scripts.db_cli import main as cli_main
        with pytest.raises(SystemExit):
            cli_main(["query", "nonexistent_profile", "SELECT 1"])
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower() or "not found" in captured.err.lower()
