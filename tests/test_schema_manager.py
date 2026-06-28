"""Tests for table schema manager (scripts/schema_manager.py)."""
import os, sys, pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import scripts.schema_manager as sm

# also patch db_config globals that schema_manager doesn't touch
import scripts.db_config as dbcfg


@pytest.fixture
def temp_skill_root(tmp_path, monkeypatch):
    """Override schema store to temp directory."""
    gs = tmp_path / "references" / "table_schemas.txt"
    idx = tmp_path / "references" / "project_schema_index.json"
    monkeypatch.setattr(sm, "GLOBAL_SCHEMA_PATH", gs)
    monkeypatch.setattr(sm, "SCHEMA_INDEX_PATH", idx)
    monkeypatch.setattr(sm, "PROJECT_ROOT", tmp_path)
    # also patch db_config's globals for effective config tests
    monkeypatch.setattr(dbcfg, "GLOBAL_CONFIG_PATH", tmp_path / "references" / "db_connections.txt")
    monkeypatch.setattr(dbcfg, "SKILL_ROOT", tmp_path)
    (tmp_path / "references").mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def temp_project(tmp_path):
    proj = tmp_path / "my_project"
    proj.mkdir(parents=True)
    (proj / sm.PROJECT_DIRNAME).mkdir(parents=True, exist_ok=True)
    return proj


# ── column parser ──────────────────────────────────────────────────

class TestColumnShorthand:
    def test_basic(self):
        c = sm.parse_column_shorthand("id:INT:主键:pk")  # 4 parts: name,type,desc,flag
        assert c.name == "id" and c.type == "INT" and c.primary_key
        assert c.description == "主键"

    def test_required(self):
        c = sm.parse_column_shorthand("name:VARCHAR:名称:required")
        assert not c.nullable

    def test_nullable_explicit(self):
        c = sm.parse_column_shorthand("note:TEXT:备注:nullable")
        assert c.nullable

    def test_no_flags(self):
        c = sm.parse_column_shorthand("amount:DECIMAL(10,2):金额")
        assert c.type == "DECIMAL(10,2)" and c.nullable

    def test_minimal(self):
        c = sm.parse_column_shorthand("status:VARCHAR")
        assert c.name == "status" and c.type == "VARCHAR" and not c.description

    def test_parens_in_type(self):
        c = sm.parse_column_shorthand("geo:GEOMETRY(POINT,4326):位置")
        assert c.type == "GEOMETRY(POINT,4326)"

    def test_multiple(self):
        cols = sm.parse_columns_shorthand("id:INT:ID:pk,amount:DECIMAL(18,2):金额:required,channel:VARCHAR:渠道")
        assert len(cols) == 3
        assert cols[0].primary_key
        assert not cols[1].nullable
        assert cols[2].nullable

    def test_empty(self):
        assert sm.parse_columns_shorthand("") == []


# ── CRUD ────────────────────────────────────────────────────────────

class TestAddSchema:
    def test_add_global(self, temp_skill_root):
        cols = sm.parse_columns_shorthand("id:INT::pk,name:VARCHAR:名称:required")
        s = sm.add_table_schema("users", "用户表", columns=cols, level="global")
        assert s.name == "users" and s.level == "global" and s.column_count == 2
        assert sm.GLOBAL_SCHEMA_PATH.exists()

    def test_add_project(self, temp_skill_root, temp_project, monkeypatch):
        monkeypatch.chdir(temp_project)
        s = sm.add_table_schema("proj_t", "项目表",
            columns_spec="id:INT::pk", level="project", project_dir=str(temp_project))
        assert s.level == "project"
        p = temp_project / sm.PROJECT_DIRNAME / sm.PROJECT_SCHEMA_FILENAME
        assert p.exists()

    def test_add_duplicate_overwrites(self, temp_skill_root):
        sm.add_table_schema("t", columns_spec="a:INT", level="global")
        sm.add_table_schema("t", "updated", columns_spec="b:VARCHAR", level="global")
        s = sm.get_table_schema("t")
        assert s.description == "updated" and s.column_count == 1

    def test_add_from_spec_string(self, temp_skill_root):
        s = sm.add_table_schema("orders", "订单",
            columns_spec="order_id:INT:订单ID:pk,amount:DECIMAL(18,2):金额:required,status:VARCHAR:状态")
        assert s.column_count == 3


class TestRemoveSchema:
    def test_remove_existing(self, temp_skill_root):
        sm.add_table_schema("t", columns_spec="a:INT", level="global")
        assert sm.remove_table_schema("t", "global")

    def test_remove_nonexistent(self, temp_skill_root):
        assert not sm.remove_table_schema("ghost", "global")


class TestGetSchema:
    def test_get_effective(self, temp_skill_root):
        sm.add_table_schema("t", columns_spec="a:INT::pk,b:VARCHAR", level="global")
        s = sm.get_table_schema("t")
        assert s is not None and s.columns[0].primary_key

    def test_project_overrides_global(self, temp_skill_root, temp_project, monkeypatch):
        sm.add_table_schema("shared", "global ver", columns_spec="g_col:INT", level="global")
        monkeypatch.chdir(temp_project)
        sm.add_table_schema("shared", "project ver", columns_spec="p_col:VARCHAR", level="project", project_dir=str(temp_project))
        s = sm.get_table_schema("shared", str(temp_project))
        assert s.description == "project ver" and s.columns[0].name == "p_col"

    def test_not_found(self, temp_skill_root):
        assert sm.get_table_schema("nope") is None


class TestListSchemas:
    def test_list_effective_dedup(self, temp_skill_root, temp_project, monkeypatch):
        sm.add_table_schema("shared", columns_spec="g:INT", level="global")
        monkeypatch.chdir(temp_project)
        sm.add_table_schema("shared", columns_spec="p:VARCHAR", level="project", project_dir=str(temp_project))
        result = sm.list_table_schemas("effective", str(temp_project))
        shared = [r for r in result if r.name == "shared"]
        assert len(shared) == 1 and shared[0].level == "project"

    def test_list_empty(self, temp_skill_root):
        assert sm.list_table_schemas("effective") == []


# ── CLI ─────────────────────────────────────────────────────────────

class TestCLI:
    def test_help(self, capsys):
        with pytest.raises(SystemExit) as e:
            sm.main(["--help"])
        assert e.value.code == 0

    def test_add_list_show_remove(self, temp_skill_root, capsys):
        sm.main(["add", "--name", "t", "--columns", "id:INT:pk,name:VARCHAR:名称:required"])
        sm.main(["add", "--name", "t2", "--columns", "x:INT"])
        sm.main(["list"])
        assert "t" in capsys.readouterr().out
        sm.main(["show", "t"])
        assert "pk" in capsys.readouterr().out.lower() or "✓" in capsys.readouterr().out
        sm.main(["remove", "t"])
        sm.main(["remove", "t2"])

    def test_effective_empty(self, temp_skill_root, capsys):
        sm.main(["effective"])
        assert "暂无" in capsys.readouterr().out

    def test_add_with_parens_type(self, temp_skill_root):
        sm.main(["add", "--name", "products", "--columns", "price:DECIMAL(10,2):单价:required"])
        s = sm.get_table_schema("products")
        assert s.columns[0].type == "DECIMAL(10,2)"
        sm.remove_table_schema("products", "global")


# ── Integration with db_config effective ────────────────────────────

class TestSchemaDbConfigIntegration:
    def test_effective_loads_global(self, temp_skill_root):
        sm.add_table_schema("orders", columns_spec="id:INT::pk,amount:DECIMAL:金额", level="global")
        schemas = sm.get_effective_schemas()
        assert "orders" in schemas
        sm.remove_table_schema("orders", "global")
