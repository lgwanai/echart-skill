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

    report_wrapper = (claude_dir / "echart-report.md").read_text(encoding="utf-8")
    assert str(source_dir / "_shared.md") in report_wrapper
    assert str(source_dir / "report.md") in report_wrapper

    report_source = (source_dir / "report.md").read_text(encoding="utf-8")
    assert "映射到 echart-skill 原始指令 `/report`" in report_source
    assert "$ARGUMENTS" in report_source


def test_installed_command_names_are_unique():
    import scripts.install_claude_commands as installer

    names = [spec.name for spec in installer.COMMANDS]
    assert len(names) == len(set(names))
