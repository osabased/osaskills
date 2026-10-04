"""Read-only exact Bootstrapper Git/pesde identity and installed integrity check."""
from pathlib import Path
import argparse
import hashlib
import sys
import tomllib

REPO = 'https://github.com/LDGerrits/Bootstrapper'
COMMIT = 'ff6700d32875dde5ef9e3625a159436ebd4dc3e9'
TREE = '4f94dfb887d0d0f81faaf00849d8670e5e8ed7de'
SOURCE = 'dd7f94d7a0a10de13b838e65549c9de3b540c568c7c44cf89f0b3ace2b1725fc'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--manifest', type=Path, required=True)
parser.add_argument('--lock', type=Path, required=True)
parser.add_argument('--declared', action='store_true')
parser.add_argument('--package-dir', type=Path)
args = parser.parse_args()
try:
    manifest = tomllib.loads(args.manifest.read_text(encoding='utf-8-sig'))
    lock = tomllib.loads(args.lock.read_text(encoding='utf-8-sig'))
    dep = manifest.get('dependencies', {}).get('Bootstrapper')
    if not isinstance(dep, dict) or dep.get('repo') != REPO or dep.get('rev') != COMMIT:
        raise ValueError('Bootstrapper declaration must match the selected canonical repository and commit')
    graph = lock.get('graph', {})
    if not isinstance(graph, dict):
        raise ValueError('Malformed Bootstrapper dependency graph')
    matches = [(key, entry) for key, entry in graph.items() if isinstance(entry, dict)
               and isinstance(entry.get('direct'), list) and len(entry['direct']) > 0 and entry['direct'][0] == 'Bootstrapper']
    if len(matches) != 1:
        raise ValueError('Expected exactly one direct Bootstrapper lock entry')
    key, entry = matches[0]
    if key != f'wally#ldgerrits/bootstrapper@0.0.0-{TREE} roblox':
        raise ValueError('Bootstrapper lock package/tree or target differs')
    direct = entry['direct']
    if len(direct) != 3 or not isinstance(direct[1], dict) or direct[1] != dep or direct[2] != 'standard':
        raise ValueError('Bootstrapper direct lock declaration differs')
    ref = entry.get('pkg_ref', {})
    if not isinstance(ref, dict):
        raise ValueError('Malformed Bootstrapper package reference')
    if ref.get('ref_ty') != 'git' or ref.get('repo') != REPO or ref.get('tree_id') != TREE or ref.get('new_structure') is not False:
        raise ValueError('Bootstrapper Git lock identity or Wally package layout differs')
    if args.declared:
        print(f'PASS: canonical Bootstrapper {COMMIT}; declared commit/tree')
    else:
        if args.package_dir is None:
            raise ValueError('Integrity mode requires --package-dir')
        path = args.package_dir / 'src/init.luau'
        if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE:
            raise ValueError('Installed Bootstrapper runtime source digest differs')
        if '--v1.2.2' not in path.read_text(encoding='utf-8'):
            raise ValueError('Installed Bootstrapper version header differs')
        package = tomllib.loads((args.package_dir / 'wally.toml').read_text(encoding='utf-8'))['package']
        if package.get('name') != 'ldgerrits/bootstrapper' or package.get('version') != '1.2.2':
            raise ValueError('Installed Bootstrapper manifest identity/version differs')
        print(f'PASS: canonical Bootstrapper {COMMIT}; installed 1.2.2 source {SOURCE}')
except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
    print(f'FAIL: {error}', file=sys.stderr)
    sys.exit(1)
