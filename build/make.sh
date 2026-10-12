#!/bin/bash
# Rebuild index.html (and audio/) from build/data + the committed selections. Run fetch_data.sh first.
set -e
cd "$(dirname "$0")"
# reuse the committed recordings instead of downloading them again
mkdir -p audio_src/files audio_src/words
cp -n ../audio/ref/*.mp3 audio_src/files/ 2>/dev/null || true
cp -n ../audio/word/*.mp3 audio_src/words/ 2>/dev/null || true
python -I scripts/build.py data scripts data.json -            # first pass: language list for the next two steps
python -I scripts/speakers.py data/wikidata_speakers.csv data.json data/speakers.json
python -I scripts/family.py .
rm -rf pub && mkdir -p pub
python -I scripts/build.py data scripts data.json selections/audio_index.json data/speakers.json selections/words_final.json pub
python -I scripts/assemble.py . pub/world-phoneme-atlas.html
cp pub/world-phoneme-atlas.html ../index.html && cp -r pub/audio/. ../audio/
echo "built ../index.html"
