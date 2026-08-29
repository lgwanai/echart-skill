import json

from scripts.validate_chart import (
    _custom_inline_scripts,
    _detect_period_comparison_contract_issues,
    _parse_html,
)


def _comparison(**overrides):
    comparison = {
        "type": "yoy",
        "calendar": "calendar",
        "current_start": "2026-01-01",
        "current_end": "2026-07-31",
        "baseline_start": "2025-01-01",
        "baseline_end": "2025-07-31",
        "current_period_status": "complete",
        "baseline_period_status": "complete",
        "latest_complete_period_end": "2026-07-31",
        "alignment": "same_complete_periods",
        "comparable": True,
        "current_label": "2026年1–7月",
        "baseline_label": "2025年1–7月",
    }
    comparison.update(overrides)
    return comparison


def _html(comparison=None, text="2026年1–7月同比2025年1–7月增长33.7%"):
    contract = {"version": 1, "comparisons": [comparison or _comparison()]}
    return (
        "<html><body>"
        f"<p>{text}</p>"
        '<script type="application/json" id="analysis-comparison-contract">'
        f"{json.dumps(contract, ensure_ascii=False)}"
        "</script>"
        "</body></html>"
    )


def test_temporal_claim_requires_embedded_contract():
    issues = _detect_period_comparison_contract_issues(
        "<html><body>2026年1–7月同比增长33.7%</body></html>"
    )

    assert any("no machine-readable" in issue for issue in issues)


def test_finance_qoq_claim_also_requires_embedded_contract():
    issues = _detect_period_comparison_contract_issues(
        "<html><body>Operating expense QoQ decreased 4.1%</body></html>"
    )

    assert any("no machine-readable" in issue for issue in issues)


def test_aligned_yoy_contract_passes_and_is_not_treated_as_javascript():
    content = _html()

    assert _detect_period_comparison_contract_issues(content) == []
    assert _custom_inline_scripts(_parse_html(content)) == []


def test_rejects_ytd_versus_full_year_even_when_marked_comparable():
    content = _html(
        _comparison(
            baseline_end="2025-12-31",
            baseline_label="2025年全年",
        ),
        text="2026年1–7月同比2025年全年下降22%",
    )

    issues = _detect_period_comparison_contract_issues(content)

    assert any("YoY end month/day must align" in issue for issue in issues)


def test_rejects_contract_label_not_visible_on_page():
    issues = _detect_period_comparison_contract_issues(
        _html(text="同比增长33.7%，周期详见说明")
    )

    assert any("current_label" in issue and "not shown" in issue for issue in issues)
    assert any("baseline_label" in issue and "not shown" in issue for issue in issues)


def test_rejects_malformed_contract_json():
    content = (
        "<html><body>同比增长33.7%"
        '<script type="application/json" id="analysis-comparison-contract">{oops}</script>'
        "</body></html>"
    )

    issues = _detect_period_comparison_contract_issues(content)

    assert any("not valid JSON" in issue for issue in issues)


def test_contract_must_use_application_json_type():
    content = _html().replace('type="application/json"', 'type="text/javascript"')

    issues = _detect_period_comparison_contract_issues(content)

    assert any('must use type="application/json"' in issue for issue in issues)


def test_non_temporal_chart_does_not_require_contract():
    assert _detect_period_comparison_contract_issues(
        "<html><body>各门店库存周转率排名</body></html>"
    ) == []


def test_retail_445_yoy_allows_governed_named_periods_with_shifted_dates():
    comparison = _comparison(
        calendar="retail_445",
        alignment="same_named_periods",
        current_period_key="FY2026-P07",
        baseline_period_key="FY2025-P07",
        current_start="2026-07-05",
        current_end="2026-08-01",
        baseline_start="2025-07-06",
        baseline_end="2025-08-02",
        latest_complete_period_end="2026-08-01",
        current_label="FY2026 P07",
        baseline_label="FY2025 P07",
    )

    issues = _detect_period_comparison_contract_issues(
        _html(comparison, text="FY2026 P07 同比 FY2025 P07 销售额增长8.2%")
    )

    assert issues == []


def test_finance_partial_period_cannot_compare_with_closed_period():
    comparison = _comparison(
        type="qoq",
        calendar="fiscal",
        current_period_status="partial",
        baseline_period_status="complete",
        alignment="same_elapsed_days",
        current_label="FY2026 Q3截至第40天",
        baseline_label="FY2026 Q2完整季度",
    )

    issues = _detect_period_comparison_contract_issues(
        _html(comparison, text="FY2026 Q3截至第40天环比FY2026 Q2完整季度费用下降5%")
    )

    assert any("partial and complete periods cannot be compared" in issue for issue in issues)
