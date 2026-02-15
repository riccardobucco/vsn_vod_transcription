"""Test: validate OpenAPI schema using openapi-spec-validator."""

from pathlib import Path

import pytest


def test_openapi_schema_is_valid():
    """The OpenAPI spec at contracts/openapi.yaml must be syntactically valid."""
    from openapi_spec_validator import validate

    spec_dir = Path(__file__).resolve().parents[2] / "specs" / "001-vod-transcription-utility"
    spec_path = spec_dir / "contracts" / "openapi.yaml"
    if not spec_path.exists():
        pytest.skip("OpenAPI spec file not found")

    import yaml  # type: ignore[import-untyped]

    with open(spec_path) as f:
        spec_dict = yaml.safe_load(f)

    # This will raise if invalid
    validate(spec_dict)
