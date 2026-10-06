"""Validate distribution artifacts as composed children, without host claims."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CHILDREN = ROOT.parent / 'roblox-resources'
BUNDLES = sorted(path.parent for path in CHILDREN.glob('*/SKILL.md'))


def test_parent_installation_payload_contains_no_nested_skills():
    assert sorted(ROOT.rglob('SKILL.md')) == [ROOT / 'SKILL.md']


@pytest.mark.parametrize('child', BUNDLES, ids=lambda path: path.name)
def test_bundled_child_is_a_complete_composed_package(skill_mod, child):
    errors, _ = skill_mod.validate_skill(child)
    assert errors == [], '\n'.join(errors)


@pytest.mark.skipif(not CHILDREN.is_dir(), reason='Resource catalog is outside the installed parent package')
def test_bundled_catalog_can_be_distributed_together(catalog_mod):
    errors, _, _, fingerprint = catalog_mod.validate_catalog(BUNDLES, host='portable')
    assert errors == [], '\n'.join(errors)
    assert fingerprint.startswith('sha256:')
