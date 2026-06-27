import json
from datetime import datetime, timedelta


def test_log_command_and_daily_report(tmp_path, monkeypatch):
    import scripts.config_manager as cm
    from scripts.audit_report import (
        filter_entries,
        log_command,
        render_report,
        _read_entries,
    )

    config_file = tmp_path / "echart_config.txt"
    audit_log = tmp_path / "audit.log"
    config_file.write_text(f"privacy.audit_log_path={audit_log}\n", encoding="utf-8")
    monkeypatch.setattr(cm, "_CONFIG_PATH", config_file)
    monkeypatch.setattr(cm, "_config_cache", None)

    log_command("/report sales --format html", cwd=str(tmp_path), status="completed")
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    with audit_log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "ts": f"{today.isoformat()}T10:00:00",
            "tbl": "sales",
            "cols": ["amount"],
            "q": "abc123",
            "n": 10,
            "mask": False,
            "lv": "internal",
            "mut": False,
            "blk": "",
        }, ensure_ascii=False) + "\n")
        handle.write(json.dumps({
            "ts": f"{yesterday.isoformat()}T10:00:00",
            "typ": "command",
            "cmd": "/old",
        }, ensure_ascii=False) + "\n")

    entries = _read_entries(audit_log)
    selected = filter_entries(entries, today)
    report = render_report(selected, today)

    assert "/report sales --format html" in report
    assert "sales" in report
    assert "/old" not in report
    assert "指令记录数: 1" in report
    assert "查询记录数: 1" in report
