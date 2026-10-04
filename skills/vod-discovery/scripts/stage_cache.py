"""Checksum-verified local processing stages; failed work never becomes a cache hit."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import uuid


def file_hash(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def json_bytes(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'),
                      allow_nan=False).encode('utf-8')


@contextmanager
def file_lock(path):
    """The operating system releases this lock even after a terminated process."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as stream:
        stream.seek(0, os.SEEK_END)
        if not stream.tell():
            stream.write(b'0'); stream.flush()
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise RuntimeError(f'Processing is already active for {path.name}; retry after it finishes') from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def safe_artifact(folder, name):
    """Never resolve a manifest path through a link or outside its snapshot."""
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        raise ValueError('Unsafe cache artifact path')
    relative = Path(name)
    if relative.is_absolute() or PureWindowsPath(name).is_absolute() or any(p in ('', '.', '..') for p in name.split('/')):
        raise ValueError('Unsafe cache artifact path')
    root = Path(folder).resolve(strict=True)
    path = root
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError('Cache artifact links are not supported')
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError('Missing or unsafe cache artifact')
    return resolved


class StageCache:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _manifest(self, entry, stage, inputs):
        if entry.is_symlink() or (entry / 'manifest.json').is_symlink() or (entry / 'data').is_symlink():
            raise ValueError('Cache snapshot links are not supported')
        manifest = json.loads((entry / 'manifest.json').read_text(encoding='utf-8'))
        if (manifest.get('schema') != 'vod-stage-cache/v1' or manifest.get('stage') != stage
                or manifest.get('inputs') != inputs or not isinstance(manifest.get('result'), dict)
                or not isinstance(manifest.get('artifacts'), dict) or not manifest['artifacts']):
            raise ValueError('Invalid cache manifest')
        for name, record in manifest['artifacts'].items():
            path = safe_artifact(entry / 'data', name)
            if (not isinstance(record, dict) or path.stat().st_size != record.get('size')
                    or file_hash(path) != record.get('sha256')):
                raise ValueError('Cache artifact changed')
        return manifest

    def get(self, stage, inputs, produce, guard=lambda: None):
        """Return a verified stage and metadata; preserve incomplete/corrupt snapshots."""
        if not isinstance(stage, str) or not stage.replace('-', '').isalnum():
            raise ValueError('Invalid cache stage name')
        key = hashlib.sha256(json_bytes({'stage': stage, 'inputs': inputs})).hexdigest()
        parent = self.root / stage
        locks = self.root / '.locks'
        if parent.is_symlink() or locks.is_symlink():
            raise ValueError('Cache directory links are not supported')
        parent.mkdir(exist_ok=True)
        locks.mkdir(exist_ok=True)
        entry = parent / key
        lock_path = locks / (stage + '-' + key + '.lock')
        if lock_path.is_symlink():
            raise ValueError('Cache lock links are not supported')
        with file_lock(lock_path):
            guard()
            if entry.exists() or entry.is_symlink():
                try:
                    manifest = self._manifest(entry, stage, inputs)
                except (OSError, ValueError, KeyError, TypeError):
                    # Renaming, never following or deleting, preserves diagnostic evidence.
                    entry.replace(parent / ('corrupt-' + key + '-' + uuid.uuid4().hex[:12]))
                else:
                    return entry / 'data', manifest['result'], True
            pending = parent / ('incomplete-' + key + '-' + uuid.uuid4().hex[:12])
            data = pending / 'data'
            data.mkdir(parents=True)
            try:
                result = produce(data)
                if not isinstance(result, dict):
                    raise ValueError('Cache producer must return metadata')
                artifacts = {}
                for path in sorted(data.rglob('*')):
                    if path.is_symlink():
                        raise ValueError('Cache producers must not write links')
                    if path.is_file():
                        name = path.relative_to(data).as_posix()
                        safe = safe_artifact(data, name)
                        artifacts[name] = {'size': safe.stat().st_size, 'sha256': file_hash(safe)}
                if not artifacts:
                    raise ValueError('Cache stage produced no artifacts')
                manifest = {'schema': 'vod-stage-cache/v1', 'stage': stage, 'inputs': inputs,
                            'artifacts': artifacts, 'result': result}
                (pending / 'manifest.json').write_bytes(json_bytes(manifest))
                self._manifest(pending, stage, inputs)
                guard()
                pending.replace(entry)
            except BaseException as exc:
                (pending / 'error.json').write_text(json.dumps({'error': str(exc), 'type': type(exc).__name__}), encoding='utf-8')
                raise
            return entry / 'data', result, False

    @staticmethod
    def materialize(data, target):
        """Copy rather than link so edits to an attempt cannot alter cached evidence."""
        data, target = Path(data), Path(target)
        target = target.resolve(strict=True)
        manifest = json.loads((data.parent / 'manifest.json').read_text(encoding='utf-8'))
        for name, record in manifest['artifacts'].items():
            source = safe_artifact(data, name)
            if source.stat().st_size != record['size'] or file_hash(source) != record['sha256']:
                raise ValueError('Cache artifact changed before materialization')
            dest = target / Path(name)
            ancestor = dest.parent
            while ancestor != target:
                if ancestor.is_symlink():
                    raise ValueError('Attempt artifact directory links are not supported')
                ancestor = ancestor.parent
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                raise ValueError(f'Attempt artifact already exists: {name}')
            shutil.copyfile(source, dest)
            if file_hash(dest) != record['sha256']:
                raise ValueError('Cache artifact changed during materialization')
