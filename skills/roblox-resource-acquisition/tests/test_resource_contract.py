"""Contract-1 package composition and read-only resource profile behavior."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
import yaml
import fixtures
import _resource_contract as contract
import check_resource_install as install
import guard_skill_update as guard


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
    assert skill_mod.validate_skill(child)[0] == []


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


def test_live_verification_field_rejected_and_record_state_can_change(child, bundle_mod):
    data = read(child)
    data['resource']['verification'] = 'verified'
    write(child, data)
    with pytest.raises(ValueError, match='unknown fields'):
        contract.load_contract(child)
    data['resource'].pop('verification')
    write(child, data)
    record = fixtures.matching_widget_record()
    record['verification'].update(status='unavailable', validated_at='2026-08-16')
    record['resource_proof']['unavailable_claims'] = ['Studio is unavailable.']
    assert bundle_mod.validate_bundle(Path('record.yaml'), record, child)[0] == []


def test_project_scope_cannot_use_user_fallback(child):
    data = read(child)
    data['reconciliation']['no_project_record'] = '~/.roblox-resources/records/widget-resource.yaml'
    data['reconciliation']['no_project_learnings'] = '~/.roblox-resources/learnings/'
    write(child, data)
    with pytest.raises(ValueError, match='cannot fall back'):
        contract.load_contract(child)
    data['scope'] = 'user'
    write(child, data)
    assert contract.load_contract(child)['scope'] == 'user'


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
    assert install.check(child, tmp_path)['status'] == 'UNAVAILABLE'
    assert not sentinel.exists()


def test_unknown_project_is_exit_two_and_guard_stops_use(child, tmp_path, capsys):
    assert install.main([str(child)]) == 2
    assert 'UNKNOWN' in capsys.readouterr().out
    marker = guard.marker_path(child)
    marker.parent.mkdir()
    marker.write_text('{}', encoding='utf-8')
    with pytest.raises(ValueError, match='promotion'):
        install.check(child, tmp_path)


def test_denied_read_is_unavailable_without_claiming_resource_failure(child, tmp_path, monkeypatch, capsys):
    def denied(*args, **kwargs):
        raise PermissionError('source file cannot be read')
    monkeypatch.setattr(install, 'check', denied)
    assert install.main([str(child), '--project', str(tmp_path)]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result['status'] == 'UNAVAILABLE'
    assert 'read denied' in result['reason']


@pytest.fixture
def package_profile(child, tmp_path):
    source = tmp_path / 'arbitrary-mapped-source'
    source.mkdir()
    (source / 'init.luau').write_text('return {}\n', encoding='utf-8')
    data = read(child)
    data['resource']['package_id'] = 'example/widget'
    data['installation'] = {'profile': 'pesde-wally', 'dependency_section': 'dependencies',
        'registry': 'https://github.com/UpliftGames/wally-index', 'target': 'roblox',
        'integrity': {'files': {'init.luau': hashlib.sha256((source / 'init.luau').read_bytes()).hexdigest()}}}
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
    return child, source, project, data, manifest, lock


def test_canonical_pin_accepts_different_alias_and_explicit_source_root(package_profile, monkeypatch):
    child, source, project, data, manifest, lock = package_profile
    assert install.declared(data['resource'], data['installation'], manifest, lock, None) == 'RenamedWidget'
    monkeypatch.setattr(install, 'toml', lambda p: manifest if p.name == 'pesde.toml' else lock)
    result = install.check(child, project, package_dir=source)
    assert result['lane'] == 'installed-integrity'
    assert result['package_dir'] == str(source)
    (source / 'init.luau').write_text('return "changed"\n', encoding='utf-8')
    with pytest.raises(ValueError, match='digest differs'):
        install.check(child, project, package_dir=source)


def test_pin_lock_registry_and_ambiguous_binding_fail(package_profile):
    _, _, _, data, manifest, lock = package_profile
    resource, profile = data['resource'], data['installation']
    for variant in ('pin', 'lock', 'registry'):
        altered_manifest, altered_lock = deepcopy(manifest), deepcopy(lock)
        if variant == 'pin':
            altered_manifest['dependencies']['RenamedWidget']['version'] = '^1.2.3'
        elif variant == 'lock':
            altered_lock['version'] = '0.2.0'
        else:
            altered_manifest['wally_indices']['default'] = 'https://example.com/impostor'
        with pytest.raises(ValueError):
            install.declared(resource, profile, altered_manifest, altered_lock, None)
    manifest['dependencies']['Second'] = deepcopy(manifest['dependencies']['RenamedWidget'])
    with pytest.raises(ValueError, match='supply --alias'):
        install.declared(resource, profile, manifest, lock, None)
    assert install.declared(resource, profile, manifest, lock, 'RenamedWidget') == 'RenamedWidget'


def test_material_companion_identity_and_edge_required(package_profile):
    _, _, _, data, manifest, lock = package_profile
    companion = {'package_id': 'example/companion', 'version': '2.0.0', 'registry': data['installation']['registry'],
        'parent_package': 'example/widget', 'edge_alias': 'Companion', 'integrity': {'files': {'init.luau': 'a' * 64}}}
    data['installation']['companions'] = [companion]
    with pytest.raises(ValueError, match='companion'):
        install.declared(data['resource'], data['installation'], manifest, lock, None)
    key = 'wally#example/companion@2.0.0 roblox'
    lock['graph'][key] = {'pkg_ref': {'ref_ty': 'wally', 'index_url': companion['registry']}}
    with pytest.raises(ValueError, match='edge differs'):
        install.declared(data['resource'], data['installation'], manifest, lock, None)
    lock['graph']['wally#example/widget@1.2.3 roblox']['dependencies']['Companion'] = [key, 'standard']
    assert install.declared(data['resource'], data['installation'], manifest, lock, None) == 'RenamedWidget'


def test_asset_filename_is_project_binding_and_hash_is_identity(child, tmp_path):
    asset = tmp_path / 'DifferentPluginName.rbxm'
    asset.write_bytes(b'exact reviewed asset')
    data = read(child)
    data['installation'] = {'profile': 'asset', 'asset_sha256': hashlib.sha256(asset.read_bytes()).hexdigest()}
    write(child, data)
    assert install.check(child, tmp_path, asset=asset)['lane'] == 'asset-integrity'
    asset.write_bytes(b'unreviewed replacement')
    with pytest.raises(ValueError, match='mismatched'):
        install.check(child, tmp_path, asset=asset)


def test_parent_contract_input_detects_changed_shared_guidance(record_mod, child, monkeypatch, tmp_path):
    parent = tmp_path / 'parent'
    (parent / 'scripts').mkdir(parents=True)
    (parent / 'references').mkdir()
    usage = parent / 'references/child-usage.md'
    usage.write_text('Shared contract version 1\n', encoding='utf-8')
    monkeypatch.setattr(record_mod, '__file__', str(parent / 'scripts/validate_resource_record.py'))
    record = fixtures.matching_widget_record()
    record['skill_validation'].update(independent_behavioral_executed=True, independent_behavioral_passed=True,
        environment='synthetic evidence test', result='Shared interface task passed.', claim_scope='advice-only',
        checks=[{'check_id': 'shared-contract', 'kind': 'instruction-response', 'execution_mode': 'independent-agent',
            'status': 'passed', 'tested_at': '2026-08-16', 'target_version_or_commit': '1.2.3',
            'inputs': [{'role': 'parent-contract', 'path': 'references/child-usage.md', 'section': '',
                'sha256': 'sha256:' + hashlib.sha256(usage.read_bytes()).hexdigest()}], 'result': 'Shared contract respected.'}])
    assert record_mod.validate_record(Path('record.yaml'), record, current_skill_root=child, require_current_evidence=True)[0] == []
    usage.write_text('Changed shared contract\n', encoding='utf-8')
    errors, _ = record_mod.validate_record(Path('record.yaml'), record, current_skill_root=child, require_current_evidence=True)
    assert any('input hash is stale' in error for error in errors)
