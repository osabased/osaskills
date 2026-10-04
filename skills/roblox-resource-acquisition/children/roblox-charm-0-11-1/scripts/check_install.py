#!/usr/bin/env python3
"""Read-only exact pesde declaration/lock check, with deferred source integrity."""
from pathlib import Path
import argparse, hashlib, json, sys, tomllib
SPEC = {'slug': 'charm', 'package': 'littensy/charm', 'alias': 'Charm', 'version': '0.11.1', 'registry': 'https://github.com/UpliftGames/wally-index', 'graph': 'wally#littensy/charm@0.11.1 roblox', 'companions': {}, 'files': {'roblox_packages/.pesde/littensy_charm@0.11.1/charm/src/init.luau': 'ad8d276b54ee32787f9e3a6e165c80ee44aea808294a45a5070bcabddf0bef39', 'roblox_packages/.pesde/littensy_charm@0.11.1/charm/src/system.luau': 'f15e7d4b41729135d5fd12ccd93fe581ebd136598f36dcc908e8ffbe2c174d94', 'roblox_packages/Charm.luau': 'ff872fdc96067d0044cc6a16631ec9a8fa63b9a60d6749799d021f0103eab8f6'}}
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
    except (OSError,ValueError,KeyError,TypeError,AttributeError) as error: print('FAIL: '+str(error),file=sys.stderr);sys.exit(1)
