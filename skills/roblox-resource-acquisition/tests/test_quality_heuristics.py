"""Stable-identity error deduplication regression."""
from pathlib import Path
import fixtures


def test_trusted_identity_missing_coordinates_reported_once(record_mod):
    record = fixtures.verified_acquisition_record()
    record["canonical_url"] = ""
    record["package_id"] = ""
    errors, _notes = record_mod.validate_record(Path("record.yaml"), record)
    identity_errors = [e for e in errors if "canonical identity" in e]
    assert identity_errors == [
        "trusted records require canonical_url or package_id to bind trust to canonical identity"
    ]
