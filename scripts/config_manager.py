"""
Configuration Manager for echart-skill.

Provides centralized config loading with sensible defaults.
Reads ``echart_config.txt`` from the project root; auto-creates it
with defaults on first use if the file does not exist.

Example:
    from scripts.config_manager import get_config

    cfg = get_config()
    print(cfg.server.enabled)   # False (default)
    print(cfg.output.dir)       # "outputs/html" (default)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from scripts.text_config import dump_txt_config, parse_txt_config


# ---------------------------------------------------------------------------
# Default values
# ---------------------------------------------------------------------------
DEFAULT_PORT_RANGE = [8100, 8200]
DEFAULT_OUTPUT_DIR = "outputs/html"

# Path to the config txt (project root)
_CONFIG_PATH: Optional[Path] = None


# ---------------------------------------------------------------------------
# Config data models
# ---------------------------------------------------------------------------
@dataclass
class ServerConfig:
    """Server-related configuration."""
    enabled: bool = False
    port_range: list[int] = field(default_factory=lambda: DEFAULT_PORT_RANGE.copy())


@dataclass
class OutputConfig:
    """Output-related configuration."""
    dir: str = DEFAULT_OUTPUT_DIR


@dataclass
class AppConfig:
    """Top-level application configuration."""
    server: ServerConfig = field(default_factory=ServerConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    baidu_ak: str = ""


def _get_config_path() -> Path:
    """Return the absolute path to ``echart_config.txt`` in the project root."""
    global _CONFIG_PATH
    if _CONFIG_PATH is not None:
        return _CONFIG_PATH

    # When imported as a module inside scripts/, the parent is the project root
    project_root = Path(__file__).resolve().parent.parent
    _CONFIG_PATH = project_root / "echart_config.txt"
    return _CONFIG_PATH


def _default_config() -> dict:
    """Return the default config as a plain dict for serialization."""
    return {
        "server": {
            "enabled": False,
            "port_range": DEFAULT_PORT_RANGE.copy(),
        },
        "output": {
            "dir": DEFAULT_OUTPUT_DIR,
        },
        "baidu_ak": "",
    }


def _load_raw() -> dict:
    """Load raw config dict from disk, or return defaults if missing/invalid."""
    config_path = _get_config_path()

    if not config_path.exists():
        # Auto-create with defaults
        _save_raw(_default_config())
        return _default_config()

    try:
        data = parse_txt_config(config_path)
    except (ValueError, OSError):
        # Corrupted file — overwrite with defaults
        _save_raw(_default_config())
        return _default_config()

    # Merge with defaults so missing keys don't cause KeyError
    defaults = _default_config()
    _deep_merge(defaults, data)
    return defaults


def _save_raw(data: dict) -> None:
    """Persist raw config dict to disk (atomic via temp file)."""
    config_path = _get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = config_path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(dump_txt_config(data))
    tmp_path.replace(config_path)


def _deep_merge(base: dict, override: dict) -> None:
    """Recursively merge *override* into *base* (mutates base)."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
_config_cache: Optional[AppConfig] = None


def get_config(reload: bool = False) -> AppConfig:
    """Load (or return cached) application configuration.

    Args:
        reload: If True, force re-read from disk.

    Returns:
        Populated ``AppConfig`` instance.
    """
    global _config_cache
    if _config_cache is not None and not reload:
        return _config_cache

    raw = _load_raw()

    server_cfg = ServerConfig(
        enabled=raw.get("server", {}).get("enabled", False),
        port_range=raw.get("server", {}).get("port_range", DEFAULT_PORT_RANGE.copy()),
    )
    output_cfg = OutputConfig(
        dir=raw.get("output", {}).get("dir", DEFAULT_OUTPUT_DIR),
    )

    _config_cache = AppConfig(
        server=server_cfg,
        output=output_cfg,
        baidu_ak=raw.get("baidu_ak", ""),
    )
    return _config_cache


def reload_config() -> AppConfig:
    """Force reload config from disk (convenience wrapper)."""
    return get_config(reload=True)


if __name__ == "__main__":  # pragma: no cover
    cfg = get_config()
    print(f"Server enabled : {cfg.server.enabled}")
    print(f"Server ports   : {cfg.server.port_range}")
    print(f"Output dir     : {cfg.output.dir}")
    print(f"Baidu AK       : {'***' if cfg.baidu_ak else '(not set)'}")
