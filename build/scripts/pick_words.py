"""Pick one verified example word per sound: hand-picked (well-known language) first, then automatic. Re-checks strictly."""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
S = sys.argv[1]; sys.path.insert(0, S + '/scripts')
import wikt, ipa as IPA
import unicodedata as U
keys = json.load(open(S + '/colkeys.json', encoding='utf-8'))
hand = json.load(open(S + '/words_hand.json', encoding='utf-8'))
if os.path.exists(S + '/words_hand2.json'): hand.update(json.load(open(S + '/words_hand2.json', encoding='utf-8')))
auto = json.load(open(S + '/words_auto.json', encoding='utf-8'))
out, why = {}, {}
for k in keys:
    g = IPA.classify(k)[0]
    for src in (hand, auto):
        w = src.get(k) or src.get(U.normalize('NFC', k)) or src.get(U.normalize('NFD', k))
        if w and (len(w['word']) == 1 and not ('㐀' <= w['word'] <= '鿿' or '가' <= w['word'] <= '힯') or (len(w['word']) == 2 and 'ऄ' <= w['word'][0] <= 'औ')):
            why[k] = f"{w['lang']} {w['word']} is a letter, not a word"; continue
        if w and wikt.contains_strict(w['ipa'], k, g, w['lang']):
            out[k] = dict(w); break
        if w: why[k] = f"{w['lang']} {w['word']} {w['ipa']} failed strict check"
missing = [k for k in keys if k not in out]
json.dump(out, open(S + '/words_sel.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('selected', len(out), 'of', len(keys))
print('missing:', ' '.join(missing))
for k, v in why.items():
    if k not in out: print('  ', k, v)
