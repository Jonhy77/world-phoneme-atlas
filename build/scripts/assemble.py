import sys, os, json
S = sys.argv[1]
t = open(f'{S}/template2.html', encoding='utf-8').read()
dd = json.load(open(f'{S}/data.json', encoding='utf-8'))
if os.path.exists(f'{S}/data/family.json'):
    dd['fam'] = json.load(open(f'{S}/data/family.json', encoding='utf-8'))
d = json.dumps(dd, ensure_ascii=False, separators=(',', ':')).replace('</', r'<\/')
a = open(f'{S}/artic.js', encoding='utf-8').read()
assert '</script' not in a
out = t.replace('__ARTIC__', a).replace('__DATA__', d)
dest = sys.argv[2] if len(sys.argv) > 2 else f'{S}/world-phoneme-atlas.html'
open(dest, 'w', encoding='utf-8').write(out)
print(len(out.encode('utf-8')) // 1024, 'KB')
