import json, sys, os, re, time, urllib.parse, urllib.request, urllib.error
sys.stdout.reconfigure(encoding="utf-8")
SRC = sys.argv[1]
UA = {'User-Agent': 'PhonemeAtlasBuilder/1.0 (personal research)'}
M = {
 'p':'Voiceless_bilabial_plosive.ogg','b':'Voiced_bilabial_plosive.ogg','t':'Voiceless_alveolar_plosive.ogg','d':'Voiced_alveolar_plosive.ogg',
 'ʈ':'Voiceless_retroflex_stop.oga','ɖ':'Voiced_retroflex_stop.oga','c':'Voiceless_palatal_plosive.ogg','ɟ':'Voiced_palatal_plosive.ogg',
 'k':'Voiceless_velar_plosive.ogg','ɡ':'Voiced_velar_plosive_02.ogg','q':'Voiceless_uvular_plosive.ogg','ɢ':'Voiced_uvular_stop.oga',
 'ʡ':'Epiglottal_stop.ogg','ʔ':'Glottal_stop.ogg',
 'm':'Bilabial_nasal.ogg','m̥':'Voiceless_Bilabial_Nasal.ogg','ɱ':'Labiodental_nasal.ogg','n':'Alveolar_nasal.ogg','n̥':'Voiceless_Alveolar_Nasal.ogg',
 'ɳ':'Retroflex_nasal.ogg','ɲ':'Palatal_nasal.ogg','ɲ̥':'Voiceless_palatal_nasal.ogg','ŋ':'Velar_nasal.ogg','ŋ̥':'Voiceless_velar_nasal.wav','ɴ':'Uvular_nasal.ogg',
 'ʙ':'Bilabial_trill.ogg','r':'Alveolar_trill.ogg','r̥':'Voiceless_alveolar_trill.ogg','ʀ':'Uvular_trill.ogg',
 'ʜ':'Voiceless_epiglottal_trill.ogg','ʢ':'Voiced_epiglottal_trill_2.ogg',
 'ⱱ':'Labiodental_flap.ogg','ɾ':'Alveolar_tap.ogg','ɽ':'Retroflex_flap.ogg','ɺ':'Voiced_alveolar_lateral_flap.wav',
 'ɸ':'Voiceless_bilabial_fricative.ogg','β':'Voiced_bilabial_fricative.ogg','f':'Voiceless_labio-dental_fricative.ogg','v':'Voiced_labio-dental_fricative.ogg',
 'θ':'Voiceless_dental_fricative.ogg','ð':'Voiced_dental_fricative.ogg','s':'Voiceless_alveolar_sibilant.ogg','z':'Voiced_alveolar_sibilant.ogg',
 'ʃ':'Voiceless_palato-alveolar_sibilant.ogg','ʒ':'Voiced_palato-alveolar_sibilant.ogg','ʂ':'Voiceless_retroflex_sibilant.ogg','ʐ':'Voiced_retroflex_sibilant.ogg',
 'ɕ':'Voiceless_alveolo-palatal_sibilant.ogg','ʑ':'Voiced_alveolo-palatal_sibilant.ogg','ç':'Voiceless_palatal_fricative.ogg','ʝ':'Voiced_palatal_fricative.ogg',
 'x':'Voiceless_velar_fricative.ogg','ɣ':'Voiced_velar_fricative.ogg','χ':'Voiceless_uvular_fricative.ogg','ʁ':'Voiced_uvular_fricative.ogg',
 'ħ':'Voiceless_pharyngeal_fricative.ogg','ʕ':'Voiced_pharyngeal_fricative.ogg','h':'Voiceless_glottal_fricative.ogg','ɦ':'Voiced_glottal_fricative.ogg',
 'ʍ':'Voiceless_labio-velar_fricative.ogg','ɧ':'Voiceless_dorso-palatal_velar_fricative.ogg',
 'ɬ':'Voiceless_alveolar_lateral_fricative.ogg','ɮ':'Voiced_alveolar_lateral_fricative.ogg',
 'ʋ':'Labiodental_approximant.ogg','ɹ':'Alveolar_approximant.ogg','ɻ':'Retroflex_Approximant2.oga','j':'Palatal_approximant.ogg',
 'ɰ':'Voiced_velar_approximant.ogg','w':'Voiced_labio-velar_approximant.ogg','ɥ':'LL-Q150_(fra)-WikiLucas00-IPA_ɥ.wav','β̞':'Bilabial_approximant.ogg',
 'l':'Alveolar_lateral_approximant.ogg','l̥':'Voiceless_alveolar_lateral_approximant.ogg','ɭ':'Retroflex_lateral_approximant.ogg',
 'ʎ':'Palatal_lateral_approximant.ogg','ʟ':'Velar_lateral_approximant.ogg','lˠ':'Velarized_alveolar_lateral_approximant.ogg',
 'ts':'Voiceless_alveolar_sibilant_affricate.oga','dz':'Voiced_alveolar_sibilant_affricate.oga','tʃ':'Voiceless_palato-alveolar_affricate.ogg',
 'dʒ':'Voiced_palato-alveolar_affricate.ogg','ʈʂ':'Voiceless_retroflex_affricate.ogg','ɖʐ':'Voiced_retroflex_affricate.ogg',
 'tɕ':'Voiceless_alveolo-palatal_affricate.ogg','dʑ':'Voiced_alveolo-palatal_affricate.ogg','pf':'Voiceless_labiodental_affricate.ogg',
 'cç':'Voiceless_palatal_affricate.ogg','ɟʝ':'Voiced_palatal_affricate.ogg','kx':'Voiceless_velar_affricate.ogg','qχ':'Voiceless_uvular_affricate.ogg',
 'tɬ':'Voiceless_alveolar_lateral_affricate.ogg','dɮ':'Voiced_alveolar_lateral_affricate.ogg',
 'pʼ':'Bilabial_ejective_plosive.ogg','tʼ':'Alveolar_ejective_plosive.ogg','ʈʼ':'Retroflex_ejective.ogg','cʼ':'Palatal_ejective.ogg',
 'kʼ':'Velar_ejective_plosive.ogg','qʼ':'Uvular_ejective_plosive.ogg','fʼ':'Labiodental_ejective_fricative.ogg','sʼ':'Alveolar_ejective_fricative.ogg',
 'ʃʼ':'Palato-alveolar_ejective_fricative.ogg','xʼ':'Velar_ejective_fricative.ogg','χʼ':'Uvular_ejective_fricative.ogg','ɬʼ':'Alveolar_lateral_ejective_fricative.ogg',
 'tsʼ':'Alveolar_ejective_affricate.ogg','tʃʼ':'Palato-alveolar_ejective_affricate.ogg','ʈʂʼ':'Retroflex_ejective_affricate.ogg',
 'kxʼ':'Velar_ejective_affricate.ogg','qχʼ':'Uvular_ejective_affricate.ogg','tɬʼ':'Alveolar_lateral_ejective_affricate.ogg',
 'ɓ':'Voiced_bilabial_implosive.ogg','ɗ':'Voiced_alveolar_implosive.ogg','ᶑ':'Voiced-retroflex-implosive.ogg','ʄ':'Voiced_palatal_implosive.ogg',
 'ɠ':'Voiced_velar_implosive.ogg','ʛ':'Voiced_uvular_implosive.ogg',
 'ʘ':'Clic_bilabial_sourd.ogg','ǀ':'Dental_click.ogg','ǃ':'Postalveolar_click.ogg','ǂ':'Palatoalveolar_click.ogg','ǁ':'Alveolar_lateral_click.ogg','‼':'Retrflx_click.wav',
 'kp':'Voiceless_labial-velar_plosive.ogg','ɡb':'Voiced_labial-velar_plosive.ogg','ŋm':'Labial-velar_nasal_stop.ogg',
 'i':'Close_front_unrounded_vowel.ogg','y':'Close_front_rounded_vowel.ogg','ɨ':'Close_central_unrounded_vowel.ogg','ʉ':'Close_central_rounded_vowel.ogg',
 'ɯ':'Close_back_unrounded_vowel.ogg','u':'Close_back_rounded_vowel.ogg','ɪ':'Near-close_near-front_unrounded_vowel.ogg','ʏ':'Near-close_near-front_rounded_vowel.ogg',
 'ʊ':'Near-close_near-back_rounded_vowel.ogg','e':'Close-mid_front_unrounded_vowel.ogg','ø':'Close-mid_front_rounded_vowel.ogg',
 'ɘ':'Close-mid_central_unrounded_vowel.ogg','ɵ':'Close-mid_central_rounded_vowel.ogg','ɤ':'Close-mid_back_unrounded_vowel.ogg','o':'Close-mid_back_rounded_vowel.ogg',
 'ə':'Mid-central_vowel.ogg','ɛ':'Open-mid_front_unrounded_vowel.ogg','œ':'Open-mid_front_rounded_vowel_(2).ogg','ɜ':'Open-mid_central_unrounded_vowel.ogg',
 'ɞ':'Open-mid_central_rounded_vowel.ogg','ʌ':'PR-open-mid_back_unrounded_vowel2.ogg','ɔ':'PR-open-mid_back_rounded_vowel.ogg',
 'æ':'Near-open_front_unrounded_vowel.ogg','ɐ':'Near-open_central_unrounded_vowel.ogg','a':'PR-open_front_unrounded_vowel.ogg',
 'ɶ':'Open_front_rounded_vowel.ogg','ɑ':'Open_back_unrounded_vowel.ogg','ɒ':'PR-open_back_rounded_vowel.ogg',
}
pairs = json.load(open(f'{SRC}/pairs.json', encoding='utf-8'))
mp3 = {}
for _, _, href in pairs:
    if href.endswith('.mp3'):
        name = urllib.parse.unquote(href.split('/')[-1])[:-4]
        mp3[name] = 'https:' + href if href.startswith('//') else href
os.makedirs(f'{SRC}/files', exist_ok=True)
out = {}
for key, fn in M.items():
    url = mp3.get(fn)
    if not url:
        print('NO MP3 for', key, fn); continue
    dest = f'{SRC}/files/{len(out):03d}.mp3'
    if not os.path.exists(dest):
        for attempt in range(8):
            try:
                data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read(); break
            except urllib.error.HTTPError as e:
                if e.code != 429: raise
                time.sleep(5 * (attempt + 1))
        open(dest, 'wb').write(data); time.sleep(1.2)
    out[key] = {'file': fn, 'path': dest}
titles = ['File:' + v['file'] for v in out.values()]
meta = {}
for i in range(0, len(titles), 40):
    q = urllib.parse.urlencode({'action': 'query', 'titles': '|'.join(titles[i:i+40]), 'prop': 'imageinfo', 'iiprop': 'extmetadata',
                                'iiextmetadatafilter': 'Artist|LicenseShortName', 'format': 'json', 'formatversion': 2})
    d = json.load(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + q, headers=UA), timeout=60))
    norm = {n['to']: n['from'] for n in d['query'].get('normalized', [])}
    for p in d['query']['pages']:
        em = p.get('imageinfo', [{}])[0].get('extmetadata', {})
        artist = re.sub(r'<[^>]+>', '', em.get('Artist', {}).get('value', '')).strip()
        meta[norm.get(p['title'], p['title'])] = (artist, em.get('LicenseShortName', {}).get('value', ''))
for k, v in out.items():
    a = meta.get('File:' + v['file']) or meta.get('File:' + v['file'].replace('_', ' ')) or ('', '')
    v['artist'], v['license'] = a
    v['bytes'] = os.path.getsize(v['path'])
json.dump(out, open(f'{SRC}/audio_index.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(out), 'files', sum(v['bytes'] for v in out.values()) // 1024, 'KB')
from collections import Counter
print(Counter(v['license'] for v in out.values()))
print([(k, v['file']) for k, v in out.items() if not v['license']])
print(Counter(v['artist'][:40] for v in out.values()).most_common(12))
