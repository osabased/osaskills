"""Canonical fixture builders for validator tests."""


def valid_skill_text(
    name: str = "roblox-widget-resource",
    description: str = "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
    use_when: str = "- Synchronizing replicated widget state across server-owned sessions.",
) -> str:
    """Synthetic advice-only library skill; runtime behavior is deliberately unverified."""
    return f"""---
name: {name}
description: {description}
---

# Widget Resource 1.2.3

Pinned target: `1.2.3`. [resource.yaml](resource.yaml) holds the exact identity.

## Use when

{use_when}

Use a local table when replication is unnecessary.

## Check the pin

Before relying on version-specific guidance, read the project's manifest and lock:

- `pesde.toml` declares `com.example.widget` at `=1.2.3`, and `pesde.lock` resolves it to `com.example.widget@1.2.3 roblox`.

If they show another version, tell the user, keep the project's pin, use only API you can confirm
at that version, and stop where the task depends on behavior that may differ. Say what you checked.

## Core API

Use `Widget.new()`, `session:Start()`, and `session:Destroy()` for the documented lifecycle.

## Example

The server lifecycle root creates, starts and destroys the session.

## Gotchas

- Invalidate pending waits and tasks before teardown.
- Validate client payloads before changing authoritative server state.

## Read further

If initialization fails, inspect the manifest and server placement. This synthetic
resource has no runtime proof; the custom checker is reviewed independently and nothing
here executes it.
"""


def write_contract(child, *, use_when=None):
    """Explicitly author contract-2 fixture data, never adapt production prose."""
    import yaml
    from _resource_contract import CORE_ROLES
    if use_when is None:
        text = (child / 'SKILL.md').read_text(encoding='utf-8')
        start = text.index('## Use when') + len('## Use when')
        end = text.index('## Check the pin')
        use_when = [line[2:] for line in text[start:end].splitlines() if line.startswith('- ')]
    else:
        use_when = [use_when.removeprefix('- ')]
    data = {
        'schema_version': 2,
        'parent_contract': {'name': 'roblox-resource-acquisition', 'version': 2},
        'scope': 'project',
        'resource': {'slug': 'widget-resource', 'name': 'Widget Resource',
            'canonical_url': 'https://example.com/widget', 'package_id': 'com.example.widget',
            'selector': {'kind': 'version', 'value': '1.2.3'},
            'source_review_date': '2026-08-16', 'devforum_url': None},
        'routing': {'use_when': use_when, 'avoid_when': ['A local table suffices.']},
        'guidance': {'claim_scope': 'advice-only',
            'documents': [{'path': 'SKILL.md', 'roles': sorted(CORE_ROLES | {'setup', 'troubleshooting', 'api'}),
                'when': 'every activated use'}], 'executable_fixture': None},
        'installation': {'profile': 'custom', 'custom_checker': 'scripts/check_widget.py'},
    }
    (child / 'scripts').mkdir(exist_ok=True)
    (child / 'scripts/check_widget.py').write_text('# Synthetic test checker, never run as upstream proof.\n', encoding='utf-8')
    (child / 'resource.yaml').write_text(yaml.safe_dump(data, sort_keys=False), encoding='utf-8')
    return data
