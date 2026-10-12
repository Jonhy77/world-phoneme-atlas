import csv, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8')))
L1, L2 = 'Q36870', 'Q125421'
by = collections.defaultdict(list)
for r in rows:
    if r['rank'].endswith('Deprecated') or not r['n'][:1].isdigit(): continue
    part = r['part'].split('/')[-1]
    if part not in ('', L1): continue
    key = r['item'].split('/')[-1]
    by[key].append((r['rank'].endswith('PreferredRank'), part == L1, r['date'][:10], float(r['n']), r['iso'], r['glotto']))
best = {}
for item, st in by.items():
    pref, l1, date, n, iso, gl = max(st, key=lambda x: (x[1], x[0], x[2]))
    rec = {'n': int(n), 'year': date[:4], 'item': item, 'l1': l1}
    for s in st:
        if s[4]: best.setdefault(('iso', s[4]), rec)
        if s[5]: best.setdefault(('gl', s[5]), rec)
D = json.load(open(sys.argv[2], encoding='utf-8'))
out = {}
for L in D['langs']:
    rec = best.get(('iso', L[1])) or best.get(('gl', L[2]))
    if not rec: continue
    if not rec['l1'] and rec['n'] > 20_000_000: continue   # unqualified big figures are usually L1+L2 totals
    if L[2] == 'panj1256': continue                         # Wikidata figure covers all of Punjabi, not Eastern Punjabi only
    out[L[2]] = [rec['n'], rec['year'], rec['item'], 'wd']
# top 30: Ethnologue 2026 L1 figures (millions) replace Wikidata; MSA has no native speakers
for t in D['top']:
    gc = t[8] if len(t) > 8 and t[8] else D['inv'][t[5]][3]
    if t[1] == 'Western Punjabi': continue
    if t[2] is None: continue
    out[gc] = [int(t[2] * 1_000_000), '2026', '', 'eth'] if t[2] > 0 else [0, '2026', '', 'eth']
json.dump(out, open(sys.argv[3], 'w', encoding='utf-8'))
print('matched', len(out))
for name in ['English','Spanish','Hindi','French','German','Japanese','Russian','Turkish','Korean','Thai','Hausa','Swahili','Tagalog','Amharic','Vietnamese','Portuguese (European)','Bengali','Tamil','Telugu','Marathi']:
    for L in D['langs']:
        if L[0] == name: print(name, out.get(L[2]))
