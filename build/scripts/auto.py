import json, sys, os, glob
sys.stdout.reconfigure(encoding='utf-8')
S = sys.argv[1]; sys.path.insert(0, S + '/scripts')
import wikt, ipa as IPA
keys = json.load(open(S + '/colkeys.json', encoding='utf-8'))
have = json.load(open(S + '/words_hand.json', encoding='utf-8')) if os.path.exists(S + '/words_hand.json') else {}
C = json.load(open(S + '/scripts/candidates.json', encoding='utf-8'))
PRI = ['Hindi', 'Georgian', 'Korean', 'Vietnamese', 'Thai', 'Swahili', 'Persian', 'Welsh', 'Icelandic', 'Danish', 'Navajo', 'Amharic', 'Hausa',
       'Tamil', 'Malayalam', 'Bengali', 'Marathi', 'Urdu', 'Armenian', 'Malagasy', 'Ewe', 'Irish', 'Zulu', 'Yoruba']
DB = {}
for fn in glob.glob(S + '/kaikki/*.json'):
    L = os.path.basename(fn)[:-5]
    DB[L] = json.load(open(fn, encoding='utf-8'))
out = {}
todo = list(keys)
for k in todo:
    best = None
    grp = IPA.classify(k)[0]
    for L, entries in DB.items():
        pr = PRI.index(L) if L in PRI else 99
        for e in entries:
            w = e['w']
            if w.startswith('-') or w.endswith('-') or '㄰' <= w[:1] <= '㆏' or (len(w) < 2 and not ('㐀' <= w[:1] <= '鿿' or '가' <= w[:1] <= '힯')):
                continue
            okaud = [a for a in e['aud'] if a[0] and wikt.audio_ok(L, w, a[0])]
            if not okaud: continue
            hit = [x for x in e['ipa'] if '-' not in x and wikt.contains_strict(x, k, grp)]
            if not hit: continue
            score = (' ' in w, len(w) > 12, pr, len(hit[0]))
            if best is None or score < best[0]:
                best = (score, {'lang': L, 'word': e['w'], 'ipa': hit[0], 'audio': okaud[0][0].replace(' ', '_'), 'url': okaud[0][1], 'gloss': e['gloss'], 'src': 'kaikki'})
    if best: out[k] = best[1]
    print(k, '->', (best[1]['lang'] + ': ' + best[1]['word'] + ' ' + best[1]['ipa']) if best else 'MISSING')
json.dump(out, open(S + '/words_auto.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('auto found', len(out), 'of', len(todo), 'remaining')
