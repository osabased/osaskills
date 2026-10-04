"""Local meaning-based transcript retrieval; ranked leads, never verified events."""
import argparse
import hashlib
import importlib.metadata
import json
import math
import sys
from copy import deepcopy
from pathlib import Path
import urllib.request
import uuid

from evidence import input_signature
from vod import number, read, text, write

MODEL = 'BAAI/bge-small-en-v1.5'
REPO = 'Qdrant/bge-small-en-v1.5-onnx-Q'
REVISION = 'aa8f8b060edb00e03bfdd08813a2949946c8ba55'
FILES = ('model_optimized.onnx', 'config.json', 'tokenizer.json', 'tokenizer_config.json',
         'special_tokens_map.json', 'ort_config.json', 'vocab.txt')
ONNX_SHA = '51f1bd0addd6e859e42c2c8021a5e5461385bb676a649f4b269aa445449f2431'
POLICY = {'version': 2, 'token_budget': 384, 'context_seconds': 30, 'gap_seconds': 10, 'single_segments': True}
CACHE_RECIPE = {'schema': 'vod-passage-embedding/v1', 'adapter': 'fastembed/0.8.1',
                'dimension': 384, 'dtype': 'float32', 'normalization': 'l2/v1',
                'passage_method': 'passage_embed', 'query_method': 'query_embed',
                'providers': ['CPUExecutionProvider']}
LIMITS = 'English transcript retrieval only. Similarity is not confidence, event importance, or proof of simultaneity. '
LIMITS += 'Even an unrelated query can return nearest results. Inspect raw speech and images. Missing results do not establish absence.'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def model_identity(folder):
    folder = Path(folder).resolve(strict=True)
    info = read(folder / 'vod-model.json')
    if info.get('model') != MODEL or info.get('revision') != REVISION:
        raise ValueError('Unexpected semantic model; use the pinned download-model command')
    hashes = {name: digest(folder / name) for name in FILES}
    if hashes != info['sha256'] or hashes['model_optimized.onnx'] != ONNX_SHA:
        raise ValueError('Semantic model files changed; restore the pinned model')
    return info


def download_model(out):
    out = Path(out).resolve()
    if (out / 'vod-model.json').exists():
        return dict(model_identity(out), reused=True)
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a fresh model folder after an incomplete download')
    out.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        with urllib.request.urlopen(f'https://huggingface.co/{REPO}/resolve/{REVISION}/{name}?download=true', timeout=120) as response:
            with (out / name).open('wb') as target:
                while block := response.read(1024 * 1024):
                    target.write(block)
    info = {'model': MODEL, 'repo': REPO, 'revision': REVISION, 'sha256': {n: digest(out / n) for n in FILES}}
    if info['sha256']['model_optimized.onnx'] != ONNX_SHA:
        raise ValueError('Downloaded model checksum mismatch')
    write(out / 'vod-model.json', info)
    return dict(info, reused=False)


def snapshot(folder):
    folder = Path(folder).resolve(strict=True)
    index = read(folder / 'index.json')
    if index.get('schema') != 'vod-search/v1':
        raise ValueError('Build the literal transcript index with vod.py index first')
    for prepared, signature in index['inputs'].items():
        if input_signature(prepared) != signature:
            raise ValueError('Transcript index is stale; rebuild literal and semantic indexes')
    aggregates = []
    hashes = {'index.json': digest(folder / 'index.json')}
    for source in index['sources']:
        path = (folder / index['build'] / source['aggregate'] / 'transcript.json').resolve(strict=True)
        if not path.is_relative_to(folder):
            raise ValueError('Aggregate must belong to the transcript index')
        hashes[str(path.relative_to(folder))] = digest(path)
        aggregates.append((source, read(path)['segments']))
    return index, hashes, aggregates


def split_text(value, count, budget=384, base=0):
    """Split on character boundaries, preserving exact text and original time range."""
    if count(value) <= budget:
        return [(value, base, base + len(value))]
    if len(value) < 2:
        raise ValueError('Cannot fit transcript text within model token budget')
    middle = len(value) // 2
    space = value.rfind(' ', 0, middle + 1)
    cut = space + 1 if space > 0 else middle
    return split_text(value[:cut], count, budget, base) + split_text(value[cut:], count, budget, base + cut)


def passages(aggregates, count):
    documents = []
    for source, rows in aggregates:
        streams = {}
        for row in rows:
            for occurrence in row['occurrences']:
                stream = occurrence['audio_stream']
                key = (occurrence['start_sec'], occurrence['end_sec'], row['text'])
                group = streams.setdefault(stream, {})
                unit = group.setdefault(key, {'start_sec': key[0], 'end_sec': key[1], 'text': key[2], 'occurrences': []})
                unit['occurrences'].append(occurrence)
        for stream, entries in sorted(streams.items()):
            units = []
            for unit in sorted(entries.values(), key=lambda u: (u['start_sec'], u['text'])):
                for value, a, b in split_text(unit['text'], count):
                    units.append({**unit, 'text': value, 'text_char_start': a, 'text_char_end': b})
            for position, first in enumerate(units):
                base = {'source_id': source['source_id'], 'source': source['source'], 'audio_stream': stream,
                        'start_sec': first['start_sec']}
                documents.append({**base, 'end_sec': first['end_sec'], 'text': first['text'],
                                  'segments': [first], 'passage_kind': 'segment'})
                chosen, value, end = [first], first['text'], first['end_sec']
                for following in units[position + 1:]:
                    combined = value + '\n' + following['text']
                    if following['end_sec'] - first['start_sec'] > 30 or following['start_sec'] - end > 10 or count(combined) > 384:
                        break
                    chosen.append(following); value = combined; end = max(end, following['end_sec'])
                if len(chosen) > 1:
                    documents.append({**base, 'end_sec': end, 'text': value, 'segments': chosen, 'passage_kind': 'context'})
    return documents


def load_model(folder):
    if importlib.metadata.version('fastembed') != '0.8.1':
        raise RuntimeError('Semantic adapter requires fastembed 0.8.1')
    from fastembed import TextEmbedding
    from tokenizers import Tokenizer
    folder = Path(folder).resolve(strict=True)
    model = TextEmbedding(model_name=MODEL, specific_model_path=str(folder), local_files_only=True,
                          cache_dir=str(folder / 'cache'), providers=['CPUExecutionProvider'], threads=4)
    tokenizer = Tokenizer.from_file(str(folder / 'tokenizer.json'))
    tokenizer.no_truncation(); tokenizer.no_padding()
    return model, lambda value: len(tokenizer.encode(value, add_special_tokens=False).ids)


def embedding_scope(identity):
    value = {'recipe': CACHE_RECIPE, 'model': identity, 'policy': POLICY}
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False, separators=(',', ':')).encode('utf-8')).hexdigest()


def vector_digest(vector):
    return hashlib.sha256(vector.astype('<f4', copy=False).tobytes()).hexdigest()


def cached_vector(path, scope, key):
    import numpy as np
    try:
        entry = read(path)
        if (entry.get('schema') != CACHE_RECIPE['schema'] or entry.get('scope') != scope
                or entry.get('text_sha256') != key):
            return None
        values = entry['vector']
        if not isinstance(values, list) or any(type(v) not in (int, float) for v in values):
            return None
        vector = np.asarray(values, dtype=np.float32)
        if (vector.shape != (384,) or not np.isfinite(vector).all()
                or not np.isclose(np.linalg.norm(vector), 1., rtol=1e-5, atol=1e-6)
                or vector_digest(vector) != entry['vector_sha256']):
            return None
        return vector
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        return None


def save_cached_vector(path, scope, key, vector):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temp.write_text(json.dumps({'schema': CACHE_RECIPE['schema'], 'scope': scope,
              'text_sha256': key, 'vector_sha256': vector_digest(vector), 'vector': vector.tolist()},
              ensure_ascii=False, allow_nan=False), encoding='utf-8')
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def passage_embeddings(model, docs, cache_folder, identity):
    """Cache exact passage text independently of its source clocks and references."""
    import numpy as np
    scope = embedding_scope(identity)
    folder = Path(cache_folder).resolve() / scope
    unique = dict.fromkeys(d['text'] for d in docs)
    vectors, missing = {}, []
    for value in unique:
        key = hashlib.sha256(value.encode('utf-8')).hexdigest()
        vector = cached_vector(folder / (key + '.json'), scope, key)
        if vector is None:
            missing.append((value, key))
        else:
            vectors[value] = vector
    reused = len(vectors)
    for start in range(0, len(missing), 32):
        batch = missing[start:start + 32]
        embedded = np.asarray(list(model.passage_embed([value for value, _ in batch], batch_size=32)), dtype=np.float32)
        if embedded.shape != (len(batch), 384) or not np.isfinite(embedded).all():
            raise ValueError('Invalid embeddings')
        norms = np.linalg.norm(embedded, axis=1, keepdims=True)
        if not np.isfinite(norms).all() or (norms <= 0).any():
            raise ValueError('Invalid or zero embedding norm')
        embedded /= norms
        if not np.isfinite(embedded).all() or not np.allclose(np.linalg.norm(embedded, axis=1), 1., rtol=1e-5, atol=1e-6):
            raise ValueError('Invalid normalized embeddings')
        # Validate the entire batch before publishing any of its entries.
        for (value, key), vector in zip(batch, embedded):
            save_cached_vector(folder / (key + '.json'), scope, key, vector)
            vectors[value] = vector
    matrix = np.asarray([vectors[d['text']] for d in docs], dtype=np.float32) if docs else np.empty((0, 384), dtype=np.float32)
    return matrix, {'embeddings_reused': reused, 'embeddings_computed': len(missing)}


def build(index_folder, out, model_folder, cache_folder=None):
    import numpy as np
    index_folder, out = Path(index_folder).resolve(), Path(out).resolve()
    identity = model_identity(model_folder)
    index, hashes, aggregates = snapshot(index_folder)
    pointer = out / 'semantic.json'
    if pointer.exists():
        previous = read(pointer)
        if previous.get('schema') == 'vod-semantic/v1' and previous.get('policy') == POLICY and previous.get('embedding_recipe') == CACHE_RECIPE and previous['literal_index'] == str(index_folder) and previous['inputs'] == hashes and previous['model'] == identity:
            folder = (out / previous['build']).resolve()
            artifacts = previous['artifacts']
            if folder.parent == out and set(artifacts) == {'passages.json', 'vectors.npy'} and all((folder / name).is_file() and digest(folder / name) == sha for name, sha in artifacts.items()):
                return {'passages': previous['passages'], 'reused': True}
    model, count = load_model(model_folder)
    docs = passages(aggregates, count)
    vectors, cache_info = passage_embeddings(model, docs, cache_folder or out / 'embedding-cache', identity)
    folder = out / ('build-' + uuid.uuid4().hex[:12]); folder.mkdir(parents=True)
    write(folder / 'passages.json', docs)
    np.save(folder / 'vectors.npy', vectors, allow_pickle=False)
    if snapshot(index_folder)[1] != hashes:
        raise RuntimeError('Transcript inputs changed during embedding; previous index preserved')
    write(pointer, {'schema': 'vod-semantic/v1', 'policy': POLICY, 'embedding_recipe': CACHE_RECIPE, 'literal_index': str(index_folder), 'inputs': hashes,
          'model': identity, 'build': folder.name, 'passages': len(docs), 'coverage': index['sources'],
          'excluded_invalid_segments': index['summary']['invalid_transcript_segments'],
          'artifacts': {n: digest(folder / n) for n in ('passages.json', 'vectors.npy')}})
    return {'passages': len(docs), 'reused': False, **cache_info}


def rank(docs, scores, limit):
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
        raise ValueError('Search limit must be between 1 and 200')
    if len(docs) != len(scores): raise ValueError('Embedding/document count mismatch')
    selected, suppressed, buckets = [], 0, {}
    for i in sorted(range(len(docs)), key=lambda i: (-float(scores[i]), i)):
        row = docs[i]
        keys = [(row['source_id'], row['audio_stream'], slot) for slot in range(
            math.floor(row['start_sec'] / 30), math.floor(row['end_sec'] / 30) + 1)]
        neighbors = {j for key in keys for j in buckets.get(key, [])}
        for j in neighbors:
            chosen = selected[j]
            overlap = min(row['end_sec'], chosen['end_sec']) - max(row['start_sec'], chosen['start_sec'])
            shorter = min(row['end_sec'] - row['start_sec'], chosen['end_sec'] - chosen['start_sec'])
            if row['source_id'] == chosen['source_id'] and row['audio_stream'] == chosen['audio_stream'] and overlap > 0 and overlap >= shorter * .5:
                suppressed += 1
                break
        else:
            for key in keys: buckets.setdefault(key, []).append(len(selected))
            selected.append({**row, 'similarity': float(scores[i])})
    return selected[:limit], {'distinct_results': len(selected), 'overlapping_results_grouped': suppressed,
                              'more_available': len(selected) > limit, 'indexed_passages': len(docs)}


def search_snapshot(out, model_folder):
    import numpy as np
    out = Path(out).resolve(strict=True)
    manifest = read(out / 'semantic.json')
    if manifest.get('schema') != 'vod-semantic/v1': raise ValueError('Unsupported semantic index')
    if manifest.get('policy') != POLICY: raise ValueError('Semantic passage policy changed; rebuild the index')
    if 'embedding_recipe' in manifest and manifest['embedding_recipe'] != CACHE_RECIPE:
        raise ValueError('Semantic embedding recipe changed; rebuild the index')
    if snapshot(manifest['literal_index'])[1] != manifest['inputs']:
        raise ValueError('Semantic index is stale; rebuild it')
    if model_identity(model_folder) != manifest['model']:
        raise ValueError('Semantic model differs from the indexed model')
    folder = (out / manifest['build']).resolve(strict=True)
    if folder.parent != out: raise ValueError('Invalid semantic build folder')
    for name, sha in manifest['artifacts'].items():
        if name not in ('passages.json', 'vectors.npy') or digest(folder / name) != sha:
            raise ValueError('Semantic artifacts changed; rebuild the index')
    docs = read(folder / 'passages.json')
    vectors = np.load(folder / 'vectors.npy', allow_pickle=False)
    if vectors.shape != (len(docs), 384) or not np.isfinite(vectors).all(): raise ValueError('Invalid embedding matrix')
    return manifest, docs, vectors


class SearchSession:
    """Keep only the model warm; validate evidence and artifacts on every query."""
    def __init__(self, out, model_folder):
        self.out, self.model_folder = out, model_folder
        self.model = self.count = self.identity = None

    def start(self):
        manifest, _, _ = search_snapshot(self.out, self.model_folder)
        self._load(manifest['model'])

    def _load(self, identity):
        if self.model is None:
            self.model, self.count = load_model(self.model_folder)
            self.identity = deepcopy(identity)
        elif self.identity != identity:
            raise ValueError('Model changed while worker was running; restart the worker')

    def search(self, query, limit=10):
        import numpy as np
        query = text(query, 'search query').strip()
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
            raise ValueError('Search limit must be between 1 and 200')
        manifest, docs, vectors = search_snapshot(self.out, self.model_folder)
        self._load(manifest['model'])
        if self.count(query) > 384: raise ValueError('Shorten the query to at most 384 model tokens')
        vector = np.asarray(next(self.model.query_embed(query)), dtype=np.float32)
        norm = np.linalg.norm(vector)
        if vector.shape != (384,) or not np.isfinite(vector).all() or norm <= 0: raise ValueError('Invalid query embedding')
        hits, summary = rank(docs, vectors @ (vector / norm), limit)
        return {'query': query, 'hits': hits, 'limit': limit, **summary, 'coverage': manifest['coverage'],
                'excluded_invalid_segments': manifest['excluded_invalid_segments'], 'limitations': LIMITS}


def search(out, model_folder, query, limit=10):
    return SearchSession(out, model_folder).search(query, limit)


def worker(session, source, target):
    session.start()
    def emit(value):
        target.write(json.dumps(value, ensure_ascii=True, allow_nan=False) + '\n'); target.flush()
    emit({'ready': True, 'protocol': 'vod-semantic-worker/v1'})
    while True:
        line = source.readline(16385)
        if not line:
            return
        if len(line) > 16384:
            emit({'error': 'Request exceeds 16384 characters; worker stopped'})
            return
        request_id = None
        try:
            request = json.loads(line)
            if not isinstance(request, dict): raise ValueError('Expected a JSON object')
            request_id = request.get('id')
            if request_id is not None and not isinstance(request_id, (str, int)):
                raise ValueError('Request id must be a string or integer')
            result = session.search(request.get('query'), request.get('limit', 10))
            emit({'id': request_id, 'result': result})
        except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
            emit({'id': request_id, 'error': str(exc)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('download-model'); p.add_argument('--out', required=True)
    p = commands.add_parser('index'); p.add_argument('--literal-index', required=True); p.add_argument('--out', required=True); p.add_argument('--model-dir', required=True)
    p.add_argument('--cache-dir', help='Reusable passage embeddings (default: OUT/embedding-cache)')
    p = commands.add_parser('search'); p.add_argument('--index', required=True); p.add_argument('--model-dir', required=True)
    p.add_argument('--query', required=True); p.add_argument('--limit', type=int, default=10); p.add_argument('--out')
    p = commands.add_parser('worker', help='Persistent JSON-lines search over stdin/stdout; EOF stops it')
    p.add_argument('--index', required=True); p.add_argument('--model-dir', required=True)
    p = commands.add_parser('search-many', help='Search multiple queries with one model initialization')
    p.add_argument('--index', required=True); p.add_argument('--model-dir', required=True)
    p.add_argument('--queries', required=True, help='JSON array of query strings')
    p.add_argument('--limit', type=int, default=10); p.add_argument('--out', required=True)
    args = parser.parse_args()
    if args.command == 'worker':
        worker(SearchSession(args.index, args.model_dir), sys.stdin, sys.stdout)
        return
    if args.command == 'search-many':
        queries = read(args.queries)
        if not isinstance(queries, list) or not queries or any(not isinstance(q, str) or not q.strip() for q in queries):
            raise ValueError('Queries must be a nonempty JSON array of nonempty strings')
        if Path(args.out).exists(): raise ValueError('Use a fresh output file')
        session = SearchSession(args.index, args.model_dir)
        result = {'results': [session.search(query, args.limit) for query in queries]}
        write(args.out, result)
        print(json.dumps({'queries': len(queries), 'out': str(Path(args.out).resolve())}))
        return
    if args.command == 'download-model': result = download_model(args.out)
    elif args.command == 'index': result = build(args.literal_index, args.out, args.model_dir, args.cache_dir)
    else:
        result = search(args.index, args.model_dir, args.query, args.limit)
        if args.out: write(args.out, result)
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
