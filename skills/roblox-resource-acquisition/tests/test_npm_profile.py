"""Exact npm declarations, material companions, relocation and source tampering."""
from copy import deepcopy
from pathlib import Path
import base64
import hashlib
import json
import shutil

import pytest
import yaml
import fixtures
import _resource_contract as contract
import check_resource_install as install


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
    specifications = []
    for name, version in (('@example/widget', '1.2.3'), ('@example/lifetime', '2.3.4')):
        root = project / 'node_modules' / name
        source = root / 'src/nested'
        source.mkdir(parents=True)
        (source / 'Widget.lua').write_text('return {}\n', encoding='utf-8')
        payload = ('nested/Widget.lua ' + hashlib.sha256((source / 'Widget.lua').read_bytes()).hexdigest()).encode()
        dump(root / 'package.json', {'name': name, 'version': version,
            'scripts': {'postinstall': 'this script must never execute'}})
        specifications.append({'package_id': name, 'version': version, 'dependency_section': 'dependencies',
            'archive_url': f'https://registry.npmjs.org/{name}/-/{name.split("/")[-1]}-{version}.tgz',
            'archive_integrity': 'sha512-' + base64.b64encode(hashlib.sha512(name.encode()).digest()).decode(),
            'integrity': {'aggregate': {'directory': 'src', 'suffix': '.lua', 'recursive': True,
                'sha256': hashlib.sha256(payload).hexdigest()},
                'manifest': {'path': 'package.json', 'name': name, 'version': version}}})
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


def test_exact_npm_declaration_and_recursive_installed_sources(npm_case, monkeypatch):
    child, project, _, _, _ = npm_case
    monkeypatch.setattr('subprocess.run', lambda *a, **k: pytest.fail('Package checking must never execute a subprocess'))
    assert contract.load_contract(child)['installation']['profile'] == 'npm'
    assert install.check(child, project, declared_only=True)['lane'] == 'declaration-lock'
    assert install.check(child, project)['lane'] == 'installed-integrity'
    (project / 'node_modules/@example/lifetime/src/nested/Widget.lua').write_text('return {changed = true}\n')
    with pytest.raises(ValueError, match='aggregate source digest'):
        install.check(child, project)


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
    with pytest.raises(ValueError):
        install.check(child, project, declared_only=True)


@pytest.mark.parametrize('change', ['root-declaration', 'missing-companion', 'project-identity', 'format', 'packages'])
def test_npm_lock_root_companions_and_identity_are_material(npm_case, change):
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
    with pytest.raises(ValueError):
        install.check(child, project, declared_only=True)


def test_exact_npm_aliases_and_relocated_sources(npm_case, tmp_path):
    child, project, _, manifest, lock = npm_case
    version = manifest['dependencies'].pop('@example/widget')
    manifest['dependencies']['ReactiveWidget'] = 'npm:@example/widget@' + version
    lock['packages']['']['dependencies'] = deepcopy(manifest['dependencies'])
    entry = lock['packages'].pop('node_modules/@example/widget')
    entry['name'] = '@example/widget'
    lock['packages']['node_modules/ReactiveWidget'] = entry
    source = project / 'node_modules/@example/widget'
    source.rename(project / 'node_modules/ReactiveWidget')
    dump(project / 'package.json', manifest)
    dump(project / 'package-lock.json', lock)
    assert install.check(child, project)['alias'] == 'ReactiveWidget'
    relocated = tmp_path / 'mapped widget'
    shutil.move(project / 'node_modules/ReactiveWidget', relocated)
    lifetime = tmp_path / 'mapped lifetime'
    shutil.move(project / 'node_modules/@example/lifetime', lifetime)
    with pytest.raises(ValueError, match='source directory is missing'):
        install.check(child, project)
    assert install.check(child, project, package_dir=relocated,
        companions={'@example/lifetime': lifetime})['status'] == 'PASS'
    with pytest.raises(ValueError, match='not part'):
        install.check(child, project, companions={'@example/unrelated': lifetime})


def test_multiple_exact_npm_aliases_require_explicit_binding(npm_case):
    child, project, _, manifest, lock = npm_case
    manifest['dependencies']['SecondBinding'] = 'npm:@example/widget@1.2.3'
    lock['packages']['']['dependencies'] = deepcopy(manifest['dependencies'])
    lock['packages']['node_modules/SecondBinding'] = {**lock['packages']['node_modules/@example/widget'], 'name': '@example/widget'}
    dump(project / 'package.json', manifest)
    dump(project / 'package-lock.json', lock)
    with pytest.raises(ValueError, match='one exact direct npm binding'):
        install.check(child, project, declared_only=True)
    assert install.check(child, project, declared_only=True, alias='SecondBinding')['alias'] == 'SecondBinding'


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


def test_added_nested_source_and_wrong_installed_package_fail(npm_case):
    child, project, _, _, _ = npm_case
    root = project / 'node_modules/@example/widget'
    extra = root / 'src/nested/Unexpected.lua'
    extra.write_text('return {}\n')
    with pytest.raises(ValueError, match='aggregate source digest'):
        install.check(child, project)
    extra.unlink()
    dump(root / 'package.json', {'name': '@example/fork', 'version': '1.2.3'})
    with pytest.raises(ValueError, match='manifest identity/version'):
        install.check(child, project)


def test_missing_project_and_escaping_alias_fail(npm_case, capsys):
    child, project, _, manifest, lock = npm_case
    assert install.main([str(child)]) == 2
    assert 'UNKNOWN' in capsys.readouterr().out
    manifest['dependencies'] = {'../../outside': 'npm:@example/widget@1.2.3', '@example/lifetime': '2.3.4'}
    lock['packages']['']['dependencies'] = deepcopy(manifest['dependencies'])
    dump(project / 'package.json', manifest)
    dump(project / 'package-lock.json', lock)
    with pytest.raises(ValueError, match='escapes'):
        install.check(child, project, declared_only=True)
