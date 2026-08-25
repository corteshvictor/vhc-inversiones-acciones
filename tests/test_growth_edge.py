"""Growth edge cases with a single metric available."""

import pytest


@pytest.mark.parametrize(
    ("revenue_growth", "expected_aqr"),
    [(-0.01, "Medio"), (0.0, "Sí"), (0.01, "Sí")],
)
def test_single_non_positive_growth_metric(
    evaluate_row, make_case, revenue_growth, expected_aqr
):
    row, _, raw, number, percentage = make_case(
        {"Avg EPS Growth (5y)": None, "Revenue CAGR (5y)": revenue_growth}
    )

    result = evaluate_row(row, raw, number, percentage)

    assert result["lenses"][2] == expected_aqr
