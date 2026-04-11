"""Unit tests for HTML Exporter module."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from scripts.html_exporter import HTMLExporter


class TestHTMLExporter:
    """Tests for HTMLExporter class."""
    
    @pytest.fixture
    def exporter(self, tmp_path):
        """Create exporter with temp directory."""
        # Create fake assets directory
        assets_dir = tmp_path / "assets" / "echarts"
        assets_dir.mkdir(parents=True)
        
        # Create fake echarts.min.js
        echarts_content = "// Fake ECharts library\nvar echarts = {};"
        (assets_dir / "echarts.min.js").write_text(echarts_content, encoding='utf-8')
        
        # Create fake china.js
        china_content = "// Fake China map\necharts.registerMap('china', {});"
        (assets_dir / "china.js").write_text(china_content, encoding='utf-8')
        
        return HTMLExporter(base_dir=str(tmp_path))
    
    def test_load_echarts(self, exporter):
        """Test ECharts library loading and caching."""
        content = exporter._load_echarts()
        
        assert content is not None
        assert "echarts" in content
        assert exporter._echarts_content is not None  # Cached
        
        # Second call should use cache
        content2 = exporter._load_echarts()
        assert content2 == content
    
    def test_load_map_script(self, exporter):
        """Test map script loading."""
        content = exporter._load_map_script("china")
        
        assert content is not None
        assert "china" in content.lower()
        assert exporter._map_cache.get("china") == content
    
    def test_load_map_script_not_found(self, exporter):
        """Test map script returns empty string when not found."""
        content = exporter._load_map_script("nonexistent")
        
        assert content == ""
    
    def test_detect_required_maps_china(self, exporter):
        """Test detection of China map requirement."""
        option = '{"geo": {"map": "china"}}'
        maps = exporter._detect_required_maps(option, "")
        
        assert "china" in maps
    
    def test_detect_required_maps_world(self, exporter):
        """Test detection of World map requirement."""
        option = '{"geo": {"map": "world"}}'
        maps = exporter._detect_required_maps(option, "")
        
        assert "world" in maps
    
    def test_detect_required_maps_province(self, exporter):
        """Test detection of province map requirement."""
        option = '{"geo": {"map": "beijing"}}'
        custom_js = "// Using 北京 map"
        maps = exporter._detect_required_maps(option, custom_js)
        
        assert "beijing" in maps
    
    def test_detect_required_maps_none(self, exporter):
        """Test no maps detected for regular charts."""
        option = '{"xAxis": {"type": "category"}, "series": [{"type": "bar"}]}'
        maps = exporter._detect_required_maps(option, "")
        
        assert len(maps) == 0
    
    def test_generate_standalone_html(self, exporter):
        """Test standalone HTML generation."""
        option_json = '{"xAxis": {"type": "category"}, "series": [{"type": "bar"}]}'
        data_json = '[{"category": "A", "value": 100}]'
        
        html = exporter.generate_standalone_html(
            title="Test Chart",
            option_json=option_json,
            data_json=data_json
        )
        
        assert "<!DOCTYPE html>" in html
        assert "<title>Test Chart</title>" in html
        assert "Test Chart</div>" in html  # Title div
        assert "var option =" in html
        assert "var rawData =" in html
        assert "echarts.init" in html
    
    def test_generate_standalone_html_with_custom_js(self, exporter):
        """Test HTML generation with custom JavaScript."""
        option_json = '{"series": [{"type": "bar"}]}'
        data_json = '[]'
        custom_js = "console.log('custom');"
        
        html = exporter.generate_standalone_html(
            title="Test",
            option_json=option_json,
            data_json=data_json,
            custom_js=custom_js
        )
        
        assert "console.log('custom');" in html
    
    def test_generate_standalone_html_with_theme(self, exporter):
        """Test HTML generation with dark theme."""
        option_json = '{"series": [{"type": "bar"}]}'
        data_json = '[]'
        
        html = exporter.generate_standalone_html(
            title="Test",
            option_json=option_json,
            data_json=data_json,
            theme="dark"
        )
        
        assert "backgroundColor: '#1a1a1a'" in html
    
    def test_generate_standalone_html_full_screen(self, exporter):
        """Test full screen layout."""
        option_json = '{"series": [{"type": "bar"}]}'
        data_json = '[]'
        
        html = exporter.generate_standalone_html(
            title="Test",
            option_json=option_json,
            data_json=data_json,
            full_screen=True
        )
        
        assert "height: 100vh" in html
        assert "position: absolute" in html
    
    def test_generate_standalone_html_not_full_screen(self, exporter):
        """Test non-full screen layout."""
        option_json = '{"series": [{"type": "bar"}]}'
        data_json = '[]'
        
        html = exporter.generate_standalone_html(
            title="Test",
            option_json=option_json,
            data_json=data_json,
            full_screen=False
        )
        
        assert "height: 600px" in html
        assert "margin: 20px" in html
    
    def test_chinese_characters_preserved(self, exporter):
        """Test Chinese characters are preserved in embedded data."""
        option_json = '{"series": [{"type": "bar"}]}'
        data_json = '[{"城市": "北京", "数值": 100}]'
        
        html = exporter.generate_standalone_html(
            title="中文图表",
            option_json=option_json,
            data_json=data_json
        )
        
        assert "中文图表" in html
        assert "北京" in html
        assert "数值" in html
    
    def test_export_to_file(self, exporter, tmp_path):
        """Test HTML export to file."""
        html = "<html><body>Test</body></html>"
        output_path = tmp_path / "output" / "test.html"
        
        result = exporter.export_to_file(html, str(output_path))
        
        assert output_path.exists()
        assert output_path.read_text(encoding='utf-8') == html
        assert result == str(output_path.absolute())
    
    def test_export_creates_directories(self, exporter, tmp_path):
        """Test export creates parent directories."""
        html = "<html>Test</html>"
        output_path = tmp_path / "deep" / "nested" / "dir" / "test.html"
        
        result = exporter.export_to_file(html, str(output_path))
        
        assert output_path.exists()
