"""Build the data bundle for the IPA atlas page from PHOIBLE + Glottolog."""
import csv, sys, json, collections, os
sys.stdout.reconfigure(encoding="utf-8")
DATA, SCRIPTS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, SCRIPTS)
import ipa

rows = list(csv.DictReader(open(f"{DATA}/phoible.csv", encoding='utf-8')))
inv = collections.OrderedDict(); meta = {}
for r in rows:
    inv.setdefault(r['InventoryID'], []).append(r); meta[r['InventoryID']] = r

# ---------- Glottolog family / macroarea ----------
gl = {r['ID']: r for r in csv.DictReader(open(f"{DATA}/glottolog_languages.csv", encoding='utf-8'))}
def glotto(gc):
    r = gl.get(gc)
    if not r:
        return 'Unknown', 'Unknown'
    area = r['Macroarea'] or (gl.get(r['Language_ID'], {}).get('Macroarea') if r['Language_ID'] else '') or 'Unknown'
    fam = gl[r['Family_ID']]['Name'] if r['Family_ID'] in gl else ('Isolate' if r['Is_Isolate'] == 'true' else '—')
    return fam, area

# ---------- Top 38 (Ethnologue 2026, Wikipedia's table; Levantine Arabic (#35) left out: no PHOIBLE inventory, total speakers, millions) ----------
# rank, name, L1, L2, total, default inventory, note
TOP = [
 (1, 'English', 372, 1121, 1493, '2252', 'British RP (Received Pronunciation). Switch to an American inventory with the variety menu.'),
 (2, 'Mandarin Chinese', 988, 194, 1183, '1047', 'This source writes the "retroflex" series as apical postalveolars (t̠ʃ̺ ʃ̺ ɹ̺), so they show under /t͡ʃ ʃ ɹ/. Most textbooks write them ʈ͡ʂ ʂ ʐ (the SPA inventory in the variety menu uses those symbols).'),
 (3, 'Hindi', 347, 264, 611, '2542', ''),
 (4, 'Spanish', 487, 75, 561, '2210', 'Castilian (Spain). Diphthongs are listed as units in this source.'),
 (5, 'Modern Standard Arabic', 0, 335, 335, '2157', 'MSA as read by speakers from Safad, Beirut, Damascus and Kuwait. Ethnologue counts no native speakers of MSA.'),
 (6, 'French', 75, 258, 334, '2182', 'Parisian speaker.'),
 (7, 'Bengali', 234, 43, 274, '2624', 'Dhaka standard. This source writes the series often called retroflex (ট ড) as apical alveolar t d, so it shows under /t d/ alongside the dental t̪ d̪ (also /t d/ here). Bengali has two distinct coronal stop series.'),
 (8, 'Portuguese', 252, 18, 269, '2206', 'European Portuguese (Lisbon). Brazilian Portuguese (São Paulo) is in the variety menu. The source writes the reduced vowel as ɯ; most descriptions use ɨ.'),
 (9, 'Indonesian', 78, 177, 255, '1144', 'As spoken in Central Java. Chosen over the "Standard" PHOIBLE inventory, which lists a front rounded /y/ that Indonesian does not have.'),
 (10, 'Urdu', 78, 168, 246, '2466', ''),
 (11, 'Russian', 133, 77, 210, '2261', ''),
 (12, 'German', 76, 57, 133, '2398', 'Standard German. This source writes the r-sound as uvular trill ʀ; many speakers use ʁ.'),
 (13, 'Japanese', 124, 2, 126, '2196', 'Tokyo. Long vowels and geminates are treated as sequences in this source.'),
 (14, 'Nigerian Pidgin', 5, 116, 121, '1134', ''),
 (15, 'Egyptian Arabic', 83, 35, 118, '132', 'Cairo. This source counts geminate consonants as separate phonemes.'),
 (16, 'Marathi', 83, 16, 99, '1766', ''),
 (17, 'Vietnamese', 86, 11, 97, '2233', 'Hanoi.'),
 (18, 'Telugu', 83, 13, 96, '2387', ''),
 (19, 'Swahili', 4, 91, 95, '823', 'This source treats prenasalized stops (ᵐb ⁿd …) as single phonemes.'),
 (20, 'Hausa', 58, 36, 94, '2188', 'Kano (Standard).'),
 (21, 'Turkish', 86, 7, 94, '2217', 'Istanbul.'),
 (22, 'Western Punjabi', None, None, 90, '2479', 'PHOIBLE has no inventory for Western Punjabi (pnb). This column shows Eastern Punjabi (pan) as the closest documented variety. The source does not list Punjabi\'s lexical tones.'),
 (23, 'Tagalog', 33, 54, 87, '1666', ''),
 (24, 'Tamil', 79, 8, 86, '1058', 'Standard Spoken Tamil. Voiced stops are marginal in this analysis.'),
 (25, 'Yue Chinese (Cantonese)', 85, 1, 86, '2309', 'Hong Kong Cantonese.'),
 (26, 'Wu Chinese', 83, 0.5, 83, '17', 'The SPA source does not name the Wu variety. b̤̥ d̤̥ ɡ̤̥ are the "slack-voiced" series.'),
 (27, 'Persian', 65, 17, 82, '2205', 'Iranian Persian.'),
 (28, 'Korean', 82, 1, 82, '2197', 'Seoul. This source marks one of the three stop series (lax / aspirated / tense) with ◌͉.'),
 (29, 'Amharic', 39, 39, 78, '131', 'This source counts geminate consonants as separate phonemes.'),
 (30, 'Thai', 27, 44, 71, '2215', 'Standard Thai.'),
 (31, 'Javanese', None, None, 69.2, '36', 'The SPA source writes the "heavy" (slack-voiced) stop series as b̤̥ d̤̥ ɡ̤̥, which is how phoneticians describe them. Chosen over the PHOIBLE Yogya-Solo inventory, which lists a front rounded /y/ that Javanese does not have.'),
 (32, 'Italian', 60, 6, 65.6, '2195', 'Standard Italian. Long (geminate) consonants are listed as separate phonemes; ts dz ɲ ʎ ʃ only occur long between vowels, so the source lists them long.'),
 (33, 'Gujarati', 58, 5, 62.5, '2452', 'Standard Gujarati, with its breathy (murmured) vowels.'),
 (34, 'Kannada', 44, 15, 58.7, '2277', 'Standard Kannada.'),
 (36, 'Sudanese Arabic', 43, 11, 54.3, '659', 'This source counts geminate consonants as separate phonemes.'),
 (37, 'Yoruba', 48, 5, 52.9, '848', 'Nigerian Yoruba. Yoruba p is the double stop k͡p.'),
 (38, 'Bhojpuri', 53, 0.5, 52.7, '2357', ''),
]
TOP_INV = {t[5] for t in TOP if t[5]}

# ---------- Corrections to clear errors in the chosen inventories ----------
# type: add (raw segment) | replace (raw -> new raw)
ERRATA = {
 '2210': [('add', 'k', None, 'PHOIBLE omits /k/ from this Castilian inventory; Spanish has /k/ (casa, que). Source: Martínez-Celdrán, Fernández-Planas & Carrera-Sabaté (2003), "Castilian Spanish", JIPA 33(2).')],
 '2196': [('add', 'ɾ', None, 'PHOIBLE omits the Japanese liquid /ɾ/ (ら行) from this inventory. Source: Okada (1991), "Japanese", JIPA 21(2).')],
 '2233': [('add', 'ɓ', None, 'PHOIBLE omits /ɓ/ (written b) from this Hanoi inventory. Source: Kirby (2011), "Vietnamese (Hanoi Vietnamese)", JIPA 41(3).')],
 '2157': [('replace', 'ii̯', 'iː', 'The source writes MSA long /iː/ as ii̯. Mapped to iː so it lines up with the other long vowels.'),
          ('replace', 'uu̯', 'uː', 'The source writes MSA long /uː/ as uu̯. Mapped to uː so it lines up with the other long vowels.'),
          ('replace', 'xʀ̥', 'x', 'The source transcribes خ as a fricative with uvular trilling [xʀ̥]. Phonemically this is /x/ (often realized [χ]).')],
 '2604': [('add', 'l', None, 'PHOIBLE omits /l/ from this Polish inventory. Source: Jassem (2003), "Polish", JIPA 33(1).'),
          ('add', 'r', None, 'PHOIBLE omits the trill /r/ from this Polish inventory. Source: Jassem (2003), "Polish", JIPA 33(1).')],
 '2309': [('add', t, None, 'This Cantonese inventory has no tones. Added the six citation tones 55, 25, 33, 21, 23, 22 (Matthews & Yip, "Cantonese: A Comprehensive Grammar", 2nd ed., 2011).')
          for t in ['˥', '˨˥', '˧', '˨˩', '˨˧', '˨']],
}

# ---------- one inventory per language ----------
PRI = ['ph', 'ea', 'er', 'saphon', 'aa', 'ra', 'spa', 'upsid']
pick = {}
for i in inv:
    g = meta[i]['Glottocode']
    if g == 'NA':
        continue
    if g not in pick or PRI.index(meta[i]['Source']) < PRI.index(meta[pick[g]]['Source']):
        pick[g] = i
for t in TOP:  # curated choice overrides the rule
    if t[5] is None: continue
    g = meta[t[5]]['Glottocode']
    if t[1] != 'Western Punjabi':
        pick[g] = t[5]

# ---------- segment dictionary ----------
seg_index = {}; SEGS = []
def sidx(norm):
    if norm not in seg_index:
        g, key, desc = ipa.classify(norm)
        seg_index[norm] = len(SEGS)
        SEGS.append({'k': norm, 'g': g, 'key': key, 'desc': desc, 'd': ipa.display(norm, g), 'b': ipa.base_key(norm)})
    return seg_index[norm]

INV = {}
for i, rs in inv.items():
    m = meta[i]; segs = []
    for r in rs:
        raw = r['Phoneme']; marg = 1 if r['Marginal'] == 'TRUE' else 0
        segs.append([raw, sidx(ipa.normalize(raw)), marg, -1])
    INV[i] = {'name': m['LanguageName'], 'dialect': '' if m['SpecificDialect'] == 'NA' else m['SpecificDialect'],
              'src': m['Source'], 'gc': m['Glottocode'], 'iso': m['ISO6393'], 'segs': segs}

NOTES = []
for i, errs in ERRATA.items():
    for typ, a, b, note in errs:
        NOTES.append(note); ni = len(NOTES) - 1
        if typ == 'add':
            INV[i]['segs'].append([a, sidx(ipa.normalize(a)), 2, ni])
        else:
            hit = [s for s in INV[i]['segs'] if s[0] == a]
            assert hit, (i, a)
            for s in hit:
                s[1] = sidx(ipa.normalize(b)); s[3] = ni

# ---------- columns ----------
freq = collections.Counter()
for g, i in pick.items():
    for s in {s[1] for s in INV[i]['segs']}:
        freq[s] += 1
THR = round(0.01 * len(pick))
CLICK_TYPES = ['ʘ', 'ǀ', 'ǃ', 'ǂ', 'ǁ']
cols = set()
for n, S in enumerate(SEGS):
    if S['g'] in ('Tone', 'Other') and S['k'] != 'R':
        continue
    if S['g'] == 'Click':
        continue
    if freq[n] >= THR or S['k'] in ipa.IPA_CHART:
        cols.add(n)
for k in ipa.IPA_CHART:  # chart symbols with zero attestations still get a column
    if ipa.classify(k)[0] != 'Click':
        cols.add(sidx(k))
for ct in CLICK_TYPES:
    cols.add(sidx(ct))
GO = ipa.GROUP_ORDER
order = sorted(cols, key=lambda n: (GO.index(SEGS[n]['g']), SEGS[n]['key']))
colpos = {n: p for p, n in enumerate(order)}

# credit: segment -> columns it counts for; variant: segment -> plain column it is a variant of
plain_by_base = {SEGS[n]['b']: n for n in order if SEGS[n]['k'] == SEGS[n]['b']}
for n, S in enumerate(SEGS):
    credit = []
    if n in colpos:
        credit.append(colpos[n])
    if S['g'] == 'Click':
        for ct in CLICK_TYPES:
            if ct in S['k']:
                credit.append(colpos[seg_index[ct]])
    S['cr'] = credit
    var = -1
    if n not in colpos and S['g'] not in ('Tone', 'Click') and 'ʼ' not in S['k']:
        pb = plain_by_base.get(S['b'])
        if pb is not None:
            var = colpos[pb]
    elif n in colpos and S['k'] != S['b'] and 'ʼ' not in S['k'] and S['g'] not in ('Tone', 'Click'):
        pb = plain_by_base.get(S['b'])
        if pb is not None:
            var = colpos[pb]
    S['v'] = var

# world frequency per column (share of the 2,176 languages)
colfreq = [0] * len(order)
for g, i in pick.items():
    present = set()
    for s in INV[i]['segs']:
        present.update(SEGS[s[1]]['cr'])
    for c in present:
        colfreq[c] += 1

# ---------- language rows ----------
LANGS = []
for g, i in sorted(pick.items(), key=lambda x: INV[x[1]]['name'].lower()):
    fam, area = glotto(g)
    alts = [j for j in inv if meta[j]['Glottocode'] == g and j != i]
    LANGS.append([INV[i]['name'], INV[i]['iso'], g, fam, area, i, alts])

# ---------- serialize ----------
CLASS = {'Plosive', 'Nasal', 'Trill', 'Tap/Flap', 'Fricative', 'Lateral fricative', 'Approximant', 'Lateral approximant',
         'Affricate', 'Ejective', 'Implosive', 'Click', 'Prenasalized', 'Double articulation', 'Other'}
allsegfreq = collections.Counter()
for g, i in pick.items():
    for s in {s[1] for s in INV[i]['segs']}:
        allsegfreq[s] += 1
rank = {n: r for r, n in enumerate(sorted(range(len(SEGS)), key=lambda n: (GO.index(SEGS[n]['g']), SEGS[n]['key'], SEGS[n]['k'])))}
out = {
    'groups': GO,
    'segs': [[S['d'], GO.index(S['g']), S['desc'], S['cr'], S['v'], rank[n], allsegfreq[n]] for n, S in enumerate(SEGS)],
    'cols': [[n, colfreq[p]] for p, n in enumerate(order)],
    'inv': {i: [v['name'], v['dialect'], v['src'], v['gc'], v['iso'],
                [[s[0], s[1], s[2]] + ([s[3]] if s[3] >= 0 else []) for s in v['segs']]] for i, v in INV.items()},
    'langs': LANGS,
    'top': [[t[0], t[1], t[2], t[3], t[4], t[5], t[6],
             [j for j in inv if t[5] and meta[j]['Glottocode'] == meta[t[5]]['Glottocode'] and j != t[5]],
             t[7] if len(t) > 7 else (meta[t[5]]['Glottocode'] if t[5] else '')] for t in TOP],
    'notes': NOTES,
    'nlang': len(pick), 'ninv': len(inv), 'thr': THR,
}
def art(S):
    b = ipa.bases(S['k']); mods = ''.join(ch for ch in S['k'] if ipa.is_mod(ch))
    if S['g'] == 'Tone' or not b:
        return ['T']
    if all(x in ipa.V for x in b):
        return ['V', [list(ipa.V[x]) for x in b], mods]
    if all(x in ipa.C for x in b):
        return ['C', [list(ipa.C[x]) + [x] for x in b], mods]
    return ['X']
out['art'] = [art(S) for S in SEGS]
EX = json.load(open(SCRIPTS + '/examples.json', encoding='utf-8'))
out['ex'] = {seg_index[k]: v for k, v in EX.items() if k in seg_index}
if len(sys.argv) > 5:
    out['speakers'] = json.load(open(sys.argv[5], encoding='utf-8'))
PUB = sys.argv[7] if len(sys.argv) > 7 else None   # folder the page is published from; audio files are copied here
import shutil
if len(sys.argv) > 4 and sys.argv[4] != '-':  # reference recordings: seg -> [published path, commons file, author, license]
    AI = json.load(open(sys.argv[4], encoding='utf-8'))
    audio, skipped = {}, []
    for key, a in AI.items():
        if key not in seg_index:
            skipped.append(key); continue
        rel = 'audio/ref/' + os.path.basename(a['path'])
        if PUB:
            os.makedirs(os.path.join(PUB, 'audio/ref'), exist_ok=True); shutil.copy(a['path'], os.path.join(PUB, rel))
        audio[seg_index[key]] = [rel, a['file'], a['artist'], a['license']]
    out['audio'] = audio
    print('audio', len(audio), 'not in any inventory:', skipped)
if len(sys.argv) > 6 and sys.argv[6] != '-':  # example words: seg -> [lang, word, ipa, gloss, path, commons file, author, license]
    W = json.load(open(sys.argv[6], encoding='utf-8'))
    words = {}
    for key, w in W.items():
        if key not in seg_index or not w.get('path'):
            continue
        rel = 'audio/word/' + os.path.basename(w['path'])
        if PUB:
            os.makedirs(os.path.join(PUB, 'audio/word'), exist_ok=True); shutil.copy(w['path'], os.path.join(PUB, rel))
        words[seg_index[key]] = [w['lang'], w['word'], w['ipa'], w.get('gloss', ''), rel, w['audio'], w.get('artist', ''), w.get('license', '')]
    out['words'] = words
    print('words', len(words))
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('langs', len(LANGS), 'cols', len(order), 'segs', len(SEGS), 'threshold', THR)
by = collections.Counter(SEGS[n]['g'] for n in order); print(dict(by))
