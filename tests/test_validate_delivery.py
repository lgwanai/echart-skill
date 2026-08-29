from pathlib import Path

import scripts.validate_delivery as delivery


def test_combined_gate_requires_browser_by_default(tmp_path: Path, monkeypatch):
    html = tmp_path / "artifact.html"
    html.write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(delivery, "validate_chart", lambda _: 0)
    monkeypatch.setattr(delivery, "validate_artifact", lambda *_: [])
    monkeypatch.setattr(
        delivery,
        "run_smoke_test",
        lambda _: (2, {"errors": ["runtime unavailable"]}),
    )

    errors = delivery.validate_delivery(html)

    assert any("runtime unavailable" in error for error in errors)


def test_combined_gate_accepts_all_three_layers(tmp_path: Path, monkeypatch):
    html = tmp_path / "artifact.html"
    html.write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(delivery, "validate_chart", lambda _: 0)
    monkeypatch.setattr(delivery, "validate_artifact", lambda *_: [])
    monkeypatch.setattr(
        delivery,
        "run_smoke_test",
        lambda _: (0, {"ok": True, "errors": []}),
    )

    assert delivery.validate_delivery(html) == []
