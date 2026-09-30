"""Regression tests for small validator heuristics fixed during maintenance."""
from pathlib import Path

import fixtures
import pytest


def test_pass_condition_recognizes_past_tense_sent(skill_mod):
    # OBSERVABLE_VERB_RE previously spelled the alternation as send(?:s|sent)?,
    # which matched "send"/"sends" but never the past tense "sent". Here
    # "sent" is the only observable verb, so the fix is what makes this pass.
    assert skill_mod.is_concrete_pass_condition("Payload sent to the client table") is True


def test_pass_condition_still_rejects_generic_claims(skill_mod):
    assert skill_mod.is_concrete_pass_condition("it works") is False
    assert skill_mod.is_concrete_pass_condition("verify successful operation") is False


@pytest.mark.parametrize("condition", [
    "The command exits 0.",
    "The process exits with code 1.",
    "The build exits with exit code `0`.",
    "The report status is passed.",
    "The report status equals failed.",
    "Command exits 0 and report status is passed; omission exits 1 identifying the missing Script.",
])
def test_cli_exit_and_status_pass_conditions(skill_mod, condition):
    assert skill_mod.is_concrete_pass_condition(condition) is True


@pytest.mark.parametrize("condition", [
    "The command works.",
    "The command exits normally.",
    "The command uses version 7 and exits normally.",
    "The command exits. Version 0 is installed.",
    "The command exits; an unrelated table has 0 entries.",
    "The report status is good.",
])
def test_cli_pass_conditions_need_a_bound_observation(skill_mod, condition):
    assert skill_mod.is_concrete_pass_condition(condition) is False


def test_trusted_identity_missing_coordinates_reported_once(record_mod):
    record = fixtures.verified_acquisition_record()
    record["canonical_url"] = ""
    record["package_id"] = ""
    errors, _notes = record_mod.validate_record(Path("record.yaml"), record)
    identity_errors = [e for e in errors if "canonical identity" in e]
    assert identity_errors == [
        "trusted records require canonical_url or package_id to bind trust to canonical identity"
    ]
