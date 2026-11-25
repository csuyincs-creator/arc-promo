"""Write CREDITS.md from shots.json (credit/license/url fields), timeline.json and project.json.
    python make_credits.py shots.json src/data/timeline.json src/data/project.json CREDITS.md [--music-note "..."]"""
import json
import sys
args = sys.argv[1:]
note = ''
if '--music-note' in args:
    i = args.index('--music-note')
    note = args[i + 1]
    args = args[:i] + args[i + 2:]
shots_p, timeline_p, project_p, out = args
shots = json.load(open(shots_p))
tl = json.load(open(timeline_p))
pj = json.load(open(project_p))
title = ' / '.join(c['line1'] for c in pj.get('endCards', [])[:1]) or 'Arc promo'
lines = [f'# {title} — credits', '', '## Soundtrack', '', f'Source: `{tl.get("source", "?")}`.']
if note:
    lines += ['', note]
lines += ['', '## Pictures', '', '| Shot | Source | Licence |', '| --- | --- | --- |']
for s in shots:
    if s['type'] == 'procedural':
        src, lic = f'Drawn procedurally ({s.get("kind")})', 'Original'
    else:
        src = s.get('credit', s.get('src', '?'))
        if s.get('url'):
            src = f'[{src}]({s["url"]})'
        lic = s.get('license', 'UNKNOWN - check before publishing')
    lines.append(f'| {s["name"]} | {src} | {lic} |')
open(out, 'w').write('\n'.join(lines) + '\n')
missing = [s['name'] for s in shots if s['type'] != 'procedural' and 'license' not in s]
print(f'wrote {out}' + (f'; no licence recorded for: {", ".join(missing)}' if missing else ''))
