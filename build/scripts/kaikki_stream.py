"""Stream Wiktextract (kaikki.org) per-language dumps and keep only entries with IPA + audio."""
import json, sys, urllib.request, os, time
OUT = sys.argv[1]
LANGS = sys.argv[2:]
UA = {'User-Agent': 'PhonemeAtlasBuilder/1.0 (personal research)'}
os.makedirs(OUT, exist_ok=True)
for L in LANGS:
    fn = os.path.join(OUT, L + '.json')
    if os.path.exists(fn):
        continue
    url = f'https://kaikki.org/dictionary/{L}/kaikki.org-dictionary-{L.replace(" ", "")}.jsonl'
    keep, seen = [], set()
    t0 = time.time()
    try:
        with urllib.request.urlopen(urllib.request.Request(url.replace(' ', '%20'), headers=UA), timeout=120) as r:
            for raw in r:
                if b'"audio"' not in raw or b'"ipa"' not in raw:
                    continue
                e = json.loads(raw)
                snd = e.get('sounds', [])
                ipa = [s['ipa'] for s in snd if 'ipa' in s]
                aud = [(s.get('audio'), s.get('mp3_url') or s.get('ogg_url')) for s in snd if s.get('audio')]
                if not ipa or not aud:
                    continue
                key = (e['word'], tuple(ipa))
                if key in seen:
                    continue
                seen.add(key)
                keep.append({'w': e['word'], 'ipa': ipa, 'aud': aud,
                             'gloss': next((g for s in e.get('senses', []) for g in s.get('glosses', [])), '')[:60]})
    except Exception as ex:
        print(L, 'ERROR', ex, flush=True)
        continue
    json.dump(keep, open(fn, 'w', encoding='utf-8'), ensure_ascii=False)
    print(L, len(keep), 'entries', round(time.time() - t0), 's', flush=True)
