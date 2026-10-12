"""Verify example words on English Wiktionary: the word's IPA (for that language) must contain the target sound,
and the entry must have an audio recording."""
import json, re, sys, time, html, urllib.parse, urllib.request, urllib.error, os
UA = {'User-Agent': 'PhonemeAtlasBuilder/1.0 (personal research)'}
CACHE = None

def _get(url):
    for attempt in range(8):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(4 * (attempt + 1)); continue
            raise
    raise RuntimeError('rate limited: ' + url)

def page_html(word, cache_dir):
    fn = os.path.join(cache_dir, urllib.parse.quote(word, safe='') + '.html')
    if os.path.exists(fn):
        return open(fn, encoding='utf-8').read()
    u = 'https://en.wiktionary.org/w/api.php?' + urllib.parse.urlencode({'action': 'parse', 'page': word, 'prop': 'text', 'format': 'json', 'formatversion': 2, 'redirects': 1})
    d = json.loads(_get(u))
    t = d.get('parse', {}).get('text', '') if 'error' not in d else ''
    open(fn, 'w', encoding='utf-8').write(t)
    time.sleep(0.4)
    return t

def section(t, lang):
    # split on level-2 headings
    parts = re.split(r'<div class="mw-heading mw-heading2">|<h2', t)
    for p in parts:
        m = re.search(r'id="([^"]+)"', p[:300])
        if m and m.group(1).replace('_', ' ') == lang:
            return p
    return ''

def ipas(sec):
    return [html.unescape(re.sub(r'<[^>]+>', '', m)) for m in re.findall(r'<span class="IPA[^"]*"[^>]*>(.*?)</span>', sec)]

def audios(sec):
    files = re.findall(r'data-mwtitle="([^"]+\.(?:ogg|oga|wav|mp3|opus|flac|webm))"', sec)
    files += [urllib.parse.unquote(x) for x in re.findall(r'href="/wiki/File:([^"#?]+\.(?:ogg|oga|wav|mp3|opus|flac|webm))"', sec)]
    out = []
    for f in files:
        f = html.unescape(f).replace(' ', '_')
        if f not in out:
            out.append(f)
    return out

# ---- matching ----
MINOR = set('̪̺̻̟̠̘̙̹̜̈̽ˑ͇͓̯̆̚')
SEP = set('ˈˌ.‿ /[]()-|‖ ,')
TIE = set('͜͡')
EQUIV = [('ɫ', 'lˠ'), ('ɚ', 'ə˞'), ('g', 'ɡ'), ('ʱ', '̤'), ('̊', '̥'), ('ʦ', 't͡s'), ('ʧ', 't͡ʃ'), ('ʤ', 'd͡ʒ'), ('ʣ', 'd͡z'), ('ʨ', 't͡ɕ'), ('ʥ', 'd͡ʑ'), ('ɝ', 'ɜ˞')]

def norm(s):
    s = unicodedata.normalize('NFD', s)
    for a, b in EQUIV:
        s = s.replace(a, b)
    # breathy: move ̤ written as ʱ after the consonant onto the consonant -> both forms become C + U+0324
    return ''.join(ch for ch in s if ch not in MINOR)

import unicodedata
def is_mod(ch):
    return unicodedata.category(ch) in ('Mn', 'Lm', 'Sk') and ch not in TIE and ch not in 'ˈˌ'

def contains(ipa, target_forms):
    """True if any target form occurs in ipa as a whole segment."""
    s = norm(ipa)
    for tf in target_forms:
        tf = norm(tf)
        i = s.find(tf)
        while i >= 0:
            before = s[i - 1] if i > 0 else ' '
            after = s[i + len(tf)] if i + len(tf) < len(s) else ' '
            ok = before not in TIE and after not in TIE and not is_mod(after)
            # a lone stop must not be the first half of an untied affricate written in the same source style? (keep simple)
            if ok:
                return True
            i = s.find(tf, i + 1)
    return False

def forms(key):
    """Spellings of a normalized PHOIBLE key as Wiktionary might write it."""
    out = {key}
    # affricates / doubles without tie bar in our keys: add tied versions
    b = [i for i, ch in enumerate(key) if not is_mod(ch)]
    if len(b) == 2:
        out.add(key[:b[1]] + '͡' + key[b[1]:])
    out.add(key.replace('̤', 'ʱ'))
    VOW = set('iyɨʉɯuɪʏʊeøɘɵɤoəɛœɜɞʌɔæɐaɶɑɒ')
    if key.endswith('ː') and len(b) >= 1 and key[0] not in VOW:  # geminates are often written doubled: pp, p.p, tt͡ʃ, t.t͡ʃ
        base = key[:-1]
        first = base[:b[1]] if len(b) == 2 else base
        tied = base[:b[1]] + '͡' + base[b[1]:] if len(b) == 2 else base
        for mid in ('', '.'):
            out.add(first + mid + base); out.add(first + mid + tied)
    return out

# ---- strict matching for multi-part sounds ----
SUPN = {'m': 'ᵐ', 'n': 'ⁿ', 'ŋ': 'ᵑ', 'ɲ': 'ᶮ', 'ɱ': 'ᶬ', 'ɳ': 'ᶯ'}
MINOR_KEEP_NS = MINOR - {'\u032F'}

def _norm_keep_ns(s):
    s = unicodedata.normalize('NFD', s)
    for a, b in EQUIV:
        s = s.replace(a, b)
    return ''.join(ch for ch in s if ch not in MINOR_KEEP_NS)

def contains_strict(ipa, key, group, lang=''):
    key = unicodedata.normalize('NFD', key)
    bases_idx = [i for i, ch in enumerate(key) if not is_mod(ch)]
    if group == 'Diphthong':
        v1, v2 = key[bases_idx[0]], key[bases_idx[1]]
        s = _norm_keep_ns(ipa)
        for f in (v1 + v2 + '\u032F', v1 + '\u032F' + v2):
            i = s.find(f)
            while i >= 0:
                after = s[i + len(f)] if i + len(f) < len(s) else ' '
                if not is_mod(after):
                    return True
                i = s.find(f, i + 1)
        return False
    if group == 'Prenasalized':
        n, rest = key[0], key[1:]
        fs = set()
        if n in SUPN:
            fs.add(SUPN[n] + rest); fs.add(n + '\u0361' + rest)
            rb = [i for i, ch in enumerate(rest) if not is_mod(ch)]
            if len(rb) == 2: fs.add(SUPN[n] + rest[:rb[1]] + '\u0361' + rest[rb[1]:])
        return contains(ipa, fs)
    if len(bases_idx) == 2 and group in ('Affricate', 'Double articulation', 'Ejective', 'Implosive', 'Other'):
        tied = key[:bases_idx[1]] + '\u0361' + key[bases_idx[1]:]
        fs = {tied}
        if key.endswith('ː'):
            base = tied[:-1]; first = key[:bases_idx[1]]
            fs |= {first + base, first + '.' + base}
        return contains(ipa, fs)
    return contains(ipa, forms(key))

# ---- audio file must belong to the word's language ----
LCODES = {'English': ('en', 'eng'), 'Hindi': ('hi', 'hin'), 'Russian': ('ru', 'rus'), 'Swahili': ('sw', 'swa', 'swh'), 'Spanish': ('es', 'spa'),
          'Italian': ('it', 'ita'), 'Georgian': ('ka', 'kat'), 'German': ('de', 'deu'), 'French': ('fr', 'fra'), 'Persian': ('fa', 'fas', 'pes'),
          'Portuguese': ('pt', 'por'), 'Korean': ('ko', 'kor'), 'Welsh': ('cy', 'cym'), 'Malagasy': ('mg', 'mlg', 'plt'), 'Polish': ('pl', 'pol'),
          'Icelandic': ('is', 'isl'), 'Navajo': ('nv', 'nav'), 'Arabic': ('ar', 'ara', 'arb'), 'Swedish': ('sv', 'swe'), 'Bengali': ('bn', 'ben'),
          'Amharic': ('am', 'amh'), 'Thai': ('th', 'tha'), 'Vietnamese': ('vi', 'vie'), 'Hungarian': ('hu', 'hun'), 'Malayalam': ('ml', 'mal'),
          'Japanese': ('ja', 'jpn'), 'Dutch': ('nl', 'nld'), 'Czech': ('cs', 'ces'), 'Tamil': ('ta', 'tam'), 'Mandarin': ('zh', 'cmn', 'zho'),
          'Danish': ('da', 'dan'), 'Irish': ('ga', 'gle'), 'Armenian': ('hy', 'hye'), 'Turkish': ('tr', 'tur'), 'Finnish': ('fi', 'fin'),
          'Ewe': ('ee', 'ewe'), 'Hausa': ('ha', 'hau'), 'Zulu': ('zu', 'zul'), 'Catalan': ('ca', 'cat'), 'Greek': ('el', 'ell'),
          'Ukrainian': ('uk', 'ukr'), 'Galician': ('gl', 'glg'), 'Hebrew': ('he', 'heb'), 'Yoruba': ('yo', 'yor'), 'Urdu': ('ur', 'urd'),
          'Marathi': ('mr', 'mar'), 'Norwegian Bokmål': ('nb', 'nob', 'no')}

def audio_ok(lang, word, fn):
    f = fn.replace(' ', '_')
    m = re.match(r'LL-Q\d+_\(([a-z]{2,3})\)', f)
    codes = LCODES.get(lang, ())
    if m:
        return m.group(1) in codes
    m = re.match(r'([A-Za-z]{2,3})-', f)
    if m and m.group(1).lower() in codes:
        return True
    plain = lambda s: ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').replace(' ', '_')
    return plain(word) in plain(f)
