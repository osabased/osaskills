"""Contract-2 package composition and the read-only pin comparison."""
from copy import deepcopy
import subprocess
import sys

import pytest
import yaml
import fixtures
import _resource_contract as contract
import _pins as pins


@pytest.fixture
def child(tmp_path):
    root = tmp_path / 'roblox-widget-resource'
    root.mkdir()
    (root / 'SKILL.md').write_text(fixtures.valid_skill_text(), encoding='utf-8')
    fixtures.write_contract(root)
    return root


def read(root):
    return yaml.safe_load((root / 'resource.yaml').read_text(encoding='utf-8'))


def write(root, data):
    (root / 'resource.yaml').write_text(yaml.safe_dump(data, sort_keys=False), encoding='utf-8')


def test_short_child_and_alternative_headings_work(skill_mod, child):
    assert len((child / 'SKILL.md').read_text().split()) < 300
    assert skill_mod.validate_skill(child) == ([], [])


def test_old_inline_provenance_has_no_fallback(skill_mod, child):
    (child / 'resource.yaml').unlink()
    text = (child / 'SKILL.md').read_text() + '\n## Provenance\n- Resource slug: widget-resource\n'
    (child / 'SKILL.md').write_text(text, encoding='utf-8')
    assert any('resource.yaml is required' in error for error in skill_mod.validate_skill(child)[0])


@pytest.mark.parametrize('field,value', [
    ('schema_version', 99), ('schema_version', True), ('scope', []),
    ('parent_contract', {'name': 'roblox-resource-acquisition', 'version': 99}),
    ('scope', 'global'),
])
def test_unsupported_or_malformed_contract_fails_closed(child, field, value):
    data = read(child)
    data[field] = value
    write(child, data)
    with pytest.raises(ValueError):
        contract.load_contract(child)


@pytest.mark.parametrize('field', ['schema_version', 'parent_contract'])
def test_contract_one_skill_is_told_to_reclone(child, field):
    data = read(child)
    data[field] = 1 if field == 'schema_version' else {'name': 'roblox-resource-acquisition', 'version': 1}
    write(child, data)
    with pytest.raises(ValueError, match='re-clone the skill'):
        contract.load_contract(child)


@pytest.mark.parametrize('section,field,value', [
    (None, 'reconciliation', {'policy': 'required', 'reason': 'Installed state can differ.'}),
    ('guidance', 'shared_usage', 'references/child-usage.md'),
    ('installation', 'integrity', {'files': {'init.luau': 'a' * 64}}),
])
def test_contract_one_fields_are_rejected(child, section, field, value):
    data = read(child)
    (data[section] if section else data)[field] = value
    write(child, data)
    with pytest.raises(ValueError, match='unknown fields|unsupported by custom'):
        contract.load_contract(child)


@pytest.mark.parametrize('url', [
    'http://example.com/widget', 'https://user:password@example.com/widget',
    'https://example.com/widget?access_token=secret', 'https://example.com/widget#latest',
    'https://example.com/a b',
])
def test_invalid_source_coordinates_rejected(child, url):
    data = read(child)
    data['resource']['canonical_url'] = url
    write(child, data)
    with pytest.raises(ValueError):
        contract.load_contract(child)


def test_live_verification_field_rejected(child):
    data = read(child)
    data['resource']['verification'] = 'verified'
    write(child, data)
    with pytest.raises(ValueError, match='unknown fields'):
        contract.load_contract(child)


@pytest.mark.parametrize('scope', ['project', 'user'])
def test_both_scopes_validate(skill_mod, child, scope):
    data = read(child)
    data['scope'] = scope
    write(child, data)
    assert contract.load_contract(child)['scope'] == scope
    assert skill_mod.validate_skill(child) == ([], [])


def test_check_the_pin_must_state_the_pinned_values(skill_mod, child):
    core = child / 'SKILL.md'
    text = core.read_text()
    core.write_text(text.replace('`=1.2.3`', '`=X`').replace('@1.2.3 roblox', '@X roblox'), encoding='utf-8')
    assert 'the Check the pin section must state the pinned value 1.2.3' in skill_mod.validate_skill(child)[0]
    core.write_text(text, encoding='utf-8')
    data = read(child)
    data['installation'] = {'profile': 'asset', 'asset_sha256': 'b' * 64}
    write(child, data)
    assert f'the Check the pin section must state the pinned value {"b" * 64}' in skill_mod.validate_skill(child)[0]


@pytest.mark.parametrize('placeholder', ['MANIFEST-ENTRY', 'LOCK-KEY'])
def test_unfilled_pin_entries_are_scaffold(skill_mod, child, placeholder):
    core = child / 'SKILL.md'
    core.write_text(core.read_text().replace('`com.example.widget` at', f'`{placeholder}` at'), encoding='utf-8')
    assert 'unfinished scaffold in SKILL.md' in skill_mod.validate_skill(child)[0]


def test_conditional_reference_is_reachable_and_anchor_checked(skill_mod, child):
    (child / 'references').mkdir()
    (child / 'references/setup.md').write_text('# Setup\n\n## Restore\n\nUse the pinned package.\n', encoding='utf-8')
    data = read(child)
    data['guidance']['documents'][0]['roles'].remove('setup')
    data['guidance']['documents'].append({'path': 'references/setup.md', 'roles': ['setup'], 'when': 'restoring installation'})
    write(child, data)
    assert any('unreachable' in error for error in skill_mod.validate_skill(child)[0])
    core = child / 'SKILL.md'
    core.write_text(core.read_text() + '\nFor restoration, read [setup](references/setup.md#restore).\n', encoding='utf-8')
    assert skill_mod.validate_skill(child)[0] == []
    reference = child / 'references/setup.md'
    reference.write_text(reference.read_text() + '\n[Entrypoint](../SKILL.md)\n', encoding='utf-8')
    assert skill_mod.validate_skill(child)[0] == []
    reference.write_text(reference.read_text() + '\n[Outside](../../outside.md)\n', encoding='utf-8')
    assert any('escapes package' in error for error in skill_mod.validate_skill(child)[0])
    reference.write_text('# Setup\n\n## Restore\n', encoding='utf-8')
    (child / 'references/setup.md').write_text('# Setup\n\n## Changed\n', encoding='utf-8')
    assert any('missing local guidance anchor' in error for error in skill_mod.validate_skill(child)[0])


def test_link_into_the_parent_skill_escapes_the_package(skill_mod, child):
    # A skill cloned into a project has no parent at any fixed relative path.
    core = child / 'SKILL.md'
    core.write_text(core.read_text() + '\n[library skills](../../references/library-skills.md)\n', encoding='utf-8')
    assert any('escapes package' in error for error in skill_mod.validate_skill(child)[0])


def test_missing_core_coverage_and_undeclared_markdown_fail(skill_mod, child):
    data = read(child)
    data['guidance']['documents'][0]['roles'].remove('ownership')
    write(child, data)
    assert any('entrypoint must cover' in error for error in skill_mod.validate_skill(child)[0])
    data['guidance']['documents'][0]['roles'].append('ownership')
    write(child, data)
    (child / 'extra.md').write_text('# Extra\n', encoding='utf-8')
    core = child / 'SKILL.md'
    core.write_text(core.read_text() + '\n[Extra](extra.md)\n', encoding='utf-8')
    assert any('must be declared' in error for error in skill_mod.validate_skill(child)[0])


@pytest.mark.parametrize('path', ['../outside.md', '/outside.md', 'C:/outside.md', 'references/../../outside.md', r'references\outside.md'])
def test_paths_cannot_escape_package(child, path):
    data = read(child)
    data['guidance']['documents'][0]['path'] = path
    write(child, data)
    with pytest.raises(ValueError):
        contract.load_contract(child)


def test_profile_rejects_ignored_fields_and_custom_is_never_executed(child, tmp_path):
    data = read(child)
    data['installation']['asset_sha256'] = 'a' * 64
    write(child, data)
    with pytest.raises(ValueError, match='unsupported by custom'):
        contract.load_contract(child)
    data['installation'].pop('asset_sha256')
    write(child, data)
    sentinel = tmp_path / 'unwanted'
    (child / 'scripts/check_widget.py').write_text(f'from pathlib import Path\nPath({str(sentinel)!r}).touch()\n', encoding='utf-8')
    result = pins.check(child, tmp_path)
    assert result['status'] == 'UNAVAILABLE' and 'its own script' in result['reason']
    assert not sentinel.exists()


def test_asset_pin_is_unavailable_and_points_to_hashing(child, tmp_path):
    data = read(child)
    data['installation'] = {'profile': 'asset', 'asset_sha256': 'a' * 64}
    write(child, data)
    result = pins.check(child, tmp_path)
    assert result['status'] == 'UNAVAILABLE' and 'hash it' in result['reason']


def test_missing_project_unreadable_skill_and_denied_read_are_unavailable(package_profile, tmp_path, monkeypatch):
    child = package_profile[0]
    assert pins.check(child, tmp_path / 'missing') == {'status': 'UNAVAILABLE', 'reason': 'the project directory does not exist'}
    empty = tmp_path / 'empty'
    empty.mkdir()
    assert pins.check(child, empty) == {'status': 'UNAVAILABLE', 'reason': 'the project has no pesde.toml or pesde.lock'}

    def denied(*args, **kwargs):
        raise PermissionError('pesde.lock cannot be read')
    monkeypatch.setattr(pins, 'compare', denied)
    assert pins.check(child, empty) == {'status': 'UNAVAILABLE', 'reason': 'pesde.lock cannot be read'}
    data = read(child)
    data['schema_version'] = 99
    write(child, data)
    result = pins.check(child, empty)
    assert result['status'] == 'UNAVAILABLE' and "resource.yaml can't be read" in result['reason']


@pytest.fixture
def package_profile(child, tmp_path):
    data = read(child)
    data['resource']['package_id'] = 'example/widget'
    data['installation'] = {'profile': 'pesde-wally', 'dependency_section': 'dependencies',
        'registry': 'https://github.com/UpliftGames/wally-index', 'target': 'roblox'}
    write(child, data)
    project = tmp_path / 'project'
    project.mkdir()
    dependency = {'wally': 'example/widget', 'version': '=1.2.3', 'index': 'default'}
    manifest = {'name': 'example/project', 'version': '0.1.0', 'target': {'environment': 'roblox'},
        'wally_indices': {'default': data['installation']['registry']}, 'dependencies': {'RenamedWidget': dependency}}
    key = 'wally#example/widget@1.2.3 roblox'
    lock = {'format': 2, 'name': 'example/project', 'version': '0.1.0', 'target': 'roblox',
        'graph': {key: {'direct': ['RenamedWidget', {**dependency, 'wally': 'wally#example/widget'}, 'standard'],
            'pkg_ref': {'ref_ty': 'wally', 'index_url': data['installation']['registry']}, 'dependencies': {}}}}
    return child, project, data, manifest, lock


def test_canonical_pin_accepts_a_different_alias(package_profile, monkeypatch):
    child, project, data, manifest, lock = package_profile
    pins.pesde_declared(data['resource'], data['installation'], manifest, lock)
    (project / 'pesde.toml').write_text('', encoding='utf-8')
    (project / 'pesde.lock').write_text('', encoding='utf-8')
    monkeypatch.setattr(pins, 'toml', lambda p: manifest if p.name == 'pesde.toml' else lock)
    assert pins.check(child, project) == {'status': 'PASS', 'reason': 'pesde.toml and pesde.lock match the pin'}
    lock['graph']['wally#example/widget@1.2.3 roblox']['pkg_ref']['index_url'] = 'https://example.com/impostor'
    result = pins.check(child, project)
    assert result['status'] == 'FAIL' and 'the skill targets wally#example/widget@1.2.3 roblox' in result['reason']


def test_unsupported_pesde_lock_format_says_why(package_profile):
    child, project, data, manifest, lock = package_profile
    lock['format'] = 3
    (project / 'pesde.toml').write_text('', encoding='utf-8')
    (project / 'pesde.lock').write_text('', encoding='utf-8')
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(pins, 'toml', lambda p: manifest if p.name == 'pesde.toml' else lock)
        assert pins.check(child, project) == {
            'status': 'UNAVAILABLE', 'reason': 'pesde.lock format 3 not supported (expects 2); check the pin by hand'}


def test_pin_lock_registry_and_ambiguous_binding_fail(package_profile):
    _, _, data, manifest, lock = package_profile
    resource, profile = data['resource'], data['installation']
    for variant in ('pin', 'lock', 'registry', 'fork'):
        altered_manifest, altered_lock = deepcopy(manifest), deepcopy(lock)
        if variant == 'pin':
            altered_manifest['dependencies']['RenamedWidget']['version'] = '^1.2.3'
        elif variant == 'lock':
            altered_lock['version'] = '0.2.0'
        elif variant == 'registry':
            altered_manifest['wally_indices']['default'] = 'https://example.com/impostor'
        else:
            altered_lock['graph'] = {'wally#other/widget@1.2.3 roblox': altered_lock['graph'].pop('wally#example/widget@1.2.3 roblox')}
        with pytest.raises(ValueError):
            pins.pesde_declared(resource, profile, altered_manifest, altered_lock)
    manifest['dependencies']['Second'] = deepcopy(manifest['dependencies']['RenamedWidget'])
    with pytest.raises(pins.Unavailable, match='more than once'):
        pins.pesde_declared(resource, profile, manifest, lock)


def test_material_companion_identity_and_edge_required(package_profile):
    _, _, data, manifest, lock = package_profile
    companion = {'package_id': 'example/companion', 'version': '2.0.0', 'registry': data['installation']['registry'],
        'parent_package': 'example/widget', 'edge_alias': 'Companion'}
    data['installation']['companions'] = [companion]
    with pytest.raises(ValueError, match='has no wally#example/companion@2.0.0 roblox'):
        pins.pesde_declared(data['resource'], data['installation'], manifest, lock)
    key = 'wally#example/companion@2.0.0 roblox'
    lock['graph'][key] = {'pkg_ref': {'ref_ty': 'wally', 'index_url': companion['registry']}}
    with pytest.raises(ValueError, match="doesn't link example/widget"):
        pins.pesde_declared(data['resource'], data['installation'], manifest, lock)
    lock['graph']['wally#example/widget@1.2.3 roblox']['dependencies']['Companion'] = [key, 'standard']
    pins.pesde_declared(data['resource'], data['installation'], manifest, lock)


def test_unfilled_template_fails_cli(scripts_dir, tmp_path):
    template = (scripts_dir.parent / 'templates' / 'resource-skill-template.md').read_text(encoding='utf-8')
    (tmp_path / 'SKILL.md').write_text(template, encoding='utf-8')
    proc = subprocess.run([sys.executable, str(scripts_dir / 'validate_skill.py'), str(tmp_path)],
        capture_output=True, text=True)
    assert proc.returncode == 1
    assert 'resource.yaml is required' in proc.stdout


def test_template_descriptor_is_contract_shaped_but_unfilled(scripts_dir, tmp_path):
    descriptor = yaml.safe_load((scripts_dir.parent / 'templates' / 'resource-skill-template.yaml').read_text(encoding='utf-8'))
    assert descriptor['schema_version'] == contract.SCHEMA_VERSION
    assert descriptor['parent_contract']['version'] == contract.PARENT_CONTRACT_VERSION
    write(tmp_path, descriptor)
    with pytest.raises(ValueError):
        contract.load_contract(tmp_path, check_documents=False)
