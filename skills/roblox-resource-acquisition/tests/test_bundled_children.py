"""Validate distribution artifacts as composed children, without host claims."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CHILDREN = ROOT / 'children'
BUNDLES = sorted(path.parent for path in CHILDREN.glob('*/SKILL.md'))


@pytest.mark.parametrize('child', BUNDLES, ids=lambda path: path.name)
def test_bundled_child_is_a_complete_composed_package(skill_mod, child):
    errors, _ = skill_mod.validate_skill(child)
    assert errors == [], '\n'.join(errors)


@pytest.mark.skipif(not CHILDREN.is_dir(), reason='Installed parent copies omit distribution children')
def test_bundled_catalog_can_be_distributed_together(catalog_mod):
    errors, _, _, fingerprint = catalog_mod.validate_catalog(BUNDLES, host='portable')
    assert errors == [], '\n'.join(errors)
    assert fingerprint.startswith('sha256:')
