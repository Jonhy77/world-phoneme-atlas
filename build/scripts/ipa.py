"""IPA segment normalization and classification for PHOIBLE segments."""
import unicodedata

# ---- consonant base symbols: symbol -> (manner, place, voiced, description) ----
PLACES = ['bilabial', 'labiodental', 'linguolabial', 'dental/alveolar', 'postalveolar', 'retroflex',
          'alveolo-palatal', 'palatal', 'labial-palatal', 'velar', 'labial-velar', 'uvular',
          'pharyngeal', 'epiglottal', 'glottal', 'unspecified']
C = {}
def _c(manner, place, items):
    for sym, voiced in items:
        C[sym] = (manner, place, voiced)

# plosives
_c('Plosive', 'bilabial', [('p', 0), ('b', 1)])
_c('Plosive', 'dental/alveolar', [('t', 0), ('d', 1)])
_c('Plosive', 'retroflex', [('ʈ', 0), ('ɖ', 1)])
_c('Plosive', 'alveolo-palatal', [('ȶ', 0), ('ȡ', 1)])
_c('Plosive', 'palatal', [('c', 0), ('ɟ', 1)])
_c('Plosive', 'velar', [('k', 0), ('ɡ', 1)])
_c('Plosive', 'uvular', [('q', 0), ('ɢ', 1)])
_c('Plosive', 'epiglottal', [('ʡ', 0)])
_c('Plosive', 'glottal', [('ʔ', 0)])
# nasals
_c('Nasal', 'bilabial', [('m', 1)]); _c('Nasal', 'labiodental', [('ɱ', 1)])
_c('Nasal', 'dental/alveolar', [('n', 1)]); _c('Nasal', 'retroflex', [('ɳ', 1)])
_c('Nasal', 'alveolo-palatal', [('ȵ', 1)]); _c('Nasal', 'palatal', [('ɲ', 1)])
_c('Nasal', 'velar', [('ŋ', 1)]); _c('Nasal', 'uvular', [('ɴ', 1)])
_c('Nasal', 'unspecified', [('N', 1)])
# trills
_c('Trill', 'bilabial', [('ʙ', 1)]); _c('Trill', 'dental/alveolar', [('r', 1)]); _c('Trill', 'uvular', [('ʀ', 1)])
# taps / flaps
_c('Tap/Flap', 'labiodental', [('ⱱ', 1)]); _c('Tap/Flap', 'dental/alveolar', [('ɾ', 1), ('ᴅ', 1)])
_c('Tap/Flap', 'retroflex', [('ɽ', 1)])
# fricatives
_c('Fricative', 'bilabial', [('ɸ', 0), ('β', 1)]); _c('Fricative', 'labiodental', [('f', 0), ('v', 1)])
_c('Fricative', 'dental/alveolar', [('θ', 0), ('ð', 1), ('s', 0), ('z', 1)])
_c('Fricative', 'postalveolar', [('ʃ', 0), ('ʒ', 1)]); _c('Fricative', 'retroflex', [('ʂ', 0), ('ʐ', 1)])
_c('Fricative', 'alveolo-palatal', [('ɕ', 0), ('ʑ', 1), ('ʆ', 0), ('ʓ', 1)])
_c('Fricative', 'palatal', [('ç', 0), ('ʝ', 1)]); _c('Fricative', 'velar', [('x', 0), ('ɣ', 1), ('ɧ', 0)])
_c('Fricative', 'labial-velar', [('ʍ', 0)])
_c('Fricative', 'uvular', [('χ', 0), ('ʁ', 1)]); _c('Fricative', 'pharyngeal', [('ħ', 0), ('ʕ', 1)])
_c('Fricative', 'epiglottal', [('ʜ', 0), ('ʢ', 1)]); _c('Fricative', 'glottal', [('h', 0), ('ɦ', 1)])
_c('Lateral fricative', 'dental/alveolar', [('ɬ', 0), ('ɮ', 1)])
# approximants
_c('Approximant', 'labiodental', [('ʋ', 1)]); _c('Approximant', 'dental/alveolar', [('ɹ', 1)])
_c('Approximant', 'retroflex', [('ɻ', 1)]); _c('Approximant', 'palatal', [('j', 1)])
_c('Approximant', 'labial-palatal', [('ɥ', 1)]); _c('Approximant', 'velar', [('ɰ', 1)])
_c('Approximant', 'labial-velar', [('w', 1)])
_c('Lateral approximant', 'dental/alveolar', [('l', 1)]); _c('Lateral approximant', 'retroflex', [('ɭ', 1)])
_c('Lateral approximant', 'alveolo-palatal', [('ȴ', 1)]); _c('Lateral approximant', 'palatal', [('ʎ', 1)])
_c('Lateral approximant', 'velar', [('ʟ', 1)])
_c('Lateral flap', 'dental/alveolar', [('ɺ', 1)])
# implosives & clicks
_c('Implosive', 'bilabial', [('ɓ', 1)]); _c('Implosive', 'dental/alveolar', [('ɗ', 1)])
_c('Implosive', 'retroflex', [('ᶑ', 1)]); _c('Implosive', 'palatal', [('ʄ', 1)])
_c('Implosive', 'velar', [('ɠ', 1)]); _c('Implosive', 'uvular', [('ʛ', 1)])
_c('Click', 'bilabial', [('ʘ', 0)]); _c('Click', 'dental/alveolar', [('ǀ', 0)])
_c('Click', 'postalveolar', [('ǃ', 0)]); _c('Click', 'palatal', [('ǂ', 0)])
_c('Click', 'dental/alveolar', [('ǁ', 0)]); _c('Click', 'retroflex', [('‼', 0)])
_c('Other', 'unspecified', [('R', 1)])

# order of base symbols as they appear on the IPA chart (used for sorting within a place)
CHART_ORDER = {s: i for i, s in enumerate(
    'p b t d ʈ ɖ ȶ ȡ c ɟ k ɡ q ɢ ʡ ʔ m ɱ n ɳ ȵ ɲ ŋ ɴ N ʙ r ʀ ⱱ ɾ ᴅ ɽ ɺ ɸ β f v θ ð s z ʃ ʒ ʂ ʐ ɕ ʑ ʆ ʓ ç ʝ x ɣ ɧ ʍ χ ʁ ħ ʕ ʜ ʢ h ɦ '
    'ɬ ɮ ʋ ɹ ɻ j ɥ ɰ w l ɭ ȴ ʎ ʟ ɓ ɗ ᶑ ʄ ɠ ʛ ʘ ǀ ǃ ǂ ǁ ‼ R'.split())}

# ---- vowels: symbol -> (height idx, backness idx, rounded) ----
HEIGHTS = ['Close', 'Near-close', 'Close-mid', 'Mid', 'Open-mid', 'Near-open', 'Open']
BACKS = ['front', 'central', 'back']
V = {
    'i': (0, 0, 0), 'y': (0, 0, 1), 'ɨ': (0, 1, 0), 'ʉ': (0, 1, 1), 'ɯ': (0, 2, 0), 'u': (0, 2, 1),
    'ɪ': (1, 0, 0), 'ʏ': (1, 0, 1), 'ʊ': (1, 2, 1),
    'e': (2, 0, 0), 'ø': (2, 0, 1), 'ɘ': (2, 1, 0), 'ɵ': (2, 1, 1), 'ɤ': (2, 2, 0), 'o': (2, 2, 1),
    'ə': (3, 1, 0),
    'ɛ': (4, 0, 0), 'œ': (4, 0, 1), 'ɜ': (4, 1, 0), 'ɞ': (4, 1, 1), 'ʌ': (4, 2, 0), 'ɔ': (4, 2, 1),
    'æ': (5, 0, 0), 'ɐ': (5, 1, 0),
    'a': (6, 0, 0), 'ɶ': (6, 0, 1), 'ɑ': (6, 2, 0), 'ɒ': (6, 2, 1),
}
VOWEL_ORDER = {s: i for i, s in enumerate('i y ɨ ʉ ɯ u ɪ ʏ ʊ e ø ɘ ɵ ɤ o ə ɛ œ ɜ ɞ ʌ ɔ æ ɐ a ɶ ɑ ɒ'.split())}

TONE_CHARS = set('˥˦˧˨˩↓')

# The official IPA chart (2020): every symbol gets a column even if rare.
IPA_CHART = ('p b t d ʈ ɖ c ɟ k ɡ q ɢ ʔ m ɱ n ɳ ɲ ŋ ɴ ʙ r ʀ ⱱ ɾ ɽ ɸ β f v θ ð s z ʃ ʒ ʂ ʐ ç ʝ x ɣ χ ʁ ħ ʕ h ɦ '
             'ɬ ɮ ʋ ɹ ɻ j ɰ l ɭ ʎ ʟ ʘ ǀ ǃ ǂ ǁ ɓ ɗ ʄ ɠ ʛ pʼ tʼ kʼ sʼ ʍ w ɥ ʜ ʢ ʡ ɕ ʑ ɺ ɧ '
             'i y ɨ ʉ ɯ u ɪ ʏ ʊ e ø ɘ ɵ ɤ o ə ɛ œ ɜ ɞ ʌ ɔ æ ɐ a ɶ ɑ ɒ').split()

# ---- diacritics ----
# Stripped everywhere: fine phonetic detail of place/tongue position that is not a separate IPA-chart sound.
MINOR_ALWAYS = set('̪̺̻̟̠̘̙̹̜̈̽ˑ͇͓̆̚')
# Raised/lowered: only stripped on vowels (on consonants they change manner, e.g. β̞ = approximant).
RAISE_LOWER = set('̝̞')
NONSYLLABIC = '̯'

MOD_NAMES = {
    '̥': 'voiceless', '̊': 'voiceless', 'ʰ': 'aspirated', 'ʱ': 'breathy-voiced (murmured)',
    '̤': 'breathy-voiced', '̰': 'creaky-voiced', 'ˀ': 'glottalized', '͈': 'fortis (tense)',
    '͉': 'lenis / weak', 'ʷ': 'labialized', 'ʲ': 'palatalized', 'ˠ': 'velarized', 'ˤ': 'pharyngealized',
    'ᶣ': 'labio-palatalized', '̃': 'nasalized', 'ⁿ': 'nasal release', 'ˡ': 'lateral release',
    '̩': 'syllabic', 'ː': 'long', 'ʼ': 'ejective', '˞': 'rhoticized', '̯': 'non-syllabic',
    '̬': 'voiced', '̝': 'raised', '̞': 'lowered', '̼': 'linguolabial',
}
MOD_ORDER = ['̥', '̬', 'ʰ', 'ʱ', '̤', '̰', 'ˀ', '͈', '͉', 'ʷ', 'ᶣ', 'ʲ', 'ˠ', 'ˤ',
             '̃', 'ⁿ', 'ˡ', '̩', '˞', '̝', '̞', '̯', 'ʼ', 'ː']


def is_mod(ch):
    return unicodedata.category(ch) in ('Mn', 'Lm', 'Sk') and ch not in TONE_CHARS


def bases(seg):
    return [ch for ch in seg if not is_mod(ch) and ch not in TONE_CHARS]


def normalize(raw):
    """PHOIBLE segment -> comparable segment (minor place detail stripped)."""
    s = raw  # PHOIBLE is already in its own canonical form (precomposed ç, decomposed diacritics)
    if '|' in s:                      # "t̪|t" = place left unspecified by the source -> the general symbol
        s = s.split('|')[-1]
    s = s.replace('ɫ', 'lˠ').replace('ɚ', 'ə˞').replace('̊', '̥')
    s = ''.join(ch for ch in s if ch not in MINOR_ALWAYS)
    b = bases(s)
    if b and all(x in V for x in b):  # vowels / diphthongs
        s = ''.join(ch for ch in s if ch not in RAISE_LOWER)
        if len(b) > 1:
            s = s.replace(NONSYLLABIC, '')
    return s


def classify(seg):
    """Return (group, subgroup_sort_key tuple, description) for a normalized segment."""
    if seg and all(ch in TONE_CHARS or unicodedata.category(ch) == 'Mn' for ch in seg):
        return 'Tone', (0,), 'tone ' + seg
    b = bases(seg)
    mods = [ch for ch in seg if is_mod(ch)]
    modkey = tuple(sorted(MOD_ORDER.index(m) if m in MOD_ORDER else 99 for m in mods))
    if not b:
        return 'Other', (99,), 'unclassified'
    if all(x in V for x in b):
        if len(b) == 1:
            h, bk, r = V[b[0]]
            return 'Vowel', (h, VOWEL_ORDER[b[0]], len(mods), modkey), vowel_desc(b[0], mods)
        return 'Diphthong', (len(b), VOWEL_ORDER[b[0]], VOWEL_ORDER[b[1]], len(mods), modkey), \
            'vowel sequence ' + ' + '.join(vowel_desc(x, []) for x in b)
    if any(x not in C for x in b):
        return 'Other', (99,), 'contains non-standard symbol'
    info = [C[x] for x in b]
    first = b[0]
    pk = lambda sym: (PLACES.index(C[sym][1]), CHART_ORDER.get(sym, 999))
    key = pk(first) + (tuple(CHART_ORDER.get(x, 999) for x in b[1:]), len(mods), modkey)
    manners = [i[0] for i in info]
    if 'Click' in manners:
        return 'Click', key, cons_desc(b, mods, 'click')
    if 'ʼ' in mods:
        return 'Ejective', key, cons_desc(b, [m for m in mods if m != 'ʼ'], 'ejective')
    if 'Implosive' in manners:
        return 'Implosive', key, cons_desc(b, mods, 'implosive')
    if len(b) == 1:
        m = manners[0]
        if m in ('Fricative', 'Lateral fricative') and '̞' in mods:
            m = 'Approximant'  # lowered fricative = approximant (β̞, ð̞, ɣ̞)
        if m == 'Lateral flap':
            m = 'Tap/Flap'
        return m, key, cons_desc(b, mods)
    obstr = ('Plosive', 'Fricative', 'Lateral fricative')
    if manners[0] == 'Nasal' and len(b) >= 2 and all(x in obstr for x in manners[1:]):
        return 'Prenasalized', key, 'prenasalized ' + cons_desc(b[1:], mods)
    if manners[0] == 'Nasal' and len(b) >= 3 and manners[1] == 'Nasal' and all(x in obstr for x in manners[2:]):
        return 'Prenasalized', key, 'prenasalized ' + cons_desc(b[2:], mods)
    if len(b) == 2 and manners == ['Plosive', 'Plosive'] or (len(b) == 2 and manners == ['Nasal', 'Nasal']):
        return 'Double articulation', key, cons_desc(b, mods, 'doubly-articulated')
    if len(b) == 2 and manners[0] == 'Plosive' and manners[1] in ('Fricative', 'Lateral fricative'):
        return 'Affricate', key, cons_desc(b, mods, 'affricate')
    return 'Other', key, cons_desc(b, mods, 'complex segment')


def mod_words(mods):
    out = []
    for m in mods:
        w = MOD_NAMES.get(m)
        if w and w not in out:
            out.append(w)
    return out


def cons_desc(b, mods, kind=None):
    m0, place, voiced = C[b[0]]
    if kind in ('affricate', 'doubly-articulated', 'complex segment') and len(b) > 1:
        v = 'voiced' if C[b[-1]][2] else 'voiceless'
        places = '-'.join(dict.fromkeys(C[x][1] for x in b))
        if kind == 'affricate':
            core = f"{v} {places} {'lateral ' if C[b[1]][0] == 'Lateral fricative' else ''}affricate"
        elif kind == 'doubly-articulated':
            core = f"{v} {places} {'nasal' if C[b[0]][0] == 'Nasal' else 'plosive'}"
        else:
            core = f"{places} complex segment"
    elif kind == 'click':
        core = f"{place} click" + (' (with accompaniment)' if len(b) > 1 else '')
    elif kind == 'ejective':
        man = {'Plosive': 'plosive', 'Fricative': 'fricative', 'Lateral fricative': 'lateral fricative'}.get(m0, m0.lower())
        if len(b) > 1:
            man = 'affricate'
        core = f"{place} ejective {man}"
    elif kind == 'implosive':
        core = f"voiced {place} implosive" if len(b) == 1 else f"{place} implosive (complex)"
    else:
        v = '' if m0 in ('Nasal', 'Trill', 'Tap/Flap', 'Approximant', 'Lateral approximant', 'Lateral flap') and voiced else \
            ('voiced ' if voiced else 'voiceless ')
        man = m0.lower().replace('tap/flap', 'tap/flap')
        if m0 == 'Lateral flap':
            man = 'lateral flap'
        if m0 in ('Fricative',) and '̞' in mods:
            man = 'approximant'
        core = f"{v}{place} {man}"
    w = mod_words([m for m in mods if not (m == '̞' and m0 == 'Fricative')])
    return core + (', ' + ', '.join(w) if w else '')


def vowel_desc(sym, mods):
    h, bk, r = V[sym]
    core = f"{HEIGHTS[h].lower()} {BACKS[bk]} {'rounded' if r else 'unrounded'} vowel"
    w = mod_words(mods)
    return core + (', ' + ', '.join(w) if w else '')


GROUP_ORDER = ['Plosive', 'Nasal', 'Trill', 'Tap/Flap', 'Fricative', 'Lateral fricative', 'Approximant',
               'Lateral approximant', 'Affricate', 'Ejective', 'Implosive', 'Click', 'Prenasalized',
               'Double articulation', 'Other', 'Vowel', 'Diphthong', 'Tone']


def base_key(seg):
    """Bare base letters, used to find variants of a plain sound (pʰ, pʷ, pː -> p)."""
    return ''.join(bases(seg))


PRENASAL_SUP = {'m': 'ᵐ', 'n': 'ⁿ', 'ŋ': 'ᵑ', 'ɲ': 'ᶮ', 'ɱ': 'ᶬ', 'ɳ': 'ᶯ'}


def display(seg, group):
    """Human-friendly rendering: tie bars on affricates / double articulations, superscript prenasalization."""
    chars = list(seg)
    idx = [i for i, ch in enumerate(chars) if not is_mod(ch) and ch not in TONE_CHARS]
    if group in ('Affricate', 'Double articulation', 'Ejective', 'Implosive', 'Click', 'Other') and len(idx) == 2 \
            and all(chars[i] in C for i in idx):
        # tie bar after the last diacritic of the first base
        j = idx[1]
        return ''.join(chars[:j]) + '͡' + ''.join(chars[j:]) if group != 'Click' else seg
    if group == 'Prenasalized' and chars[0] in PRENASAL_SUP:
        rest = ''.join(chars[1:])
        b = bases(rest)
        if len(b) == 2:
            k = [i for i, ch in enumerate(rest) if not is_mod(ch)][1]
            rest = rest[:k] + '͡' + rest[k:]
        return PRENASAL_SUP[chars[0]] + rest
    return seg
