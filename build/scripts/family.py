"""Family trees (Glottolog) and ancestor chains (Wiktionary language data) for every PHOIBLE language."""
import csv, json, re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')
S = sys.argv[1]
D = json.load(open(S + '/data.json', encoding='utf-8'))

# ---------- Glottolog: names + classification trees (Newick per family) ----------
GL = {r['ID']: r for r in csv.DictReader(open(S + '/data/glottolog_languages.csv', encoding='utf-8'))}
parent = {}
def parse_newick(s):
    stack, i, cur_children = [], 0, []
    # iterative parser: '(' push, ',' sep, ')' close then read label of the closed group
    tok = re.findall(r'\(|\)|,|;|[^(),;]+', s)
    groups = [[]]
    for t in tok:
        if t == '(':
            groups.append([])
        elif t == ',' or t == ';':
            continue
        elif t == ')':
            kids = groups.pop()
            groups[-1].append(('__pending__', kids))
        else:
            label = t.split(':')[0].strip()
            m = re.search(r'([a-z0-9]{4}\d{4})', label)
            gc = m.group(1) if m else label
            last = groups[-1][-1] if groups[-1] else None
            if last and last[0] == '__pending__':
                groups[-1][-1] = (gc, last[1])
                for k in last[1]:
                    parent[k[0]] = gc
            else:
                groups[-1].append((gc, []))
for r in csv.DictReader(open(S + '/data/glottolog_values.csv', encoding='utf-8')):
    if r['Parameter_ID'] == 'subclassification' and r['Value'].strip().startswith('('):
        parse_newick(r['Value'])
def path(gc):
    out, seen = [gc], {gc}
    while out[-1] in parent and parent[out[-1]] not in seen:
        out.append(parent[out[-1]]); seen.add(out[-1])
    return out[::-1]
children = {}
for k, p in parent.items():
    children.setdefault(p, []).append(k)

phoible = {L[2] for L in D['langs']}
lang_desc = {}
def langs_under(n):
    if n in lang_desc: return lang_desc[n]
    out = []
    for k in children.get(n, []):
        if GL.get(k, {}).get('Level') == 'language': out.append(k)
        elif GL.get(k, {}).get('Level') == 'family': out.extend(langs_under(k))
    lang_desc[n] = out
    return out
nodes, paths, rel = {}, {}, {}
def add(n):
    if n in GL and n not in nodes:
        nodes[n] = [GL[n]['Name'], parent.get(n, ''), GL[n]['Level'][:1]]  # level: l(anguage) / f(amily) / d(ialect)
for L in D['langs']:
    gc = L[2]
    p = path(gc)
    paths[gc] = p
    for n in p: add(n)
    # closest relatives: smallest enclosing group with at least 4 other languages (the language itself may be a dialect node)
    me = {gc} | set(p[-2:] if GL.get(gc, {}).get('Level') == 'dialect' else [])
    for anc in reversed(p[:-1]):
        if GL.get(anc, {}).get('Level') != 'family': continue
        others = [x for x in langs_under(anc) if x not in me]
        if len(others) >= 4 or anc == p[0]:
            others.sort(key=lambda x: (x not in phoible, GL[x]['Name']))
            entry = [[anc, others[:40], len(others)]]
            # wider group: next ancestor with at least twice as many languages, listing only the new ones
            i = p.index(anc)
            for anc2 in reversed(p[:i]):
                if GL.get(anc2, {}).get('Level') != 'family': continue
                o2 = [x for x in langs_under(anc2) if x not in me and x not in set(others)]
                if len(o2) + len(others) >= 2 * len(others) and o2:
                    o2.sort(key=lambda x: (x not in phoible, GL[x]['Name']))
                    entry.append([anc2, o2[:40], len(o2)])
                    break
            rel[gc] = entry
            for a, xs, _ in entry:
                add(a)
                for x in xs: add(x)
            break
print('glottolog paths', len(paths), 'nodes', len(nodes), 'isolates/flat', sum(1 for p in paths.values() if len(p) == 1))

# ---------- Wiktionary: languages, etymology languages, families ----------
def blocks(text):
    for m in re.finditer(r'^m\["([^"]+)"\]\s*=\s*\{(.*?)^\}', text, re.S | re.M):
        code, body = m.group(1), m.group(2)
        pos = []
        for line in body.split('\n'):
            s = re.sub(r'\s*--.*$', '', line).strip()
            if not s: continue
            if re.match(r'^[A-Za-z_]+\s*=', s): break
            mm = re.match(r'^("([^"]*)"|-?\d+|nil),?$', s)
            if mm: pos.append(mm.group(2) if mm.group(2) is not None else mm.group(1))
            else: break
        anc = re.search(r'\bancestors\s*=\s*(?:"([^"]+)"|\{([^}]*)\})', body)
        ancs = []
        if anc:
            ancs = [a.strip() for a in (anc.group(1) or '').split(',') if a.strip()] or re.findall(r'"([^"]+)"', anc.group(2) or '')
        proto = re.search(r'\bprotoLanguage\s*=\s*"([^"]+)"', body)
        typ = re.search(r'\btype\s*=\s*"([^"]+)"', body)
        par = re.search(r'\bparent\s*=\s*"([^"]+)"', body)
        yield code, pos, ancs, proto.group(1) if proto else None, typ.group(1) if typ else '', par.group(1) if par else None
W = os.path.join(S, 'data', 'wikt')
LANG, FAM, ETY = {}, {}, {}
for fn in glob.glob(W + '/languages_data_*.lua'):
    for code, pos, ancs, proto, typ, par in blocks(open(fn, encoding='utf-8').read()):
        LANG[code] = {'name': pos[0] if pos else code, 'fam': pos[2] if len(pos) > 2 else None, 'anc': ancs, 'recon': typ == 'reconstructed' or code.endswith('-pro')}
for code, pos, ancs, proto, typ, par in blocks(open(W + '/etymology_languages_data.lua', encoding='utf-8').read()):
    ETY[code] = {'name': pos[0] if pos else code, 'parent': pos[2] if len(pos) > 2 and pos[2] else par, 'anc': ancs, 'recon': typ == 'reconstructed'}
for fn in (W + '/families_data.lua', W + '/families_data_etymology.lua'):
    for code, pos, ancs, proto, typ, par in blocks(open(fn, encoding='utf-8').read()):
        FAM[code] = {'name': pos[0] if pos else code, 'parent': pos[2] if len(pos) > 2 else None, 'proto': proto}
print('wiktionary languages', len(LANG), 'etymology languages', len(ETY), 'families', len(FAM))

def info(code):
    return LANG.get(code) or ETY.get(code)
def fam_of(code):
    if code in LANG: return LANG[code]['fam']
    if code in ETY:
        p = ETY[code]['parent']
        return fam_of(p) if p and p != code else None
def proto_of(fam):
    f = FAM.get(fam)
    if not f: return None
    if f['proto']: return f['proto']
    return fam + '-pro' if fam + '-pro' in LANG else None
def ancestor(code, seen):
    i = info(code)
    if not i: return None
    for a in i['anc']:
        if a not in seen and info(a): return a
    if code in ETY and ETY[code]['parent'] and ETY[code]['parent'] not in seen and info(ETY[code]['parent']):
        return ETY[code]['parent']   # e.g. Sauraseni Apabhramsa -> Apabhramsa
    # no usable explicit ancestor: climb the family tree to the nearest proto-language not yet visited
    fam = fam_of(code)
    hops = 0
    while fam and hops < 25:
        p = proto_of(fam)
        if p and p not in seen and info(p):
            return p
        fam = FAM.get(fam, {}).get('parent'); hops += 1
    return None
def chain(code):
    out, seen = [], {code}
    c = code
    while True:
        a = ancestor(c, seen)
        if not a or a in seen or not info(a): break
        seen.add(a); i = info(a)
        out.append([i['name'], a, 1 if (i.get('recon') or a.endswith('-pro') or i['name'].startswith('Proto-')) else 0])
        c = a
        if len(out) > 14: break
    return out

# ISO 639-3 -> Wiktionary code (639-1 where Wiktionary uses it; macrolanguage fallback)
P1, MACRO = {}, {}
for r in csv.DictReader(open(S + '/data/iso639-3.tab', encoding='utf-8'), delimiter='\t'):
    if r['Part1']: P1[r['Id']] = r['Part1']
if os.path.exists(S + '/data/iso639-3-macro.tab'):
    for r in csv.DictReader(open(S + '/data/iso639-3-macro.tab', encoding='utf-8'), delimiter='\t'):
        MACRO[r['I_Id']] = r['M_Id']
def wcode(iso):
    for c in (P1.get(iso), iso, P1.get(MACRO.get(iso, '')), MACRO.get(iso)):
        if c and c in LANG: return c
    return None
anc, wnames = {}, {}
for L in D['langs']:
    c = wcode(L[1])
    if not c: continue
    ch = chain(c)
    if ch:
        anc[L[2]] = ch
        wnames[L[2]] = [LANG[c]['name'], c]
print('ancestor chains', len(anc))
for name in ['French', 'German', 'Italian', 'Bengali', 'Persian', 'Vietnamese', 'Thai', 'Hausa', 'Amharic', 'Georgian', 'Finnish', 'Zulu', 'Navajo', 'Quechua', 'Portuguese (European)', 'English', 'Hindi', 'Japanese', 'Spanish', 'Russian', 'Hungarian', 'Swahili', 'Arabic', 'Standard Chinese; Mandarin', 'Tamil', 'Turkish', 'Korean']:
    for L in D['langs']:
        if L[0] == name:
            print(name, '->', ' ← '.join(('*' if x[2] else '') + x[0] for x in anc.get(L[2], [])) or '(none)', '| glottolog:', ' › '.join(nodes[n][0] for n in paths[L[2]] if n in nodes))
json.dump({'nodes': nodes, 'paths': paths, 'anc': anc, 'wname': wnames, 'rel': rel}, open(S + '/data/family.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
