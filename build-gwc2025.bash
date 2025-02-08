###
### create the data described in the GWC 2025 paper
###

mkdir -p build

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
    python -c "import nltk; nltk.download('wordnet')"
else
    source .venv/bin/activate
fi

### Map synsets to corelex types

python src/s01_synset_corelex.py
cp data/offset_to_type.json data/synset_to_type.json build/.

### Make heatmaps

# don't show plots
MPLBACKEND=Agg python src/s02_chainnet_alternation_patterns.py
cp bin/*_heatmap.png build

echo
echo 'Check related senses and get morphological links'
echo

# output build/deriv-links.tsv

python src/s03_get_related.py


echo
echo 'Calculate translatability (slow)'
echo

python src/s04_translations.py

echo
echo 'Compare to unimet (and build db)'
echo

python src/s05_compare_unimet.py 
mv chainnet_plus.db build/

tar cfz build.tgz build
