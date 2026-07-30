def test_install_claude_commands_generates_source_and_wrappers(tmp_path, monkeypatch):
    import scripts.install_claude_commands as installer

    source_dir = tmp_path / "commands" / "echart"
    claude_dir = tmp_path / ".claude" / "commands"
    monkeypatch.setattr(installer, "SOURCE_DIR", source_dir)
    monkeypatch.setattr(installer, "CLAUDE_COMMANDS_DIR", claude_dir)

    installer.install()

    source_files = sorted(source_dir.glob("*.md"))
    wrapper_files = sorted(claude_dir.glob("echart-*.md"))

    assert len(source_files) == len(installer.COMMANDS) + 1  # includes _shared.md
    assert len(wrapper_files) == len(installer.COMMANDS)

    shared = (source_dir / "_shared.md").read_text(encoding="utf-8")
    assert "/echart-report" in shared
    assert "/echart-dashboard" in shared
    assert "/echart-quality" in shared
    assert "/echart-analysis-query" in shared
    assert "scripts/analysis_runner.py" in shared
    assert "scripts/sql_runner.py" in shared
    assert "sql_runner.py --sql" in shared
    assert "sql_runner.py --file" in shared
    assert "生成 SQL" in shared
    assert "可以写 SQL 文件" in shared
    assert "临时 heredoc Python" in shared
    assert "validate_output_quality.py" in shared
    assert ".meta.json" in shared
    assert "查看数据" in shared

    report_wrapper = (claude_dir / "echart-report.md").read_text(encoding="utf-8")
    assert str(source_dir / "_shared.md") in report_wrapper
    assert str(source_dir / "report.md") in report_wrapper

    report_source = (source_dir / "report.md").read_text(encoding="utf-8")
    assert "映射到 echart-skill 原始指令 `/report`" in report_source
    assert "$ARGUMENTS" in report_source

    query_source = (source_dir / "query.md").read_text(encoding="utf-8")
    assert "scripts/sql_runner.py" in query_source
    assert "--sql \"<SELECT ...>\"" in query_source
    assert "--file queries/<task>.sql" in query_source
    assert "metrics_manager.py effective" in query_source
    assert "psycopg2.connect" in query_source
    assert "--type postgresql --host" in query_source
    assert "DuckDB/Python 在本地计算" not in query_source

    dbconn_source = (source_dir / "dbconn.md").read_text(encoding="utf-8")
    assert "scripts/sql_runner.py" in dbconn_source
    assert "pymysql.connect" in dbconn_source

    dashboard_source = (source_dir / "dashboard.md").read_text(encoding="utf-8")
    assert "禁止 CDN" in dashboard_source
    assert "dashboard-grid" in dashboard_source
    assert "禁止 `.row` / `.full`" in dashboard_source
    assert "validate_chart.py" in dashboard_source
    assert "validate_output_quality.py" in dashboard_source
    assert "查看数据" in dashboard_source
    assert "绝不能把文件路径返回给用户" in dashboard_source

    chart_source = (source_dir / "chart.md").read_text(encoding="utf-8")
    assert "assets/echarts/echarts.min.js" in chart_source
    assert "json.dumps" in chart_source


def test_installed_command_names_are_unique():
    import scripts.install_claude_commands as installer

    names = [spec.name for spec in installer.COMMANDS]
    assert len(names) == len(set(names))


def test_all_generated_commands_include_global_sql_execution_gate(tmp_path, monkeypatch):
    import scripts.install_claude_commands as installer

    source_dir = tmp_path / "commands" / "echart"
    claude_dir = tmp_path / ".claude" / "commands"
    monkeypatch.setattr(installer, "SOURCE_DIR", source_dir)
    monkeypatch.setattr(installer, "CLAUDE_COMMANDS_DIR", claude_dir)

    installer.install()

    for spec in installer.COMMANDS:
        source = (source_dir / f"{spec.name}.md").read_text(encoding="utf-8")
        assert "所有数据库查询和取数动作" in source
        assert "scripts/analysis_runner.py" in source
        assert "scripts/sql_runner.py" in source
        assert "metrics_manager.py effective" in source
        assert "--sql \"<SELECT ...>\"" in source
        assert "--file queries/<task>.sql" in source
        assert "python3 << 'PYEOF'" in source
        assert "psycopg2.connect" in source
        assert "--type postgresql --host" in source
        assert "validate_agent_output.py" in source
        assert "validate_output_quality.py" in source
