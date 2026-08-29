import json
import subprocess
import sys
from pathlib import Path

from scripts.validate_analysis_plan import validate_plan


ROOT = Path(__file__).resolve().parents[1]


def valid_plan():
    return {
        "decision_context": "决定下月区域资源调整",
        "audience": "销售负责人",
        "analysis_mode": "decision_support",
        "questions": ["哪些区域贡献了本月下滑？"],
        "views": [{
            "id": "v1",
            "message": "华东贡献本月销售额同比下滑的 62%",
            "relation": "deviation",
            "primary_view": "waterfall",
            "reason": "需要表达各区域对总变化的正负贡献",
            "rejected_alternatives": [{"view": "pie", "reason": "无法表达负贡献"}],
            "table_mode": "companion",
            "table_reason": "需要核对区域贡献额和贡献率",
            "table_columns": ["区域", "销售额变化", "贡献率"],
            "category_count": 8,
            "exact_lookup": True,
            "measure_count": 2,
            "evidence_ref": "Data A3",
            "comparison": {
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
            },
        }],
        "findings": [{
            "id": "f1",
            "importance": "major",
            "what": "销售额环比下降 12%，华东贡献 62% 的降幅",
            "baseline": "与上月同口径完整周期比较",
            "why_status": "hypothesis",
            "why": "订单量下降是优先假设，尚需验证",
            "so_what": "优先定位华东问题，而不是全局调价",
            "next_check": "按华东渠道拆分订单量、客单价和库存可用率",
            "evidence_refs": ["Data A1", "Data A3"],
            "limitations": ["当前数据不含投放和库存字段"],
        }],
    }


def test_accepts_decision_ready_plan():
    assert validate_plan(valid_plan()) == []


def test_rejects_topic_only_message():
    plan = valid_plan()
    plan["views"][0]["message"] = "区域销售分析"
    assert any("must state a finding" in error for error in validate_plan(plan))


def test_rejects_pie_with_too_many_categories():
    plan = valid_plan()
    plan["views"][0].update({"relation": "composition", "primary_view": "pie", "category_count": 8})
    assert any("pie is limited" in error for error in validate_plan(plan))


def test_rejects_chart_only_for_exact_lookup():
    plan = valid_plan()
    plan["views"][0]["table_mode"] = "source_toggle"
    assert any("require companion or primary" in error for error in validate_plan(plan))


def test_rejects_shallow_finding():
    plan = valid_plan()
    plan["findings"][0]["next_check"] = ""
    assert any("next_check" in error for error in validate_plan(plan))


def test_cli_accepts_valid_json(tmp_path):
    plan_path = tmp_path / "analysis-plan.json"
    plan_path.write_text(json.dumps(valid_plan(), ensure_ascii=False), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_analysis_plan.py"), str(plan_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "decision-ready" in result.stdout


def test_rejects_ytd_compared_with_full_year():
    plan = valid_plan()
    plan["views"][0]["comparison"]["baseline_end"] = "2025-12-31"
    errors = validate_plan(plan)
    assert any("YoY end month/day must align" in error for error in errors)


def test_rejects_complete_period_beyond_latest_complete_date():
    plan = valid_plan()
    plan["views"][0]["comparison"]["current_end"] = "2026-08-25"
    errors = validate_plan(plan)
    assert any("exceeds the latest complete period" in error for error in errors)


def test_rejects_comparison_claim_without_period_contract():
    plan = valid_plan()
    del plan["views"][0]["comparison"]
    errors = validate_plan(plan)
    assert any("comparison: required" in error for error in errors)


def test_accepts_retail_445_named_period_yoy_with_shifted_calendar_dates():
    plan = valid_plan()
    plan["views"][0]["comparison"] = {
        "type": "yoy",
        "calendar": "retail_445",
        "current_period_key": "FY2026-P07",
        "baseline_period_key": "FY2025-P07",
        "current_start": "2026-07-05",
        "current_end": "2026-08-01",
        "baseline_start": "2025-07-06",
        "baseline_end": "2025-08-02",
        "current_period_status": "complete",
        "baseline_period_status": "complete",
        "latest_complete_period_end": "2026-08-01",
        "alignment": "same_named_periods",
        "comparable": True,
    }

    assert validate_plan(plan) == []


def test_rejects_finance_open_quarter_compared_with_closed_quarter():
    plan = valid_plan()
    plan["views"][0]["comparison"].update({
        "type": "qoq",
        "calendar": "fiscal",
        "current_period_status": "partial",
        "baseline_period_status": "complete",
        "alignment": "same_elapsed_days",
    })

    errors = validate_plan(plan)

    assert any("partial and complete periods cannot be compared" in error for error in errors)
