"""Tests for API key configuration and app config."""

import os
import sys

import pytest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "scripts"))


def test_baidu_ak_from_config_file(monkeypatch, tmp_path):
    """Baidu AK should be read from config file."""
    import scripts.config_manager as cm
    config_file = tmp_path / "echart_config.txt"
    config_file.write_text("baidu_ak=env_key_123\n", encoding="utf-8")
    monkeypatch.setattr(cm, "_CONFIG_PATH", config_file)
    monkeypatch.setattr(cm, "_config_cache", None)
    cfg = cm.get_config(reload=True)
    assert cfg.baidu_ak == "env_key_123"


def test_baidu_ak_missing(monkeypatch, tmp_path):
    """Missing BAIDU_AK should result in empty string."""
    import scripts.config_manager as cm
    config_file = tmp_path / "echart_config.txt"
    config_file.write_text("", encoding="utf-8")
    monkeypatch.setattr(cm, "_CONFIG_PATH", config_file)
    monkeypatch.setattr(cm, "_config_cache", None)
    cfg = cm.get_config(reload=True)
    assert cfg.baidu_ak == ""


def test_app_config_txt_roundtrip(monkeypatch, tmp_path):
    """App config should read and write echart_config.txt."""
    import scripts.config_manager as cm

    config_file = tmp_path / "echart_config.txt"
    monkeypatch.setattr(cm, "_CONFIG_PATH", config_file)
    monkeypatch.setattr(cm, "_config_cache", None)

    cfg = cm.get_config(reload=True)
    assert config_file.exists()
    assert cfg.server.enabled is False
    assert cfg.server.port_range == [8100, 8200]
    assert cfg.privacy.mask_pii is False
    assert cfg.privacy.audit_enabled is True
    assert cfg.privacy.read_only is False

    config_file.write_text(
        "server.enabled=true\n"
        "server.port_range=8201,8210\n"
        "output.dir=custom/html\n"
        "privacy.mask_pii=true\n"
        "privacy.audit_enabled=false\n"
        "privacy.audit_log_path=tmp/audit.log\n"
        "baidu_ak=abc123\n",
        encoding="utf-8",
    )

    cfg = cm.get_config(reload=True)
    assert cfg.server.enabled is True
    assert cfg.server.port_range == [8201, 8210]
    assert cfg.output.dir == "custom/html"
    assert cfg.privacy.mask_pii is True
    assert cfg.privacy.audit_enabled is False
    assert cfg.privacy.audit_log_path == "tmp/audit.log"
    assert cfg.baidu_ak == "abc123"
