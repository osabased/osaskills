#!/usr/bin/env python3
"""Recoverable skill/record promotion; receipts attest checks, never execute them.

The sibling marker serializes cooperating writers and blocks ordinary skill use.
Individual files are replaced atomically; the marker guards the multi-file window.
Recovery covers file bytes, not permission metadata or empty-directory topology.
File/directory conversions are rejected before a transaction is created.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import uuid
from pathlib import Path

IGNORED = {"__pycache__", ".pytest_cache", ".git"}


def marker_path(skill: Path) -> Path:
    return skill.parent / ".skill-maintenance" / (skill.name + ".json")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_digest(files: dict[str, str]) -> str:
    return digest(json.dumps(files, sort_keys=True, separators=(",", ":")).encode())


def regular(path: Path) -> Path:
    path = path.expanduser().absolute()
    for ancestor in (path, *path.parents):
        if ancestor.is_symlink() or (hasattr(ancestor, "is_junction") and ancestor.is_junction()):
            raise ValueError(f"symbolic link/junction is outside the update contract: {ancestor}")
    return path.resolve()


def files_at(root: Path, transaction_id: str = "") -> dict[str, str]:
    files = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in IGNORED for part in relative.parts):
            continue
        regular(path)
        if path.is_file() and not (transaction_id and path.name.endswith(f".maintenance-{transaction_id}.tmp")):
            files[relative.as_posix()] = digest(path.read_bytes())
    return files


def child_path(root: Path, relative: str) -> Path:
    path = regular(root / relative)
    if not path.is_relative_to(root) or path == root:
        raise ValueError(f"file escapes its declared root: {relative}")
    return path


def atomic_write(path: Path, data: bytes, transaction_id: str) -> None:
    path = regular(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".maintenance-{transaction_id}.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def save(directory: Path, state: dict) -> None:
    atomic_write(directory / "transaction.json", (json.dumps(state, indent=2) + "\n").encode(), state["id"])


def snapshot(source: Path, destination: Path, files: dict[str, str]) -> None:
    for relative, expected in files.items():
        data = child_path(source, relative).read_bytes()
        if digest(data) != expected:
            raise ValueError("source changed during snapshot; live state was not modified")
        target = child_path(destination, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def begin(skill: Path, candidate: Path, directory: Path, record: Path | None = None,
          candidate_record: Path | None = None) -> dict:
    skill, candidate, directory = map(regular, (skill, candidate, directory))
    if not (skill / "SKILL.md").is_file() or not (candidate / "SKILL.md").is_file():
        raise ValueError("live skill and candidate must each contain SKILL.md")
    for left, right in ((skill, candidate), (skill, directory), (candidate, directory)):
        if left.is_relative_to(right) or right.is_relative_to(left):
            raise ValueError("live skill, candidate and recovery directory must be disjoint")
    for path in (candidate, directory):
        parts = tuple(part.lower() for part in path.parts)
        if any(parts[index:index + 2] in ((".agents", "skills"), (".codex", "skills"))
               for index in range(len(path.parts) - 1)):
            raise ValueError("candidate and recovery directory must be outside skill discovery")
    if bool(record) != bool(candidate_record):
        raise ValueError("record and candidate-record must be supplied together")
    record = regular(record) if record else None
    candidate_record = regular(candidate_record) if candidate_record else None
    for path in (record, candidate_record):
        if path and (not path.is_file() or path.is_relative_to(skill) or path.is_relative_to(candidate)):
            raise ValueError("records must be existing files outside skill packages")
    if record and (record == candidate_record or record.is_relative_to(directory) or candidate_record.is_relative_to(directory)):
        raise ValueError("record inputs and recovery directory must be disjoint")
    name = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
    live_name = name.search((skill / "SKILL.md").read_text(encoding="utf-8"))
    new_name = name.search((candidate / "SKILL.md").read_text(encoding="utf-8"))
    if not live_name or not new_name or live_name.group(1) != new_name.group(1):
        raise ValueError("repair preserves skill name; identity changes need a separate adoption workflow")
    before = files_at(skill)
    after = files_at(candidate)
    for relative in sorted(set(before) | set(after)):
        if ((relative in before and child_path(candidate, relative).is_dir())
                or (relative in after and child_path(skill, relative).is_dir())):
            raise ValueError(f"file/directory conversion is outside the update contract: {relative}")
    directory.mkdir(parents=True, exist_ok=False)
    transaction_id = uuid.uuid4().hex
    marker = regular(marker_path(skill))
    marker.parent.mkdir(parents=True, exist_ok=True)
    with marker.open("x", encoding="utf-8") as stream:
        json.dump({"transaction": str(directory), "id": transaction_id}, stream)
        stream.flush()
        os.fsync(stream.fileno())
    state = {"format": "guarded-skill-update-v1", "id": transaction_id, "skill": str(skill),
             "record": str(record) if record else None, "phase": "preparing"}
    save(directory, state)
    try:
        state["before"] = before
        state["after"] = after
        snapshot(skill, directory / "before", state["before"])
        snapshot(candidate, directory / "after", state["after"])
        for label, source in (("record-before", record), ("record-after", candidate_record)):
            data = source.read_bytes() if source else None
            state[label] = digest(data) if data is not None else None
            if data is not None:
                (directory / label).write_bytes(data)
        if files_at(skill) != state["before"] or (record and digest(record.read_bytes()) != state["record-before"]):
            raise ValueError("live state changed during preparation; reconcile without overwriting it")
        state["phase"] = "prepared"
        save(directory, state)
    except Exception:
        # A preparation failure cannot have changed live files; retain the guard
        # and available state so failure is explicit rather than reported healthy.
        save(directory, state)
        raise
    return info(state)


def load(directory: Path) -> tuple[Path, dict]:
    directory = regular(directory)
    state = json.loads((directory / "transaction.json").read_text(encoding="utf-8"))
    if state.get("format") != "guarded-skill-update-v1":
        raise ValueError("unknown transaction format")
    skill = regular(Path(state["skill"]))
    marker = json.loads(regular(marker_path(skill)).read_text(encoding="utf-8"))
    if marker != {"transaction": str(directory), "id": state["id"]}:
        raise ValueError("transaction does not own the current guard")
    return directory, state


def info(state: dict) -> dict:
    return {"phase": state["phase"], "skill": state["skill"],
            "candidate_skill_sha256": tree_digest(state["after"]) if "after" in state else None,
            "candidate_record_sha256": state.get("record-final", state.get("record-after"))}


def assert_state(state: dict, expected: dict[str, str], expected_record: str | None) -> None:
    if files_at(regular(Path(state["skill"])), state["id"]) != expected:
        raise ValueError("live skill changed; guard retained for reconciliation")
    if state["record"] and digest(regular(Path(state["record"])).read_bytes()) != expected_record:
        raise ValueError("live record changed; guard retained for reconciliation")


def replace_tree(directory: Path, state: dict, label: str) -> None:
    skill = regular(Path(state["skill"]))
    expected = state[label]
    for relative in sorted(set(state["before"]) | set(state["after"])):
        target = child_path(skill, relative)
        current = digest(target.read_bytes()) if target.is_file() else None
        if current not in {state["before"].get(relative), state["after"].get(relative)}:
            raise ValueError("unknown concurrent file change; guard retained without overwriting it")
        if relative in expected:
            source = child_path(directory / label, relative)
            data = source.read_bytes()
            if digest(data) != expected[relative]:
                raise ValueError("recovery/candidate snapshot changed; guard retained")
            if not target.is_file() or digest(target.read_bytes()) != expected[relative]:
                atomic_write(target, data, state["id"])
        else:
            target.unlink(missing_ok=True)
        target.with_name(target.name + f".maintenance-{state['id']}.tmp").unlink(missing_ok=True)


def apply(directory: Path) -> dict:
    directory, state = load(directory)
    if state["phase"] != "prepared":
        raise ValueError("apply requires prepared state; recover an interrupted promotion first")
    assert_state(state, state["before"], state["record-before"])
    state["phase"] = "applying"
    save(directory, state)
    replace_tree(directory, state, "after")
    if state["record"]:
        data = (directory / "record-after").read_bytes()
        if digest(data) != state["record-after"]:
            raise ValueError("candidate record snapshot changed; guard retained")
        if digest(regular(Path(state["record"])).read_bytes()) != state["record-before"]:
            raise ValueError("record changed during promotion; guard retained without overwriting it")
        atomic_write(regular(Path(state["record"])), data, state["id"])
    assert_state(state, state["after"], state["record-after"])
    state["phase"] = "applied"
    save(directory, state)
    return info(state)


def complete(directory: Path, receipt: Path, final_record: Path | None = None) -> dict:
    directory, state = load(directory)
    if state["phase"] != "applied":
        raise ValueError("completion requires applied state")
    assert_state(state, state["after"], state["record-after"])
    proof = json.loads(regular(receipt).read_text(encoding="utf-8"))
    final_data = regular(final_record).read_bytes() if final_record else None
    if final_record and not state["record"]:
        raise ValueError("transaction has no authoritative record")
    record_hash = digest(final_data) if final_data is not None else state["record-after"]
    if proof.get("candidate_skill_sha256") != tree_digest(state["after"]) or proof.get("candidate_record_sha256") != record_hash:
        raise ValueError("check receipt is not bound to the promoted skill/final record")
    checks = proof.get("checks")
    if not isinstance(checks, list):
        raise ValueError("receipt requires artifact, host and explicit-activation checks")
    scope = proof.get("completion_scope", "operational")
    if scope not in {"operational", "installed"}:
        raise ValueError("unknown receipt completion_scope")
    if scope == "installed":
        authorization = proof.get("authorization")
        if not isinstance(authorization, str) or not authorization.strip():
            raise ValueError("installed-only completion requires the user's scoped authorization")
        if any(not isinstance(check, dict) or check.get("status") not in {"passed", "unavailable"}
               or (check.get("status") == "unavailable" and check.get("gate") not in {"host", "explicit-activation"})
               or not isinstance(check.get("evidence"), str) or not check["evidence"].strip() for check in checks):
            raise ValueError("installed-only completion cannot bypass failed checks or artifact validation")
        for gate in ("host", "explicit-activation"):
            if not any(check.get("gate") == gate for check in checks):
                raise ValueError(f"installed-only receipt must explicitly report the {gate} lane")
        if state["record"]:
            from _common import load_yaml
            record_data = final_data if final_data is not None else (directory / "record-after").read_bytes()
            record = load_yaml(record_data.decode("utf-8-sig"))
            if not isinstance(record, dict) or not isinstance(record.get("host_adoptions"), list):
                raise ValueError("installed-only completion requires truthful host_adoptions state")
            for adoption in record["host_adoptions"]:
                if not isinstance(adoption, dict) or adoption.get("status") == "operational":
                    raise ValueError("installed-only completion cannot publish operational host state")
                evidence = adoption.get("evidence", {})
                if not isinstance(evidence, dict) or evidence.get("explicit_activation") == "passed":
                    raise ValueError("installed-only completion cannot carry an unobserved activation pass")
        gates = ("artifact", "installed-files")
    else:
        if any(not isinstance(check, dict) or check.get("status") != "passed" for check in checks):
            raise ValueError("a receipt check is incomplete or failed; guard retained")
        gates = ("artifact", "host", "explicit-activation")
    for gate in gates:
        if not any(isinstance(check, dict) and check.get("gate") == gate and check.get("status") == "passed"
                   and isinstance(check.get("evidence"), str) and check["evidence"].strip() for check in checks):
            raise ValueError(f"required {gate} check has not passed; candidate remains guarded")
    state["record-final"] = record_hash
    state["phase"] = "finishing"
    save(directory, state)
    if final_data is not None:
        (directory / "record-final").write_bytes(final_data)
        if digest(regular(Path(state["record"])).read_bytes()) != state["record-after"]:
            raise ValueError("record changed during completion; guard retained without overwriting it")
        atomic_write(regular(Path(state["record"])), final_data, state["id"])
    assert_state(state, state["after"], record_hash)
    atomic_write(directory / "receipt.json", (json.dumps(proof, indent=2) + "\n").encode(), state["id"])
    state["phase"] = "completed"
    save(directory, state)
    marker_path(regular(Path(state["skill"]))).unlink()
    return info(state)


def rollback(directory: Path) -> dict:
    directory, state = load(directory)
    if state["phase"] == "preparing":
        raise ValueError("incomplete preparation needs manual reconciliation; no live write was attempted")
    skill = regular(Path(state["skill"]))
    current = files_at(skill, state["id"])
    for relative in set(current) | set(state["before"]) | set(state["after"]):
        if current.get(relative) not in {state["before"].get(relative), state["after"].get(relative)}:
            raise ValueError("unknown concurrent skill change; recovery will not overwrite it")
    if state["record"]:
        current_record = digest(regular(Path(state["record"])).read_bytes())
        if current_record not in {state["record-before"], state["record-after"], state.get("record-final")}:
            raise ValueError("unknown concurrent record change; recovery will not overwrite it")
    state["phase"] = "recovering"
    save(directory, state)
    replace_tree(directory, state, "before")
    if state["record"]:
        data = (directory / "record-before").read_bytes()
        if digest(data) != state["record-before"]:
            raise ValueError("original record snapshot changed; guard retained")
        if digest(regular(Path(state["record"])).read_bytes()) not in {
                state["record-before"], state["record-after"], state.get("record-final")}:
            raise ValueError("record changed during recovery; guard retained without overwriting it")
        atomic_write(regular(Path(state["record"])), data, state["id"])
    assert_state(state, state["before"], state["record-before"])
    state["phase"] = "recovered"
    save(directory, state)
    marker_path(skill).unlink()
    return info(state)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("begin", help="guard and snapshot an already validated factual repair")
    for option in ("skill", "candidate", "transaction"):
        start.add_argument(f"--{option}", type=Path, required=True)
    start.add_argument("--record", type=Path)
    start.add_argument("--candidate-record", type=Path)
    for command in ("apply", "info", "complete", "rollback"):
        sub = commands.add_parser(command)
        sub.add_argument("--transaction", type=Path, required=True)
        if command == "complete":
            sub.add_argument("--receipt", type=Path, required=True)
            sub.add_argument("--final-record", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "begin":
            result = begin(args.skill, args.candidate, args.transaction, args.record, args.candidate_record)
        elif args.command == "info":
            result = info(load(args.transaction)[1])
        elif args.command == "complete":
            result = complete(args.transaction, args.receipt, args.final_record)
        else:
            result = {"apply": apply, "rollback": rollback}[args.command](args.transaction)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
