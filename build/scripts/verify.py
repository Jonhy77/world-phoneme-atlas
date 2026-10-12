import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
S = sys.argv[1]; sys.path.insert(0, S + '/scripts')
import wikt
CF = sys.argv[2] if len(sys.argv) > 2 else S + '/scripts/candidates.json'
OF = sys.argv[3] if len(sys.argv) > 3 else S + '/words_hand.json'
C = json.load(open(CF, encoding='utf-8'))
import ipa as IPA
out = {}
for key, cands in C.items():
    for lang, word in cands:
        sec_lang = 'Chinese' if lang == 'Mandarin' else lang
        try:
            t = wikt.page_html(word, S + '/wcache')
        except Exception as e:
            print('ERR', key, word, e); continue
        sec = wikt.section(t, sec_lang)
        if not sec: continue
        au = wikt.audios(sec)
        au = [a for a in au if wikt.audio_ok(lang, word, a)]
        if not au: continue
        hit = [x for x in wikt.ipas(sec) if '-' not in x and not x.startswith('*') and len(x.strip('/[]')) > 1 and wikt.contains_strict(x, key, IPA.classify(key)[0], lang)]
        if not hit: continue
        out[key] = {'lang': lang, 'word': word, 'ipa': hit[0], 'audio': au[0], 'src': 'wiktionary'}
        break
    print(key, '->', out.get(key, {}).get('word', 'MISSING'), out.get(key, {}).get('ipa', ''), flush=True)
json.dump(out, open(OF, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('verified', len(out), 'of', len(C))
