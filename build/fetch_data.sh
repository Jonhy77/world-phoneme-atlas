#!/bin/bash
# Download the open datasets the build needs into build/data/ (about 50 MB).
set -e
cd "$(dirname "$0")"; mkdir -p data/wikt
UA="world-phoneme-atlas build (github.com/Jonhy77/world-phoneme-atlas)"
curl -sSL -A "$UA" -o data/phoible.csv https://raw.githubusercontent.com/phoible/dev/master/data/phoible.csv
curl -sSL -A "$UA" -o data/glottolog_languages.csv https://raw.githubusercontent.com/glottolog/glottolog-cldf/master/cldf/languages.csv
curl -sSL -A "$UA" -o data/glottolog_values.csv https://raw.githubusercontent.com/glottolog/glottolog-cldf/master/cldf/values.csv
curl -sSL -A "$UA" -o data/iso639-3.tab https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3.tab
curl -sSL -A "$UA" -o data/iso639-3-macro.tab https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3-macrolanguages.tab
curl -sS -A "$UA" -H "Accept: text/csv" --data-urlencode "query@scripts/wikidata_speakers.rq" https://query.wikidata.org/sparql -o data/wikidata_speakers.csv
for m in "languages/data/2" "languages/data/exceptional" "etymology_languages/data" "families/data" "families/data/etymology"; do
  curl -sS -A "$UA" -o "data/wikt/$(echo "$m" | tr '/' '_').lua" "https://en.wiktionary.org/w/index.php?title=Module:$m&action=raw"; sleep 2; done
for c in a b c d e f g h i j k l m n o p q r s t u v w x y z; do
  curl -sS -A "$UA" -o "data/wikt/languages_data_3_$c.lua" "https://en.wiktionary.org/w/index.php?title=Module:languages/data/3/$c&action=raw"; sleep 1.5; done
echo "done"
