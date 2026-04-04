"""
Tests for dashboard schema validation.

This module tests the pydantic models for dashboard configuration:
- ChartPosition: Validates row/col positioning and spans
- ChartConfig: Validates individual chart configuration
- DashboardConfig: Validates overall dashboard layout and overlap detection
"""
import pytest
from pydantic import ValidationError


class TestValidConfig:
    """Test valid dashboard configurations."""

    def test_minimal_valid_config(self):
        """Minimal valid config with single chart should pass validation."""
        from scripts.dashboard_schema import ChartPosition, ChartConfig, DashboardConfig

        config = DashboardConfig(
            charts=[
                ChartConfig(
                    id="chart1",
                    position=ChartPosition(row=0, col=0),
                    query="SELECT * FROM data"
                )
            ]
        )
        assert config.title == "Dashboard"
        assert config.columns == 2
        assert len(config.charts) == 1

    def test_multiple_charts_valid(self):
        """Multiple charts at non-overlapping positions should pass validation."""
        from scripts.dashboard_schema import ChartPosition, ChartConfig, DashboardConfig

        config = DashboardConfig(
            title="Multi-Chart Dashboard",
            columns=3,
            charts=[
                ChartConfig(
                    id="chart1",
                    position=ChartPosition(row=0, col=0),
                    query="SELECT * FROM sales"
                ),
                ChartConfig(
                    id="chart2",
                    position=ChartPosition(row=0, col=1),
                    query="SELECT * FROM orders"
                ),
                ChartConfig(
                    id="chart3",
                    position=ChartPosition(row=1, col=0, col_span=2),
                    query="SELECT * FROM metrics"
                ),
            ]
        )
        assert len(config.charts) == 3
        assert config.columns == 3

    def test_chart_with_spans(self):
        """Charts with row_span and col_span should pass validation."""
        from scripts.dashboard_schema import ChartPosition, ChartConfig, DashboardConfig

        config = DashboardConfig(
            charts=[
                ChartConfig(
                    id="big_chart",
                    position=ChartPosition(row=0, col=0, row_span=2, col_span=2),
                    query="SELECT * FROM data"
                )
            ],
            columns=4
        )
        assert config.charts[0].position.row_span == 2
        assert config.charts[0].position.col_span == 2


class TestInvalidPositions:
    """Test invalid position configurations."""

    def test_overlapping_positions(self):
        """Overlapping chart positions should raise ValueError."""
        from scripts.dashboard_schema import ChartPosition, ChartConfig, DashboardConfig

        with pytest.raises(ValueError, match="overlaps"):
            DashboardConfig(
                charts=[
                    ChartConfig(
                        id="chart1",
                        position=ChartPosition(row=0, col=0),
                        query="SELECT * FROM data"
                    ),
                    ChartConfig(
                        id="chart2",
                        position=ChartPosition(row=0, col=0),
                        query="SELECT * FROM other"
                    ),
                ]
            )

    def test_negative_row(self):
        """Negative row value should raise ValidationError."""
        from scripts.dashboard_schema import ChartPosition, ChartConfig, DashboardConfig

        with pytest.raises(ValidationError):
            ChartPosition(row=-1, col=0)

    def test_negative_col(self):
        """Negative col value should raise ValidationError."""
        from scripts.dashboard_schema import ChartPosition

        with pytest.raises(ValidationError):
            ChartPosition(row=0, col=-1)

    def test_zero_span(self):
        """Zero span value should raise ValidationError."""
        from scripts.dashboard_schema import ChartPosition

        with pytest.raises(ValidationError):
            ChartPosition(row=0, col=0, row_span=0)

        with pytest.raises(ValidationError):
            ChartPosition(row=0, col=0, col_span=0)

    def test_col_span_exceeds_columns(self):
        """col_span exceeding grid columns should raise ValueError."""
        from scripts.dashboard_schema import ChartPosition, ChartConfig, DashboardConfig

        with pytest.raises(ValueError, match="exceeds grid columns"):
            DashboardConfig(
                columns=2,
                charts=[
                    ChartConfig(
                        id="wide_chart",
                        position=ChartPosition(row=0, col=0, col_span=3),
                        query="SELECT * FROM data"
                    )
                ]
            )

    def test_chart_position_exceeds_columns(self):
        """Chart starting position plus span exceeding columns should raise ValueError."""
        from scripts.dashboard_schema import ChartPosition, ChartConfig, DashboardConfig

        with pytest.raises(ValueError):
            DashboardConfig(
                columns=2,
                charts=[
                    ChartConfig(
                        id="chart1",
                        position=ChartPosition(row=0, col=1, col_span=2),
                        query="SELECT * FROM data"
                    )
                ]
            )


class TestSchemaGeneration:
    """Test JSON schema generation."""

    def test_json_schema_generated(self):
        """get_dashboard_json_schema() should return dict with properties."""
        from scripts.dashboard_schema import get_dashboard_json_schema

        schema = get_dashboard_json_schema()
        assert isinstance(schema, dict)
        assert "properties" in schema

    def test_json_schema_has_required_fields(self):
        """Schema should list charts as required field."""
        from scripts.dashboard_schema import get_dashboard_json_schema

        schema = get_dashboard_json_schema()
        assert "required" in schema
        assert "charts" in schema["required"]


class TestPositionOverlap:
    """Test overlap detection for complex scenarios."""

    def test_overlapping_with_spans(self):
        """Charts with spans overlapping should raise ValueError."""
        from scripts.dashboard_schema import ChartPosition, ChartConfig, DashboardConfig

        # chart1 occupies (0,0), (0,1), (1,0), (1,1)
        # chart2 at (1,1) overlaps
        with pytest.raises(ValueError, match="overlaps"):
            DashboardConfig(
                charts=[
                    ChartConfig(
                        id="chart1",
                        position=ChartPosition(row=0, col=0, row_span=2, col_span=2),
                        query="SELECT * FROM data"
                    ),
                    ChartConfig(
                        id="chart2",
                        position=ChartPosition(row=1, col=1),
                        query="SELECT * FROM other"
                    ),
                ]
            )

    def test_adjacent_not_overlapping(self):
        """Adjacent charts should not overlap."""
        from scripts.dashboard_schema import ChartPosition, ChartConfig, DashboardConfig

        # Should not raise - adjacent but not overlapping
        config = DashboardConfig(
            columns=2,
            charts=[
                ChartConfig(
                    id="chart1",
                    position=ChartPosition(row=0, col=0),
                    query="SELECT * FROM data"
                ),
                ChartConfig(
                    id="chart2",
                    position=ChartPosition(row=0, col=1),
                    query="SELECT * FROM other"
                ),
            ]
        )
        assert len(config.charts) == 2
