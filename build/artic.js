// Schematic midsagittal articulation animator. Face looks left. Coordinates in a 250x210 viewBox.
window.Artic = (() => {
  const REST = [[61, 111], [72, 104], [92, 97], [115, 94], [136, 98], [152, 112], [157, 136], [150, 154]];
  const FLOOR = [[124, 148], [94, 134], [68, 121]];
  // tongue targets per place: [index, x, y, weight]
  const TGT = {
    dental: [[0, 55, 99, 1], [1, 70, 100, .4]],
    alveolar: [[0, 65, 87, 1], [1, 76, 96, .5]],
    postalveolar: [[1, 77, 81, 1], [0, 67, 90, .9], [2, 94, 90, .4]],
    retroflex: [[0, 84, 79, 1], [1, 73, 96, .6]],
    'alveolo-palatal': [[1, 80, 80, 1], [2, 97, 75, 1], [0, 61, 104, .5]],
    palatal: [[2, 104, 74, 1], [3, 120, 77, .8], [1, 82, 90, .3]],
    velar: [[4, 141, 79, 1], [3, 124, 83, .6]],
    uvular: [[4, 151, 95, 1], [5, 159, 106, .6]],
    pharyngeal: [[5, 165, 122, 1], [6, 167, 140, 1]],
    epiglottal: [[6, 166, 140, .7], [5, 163, 122, .5]],
    linguolabial: [[0, 46, 104, 1]],
  };
  const PLACE_NAME = {
    bilabial: ['both lips', 'each other'], labiodental: ['lower lip', 'the upper teeth'], linguolabial: ['tongue tip', 'the upper lip'],
    dental: ['tongue tip', 'the back of the upper teeth'], alveolar: ['tongue tip', 'the alveolar ridge (the bump behind the upper teeth)'],
    postalveolar: ['tongue blade', 'the area just behind the alveolar ridge'], retroflex: ['curled-back tongue tip', 'the roof of the mouth behind the alveolar ridge'],
    'alveolo-palatal': ['tongue blade and front', 'the front of the hard palate'], palatal: ['middle of the tongue', 'the hard palate'],
    velar: ['back of the tongue', 'the soft palate (velum)'], uvular: ['back of the tongue', 'the uvula'],
    pharyngeal: ['tongue root', 'the back wall of the throat'], epiglottal: ['epiglottis', 'the back wall of the throat'], glottal: ['vocal folds', 'each other'],
  };
  const lerp = (a, b, t) => a + (b - a) * t;
  const ease = t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  const clone = s => ({ ...s, T: s.T.map(p => p.slice()), fx: s.fx });
  const rest = () => ({ T: REST.map(p => p.slice()), jaw: 3, lip: 9, prot: 0, ld: 0, ldGap: 0, vel: 0, epi: 0, lar: 0, glot: .2, voice: 0, mid: 0 });

  function placeOf(b) {  // b = [manner, place, voiced, sym]
    let p = b[1];
    if (p === 'dental/alveolar') p = (b[3] === 'θ' || b[3] === 'ð' || b[3] === 'ǀ') ? 'dental' : 'alveolar';
    if (p === 'unspecified') p = 'alveolar';
    if (b[3] === 'ǃ') p = 'postalveolar';
    return p;
  }
  function moveTongue(s, targets, gap, horiz) {
    const done = new Set(targets.map(t => t[0]));
    for (const [i, x, y, w] of targets) {
      const tx = horiz ? x - gap : x, ty = horiz ? y : y + gap;
      const dx = (tx - s.T[i][0]) * w, dy = (ty - s.T[i][1]) * w;
      s.T[i][0] += dx; s.T[i][1] += dy;
      for (const [o, f] of [[-1, .35], [1, .35], [-2, .12], [2, .12]]) {
        const j = i + o; if (j < 0 || j > 7 || done.has(j)) continue;
        s.T[j][0] += dx * f; s.T[j][1] += dy * f;
      }
    }
  }
  // articulate one consonant base into state s; returns info used for effects and text
  function constrict(s, b, gap) {
    const place = placeOf(b), info = { place, at: null };
    if (b[1] === 'labial-velar') {
      moveTongue(s, TGT.velar, gap);
      if (gap > 4) { s.lip = 5; s.prot = 5; } else s.lip = gap;
      info.at = [46, 106]; info.place = 'labial-velar'; return info;
    }
    if (b[1] === 'labial-palatal') { moveTongue(s, TGT.palatal, gap); s.lip = 5; s.prot = 5; info.at = [104, 76]; return info; }
    if (place === 'bilabial') { s.lip = gap; info.at = [42, 106]; return info; }
    if (place === 'labiodental') { s.ld = 1; s.ldGap = gap; s.lip = 12; info.at = [52, 104]; return info; }
    if (place === 'glottal') { info.at = [162, 182]; return info; }
    if (place === 'epiglottal') { s.epi = 1; moveTongue(s, TGT.epiglottal, 0); info.at = [166, 148]; return info; }
    const tg = TGT[place];
    if (!tg) return info;
    moveTongue(s, tg, gap, place === 'pharyngeal');
    if (place === 'uvular') s.vel = .55;
    info.at = [tg[0][1], tg[0][2]];
    return info;
  }
  const GAP = { Plosive: 0, Nasal: 0, Trill: 0, 'Tap/Flap': 0, Fricative: 2.6, 'Lateral fricative': 0, Approximant: 6.5,
    'Lateral approximant': 0, 'Lateral flap': 0, Implosive: 0, Click: 0 };

  function applyMods(s, mods) {
    if (mods.includes('ʷ') || mods.includes('ᶣ')) { if (s.lip > 4) s.lip = 4.5; s.prot = 5; }
    if (mods.includes('ʲ') || mods.includes('ᶣ')) moveTongue(s, [[2, 104, 80, .7]], 0);
    if (mods.includes('ˠ')) moveTongue(s, [[4, 140, 88, .7]], 0);
    if (mods.includes('ˤ')) moveTongue(s, [[5, 163, 124, .8], [6, 165, 142, .8]], 0);
    if (mods.includes('̃')) s.vel = 1;
  }
  function phonation(s, voiced, mods) {
    if (mods.includes('̥')) voiced = 0;
    if (mods.includes('̬')) voiced = 1;
    s.glot = voiced ? .85 : .15; s.voice = voiced ? 1 : 0;
    if (mods.includes('̤') || mods.includes('ʱ')) { s.glot = .55; s.voice = 1; }
    if (mods.includes('̰')) { s.glot = .95; s.voice = .5; }
    return voiced;
  }

  function vowelState(v, mods) {
    const [h, bk, r] = v, s = rest();
    s.jaw = 1 + h * 1.8;
    s.T = s.T.map(([x, y], i) => [x, y + s.jaw * .45]);
    const x = 98 + bk * 21, y = 80 + h * 4.3;
    const tg = bk === 0 ? [[2, x, y, 1], [3, x + 18, y + 3, .7]] : bk === 1 ? [[3, x, y, 1], [2, x - 20, y + 4, .5], [4, x + 20, y + 4, .5]] : [[4, x, y, 1], [3, x - 20, y + 2, .6]];
    moveTongue(s, tg, 0);
    if (h >= 4 && bk === 2) moveTongue(s, [[5, 160 + h * .4, 118, .6], [6, 163, 140, .5]], 0);
    if (r) { s.lip = 4 + h * .9; s.prot = 5 - h * .3; } else { s.lip = 7 + h * 1.6; s.prot = -1; }
    s.glot = .85; s.voice = 1;
    applyMods(s, mods);
    if (mods.includes('̤')) { s.glot = .55; }
    if (mods.includes('̰')) { s.glot = .95; s.voice = .5; }
    if (mods.includes('̥')) { s.glot = .15; s.voice = 0; }
    return s;
  }

  // ---------- plan: list of {t, s, fx} keyframes over one loop ----------
  function plan(art, group) {
    const R = rest();
    const keys = [];
    const K = (t, s, fx) => keys.push({ t, s, fx: fx || {} });
    const long = art[2] && art[2].includes('ː');
    if (art[0] === 'V') {
      const vs = art[1].map((v, i) => vowelState(v, i === 0 ? art[2] : ''));
      const fx = { oral: 1, nasal: art[2].includes('̃') };
      if (vs.length === 1) { K(0, R); K(.22, vs[0], fx); K(long ? .86 : .72, vs[0], fx); K(1, R); }
      else { const step = .6 / vs.length; K(0, R); vs.forEach((v, i) => { K(.18 + i * step, v, fx); K(.18 + i * step + step * .45, v, fx); }); K(.9, R); K(1, R); }
      return keys;
    }
    if (art[0] !== 'C') { K(0, R); K(1, R); return keys; }
    const B = art[1], mods = art[2] || '';
    const manner = B[0][0];
    const ejective = mods.includes('ʼ'), asp = mods.includes('ʰ');
    const holdEnd = long ? .7 : .58;

    if (group === 'Click' || B.some(b => b[0] === 'Click')) {
      const ck = B.find(b => b[0] === 'Click'), acc = B.find(b => b[0] !== 'Click');
      const s1 = clone(R); s1.jaw = 2;
      moveTongue(s1, TGT.velar, 0);
      const front = ck[3] === 'ʘ' ? 'bilabial' : ck[3] === 'ǂ' ? 'palatal' : ck[3] === '‼' ? 'retroflex' : ck[3] === 'ǀ' ? 'dental' : 'alveolar';
      if (front === 'bilabial') s1.lip = 0; else moveTongue(s1, front === 'palatal' ? [[1, 82, 79, 1], [2, 100, 75, 1]] : TGT[front], 0);
      const voiced = acc && (acc[2] || acc[0] === 'Nasal');
      s1.glot = voiced ? .85 : .15; s1.voice = voiced ? 1 : 0;
      if (acc && acc[0] === 'Nasal') s1.vel = 1;
      const s2 = clone(s1); s2.T[2][1] += 7; s2.T[3][1] += 6;  // hollow: lower the middle of the tongue
      const s3 = clone(s2);
      if (front === 'bilabial') s3.lip = 9; else { s3.T[0] = [61, 108]; s3.T[1] = [72, 103]; if (front === 'palatal') s3.T[2] = [92, 100]; }
      const at = front === 'bilabial' ? [42, 106] : front === 'palatal' ? [96, 78] : [64, 92];
      K(0, R); K(.25, s1, { nasal: s1.vel > .5 }); K(.42, s1, { nasal: s1.vel > .5 }); K(.55, s2, { vacuum: at, nasal: s1.vel > .5 });
      K(.62, s3, { inward: at, lateral: ck[3] === 'ǁ' }); K(.74, R); K(1, R);
      return keys;
    }

    const pose = (b, gap) => { const s = clone(R); s.jaw = 2; const info = constrict(s, b, gap); return [s, info]; };

    if (group === 'Prenasalized') {
      const oral = B[B.length - 1], stopB = B.length > 2 ? B[B.length - 2] : oral;
      const [s, info] = pose(B[1], 0);
      if (B.length > 2) constrict(s, B[2], 0);
      phonation(s, oral[2], mods); s.vel = 1;
      const s2 = clone(s); s2.vel = 0;
      K(0, R); K(.24, s, { nasal: 1 }); K(.44, s, { nasal: 1 }); K(.52, s2, {}); K(.6, s2, { burst: info.at, oral: 1 }); K(.72, R); K(1, R);
      return keys;
    }

    if (group === 'Double articulation') {
      const [s, info] = pose(B[0], 0); constrict(s, B[1], 0);
      const nas = B[0][0] === 'Nasal'; if (nas) s.vel = 1;
      phonation(s, B[1][2] || nas, mods);
      K(0, R); K(.28, s, { nasal: nas }); K(holdEnd, s, { burst: info.at, oral: 1, nasal: nas }); K(.72, R); K(1, R);
      return keys;
    }

    if (group === 'Affricate' || (B.length === 2 && ejective)) {
      const [s1, i1] = pose(B[0], 0);
      const fricGap = B[1][0] === 'Lateral fricative' ? 0 : 2.6;
      const s2 = clone(R); s2.jaw = 2; const i2 = constrict(s2, B[1], fricGap);
      phonation(s1, B[0][2], mods); phonation(s2, B[1][2], mods);
      applyMods(s1, mods); applyMods(s2, mods);
      if (ejective) { s1.glot = s2.glot = 1; s1.voice = s2.voice = 0; s1.lar = s2.lar = -8; }
      const lat = B[1][0] === 'Lateral fricative';
      K(0, R); K(.26, s1, { ej: ejective }); K(.44, s1, { burst: i1.at }); K(.5, s2, { fric: i2.at, oral: !ejective, lateral: lat });
      K(holdEnd + .12, s2, asp ? { asp: 1, oral: 1 } : {}); K(.84, R); K(1, R);
      return keys;
    }

    // single consonant
    const b = B[0];
    let m = b[0];
    if (m === 'Fricative' && mods.includes('̞')) m = 'Approximant';
    const gap = GAP[m] != null ? GAP[m] : 0;
    const [s, info] = pose(b, gap);
    const voiced = phonation(s, b[2], mods);
    applyMods(s, mods);
    if (b[3] === 'ʔ') { s.glot = 1; s.voice = 0; }
    if (b[3] === 'h') { s.glot = .25; s.voice = 0; }
    if (b[3] === 'ɦ') { s.glot = .55; s.voice = 1; }
    if (m === 'Nasal') s.vel = 1;
    if (b[3] === 'ʜ' || b[3] === 'ʢ') s.epi = 1;
    if (ejective) { s.glot = 1; s.voice = 0; s.lar = -8; }
    if (m === 'Implosive') { s.lar = 7; }
    const lateral = m === 'Lateral fricative' || m === 'Lateral approximant' || b[3] === 'ɺ';
    const hold = {};
    if (m === 'Nasal') { hold.nasal = 1; }
    if (m === 'Fricative' || m === 'Lateral fricative') { hold.fric = b[1] === 'glottal' ? [164, 172] : info.at; hold.oral = 1; }
    if (m === 'Approximant' || m === 'Lateral approximant') hold.oral = 1;
    if (m === 'Trill') hold.trill = info.place;
    if (lateral) hold.lateral = 1;
    if (s.vel > .6) hold.nasal = 1;
    if (ejective) hold.ej = 1;
    if (m === 'Implosive') hold.imp = 1;
    if (m === 'Tap/Flap' || m === 'Lateral flap') {
      K(0, R); K(.38, R); K(.46, s, hold); K(.5, s, hold); K(.58, R); K(1, R);
      return keys;
    }
    const stop = m === 'Plosive' || m === 'Implosive' || (m === 'Nasal' && false);
    K(0, R); K(.28, s, hold);
    if (stop || ejective) {
      const after = clone(R); after.jaw = 3;
      if (asp) { after.glot = .15; after.voice = 0; }
      K(holdEnd, s, { burst: info.at, inward: m === 'Implosive' ? info.at : null, oral: !ejective && m !== 'Implosive', ej: ejective });
      K(holdEnd + .1, after, asp ? { asp: 1, oral: 1 } : {}); K(asp ? .84 : .76, R); K(1, R);
    } else {
      K(holdEnd + .1, s, {}); K(.84, R); K(1, R);
    }
    return keys;
  }

  // ---------- text ----------
  function describe(art, group, desc) {
    if (art[0] === 'T') return ['A tone: a pitch pattern on a syllable that changes word meaning.'];
    if (art[0] === 'X') return [];
    const mods = art[2] || '', out = [];
    if (art[0] === 'V') {
      const H = ['high (close)', 'near-high', 'mid-high (close-mid)', 'mid', 'mid-low (open-mid)', 'near-low', 'low (open)'];
      const Bk = ['front', 'central', 'back'];
      if (art[1].length > 1) out.push(`A diphthong: the tongue glides from one vowel position to another within a single syllable.`);
      for (const v of art[1].slice(0, 1)) out.push(`The tongue body is ${H[v[0]]} and ${Bk[v[1]]} in the mouth. The jaw is ${v[0] <= 1 ? 'nearly closed' : v[0] >= 5 ? 'wide open' : 'half open'}.`);
      out.push(art[1][0][2] ? 'The lips are rounded and pushed forward.' : 'The lips are spread or relaxed, not rounded.');
      out.push('The vocal folds vibrate, and air flows freely through the mouth.');
    } else {
      const B = art[1], b = B[0];
      const pl = placeOf(b), [act, pas] = PLACE_NAME[pl] || ['tongue', 'the roof of the mouth'];
      const voiced = (b[2] && !mods.includes('̥')) || mods.includes('̬');
      const m = b[0];
      if (group === 'Click' || B.some(x => x[0] === 'Click')) {
        out.push('Make a closure with the back of the tongue against the soft palate and a second closure further forward.');
        out.push('Lower the middle of the tongue to create a small vacuum between the two closures, then release the front closure: air rushes in with a sharp pop (velaric ingressive airstream).');
        if (B.length > 1) out.push('The accompanying sound (nasal, voicing, aspiration) is made at the same time through the nose or throat.');
      } else if (mods.includes('ʼ')) {
        out.push(`Close the ${act} against ${pas} and close the vocal folds at the same time.`);
        out.push('Raise the larynx like a piston to compress the trapped air, then release the oral closure with a sharp pop. No air comes from the lungs (glottalic egressive airstream).');
      } else if (m === 'Implosive') {
        out.push(`Close the ${act} against ${pas}.`);
        out.push('Lower the larynx while the vocal folds vibrate. This briefly lowers the air pressure in the mouth, so air is pulled inward at the release (glottalic ingressive airstream).');
      } else if (group === 'Prenasalized') {
        out.push(`Close the mouth at the place of the following stop with the soft palate lowered, so a short nasal comes first.`);
        out.push('Then raise the soft palate and release the closure as an ordinary stop, all as one sound.');
      } else if (group === 'Double articulation') {
        const [a2, p2] = PLACE_NAME[placeOf(B[1])] || ['', ''];
        out.push(`Make two closures at the same time: ${act} against ${pas}, and ${a2} against ${p2}.`);
        out.push('Release both together.');
      } else if (group === 'Affricate') {
        const [a2, p2] = PLACE_NAME[placeOf(B[1])] || [act, pas];
        out.push(`Start like a stop: close the ${act} against ${pas}.`);
        out.push(`Release it slowly into a fricative, with the ${a2} near ${p2} leaving a narrow gap.`);
      } else if (pl === 'glottal') {
        if (b[3] === 'ʔ') out.push('Close the vocal folds tightly to stop the airflow, then release them suddenly.');
        else out.push(`Air passes through the open glottis with some friction${b[3] === 'ɦ' ? ', while the vocal folds vibrate in a breathy way' : ''}. The mouth is shaped for the neighbouring vowel.`);
      } else {
        const T = {
          Plosive: `Block the airflow completely with the ${act} against ${pas}, let air pressure build up, then release it suddenly.`,
          Nasal: `Close the ${act} against ${pas} and lower the soft palate, so the air flows out through the nose.`,
          Trill: `Hold the ${act} loosely near ${pas} so the airflow makes it vibrate against it several times.`,
          'Tap/Flap': `Flick the ${act} against ${pas} once, very quickly.`,
          'Lateral flap': `Flick the tongue tip against ${pas} once, letting air pass over the sides of the tongue.`,
          Fricative: `Bring the ${act} close to ${pas}, leaving a narrow gap so the air becomes turbulent and hisses.`,
          'Lateral fricative': `Touch the ${act} to ${pas} along the middle, and let air hiss out over the side of the tongue.`,
          Approximant: `Bring the ${act} toward ${pas}, but not close enough to make the air hiss.`,
          'Lateral approximant': `Touch the ${act} to ${pas} along the middle, and let air flow smoothly around the sides of the tongue.`,
        };
        out.push(T[m] || `Articulated with the ${act} against ${pas}.`);
        if (mods.includes('̞') && m === 'Fricative') out.push('Here the gap is wider, so there is no hiss (an approximant).');
        if (b[1] === 'labial-velar') out.push('At the same time, the lips are rounded (or closed, for a stop).');
        if (b[1] === 'labial-palatal') out.push('At the same time, the lips are rounded.');
        if (b[3] === 'θ' || b[3] === 'ð') out.push('The tongue tip may rest between the teeth.');
      }
      if (!mods.includes('ʼ') && !(group === 'Click') && pl !== 'glottal')
        out.push(voiced ? 'The vocal folds vibrate (voiced).' : 'The vocal folds are apart and do not vibrate (voiceless).');
      if (m === 'Nasal' || group === 'Prenasalized') {} else if (!mods.includes('̃')) out.push('The soft palate is raised, so no air goes through the nose.');
    }
    const M = {
      'ʰ': 'Aspirated: after the release, a puff of air comes before the vocal folds start vibrating.',
      'ʱ': 'Breathy-voiced (murmured): the vocal folds vibrate while partly open, letting extra air through.',
      '̤': 'Breathy-voiced (murmured): the vocal folds vibrate while partly open, letting extra air through.',
      '̰': 'Creaky-voiced: the vocal folds are pressed together and vibrate slowly and irregularly.',
      'ʷ': 'Labialized: the lips are rounded at the same time.',
      'ʲ': 'Palatalized: the middle of the tongue is raised toward the hard palate at the same time, like a slight [j].',
      'ˠ': 'Velarized: the back of the tongue is raised toward the soft palate at the same time.',
      'ˤ': 'Pharyngealized: the tongue root is pulled back toward the throat at the same time (the "emphatic" sounds of Arabic).',
      '̃': 'Nasalized: the soft palate is lowered, so air also flows through the nose.',
      'ː': 'Long: held about twice as long as the short version.',
      'ˀ': 'Glottalized: accompanied by a closure or tightening of the vocal folds.',
      '͈': 'Fortis (tense): made with extra muscular tension and stronger airflow.',
      '͉': 'Lenis (lax): made with less muscular tension.',
      '̩': 'Syllabic: forms the core of a syllable on its own.',
      'ⁿ': 'Nasal release: the closure is released through the nose.',
      'ˡ': 'Lateral release: the closure is released over the sides of the tongue.',
      '̥': 'Voiceless: made without vocal fold vibration.',
      '˞': 'Rhoticized: has an r-like quality, with the tongue tip curled or bunched.',
    };
    const seen = new Set();
    for (const ch of mods) if (M[ch] && !seen.has(M[ch])) { seen.add(M[ch]); out.push(M[ch]); }
    return out;
  }

  // ---------- render ----------
  function catmull(P, closed) {
    const n = P.length, pt = i => P[closed ? (i + n) % n : Math.max(0, Math.min(n - 1, i))];
    let d = `M${P[0][0].toFixed(1)},${P[0][1].toFixed(1)}`;
    const last = closed ? n : n - 1;
    for (let i = 0; i < last; i++) {
      const p0 = pt(i - 1), p1 = pt(i), p2 = pt(i + 1), p3 = pt(i + 2);
      const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6], c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
      d += `C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
    }
    return d + (closed ? 'Z' : '');
  }
  const SVG = `<svg viewBox="0 0 250 214" class="artic" role="img" aria-label="Animated side view of the mouth and throat">
    <path class="a-skin" d="M74,0 C70,12 64,20 60,26 C56,32 50,40 34,54 C30,58 31,64 38,66 C42,67 44,70 44,74 L172,74 L172,0 Z"/>
    <path class="a-skin" id="aJawSkin" d=""/>
    <path class="a-face" d="M74,0 C70,12 64,20 60,26 C56,32 50,40 34,54 C30,58 31,64 38,66 C42,67 44,70 44,74"/>
    <path class="a-face" id="aChin" d=""/>
    <path class="a-air-cav" d="M40,66 C52,56 92,46 140,49 C158,50 170,56 172,66 L172,200 L156,200 L156,178 C150,172 146,166 146,160 L150,112 C156,100 162,90 166,74 L140,74 Z"/>
    <path class="a-cav" d="M40,66 C52,56 92,46 140,49 C158,50 170,56 172,66 L172,214"/>
    <path class="a-bone" d="M58,93 C61,89 63,86 66,84 C72,80 82,77 96,74 C108,72 122,71 134,73 L134,67 C112,64 86,66 64,74 C57,78 54,84 54,89 Z"/>
    <path class="a-bone" id="aMand" d=""/>
    <path class="a-tooth" d="M50,88 L58,90 L57,106 C55,108 52,108 51,106 Z"/>
    <path class="a-tooth" id="aLT" d=""/>
    <path class="a-vel" id="aVel" d=""/>
    <path class="a-epi" id="aEpi" d=""/>
    <path class="a-tongue" id="aTon" d=""/>
    <path class="a-lip" id="aUL" d=""/>
    <path class="a-lip" id="aLL" d=""/>
    <g id="aLar"><rect class="a-lar" x="152" y="176" width="22" height="16" rx="4"/>
      <path id="aFoldS" class="a-fold" d=""/></g>
    <g id="aFx"></g>
    <circle id="aAt" class="a-at" r="5" cx="-20" cy="-20"/>
    <g class="a-inset"><rect x="198" y="150" width="46" height="56" rx="6" class="a-ibox"/>
      <path id="aF1" class="a-fold" d=""/><path id="aF2" class="a-fold" d=""/>
      <text x="221" y="161" class="a-lab" text-anchor="middle">vocal folds</text></g>
    <g class="a-labs">
      <text x="92" y="60" class="a-lab">nasal cavity</text><text x="104" y="84" class="a-lab">hard palate</text>
      <text x="178" y="76" class="a-lab">soft palate</text><text x="178" y="128" class="a-lab">throat</text>
      <text x="96" y="126" class="a-lab a-on">tongue</text><text x="4" y="100" class="a-lab">lips</text><text x="178" y="188" class="a-lab">larynx</text>
    </g></svg>`;

  function mount(el, art, group) {
    el.innerHTML = SVG;
    const q = id => el.querySelector('#' + id);
    const keys = plan(art, group);
    let paused = matchMedia('(prefers-reduced-motion: reduce)').matches, slow = false, raf = 0, t0 = performance.now(), frozen = .4;
    const PERIOD = 2400;
    function stateAt(t) {
      let i = 0; while (i < keys.length - 2 && t >= keys[i + 1].t) i++;
      const a = keys[i], b = keys[i + 1];
      const u = b.t > a.t ? ease(Math.min(1, Math.max(0, (t - a.t) / (b.t - a.t)))) : 1;
      const s = { T: a.s.T.map((p, k) => [lerp(p[0], b.s.T[k][0], u), lerp(p[1], b.s.T[k][1], u)]) };
      for (const k of ['jaw', 'lip', 'prot', 'ld', 'ldGap', 'vel', 'epi', 'lar', 'glot', 'voice']) s[k] = lerp(a.s[k], b.s[k], u);
      s.fx = a.fx; s.u = (t - a.t) / Math.max(1e-6, b.t - a.t);
      return s;
    }
    function draw(t, now) {
      const s = stateAt(t), fx = s.fx || {};
      // trill: oscillate the active articulator
      if (fx.trill) {
        const o = 3.2 * Math.abs(Math.sin(now / 22));
        if (fx.trill === 'bilabial') s.lip += o;
        else if (fx.trill === 'uvular') s.uvo = o;
        else if (fx.trill === 'epiglottal') s.epi -= o / 6;
        else { s.T[0][1] += o; s.T[1][1] += o * .4; }
      }
      const j = s.jaw;
      const T = s.T, floor = FLOOR.map(([x, y]) => [x, y + j * .8]);
      q('aTon').setAttribute('d', catmull(T.concat(floor), true));
      q('aLT').setAttribute('d', `M52,${109 + j} C54,${107 + j} 57,${108 + j} 58,${110 + j} L59,${125 + j} L52,${125 + j} Z`);
      q('aMand').setAttribute('d', `M50,${124 + j} L60,${124 + j} C70,${134 + j} 90,${140 + j} 118,${144 + j} L124,${150 + j} C96,${150 + j} 66,${150 + j} 54,${146 + j} C48,${140 + j} 47,${130 + j} 50,${124 + j} Z`);
      const c = 105 + j * .35, uy = c - Math.max(0, s.lip) / 2;
      let ly = c + Math.max(0, s.lip) / 2, lx = 0;
      if (s.ld > 0) { ly = lerp(ly, 102 + s.ldGap, s.ld); lx = lerp(0, 7, s.ld); }
      const pr = s.prot;
      q('aUL').setAttribute('d', `M44,74 C${40 - pr},80 ${34 - pr},${uy - 12} ${35 - pr},${uy - 5} C${36 - pr},${uy - 1} ${41 - pr},${uy} 49,${uy} L52,${uy - 6} C52,86 50,79 44,74 Z`);
      q('aLL').setAttribute('d', `M${49 + lx},${ly} C${41 - pr + lx},${ly} ${36 - pr + lx * .6},${ly + 2} ${35 - pr + lx * .5},${ly + 7} C${35 - pr},${ly + 15} ${40},${ly + 21} 47,${ly + 23} L${52},${ly + 13} C${52 + lx * .3},${ly + 7} ${51 + lx},${ly + 3} ${49 + lx},${ly} Z`);
      q('aChin').setAttribute('d', `M47,${ly + 23} C42,${ly + 30} 42,${142 + j} 50,${150 + j} C62,${160 + j} 92,${160 + j} 116,${160 + j} C122,${168} 124,${190} 124,214`);
      q('aJawSkin').setAttribute('d', `M47,${ly + 23} C42,${ly + 30} 42,${142 + j} 50,${150 + j} C62,${160 + j} 92,${160 + j} 116,${160 + j} C122,${168} 124,${190} 124,214 L150,214 L150,${120} L52,${110 + j} Z`);
      // velum: raised tip touches the throat wall, lowered tip hangs down
      const tipx = lerp(167, 153, s.vel), tipy = lerp(67, 99, s.vel) + (s.uvo || 0), cx = lerp(150, 148, s.vel), cy = lerp(75, 82, s.vel);
      q('aVel').setAttribute('d', `M132,73 Q${cx},${cy} ${tipx},${tipy}`);
      const et = lerp(0, 1, Math.max(0, s.epi));
      q('aEpi').setAttribute('d', `M150,168 Q${lerp(150, 158, et)},${lerp(156, 152, et)} ${lerp(157, 168, et)},${lerp(144, 150, et)}`);
      q('aLar').setAttribute('transform', `translate(0,${s.lar.toFixed(1)})`);
      // vocal folds, top view: V-shape; open = wide, closed = touching, voiced = vibrating
      const vib = s.voice > .05 ? Math.sin(now / 9) * 2.4 * s.voice : 0;
      const w = Math.max(0, (1 - s.glot) * 14 + (s.voice > .05 ? 1.2 + vib : 0));
      q('aF1').setAttribute('d', `M221,166 L${221 - w},200`); q('aF2').setAttribute('d', `M221,166 L${221 + w},200`);
      q('aFoldS').setAttribute('d', `M154,183 L${170 - w * .3},${183 + vib * .4}`);
      // effects
      let fxh = '';
      const ph = Math.max(0, Math.min(1, s.u));
      if (fx.oral) for (let k = 0; k < 3; k++) { const o = ((now / 12 + k * 7) % 21); fxh += `<line class="a-air" x1="${31 - o}" y1="${103 + k * 3}" x2="${25 - o}" y2="${103 + k * 3}"/>`; }
      if (fx.nasal || s.vel > .6) for (let k = 0; k < 2; k++) { const o = ((now / 12 + k * 9) % 18); fxh += `<line class="a-air n" x1="${32 - o}" y1="${64 + k * 3}" x2="${26 - o}" y2="${65 + k * 3}"/>`; }
      if (fx.fric) for (let k = 0; k < 7; k++) { const rx = fx.fric[0] - 3 - Math.random() * 12, ry = fx.fric[1] + 3 + (Math.random() - .5) * 6; fxh += `<circle class="a-turb" cx="${rx.toFixed(1)}" cy="${ry.toFixed(1)}" r="1"/>`; }
      if (fx.burst) { const r = 2 + ph * 12; fxh += `<circle class="a-burst" cx="${fx.burst[0]}" cy="${fx.burst[1] + 4}" r="${r.toFixed(1)}" style="opacity:${(1 - ph).toFixed(2)}"/>`; }
      if (fx.asp) for (let k = 0; k < 3; k++) { const o = ph * 18; fxh += `<text class="a-asp" x="${28 - o - k * 5}" y="${100 + k * 5}" style="opacity:${(1 - ph).toFixed(2)}">h</text>`; }
      if (fx.inward) { const o = 8 - ph * 8; fxh += `<path class="a-in" d="M${fx.inward[0] - 16 - o},${fx.inward[1] + 2} l9,0 m-3,-3 l3,3 l-3,3"/>`; }
      if (fx.vacuum) fxh += `<text class="a-lab a-acc" x="${fx.vacuum[0] + 18}" y="${fx.vacuum[1] + 18}">vacuum</text>`;
      if (fx.lateral) fxh += `<path class="a-latair" d="M118,104 C96,116 72,118 44,110"/><text class="a-lab a-acc" x="70" y="140">air over the side</text>`;
      if (fx.ej) fxh += `<path class="a-in" d="M140,${186 + s.lar} l0,-8 m-3,3 l3,-3 l3,3"/><text class="a-lab a-acc" x="104" y="${190 + s.lar}">larynx up</text>`;
      if (fx.imp) fxh += `<path class="a-in" d="M140,${176 + s.lar} l0,8 m-3,-3 l3,3 l3,-3"/><text class="a-lab a-acc" x="98" y="${190 + s.lar}">larynx down</text>`;
      q('aFx').innerHTML = fxh;
      const hl = keys.find(k => k.fx && (k.fx.burst || k.fx.fric || k.fx.inward));
      const at = hl ? (hl.fx.fric || hl.fx.burst || hl.fx.inward) : null;
      const A = q('aAt'); if (at) { A.setAttribute('cx', at[0]); A.setAttribute('cy', at[1]); }
    }
    function loop(now) {
      if (!el.isConnected) return;
      const per = PERIOD * (slow ? 4 : 1);
      const t = paused ? frozen : ((now - t0) % per) / per;
      draw(t, paused ? 0 : now);
      raf = requestAnimationFrame(loop);
    }
    raf = requestAnimationFrame(loop);
    return {
      toggle() { if (paused) { t0 = performance.now() - frozen * PERIOD * (slow ? 4 : 1); paused = false; } else { const per = PERIOD * (slow ? 4 : 1); frozen = ((performance.now() - t0) % per) / per; paused = true; } return paused; },
      slow(v) { const per0 = PERIOD * (slow ? 4 : 1), ph = ((performance.now() - t0) % per0) / per0; slow = v; t0 = performance.now() - ph * PERIOD * (slow ? 4 : 1); },
      seek(v) { paused = true; frozen = v; },
      get paused() { return paused; },
      stop() { cancelAnimationFrame(raf); }
    };
  }
  return { mount, describe, PLACE_NAME };
})();
