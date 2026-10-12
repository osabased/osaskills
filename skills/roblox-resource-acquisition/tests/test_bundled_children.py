"""Validate the bundled resource children (sibling skills with resource.yaml), without host claims."""
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT.parent
BUNDLES = sorted(path.parent for path in SKILLS.glob('*/resource.yaml') if path.parent != ROOT)


def test_parent_installation_payload_contains_no_nested_skills():
    assert sorted(ROOT.rglob('SKILL.md')) == [ROOT / 'SKILL.md']


@pytest.mark.parametrize('child', BUNDLES, ids=lambda path: path.name)
def test_bundled_child_is_a_complete_composed_package(skill_mod, child):
    errors, _ = skill_mod.validate_skill(child)
    assert errors == [], '\n'.join(errors)


@pytest.mark.parametrize('child', BUNDLES, ids=lambda path: path.name)
def test_bundled_child_routes_to_sibling_parent(child):
    text = (child / 'SKILL.md').read_text(encoding='utf-8')
    assert '../roblox-resource-acquisition/references/child-usage.md' in text
    assert (child.parent / 'roblox-resource-acquisition/references/child-usage.md').is_file()


@pytest.mark.skipif(not BUNDLES, reason='No bundled children beside the parent (standalone install)')
def test_bundled_children_are_present_without_record_paths():
    assert {child.name for child in BUNDLES} >= {
        'roblox-vide', 'roblox-charm', 'roblox-ui-labs', 'roblox-bootstrapper',
        'roblox-janitor', 'roblox-lemonsignal', 'roblox-blink', 'roblox-nevermore-ui'}
    for child in BUNDLES:
        reconciliation = yaml.safe_load((child / 'resource.yaml').read_text(encoding='utf-8'))['reconciliation']
        assert set(reconciliation) == {'policy', 'reason'}, child.name
