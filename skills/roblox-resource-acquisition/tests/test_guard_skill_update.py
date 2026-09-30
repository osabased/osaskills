"""Real filesystem failure/recovery checks; synthetic receipts are not runtime proof."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys

import fixtures
import pytest
import yaml

import guard_skill_update as guard


@pytest.fixture
def repair(tmp_path):
    live = tmp_path / "host" / "roblox-widget-resource"
    live.mkdir(parents=True)
    (live / "SKILL.md").write_text(fixtures.valid_skill_text(), encoding="utf-8")
    (live / "unchanged.txt").write_text("unchanged", encoding="utf-8")
    (live / "removed.txt").write_text("original", encoding="utf-8")
    candidate = tmp_path / "candidate"
    shutil.copytree(live, candidate)
    (candidate / "SKILL.md").write_text(fixtures.valid_skill_text() + "\nFactual correction.\n", encoding="utf-8")
    (candidate / "removed.txt").unlink()
    (candidate / "added.txt").write_text("new", encoding="utf-8")
    record = fixtures.matching_widget_record()
    record["reconciliation"]["status"] = "matched"
    adoption = fixtures.operational_adoption()
    adoption["location"] = str(live)
    adoption["status"] = "installed"
    record["host_adoptions"] = [adoption]
    record_path = tmp_path / "record.yaml"
    record_path.write_text(yaml.safe_dump(record), encoding="utf-8")
    candidate_record = tmp_path / "candidate-record.yaml"
    candidate_record.write_bytes(record_path.read_bytes())
    return live, candidate, tmp_path / "transaction", record_path, candidate_record


def receipt_for(transaction, path, **changes):
    values = guard.info(guard.load(transaction)[1])
    values["checks"] = [{"gate": gate, "status": "passed", "evidence": "synthetic test receipt"}
                        for gate in ("artifact", "host", "explicit-activation")]
    values.update(changes)
    path.write_text(json.dumps(values), encoding="utf-8")
    return path


def test_guard_blocks_installed_host_through_apply_until_bound_completion(repair, status_mod, tmp_path):
    live, candidate, transaction, record, candidate_record = repair
    assert status_mod.query_pair(live, record)["status"] == "healthy"
    unchanged_time = (live / "unchanged.txt").stat().st_mtime_ns
    guard.begin(*repair)
    assert status_mod.query_pair(live, record)["status"] == "blocked"
    guard.apply(transaction)
    assert status_mod.query_pair(live, record)["status"] == "blocked"
    assert not (live / "removed.txt").exists()
    assert (live / "added.txt").read_text() == "new"
    assert (live / "unchanged.txt").stat().st_mtime_ns == unchanged_time
    proof = receipt_for(transaction, tmp_path / "receipt.json", command="create an unwanted file")
    guard.complete(transaction, proof)
    assert status_mod.query_pair(live, record)["status"] == "healthy"
    assert (transaction / "before" / "removed.txt").is_file()
    assert (transaction / "receipt.json").is_file()


def test_required_unavailable_or_unbound_checks_keep_candidate_guarded(repair, tmp_path):
    _, _, transaction, _, _ = repair
    guard.begin(*repair)
    guard.apply(transaction)
    proof = receipt_for(transaction, tmp_path / "receipt.json")
    values = json.loads(proof.read_text())
    values["checks"][-1]["status"] = "unavailable"
    proof.write_text(json.dumps(values))
    with pytest.raises(ValueError, match="incomplete or failed"):
        guard.complete(transaction, proof)
    receipt_for(transaction, proof, candidate_skill_sha256="wrong")
    with pytest.raises(ValueError, match="not bound"):
        guard.complete(transaction, proof)
    assert guard.marker_path(repair[0]).exists()


def test_second_writer_and_changed_baseline_cannot_overwrite_live_work(repair, tmp_path):
    live, candidate, transaction, record, candidate_record = repair
    guard.begin(*repair)
    with pytest.raises(FileExistsError):
        guard.begin(live, candidate, tmp_path / "other-transaction", record, candidate_record)
    (live / "unchanged.txt").write_text("concurrent work")
    with pytest.raises(ValueError, match="live skill changed"):
        guard.apply(transaction)
    with pytest.raises(ValueError, match="unknown concurrent"):
        guard.rollback(transaction)
    assert (live / "unchanged.txt").read_text() == "concurrent work"
    assert guard.marker_path(live).exists()


def test_interrupted_multifile_apply_is_blocked_and_recovers_original_hard_block(repair, status_mod, monkeypatch):
    live, _, transaction, record, candidate_record = repair
    original = yaml.safe_load(record.read_text())
    original["blocked_use_or_version"] = "Original hard resource block"
    record.write_text(yaml.safe_dump(original))
    original_skill = guard.files_at(live)
    original_record = record.read_bytes()
    guard.begin(*repair)
    writer = guard.atomic_write
    writes = 0

    def interrupted(path, data, transaction_id):
        nonlocal writes
        writer(path, data, transaction_id)
        if path.is_relative_to(live):
            writes += 1
            if writes == 1:
                raise OSError("simulated process interruption")

    monkeypatch.setattr(guard, "atomic_write", interrupted)
    with pytest.raises(OSError, match="interruption"):
        guard.apply(transaction)
    assert status_mod.query_pair(live, record)["status"] == "blocked"
    monkeypatch.setattr(guard, "atomic_write", writer)
    guard.rollback(transaction)
    assert guard.files_at(live) == original_skill
    assert record.read_bytes() == original_record
    assert status_mod.query_pair(live, record)["reason"] == "Original hard resource block"
    assert not guard.marker_path(live).exists()


def test_recovery_refuses_unknown_record_changes(repair):
    _, _, transaction, record, _ = repair
    guard.begin(*repair)
    guard.apply(transaction)
    record.write_text(record.read_text() + "\n# other writer's change\n")
    with pytest.raises(ValueError, match="unknown concurrent record"):
        guard.rollback(transaction)
    assert "other writer" in record.read_text()


def test_concurrent_edit_during_apply_is_preserved(repair, monkeypatch):
    live, _, transaction, _, _ = repair
    guard.begin(*repair)
    writer = guard.atomic_write

    def another_writer(path, data, transaction_id):
        writer(path, data, transaction_id)
        if path == live / "SKILL.md":
            (live / "unchanged.txt").write_text("mid-promotion concurrent work")

    monkeypatch.setattr(guard, "atomic_write", another_writer)
    with pytest.raises(ValueError, match="unknown concurrent file"):
        guard.apply(transaction)
    assert (live / "unchanged.txt").read_text() == "mid-promotion concurrent work"
    assert guard.marker_path(live).exists()


def test_concurrent_record_edit_during_apply_is_preserved(repair, monkeypatch):
    live, _, transaction, record, _ = repair
    guard.begin(*repair)
    writer = guard.atomic_write

    def another_writer(path, data, transaction_id):
        writer(path, data, transaction_id)
        if path == live / "SKILL.md":
            record.write_text(record.read_text() + "\n# concurrent record work\n")

    monkeypatch.setattr(guard, "atomic_write", another_writer)
    with pytest.raises(ValueError, match="record changed during promotion"):
        guard.apply(transaction)
    assert "concurrent record work" in record.read_text()
    assert guard.marker_path(live).exists()


def test_final_record_is_bound_and_can_be_recovered_after_finish_interruption(repair, tmp_path, monkeypatch):
    live, _, transaction, record, _ = repair
    original = record.read_bytes()
    guard.begin(*repair)
    guard.apply(transaction)
    final_record = tmp_path / "final.yaml"
    final_record.write_bytes(record.read_bytes() + b"\n# actual host proof would be recorded here\n")
    proof = receipt_for(transaction, tmp_path / "receipt.json", candidate_record_sha256=guard.digest(final_record.read_bytes()))
    writer = guard.atomic_write

    def interrupted(path, data, transaction_id):
        writer(path, data, transaction_id)
        if path == record:
            raise OSError("finish interrupted")

    monkeypatch.setattr(guard, "atomic_write", interrupted)
    with pytest.raises(OSError, match="finish interrupted"):
        guard.complete(transaction, proof, final_record)
    assert guard.marker_path(live).exists()
    monkeypatch.setattr(guard, "atomic_write", writer)
    guard.rollback(transaction)
    assert record.read_bytes() == original


def test_corrupt_guard_blocks_query_without_reading_or_executing_contents(repair, status_mod):
    live, _, _, record, _ = repair
    marker = guard.marker_path(live)
    marker.parent.mkdir()
    marker.write_text("malformed guard; execute nothing")
    assert status_mod.query_pair(live, record)["status"] == "blocked"


def test_candidate_and_recovery_must_be_outside_discovery(repair, tmp_path):
    live, candidate, _, _, _ = repair
    with pytest.raises(ValueError, match="disjoint"):
        guard.begin(live, candidate, live / "transaction")
    with pytest.raises(ValueError, match="outside skill discovery"):
        guard.begin(live, candidate, tmp_path / ".agents" / "skills" / "transaction")


def test_snapshot_corruption_never_reports_an_applied_repair(repair):
    _, _, transaction, _, _ = repair
    guard.begin(*repair)
    (transaction / "after" / "SKILL.md").write_text("tampered candidate")
    with pytest.raises(ValueError, match="snapshot changed"):
        guard.apply(transaction)
    assert guard.marker_path(repair[0]).exists()


def test_real_cli_promotes_and_recovers_without_executing_receipt_commands(repair, scripts_dir, tmp_path):
    live, candidate, transaction, _, _ = repair
    script = scripts_dir / "guard_skill_update.py"
    for args in (["begin", "--skill", str(live), "--candidate", str(candidate), "--transaction", str(transaction)],
                 ["apply", "--transaction", str(transaction)],
                 ["rollback", "--transaction", str(transaction)]):
        run = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)
        assert run.returncode == 0, run.stderr
    assert not guard.marker_path(live).exists()


@pytest.mark.parametrize("live_kind,candidate_kind", [
    ("file", "directory"),
    ("file", "empty-directory"),
    ("directory", "file"),
    ("empty-directory", "file"),
])
def test_path_type_change_is_rejected_before_guard_or_transaction(repair, live_kind, candidate_kind):
    live, candidate, transaction, record, candidate_record = repair
    for root, kind in ((live, live_kind), (candidate, candidate_kind)):
        path = root / "guide"
        if kind == "file":
            path.write_text("original guide", encoding="utf-8")
        else:
            path.mkdir()
            if kind == "directory":
                (path / "detail.md").write_text("nested guide", encoding="utf-8")
    original_files = guard.files_at(live)
    candidate_files = guard.files_at(candidate)
    original_record = record.read_bytes()
    with pytest.raises(ValueError, match="file/directory"):
        guard.begin(*repair)
    assert not transaction.exists()
    assert not guard.marker_path(live).exists()
    assert guard.files_at(live) == original_files
    assert guard.files_at(candidate) == candidate_files
    assert record.read_bytes() == original_record == candidate_record.read_bytes()
    assert (live / "guide").is_file() == (live_kind == "file")
    assert (candidate / "guide").is_file() == (candidate_kind == "file")
