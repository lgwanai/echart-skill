"""Tests for the Report Engine module."""

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.report_engine import (
    ReportEngine,
    Report,
    ReportSection,
    REPORT_TEMPLATES,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db_path():
    """Create a DuckDB database with test sales data."""
    import duckdb

    tmp_path = os.path.join(tempfile.gettempdir(), f"test_report_{os.getpid()}.duckdb")
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)

    conn = duckdb.connect(tmp_path)
    conn.execute("""
        CREATE TABLE test_sales (
            order_date DATE,
            region VARCHAR,
            product VARCHAR,
            amount DOUBLE,
            quantity INTEGER,
            category VARCHAR
        )
    """)
    conn.execute("""
        INSERT INTO test_sales VALUES
        ('2024-01-01', '北京', '产品A', 1000.0, 10, '电子'),
        ('2024-01-05', '上海', '产品B', 800.0, 5, '电子'),
        ('2024-01-10', '北京', '产品A', 1200.0, 12, '电子'),
        ('2024-02-01', '广东', '产品C', 500.0, 3, '家居'),
        ('2024-02-15', '北京', '产品B', 900.0, 8, '电子'),
        ('2024-02-20', '上海', '产品C', 600.0, 4, '家居'),
        ('2024-03-01', '广东', '产品A', 1500.0, 15, '电子'),
        ('2024-03-10', '北京', '产品C', 700.0, 6, '家居'),
        ('2024-03-15', '上海', '产品B', 1100.0, 9, '电子'),
        ('2024-03-20', '广东', '产品B', 950.0, 7, '电子'),
        ('2024-04-01', '北京', '产品A', 1300.0, 11, '电子'),
        ('2024-04-10', '上海', '产品A', 1400.0, 14, '电子'),
        ('2024-04-15', '广东', '产品C', 400.0, 2, '家居'),
        ('2024-04-20', '北京', '产品B', 850.0, 7, '电子'),
        ('2024-05-01', '广东', '产品A', 1600.0, 16, '电子'),
        ('2024-05-10', '上海', '产品C', 550.0, 5, '家居'),
        ('2024-05-15', '北京', '产品B', 1000.0, 10, '电子'),
        ('2024-05-20', '广东', '产品B', 900.0, 8, '电子'),
        ('2024-06-01', '上海', '产品A', 1700.0, 18, '电子'),
        ('2024-06-10', '北京', '产品C', 650.0, 4, '家居'),
        ('2024-06-15', '广东', '产品A', 1800.0, 20, '电子'),
        ('2024-06-20', '上海', '产品B', 1200.0, 12, '电子'),
        ('2024-06-25', '北京', NULL, NULL, NULL, '电子'),
        ('2024-06-30', '上海', NULL, 500.0, 3, NULL)
    """)
    conn.close()

    yield tmp_path

    try:
        os.unlink(tmp_path)
    except OSError:
        pass


@pytest.fixture
def engine(db_path, tmp_path):
    """Create a ReportEngine with temp output dir."""
    output_dir = os.path.join(tmp_path, "reports")
    eng = ReportEngine(db_path=db_path, output_dir=output_dir)
    yield eng
    # Close database connections to allow clean temp file removal
    eng.insight_engine.repo.close_all()


# ---------------------------------------------------------------------------
# Report data structures
# ---------------------------------------------------------------------------

class TestReportDataStructures:
    """Tests for Report and ReportSection dataclasses."""

    def test_empty_report(self):
        report = Report(title="测试报告")
        assert report.title == "测试报告"
        assert report.sections == []
        assert report.generated_at != ""

    def test_report_with_sections(self):
        section = ReportSection(heading="摘要", level=2, content="这是一个摘要。")
        report = Report(title="完整报告", subtitle="副标题")
        report.sections.append(section)
        assert len(report.sections) == 1
        assert report.subtitle == "副标题"
        assert report.sections[0].heading == "摘要"

    def test_section_with_subsections(self):
        sub = ReportSection(heading="明细", level=3, content="明细内容")
        section = ReportSection(heading="概况", level=2, subsections=[sub])
        assert len(section.subsections) == 1
        assert section.subsections[0].heading == "明细"

    def test_report_templates_structure(self):
        """Verify all templates have required fields."""
        for name, tmpl in REPORT_TEMPLATES.items():
            assert "name" in tmpl, f"Template {name} missing 'name'"
            assert "sections" in tmpl, f"Template {name} missing 'sections'"
            assert len(tmpl["sections"]) > 0
            for s in tmpl["sections"]:
                assert "heading" in s
                assert "slug" in s


# ---------------------------------------------------------------------------
# Engine initialization
# ---------------------------------------------------------------------------

class TestReportEngineInit:
    """Tests for engine initialization."""

    def test_init_creates_output_dir(self, db_path, tmp_path):
        output_dir = os.path.join(tmp_path, "custom_reports")
        engine = ReportEngine(db_path=db_path, output_dir=output_dir)
        assert os.path.isdir(output_dir)

    def test_init_with_defaults(self, db_path):
        engine = ReportEngine(db_path=db_path)
        assert engine.db_path == db_path
        assert engine.output_dir == "outputs/reports"

    def test_engine_has_insight_engine(self, db_path):
        engine = ReportEngine(db_path=db_path)
        assert engine.insight_engine is not None


# ---------------------------------------------------------------------------
# Report generation — Markdown
# ---------------------------------------------------------------------------

class TestReportGenerateMarkdown:
    """Tests for generating Markdown reports."""

    def test_generate_markdown_default(self, engine):
        path = engine.generate("test_sales", template="general", output_format="markdown")
        assert os.path.exists(path)
        assert path.endswith(".md")

        content = open(path).read()
        assert "# " in content           # Title
        assert "test_sales" in content   # Table name
        assert "## " in content          # Sections

    def test_generate_with_custom_title(self, engine):
        path = engine.generate(
            "test_sales",
            title="自定义报告标题",
            template="general",
            output_format="markdown",
        )
        content = open(path).read()
        assert "自定义报告标题" in content

    def test_generate_markdown_quick(self, engine):
        path = engine.quick_report("test_sales", output_format="markdown")
        assert os.path.exists(path)
        assert path.endswith(".md")
        content = open(path).read()
        assert "quick" in path or len(content) > 100
        assert "# " in content  # Has a title

    def test_generate_markdown_sales_template(self, engine):
        path = engine.generate("test_sales", template="sales", output_format="markdown")
        assert os.path.exists(path)
        content = open(path).read()
        assert len(content) > 200  # Should have substantial content

    def test_generate_output_path_auto_generated(self, engine):
        path = engine.generate("test_sales", template="general", output_format="markdown")
        # Auto-generated path should include table name and template
        assert "test_sales" in path
        assert "general" in path
        assert path.endswith(".md")


# ---------------------------------------------------------------------------
# Report generation — HTML
# ---------------------------------------------------------------------------

class TestReportGenerateHTML:
    """Tests for generating HTML reports."""

    def test_generate_html(self, engine):
        path = engine.generate("test_sales", template="general", output_format="html")
        assert os.path.exists(path)
        assert path.endswith(".html")

        content = open(path).read()
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "<style>" in content or "css" in content.lower()
        assert "test_sales" in content

    def test_generate_html_quick(self, engine):
        path = engine.quick_report("test_sales", output_format="html")
        assert os.path.exists(path)
        assert path.endswith(".html")
        content = open(path).read()
        assert "<!DOCTYPE html>" in content

    def test_html_contains_dark_mode(self, engine):
        path = engine.generate("test_sales", template="general", output_format="html")
        content = open(path).read()
        assert "prefers-color-scheme" in content


# ---------------------------------------------------------------------------
# Report generation — JSON
# ---------------------------------------------------------------------------

class TestReportGenerateJSON:
    """Tests for generating JSON reports."""

    def test_generate_json(self, engine):
        path = engine.generate("test_sales", template="general", output_format="json")
        assert os.path.exists(path)
        assert path.endswith(".json")

        with open(path) as f:
            data = json.load(f)

        assert "title" in data
        assert "sections" in data
        assert "all_insights" in data
        assert isinstance(data["sections"], list)

    def test_generate_json_quick(self, engine):
        path = engine.quick_report("test_sales", output_format="json")
        assert os.path.exists(path)

        with open(path) as f:
            data = json.load(f)

        assert "all_insights" in data
        assert isinstance(data["all_insights"], list)

    def test_json_sections_have_content(self, engine):
        path = engine.generate("test_sales", template="general", output_format="json")
        with open(path) as f:
            data = json.load(f)

        for section in data["sections"]:
            assert "heading" in section
            assert "level" in section
            # Content may be empty string but key must exist
            assert "content" in section or "insights" in section


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestReportEngineErrors:
    """Tests for error handling."""

    def test_nonexistent_table_raises_error(self, engine):
        with pytest.raises(ValueError):
            engine.generate("nonexistent_table_xyz", template="general")

    def test_quick_report_nonexistent_table(self, engine):
        with pytest.raises(ValueError):
            engine.quick_report("nonexistent_table_xyz")


# ---------------------------------------------------------------------------
# Section building
# ---------------------------------------------------------------------------

class TestReportSections:
    """Tests for report section content."""

    def test_markdown_has_data_overview(self, engine):
        path = engine.generate("test_sales", template="general", output_format="markdown")
        content = open(path).read()
        # Should include table structure
        assert "test_sales" in content
        assert "行" in content or "列" in content or "|" in content

    def test_markdown_has_table_of_contents(self, engine):
        path = engine.generate("test_sales", template="general", output_format="markdown")
        content = open(path).read()
        assert "目录" in content

    def test_specific_sections_only(self, engine):
        """Test that passing specific sections limits output."""
        path = engine.generate(
            "test_sales",
            template="general",
            output_format="markdown",
            sections=["executive-summary", "data-overview"],
        )
        content = open(path).read()
        assert "报告摘要" in content or "executive" in content.lower()
        assert "数据概览" in content

    def test_all_templates_work(self, engine):
        """Verify all 3 templates generate without error."""
        for tmpl in REPORT_TEMPLATES:
            path = engine.generate("test_sales", template=tmpl, output_format="markdown")
            assert os.path.exists(path)
            assert os.path.getsize(path) > 50


# ---------------------------------------------------------------------------
# Markdown content helpers
# ---------------------------------------------------------------------------

class TestMarkdownToHTML:
    """Tests for _md_to_html helper."""

    def test_bold_conversion(self, engine):
        html = engine._md_to_html("**加粗文本**")
        assert "<strong>加粗文本</strong>" in html

    def test_table_conversion(self, engine):
        md_table = "| 列A | 列B |\n|------|------|\n| 值1 | 值2 |"
        html = engine._md_to_html(md_table)
        assert "<table>" in html
        assert "<td>值1</td>" in html

    def test_list_conversion(self, engine):
        md_list = "- 项目1\n- 项目2"
        html = engine._md_to_html(md_list)
        assert "<ul>" in html
        assert "<li>项目1</li>" in html

    def test_ordered_list_conversion(self, engine):
        md_ol = "1. 第一\n2. 第二"
        html = engine._md_to_html(md_ol)
        assert "<ol>" in html
        assert "<li>第一</li>" in html
