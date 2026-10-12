"""Download word recordings (Commons mp3 transcodes) for a selection file; keeps a file->local path index."""
import json, sys, os, time, hashlib, urllib.parse, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')
S, SEL = sys.argv[1], sys.argv[2]
UA = {'User-Agent': 'PhonemeAtlasBuilder/1.0 (personal research)'}
D = os.path.join(S, 'audio_src', 'words'); os.makedirs(D, exist_ok=True)
IDX = os.path.join(S, 'audio_src', 'words_index.json')
idx = json.load(open(IDX, encoding='utf-8')) if os.path.exists(IDX) else {}

def commons_mp3(fn):
    fn = fn.replace(' ', '_'); fn = fn[:1].upper() + fn[1:]
    h = hashlib.md5(fn.encode('utf-8')).hexdigest()
    q = urllib.parse.quote(fn)
    if fn.lower().endswith('.mp3'):
        return f'https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{q}'
    return f'https://upload.wikimedia.org/wikipedia/commons/transcoded/{h[0]}/{h[:2]}/{q}/{q}.mp3'

sel = json.load(open(SEL, encoding='utf-8'))
for key, w in sel.items():
    fn = w['audio'].replace(' ', '_')
    if fn in idx and os.path.exists(idx[fn]):
        continue
    url = commons_mp3(fn)
    dest = os.path.join(D, hashlib.md5(fn.encode('utf-8')).hexdigest()[:12] + '.mp3')
    data = None
    for attempt in range(10):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read(); break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print('404', key, fn); break
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            time.sleep(5)
    if data:
        open(dest, 'wb').write(data); idx[fn] = dest
        json.dump(idx, open(IDX, 'w', encoding='utf-8'), ensure_ascii=False)
        print('ok', key, fn, len(data), flush=True)
    time.sleep(1.5)
print('done', len(idx))
