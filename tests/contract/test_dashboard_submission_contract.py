"""Test: validate dashboard submission OpenAPI schema."""

from pathlib import Path

import pytest


def test_dashboard_submission_openapi_is_valid():
    """The OpenAPI spec for dashboard submission UX must be valid."""
    from openapi_spec_validator import validate

    spec_dir = Path(__file__).resolve().parents[2] / "specs" / "002-dashboard-submission-ux"
    spec_path = spec_dir / "contracts" / "openapi.yaml"
    if not spec_path.exists():
        pytest.skip("Dashboard submission OpenAPI spec not found")

    import yaml

    with open(spec_path) as f:
        spec_dict = yaml.safe_load(f)

    validate(spec_dict)
