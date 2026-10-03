"""THROWAWAY UI PROTOTYPE: three timeline/keybind layouts on /?variant=A|B|C.

Run: python outputs/vod-discovery/assets/review-queue/prototype/serve.py
Only memory is mutated. Reads the existing pilot previews; never writes choices.
"""
import argparse
from copy import deepcopy
from pathlib import Path
import sys
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
SKILL = HERE.parents[2]
WORKSPACE = SKILL.parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
from review_queue import Store, make_server
from vod import read


class PrototypeStore(Store):
    def __init__(self, folder):
        super().__init__(folder)
        self.memory = super().state()
        self.memory['current_id'] = 'vsmp-pilot-08'
        self.memory['decisions']['vsmp-pilot-08'].update(view=0, positions={'0': 5})

    def state(self):
        return deepcopy(self.memory) if hasattr(self, 'memory') else super().state()

    def playback_queue(self):
        result = super().playback_queue()
        result['timeline_data'] = dict(plan=self.playback_plan, sources=read(self.folder / 'events.json')['sources'])
        return result

    def mutate(self, patch, undo=False):
        with self.lock:
            state = self.memory
            if undo:
                if state['history']:
                    prior = state['history'].pop()
                    state['decisions'][prior['id']]['decision'] = prior['decision']
                    state['current_id'] = prior['id']
            else:
                eid = patch['event_id']; item = state['decisions'][eid]
                if 'decision' in patch and patch['decision'] != item['decision']:
                    state['history'].append(dict(id=eid, decision=item['decision']))
                for field in ('decision', 'note', 'view'):
                    if field in patch: item[field] = patch[field]
                if 'position_sec' in patch:
                    item['positions'][str(item['view'])] = patch['position_sec']
                state['current_id'] = eid
            state['revision'] += 1
            return deepcopy(state)

    def export(self, patch):
        raise ValueError('Prototype only; export from the accepted dashboard.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--queue', default=str(WORKSPACE / 'outputs/valorantsmp-pilot/review-queue'))
    parser.add_argument('--port', type=int, default=0)
    args = parser.parse_args()
    server = make_server(PrototypeStore(args.queue), args.port)
    base = server.RequestHandlerClass

    class PrototypeHandler(base):
        def do_GET(self):
            if not self.allowed(): return super().do_GET()
            route = urlsplit(self.path).path
            if route == '/':
                content = (HERE.parent / 'index.html').read_text(encoding='utf-8')
                content = content.replace('</head>', '<link rel="stylesheet" href="/prototype.css"><script src="/prototype.js" defer></script></head>')
                mime = 'text/html'
            elif route == '/app.js':
                content = (HERE.parent / 'app.js').read_text(encoding='utf-8')
                # Replace fixed hotkeys with the prototype's editable bindings.
                begin = content.index("document.addEventListener('keydown', event => {")
                end = content.index('}, true);', begin) + len('}, true);')
                content = content[:begin] + content[end:]
                content = content.replace("'Saved'", "'Preview only'")
                content = content.replace("$('export').disabled = !queue.cards.some(c => state.decisions[c.id].decision === 'keep');", "$('export').disabled = true;")
                mime = 'text/javascript'
            elif route in ('/prototype.js', '/prototype.css'):
                content = (HERE / route[1:]).read_text(encoding='utf-8')
                mime = 'text/javascript' if route.endswith('.js') else 'text/css'
            else:
                return super().do_GET()
            raw = content.encode('utf-8')
            self.send_headers(200, mime + '; charset=utf-8', len(raw))
            if self.command != 'HEAD': self.wfile.write(raw)

    server.RequestHandlerClass = PrototypeHandler
    print(f'http://127.0.0.1:{server.server_port}/?variant=A', flush=True)
    with server:
        try: server.serve_forever()
        except KeyboardInterrupt: pass


if __name__ == '__main__': main()
