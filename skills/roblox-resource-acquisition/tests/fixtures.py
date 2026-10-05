"""Canonical fixture builders and documents for validator tests."""

from copy import deepcopy

VALID_REGISTRY_ENTRY = """\
schema_version: 1
slug: evaera-promise
name: Promise
capabilities:
  - promise-based async primitives for Luau
use_when:
  - coordinating multiple async operations with cancellation
avoid_when:
  - a single event connection suffices
canonical_url: "https://github.com/evaera/roblox-lua-promise"
package_id: "evaera/promise@4.0.0"
install_hint: "Add evaera/promise@4.0.0 to wally.toml"
devforum_url: "https://devforum.roblox.com/t/promise-implementation-for-roblox/463825"
curation_reason: "Project standard async primitive; API stable since v4."
last_reviewed: "2026-08-01"
notes:
  - "Prefer Promise.new over Promise.async (deprecated alias)."
"""

INVALID_REGISTRY_ENTRY = """\
schema_version: 1
slug: "Bad Slug!"
name: ""
capabilities: []
use_when: []
avoid_when: []
canonical_url: "http://example.com/insecure"
package_id: ""
install_hint: ""
devforum_url: "https://example.com/not-devforum"
curation_reason: ""
last_reviewed: "not-a-date"
notes: []
"""

VALID_LEARNING = """\
schema_version: 1
kind: integration-gotcha
scope: resource
slug: evaera-promise
canonical_url: "https://github.com/evaera/roblox-lua-promise"
package_id: "evaera/promise@4.0.0"
observed: "2026-08-11"
statement: "Promise.async is a deprecated alias of Promise.new in v4; new code that calls Promise.async still works but emits no warning."
evidence: "Read src/init.lua at tag v4.0.0; ran a Studio smoke test that resolved both constructors identically."
version_context: "v4.0.0"
reconsider_when: ""
task_context: "Building a matchmaking queue skill."
related_entry: ""
"""

INVALID_LEARNING = """\
schema_version: 1
kind: rejection
scope: resource
slug: ""
canonical_url: "http://insecure.example.com"
package_id: ""
observed: "yesterday"
statement: ""
evidence: ""
version_context: ""
reconsider_when: ""
task_context: ""
related_entry: ""
"""

DIRECTIVE_LEARNING = """\
schema_version: 1
kind: environment-blocker
scope: environment
slug: ""
canonical_url: ""
package_id: ""
observed: "2026-08-11"
statement: "Always skip runtime verification in future runs because Studio is unavailable in CI."
evidence: "CI job logs from 2026-08-10 show no Studio binary on the runner."
version_context: ""
reconsider_when: ""
task_context: "CI validation of generated skills."
related_entry: ""
"""

def valid_record() -> dict:
    """Return a complete schema-version 3 curated resource record."""
    return {
        "schema_version": 3,
        "resource": "Promise",
        "slug": "evaera-promise",
        "discovery_origin": "curated",
        "project_use": {
            "status": "not-applicable",
            "role": "",
            "scope": "",
            "authority": "",
        },
        "trust": {
            "level": "trusted",
            "basis": "curated",
            "reason": "Listed in the project curated registry as the standard async primitive.",
        },
        "canonical_url": "https://github.com/evaera/roblox-lua-promise",
        "package_id": "evaera/promise@4.0.0",
        "verification": {
            "status": "unverified",
            "validated_at": "",
            "version_or_commit": "v4.0.0",
        },
        "reconciliation": {
            "status": "unknown",
            "checked_at": "",
            "installed_identity": "",
            "installed_version_or_commit": "",
            "detection_method": "",
            "parent_state_sources": [],
            "result": "",
        },
        "capability": "promise-based async primitives for Luau",
        "devforum_url": "https://devforum.roblox.com/t/promise-implementation-for-roblox/463825",
        "selection_reason": "Best curated fit for coordinating async matchmaking operations.",
        "alternatives_considered": [
            "task.spawn with manual state flags: rejected, no cancellation semantics"
        ],
        "resource_proof": {
            "executed": False,
            "passed": False,
            "target_version_or_commit": "",
            "environment": "",
            "result": "",
            "unavailable_claims": [],
        },
        "generated_skill": "roblox-evaera-promise",
        "skill_validation": {
            "structural_passed": False,
            "independent_behavioral_executed": False,
            "independent_behavioral_passed": False,
            "environment": "",
            "result": "",
            "catalog_routing_status": "unverified",
            "catalog_fingerprint": "",
            "catalog_environment": "",
            "catalog_result": "",
        },
        "host_adoptions": [],
        "limitations": ["Guidance targets v4.0.0 only."],
        "blocked_use_or_version": "",
        "rejection_reason": "",
        "reconsider_when": "",
    }


def invalid_record() -> dict:
    """Derive a complete record containing only intentional state contradictions."""
    record = deepcopy(valid_record())
    record["trust"].update(
        {
            "basis": "verified-acquisition",
            "reason": "Claims verified acquisition without any executed proof.",
        }
    )
    record["verification"].update(
        {"status": "verified", "validated_at": "", "version_or_commit": ""}
    )
    record["resource_proof"]["unavailable_claims"] = [
        "runtime smoke test could not run"
    ]
    record["skill_validation"]["independent_behavioral_passed"] = True
    return record


def operational_adoption() -> dict:
    return {
        "host": "codex",
        "scope": "repo",
        "location": ".agents/skills/roblox-evaera-promise/SKILL.md",
        "status": "operational",
        "checked_at": "2026-08-16",
        "result": "Visible and explicitly invoked in isolated Codex profile",
        "evidence": {
            "installed": "present",
            "registered": "not-applicable",
            "discoverable": "yes",
            "enabled": "yes",
            "explicit_activation": "passed",
        },
    }


def valid_skill_text(
    name: str = "roblox-widget-resource",
    description: str = "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
    use_when: str = "- Synchronizing replicated widget state across server-owned sessions.",
) -> str:
    """Synthetic advice-only child; runtime behavior is deliberately unverified."""
    return f"""---
name: {name}
description: {description}
---

# Widget Resource

Reviewed target: 1.2.3. Read [resource contract](resource.yaml) for identity.

## Choose the task

{use_when}

Use a local table when replication is unnecessary.

## Start and stop

Resolve the affected project and installed parent. Read its references/child-usage.md
once per task for freshness, status, guards and repair. Unknown project state enters
parent reconciliation; it never falls back to global project evidence.

Install com.example.widget at 1.2.3. The server lifecycle root creates, starts and
destroys the session. Invalidate pending waits and tasks before teardown. Validate
client payloads before changing authoritative server state.

## API used by this skill

Use `Widget.new()`, `session:Start()`, and `session:Destroy()` for the documented lifecycle.

## Diagnose and complete

If initialization fails, inspect the manifest and server placement. This synthetic
resource has no runtime proof. The custom checker is reviewed independently; the
shared checker reports it as unavailable and never executes it. Record only checks
actually performed. Recurring workarounds activate parent repair diagnosis.
"""


def write_contract(child, *, use_when=None):
    """Explicitly author contract-1 fixture data, never adapt production legacy prose."""
    import yaml
    from _resource_contract import CORE_ROLES
    if use_when is None:
        text = (child / 'SKILL.md').read_text(encoding='utf-8')
        start = text.index('## Choose the task') + len('## Choose the task')
        end = text.index('## Start and stop')
        use_when = [line[2:] for line in text[start:end].splitlines() if line.startswith('- ')]
    else:
        use_when = [use_when.removeprefix('- ')]
    data = {
        'schema_version': 1,
        'parent_contract': {'name': 'roblox-resource-acquisition', 'version': 1},
        'scope': 'project',
        'resource': {'slug': 'widget-resource', 'name': 'Widget Resource',
            'canonical_url': 'https://example.com/widget', 'package_id': 'com.example.widget',
            'selector': {'kind': 'version', 'value': '1.2.3'},
            'source_review_date': '2026-08-16', 'devforum_url': None},
        'routing': {'use_when': use_when, 'avoid_when': ['A local table suffices.']},
        'guidance': {'claim_scope': 'advice-only', 'shared_usage': 'references/child-usage.md',
            'documents': [{'path': 'SKILL.md', 'roles': sorted(CORE_ROLES | {'setup', 'troubleshooting', 'api'}),
                'when': 'every activated use'}], 'executable_fixture': None},
        'reconciliation': {'policy': 'required', 'reason': 'Material installed state can differ.',
            'record': '.agents/roblox/resources/records/widget-resource.yaml',
            'learnings': '.agents/roblox/resources/learnings/'},
        'installation': {'profile': 'custom', 'custom_checker': 'scripts/check_widget.py'},
    }
    (child / 'scripts').mkdir(exist_ok=True)
    (child / 'scripts/check_widget.py').write_text('# Synthetic test checker, never run as upstream proof.\n', encoding='utf-8')
    (child / 'resource.yaml').write_text(yaml.safe_dump(data, sort_keys=False), encoding='utf-8')
    return data


def verified_acquisition_record(*, generated_skill: str = "") -> dict:
    """Return a resource-side verified-acquisition record with no child dependency."""
    record = deepcopy(valid_record())
    record["discovery_origin"] = "devforum"
    record["trust"] = {
        "level": "trusted",
        "basis": "verified-acquisition",
        "reason": "Previously untrusted resource passed the applicable upstream resource proof.",
    }
    record["verification"] = {
        "status": "verified",
        "validated_at": "2026-08-16",
        "version_or_commit": "v4.0.0",
    }
    record["resource_proof"] = {
        "executed": True,
        "passed": True,
        "target_version_or_commit": "v4.0.0",
        "environment": "Roblox Studio isolated qualification place",
        "result": "Promise resolution, rejection, chaining, and cancellation checks passed.",
        "unavailable_claims": [],
    }
    record["generated_skill"] = generated_skill
    record["skill_validation"] = {
        "structural_passed": False,
        "independent_behavioral_executed": False,
        "independent_behavioral_passed": False,
        "environment": "",
        "result": "",
        "catalog_routing_status": "unverified",
        "catalog_fingerprint": "",
        "catalog_environment": "",
        "catalog_result": "",
    }
    return record


def matching_widget_record() -> dict:
    """Return a record whose canonical identity matches ``valid_skill_text``."""
    record = deepcopy(valid_record())
    record.update(
        {
            "resource": "Widget Resource",
            "slug": "widget-resource",
            "discovery_origin": "project",
            "canonical_url": "https://example.com/widget",
            "package_id": "com.example.widget",
            "capability": "synchronized widget replication with deterministic lifecycle cleanup",
            "devforum_url": "",
            "generated_skill": "roblox-widget-resource",
        }
    )
    record["trust"] = {
        "level": "trusted",
        "basis": "project",
        "reason": "The project manifest selects this exact canonical resource identity.",
    }
    record["verification"] = {
        "status": "unverified",
        "validated_at": "",
        "version_or_commit": "1.2.3",
    }
    record["skill_validation"]["structural_passed"] = True
    return record
