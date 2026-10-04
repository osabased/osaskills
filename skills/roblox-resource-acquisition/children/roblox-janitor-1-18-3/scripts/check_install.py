#!/usr/bin/env python3
"""Read-only exact pesde declaration/lock check, with deferred source integrity."""
from pathlib import Path
import argparse, hashlib, json, sys, tomllib
SPEC = {'slug': 'janitor', 'package': 'howmanysmall/janitor', 'alias': 'Janitor', 'version': '1.18.3', 'registry': 'https://github.com/UpliftGames/wally-index', 'graph': 'wally#howmanysmall/janitor@1.18.3 roblox', 'companions': {'howmanysmall/typed-promise': '4.0.6', 'evaera/promise': '4.0.0'}, 'files': {'roblox_packages/.pesde/howmanysmall_janitor@1.18.3/janitor/src/FastDefer.luau': '893e531e077d123adffc08173b7aa7423fa2ad9f74fac3a0b5d1f36c20ab7122', 'roblox_packages/.pesde/howmanysmall_janitor@1.18.3/janitor/src/init.luau': '0ce62b83af5bd461b6d3695d565e4a07488b7d0e4d343bb0c6022290131d187f', 'roblox_packages/.pesde/howmanysmall_janitor@1.18.3/janitor/src/Promise.luau': '130e4f6a172245409da0f950c8b724696a049fbfc188e727adae0d9ebf980036', 'roblox_packages/.pesde/howmanysmall_typed-promise@4.0.6/Promise.luau': 'f08c2d92489330d0cbd361a1b039bf16ba5c6315e8ab15572cd45f4467b1bebb', 'roblox_packages/.pesde/howmanysmall_typed-promise@4.0.6/typed-promise/src/init.luau': '007e01e9336958b4036a8e9d051b2d2ccf0a9fe97c2f967d5ab792eb8f2bf95b', 'roblox_packages/.pesde/evaera_promise@4.0.0/promise/lib/init.lua': '5d69cf99a9741048855decb1d8cb5d7668f362f40c769d1500ce8f9c20dd319f', 'roblox_packages/.pesde/howmanysmall_janitor@1.18.3/Promise.luau': '71e8bc945aea30523d9031c792fd85ecd525e39eb50dac463f9530ebaa6587da', 'roblox_packages/Janitor.luau': 'd60dadafd982569065e55d708b7a080d21dbbe7e78f3f6312d08c567395c945f'}}
def check(manifest, lock, declared):
    m=tomllib.loads(manifest.read_text(encoding='utf-8-sig')); l=tomllib.loads(lock.read_text(encoding='utf-8-sig'))
    if l.get('format') != 2: raise ValueError('Expected pesde lock format 2')
    if m.get('target',{}).get('environment')!='roblox' or l.get('target')!='roblox':raise ValueError('Expected Roblox manifest and lock target')
    if any(not isinstance(x.get(k),str) or not x[k].strip() for x in (m,l) for k in ('name','version')):raise ValueError('Missing manifest or lock header identity')
    if l.get('name')!=m.get('name') or l.get('version')!=m.get('version'):raise ValueError('Manifest and lock header identity differ')
    section='dev_dependencies' if SPEC['slug']=='blink' else 'dependencies'
    d=m.get(section,{}).get(SPEC['alias'],{})
    key='name' if SPEC['slug']=='blink' else 'wally'
    if d.get(key)!=SPEC['package'] or d.get('version')!='='+SPEC['version']: raise ValueError('Missing or mismatched direct package pin')
    if SPEC['slug']=='blink' and d.get('target')!='lune':raise ValueError('Blink must target lune')
    if SPEC['slug']!='blink' and d.get('target','roblox')!='roblox':raise ValueError('Library must target roblox')
    idx=d.get('index','default'); indices=m.get('indices' if SPEC['slug']=='blink' else 'wally_indices',{})
    if indices.get(idx)!=SPEC['registry']:raise ValueError('Mismatched manifest registry')
    g=l.get('graph',{}).get(SPEC['graph'],{})
    direct=g.get('direct',[])
    expected=dict(d);expected[key]=SPEC['package'] if key=='name' else 'wally#'+SPEC['package']; expected.setdefault('index','default')
    if len(direct)!=3 or direct[0]!=SPEC['alias'] or direct[1]!=expected or direct[2]!=('dev' if section=='dev_dependencies' else 'standard'):raise ValueError('Direct lock counterpart differs')
    ref=g.get('pkg_ref',{})
    if ref.get('ref_ty')!=('pesde' if SPEC['slug']=='blink' else 'wally') or ref.get('index_url')!=SPEC['registry']:raise ValueError('Locked source identity differs')
    for package,version in SPEC['companions'].items():
        c=l.get('graph',{}).get('wally#'+package+'@'+version+' roblox',{})
        if c.get('pkg_ref',{}).get('index_url')!='https://github.com/UpliftGames/wally-index':raise ValueError('Missing or mismatched companion '+package)
    if SPEC['slug']=='janitor':
        if g.get('dependencies',{}).get('Promise')!=['wally#howmanysmall/typed-promise@4.0.6 roblox','standard']:raise ValueError('Janitor Promise edge differs')
        if l['graph']['wally#howmanysmall/typed-promise@4.0.6 roblox'].get('dependencies',{}).get('Promise')!=['wally#evaera/promise@4.0.0 roblox','standard']:raise ValueError('Typed Promise edge differs')
    if not declared:
        for relative,digest in SPEC['files'].items():
            p=manifest.resolve().parent/relative
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('Installed source digest mismatch: '+relative)
    return {'status':'PASS','resource':SPEC['slug'],'version':SPEC['version'],'lane':'declaration-lock' if declared else 'installed-integrity'}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--manifest',type=Path,default=Path('pesde.toml'));a.add_argument('--lock',type=Path,default=Path('pesde.lock'));a.add_argument('--declared',action='store_true');args=a.parse_args()
    try: print(json.dumps(check(args.manifest,args.lock,args.declared)))
    except (OSError,ValueError,KeyError,TypeError) as error: print('FAIL: '+str(error),file=sys.stderr);sys.exit(1)
