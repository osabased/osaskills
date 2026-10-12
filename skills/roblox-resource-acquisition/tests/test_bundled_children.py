"""Validate the bundled resource children (skills under libraries/ with resource.yaml), without host claims."""
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
LIBRARIES = ROOT / 'libraries'
BUNDLES = sorted(path.parent for path in LIBRARIES.glob('*/resource.yaml'))


def test_nested_skills_live_only_in_libraries():
    nested = {path.parent for path in ROOT.rglob('SKILL.md')} - {ROOT}
    assert nested == set(BUNDLES)


@pytest.mark.parametrize('child', BUNDLES, ids=lambda path: path.name)
def test_bundled_child_is_a_complete_composed_package(skill_mod, child):
    errors, _ = skill_mod.validate_skill(child)
    assert errors == [], '\n'.join(errors)


@pytest.mark.parametrize('child', BUNDLES, ids=lambda path: path.name)
def test_bundled_child_routes_to_nesting_parent(child):
    text = (child / 'SKILL.md').read_text(encoding='utf-8')
    assert '../../references/child-usage.md' in text
    assert (child / '../../references/child-usage.md').resolve().is_file()


@pytest.mark.skipif(not BUNDLES, reason='No bundled children in libraries/ (standalone install)')
def test_bundled_children_are_present_without_record_paths():
    assert {child.name for child in BUNDLES} >= {
        'roblox-vide', 'roblox-charm', 'roblox-ui-labs', 'roblox-bootstrapper',
        'roblox-janitor', 'roblox-lemonsignal', 'roblox-blink', 'roblox-nevermore-ui'}
    for child in BUNDLES:
        reconciliation = yaml.safe_load((child / 'resource.yaml').read_text(encoding='utf-8'))['reconciliation']
        assert set(reconciliation) == {'policy', 'reason'}, child.name
