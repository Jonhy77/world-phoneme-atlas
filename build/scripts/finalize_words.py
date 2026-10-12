"""Attach local audio paths and Commons author/license to the selected example words."""
import json, sys, os, re, time, urllib.parse, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')
S = sys.argv[1]
UA = {'User-Agent': 'PhonemeAtlasBuilder/1.0 (personal research)'}
sel = json.load(open(S + '/words_sel.json', encoding='utf-8'))
idx = json.load(open(S + '/audio_src/words_index.json', encoding='utf-8'))
files = sorted({w['audio'].replace(' ', '_') for w in sel.values()})
meta = {}
def api(params):
    u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)
    for a in range(10):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60))
        except urllib.error.HTTPError as e:
            time.sleep(6 * (a + 1))
    raise RuntimeError('commons api failed')
for i in range(0, len(files), 40):
    d = api({'action': 'query', 'titles': '|'.join('File:' + f for f in files[i:i + 40]), 'prop': 'imageinfo',
             'iiprop': 'extmetadata|user', 'iiextmetadatafilter': 'Artist|LicenseShortName', 'format': 'json', 'formatversion': 2})
    norm = {n['to']: n['from'] for n in d['query'].get('normalized', [])}
    for p in d['query']['pages']:
        ii = (p.get('imageinfo') or [{}])[0]; em = ii.get('extmetadata', {})
        art = re.sub(r'<[^>]+>', '', em.get('Artist', {}).get('value', '')).strip()
        art = re.sub(r'\s+', ' ', art)
        m = re.match(r'No machine-readable author provided\.\s*(\S+)', art)
        if m: art = m.group(1) + ' (per Commons, assumed)'
        if not art and ii.get('user'): art = 'uploaded by ' + ii['user']
        meta[norm.get(p['title'], p['title'])[5:].replace(' ', '_')] = (art[:80], em.get('LicenseShortName', {}).get('value', ''))
    time.sleep(2)
out = {}
for k, w in sel.items():
    f = w['audio'].replace(' ', '_')
    if f not in idx: print('no audio file for', k, f); continue
    a = meta.get(f, ('', ''))
    out[k] = {**w, 'path': idx[f], 'artist': a[0], 'license': a[1]}
json.dump(out, open(S + '/words_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('final', len(out), 'licenses:', sorted({v['license'] for v in out.values()}))
