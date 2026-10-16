"""Exact npm declarations, material companions and reviewed archives in package-lock.json."""
from copy import deepcopy
import base64
import hashlib
import json

import pytest
import yaml
import fixtures
import _resource_contract as contract
import _pins as pins


def dump(path, value):
    path.write_text(json.dumps(value), encoding='utf-8')


@pytest.fixture
def npm_case(tmp_path):
    child = tmp_path / 'roblox-widget-resource'
    child.mkdir()
    (child / 'SKILL.md').write_text(fixtures.valid_skill_text(), encoding='utf-8')
    descriptor = fixtures.write_contract(child)
    project = tmp_path / 'project'
    project.mkdir()
    specifications = [
        {'package_id': name, 'version': version, 'dependency_section': 'dependencies',
            'archive_url': f'https://registry.npmjs.org/{name}/-/{name.split("/")[-1]}-{version}.tgz',
            'archive_integrity': 'sha512-' + base64.b64encode(hashlib.sha512(name.encode()).digest()).decode()}
        for name, version in (('@example/widget', '1.2.3'), ('@example/lifetime', '2.3.4'))]
    primary, companion = specifications
    descriptor['resource']['package_id'] = primary['package_id']
    descriptor['installation'] = {'profile': 'npm', 'registry': 'https://registry.npmjs.org',
        **{key: value for key, value in primary.items() if key not in {'package_id', 'version'}},
        'companions': [companion]}
    (child / 'resource.yaml').write_text(yaml.safe_dump(descriptor, sort_keys=False), encoding='utf-8')
    manifest = {'name': 'fixture', 'version': '0.0.0',
        'dependencies': {item['package_id']: item['version'] for item in specifications}}
    lock = {'name': 'fixture', 'version': '0.0.0', 'lockfileVersion': 3,
        'packages': {'': deepcopy(manifest), **{
            'node_modules/' + item['package_id']: {'version': item['version'],
                'resolved': item['archive_url'], 'integrity': item['archive_integrity']}
            for item in specifications}}}
    dump(project / 'package.json', manifest)
    dump(project / 'package-lock.json', lock)
    return child, project, descriptor, manifest, lock


def test_exact_npm_declaration_passes_without_running_anything(npm_case, monkeypatch):
    child, project, _, _, _ = npm_case
    monkeypatch.setattr('subprocess.run', lambda *a, **k: pytest.fail('the pin check must never execute a subprocess'))
    assert contract.load_contract(child)['installation']['profile'] == 'npm'
    assert pins.check(child, project) == {'status': 'PASS', 'reason': 'package.json and package-lock.json match the pin'}


@pytest.mark.parametrize('lane,field,value', [
    ('manifest', '@example/widget', '^1.2.3'),
    ('manifest', '@example/lifetime', '2.3.5'),
    ('lock', 'version', '1.2.4'),
    ('lock', 'resolved', 'https://example.com/unreviewed.tgz'),
    ('lock', 'integrity', 'sha512-unreviewed'),
    ('lock', 'link', True),
    ('lock', 'name', '@example/fork'),
])
def test_npm_ranges_forks_changed_archives_and_links_fail(npm_case, lane, field, value):
    child, project, _, manifest, lock = npm_case
    if lane == 'manifest':
        manifest['dependencies'][field] = value
        dump(project / 'package.json', manifest)
    else:
        lock['packages']['node_modules/@example/widget'][field] = value
        dump(project / 'package-lock.json', lock)
    assert pins.check(child, project)['status'] == 'FAIL'


@pytest.mark.parametrize('change,status', [
    ('root-declaration', 'FAIL'), ('missing-companion', 'FAIL'), ('project-identity', 'FAIL'),
    ('packages', 'FAIL'), ('format', 'UNAVAILABLE'),
])
def test_npm_lock_root_companions_and_identity_are_material(npm_case, change, status):
    child, project, _, _, lock = npm_case
    if change == 'root-declaration':
        lock['packages']['']['dependencies']['@example/widget'] = '^1.2.3'
    elif change == 'missing-companion':
        lock['packages'].pop('node_modules/@example/lifetime')
    elif change == 'project-identity':
        lock['name'] = 'another-project'
    elif change == 'format':
        lock['lockfileVersion'] = 1
    else:
        lock['packages'] = []
    dump(project / 'package-lock.json', lock)
    assert pins.check(child, project)['status'] == status


def test_exact_npm_alias_passes(npm_case):
    child, project, _, manifest, lock = npm_case
    version = manifest['dependencies'].pop('@example/widget')
    manifest['dependencies']['ReactiveWidget'] = 'npm:@example/widget@' + version
    lock['packages']['']['dependencies'] = deepcopy(manifest['dependencies'])
    entry = lock['packages'].pop('node_modules/@example/widget')
    entry['name'] = '@example/widget'
    lock['packages']['node_modules/ReactiveWidget'] = entry
    dump(project / 'package.json', manifest)
    dump(project / 'package-lock.json', lock)
    assert pins.check(child, project)['status'] == 'PASS'


def test_multiple_npm_bindings_are_compared_by_hand(npm_case):
    child, project, _, manifest, lock = npm_case
    manifest['dependencies']['SecondBinding'] = 'npm:@example/widget@1.2.3'
    lock['packages']['']['dependencies'] = deepcopy(manifest['dependencies'])
    lock['packages']['node_modules/SecondBinding'] = {**lock['packages']['node_modules/@example/widget'], 'name': '@example/widget'}
    dump(project / 'package.json', manifest)
    dump(project / 'package-lock.json', lock)
    result = pins.check(child, project)
    assert result['status'] == 'UNAVAILABLE' and 'more than once' in result['reason']


@pytest.mark.parametrize('field,value', [
    ('archive_url', 'https://example.com/widget.tgz'),
    ('archive_integrity', 'sha256-unreviewed'),
    ('archive_integrity', 'sha512-not-base64'),
    ('archive_integrity', 'sha512-YQ=='),
    ('dependency_section', 'optionalDependencies'),
])
def test_malformed_npm_specifications_fail_closed(npm_case, field, value):
    child, _, descriptor, _, _ = npm_case
    descriptor['installation'][field] = value
    (child / 'resource.yaml').write_text(yaml.safe_dump(descriptor), encoding='utf-8')
    with pytest.raises(ValueError):
        contract.load_contract(child)


def test_undeclared_or_unlocked_project_is_unavailable(npm_case):
    child, project, _, manifest, _ = npm_case
    (project / 'package-lock.json').unlink()
    result = pins.check(child, project)
    assert result['status'] == 'UNAVAILABLE' and 'package-lock.json' in result['reason']
    manifest['dependencies'].pop('@example/widget')
    dump(project / 'package.json', manifest)
    dump(project / 'package-lock.json', {'lockfileVersion': 3, 'packages': {'': deepcopy(manifest)}, 'name': 'fixture', 'version': '0.0.0'})
    result = pins.check(child, project)
    assert result['status'] == 'UNAVAILABLE' and "doesn't declare @example/widget" in result['reason']
