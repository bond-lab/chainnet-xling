# Find the CoreLex type of each synset
from common.common import open_text, info, open_json, save_json
from nltk.corpus import wordnet as wn

assert wn.get_version() == '3.0'

info('Loading WordNet 1.5 to 3.0 mapping')
wordnet_lookup_raw = open_text('data/mappings-upc-2007/mapping-15-30/wn15-30.noun')
wordnet_lookup = {l[0]: l[1] for l in [x.split() for x in wordnet_lookup_raw]}

info('Extracting CoreLex anchor synsets')
type_names = open_json('data/corelex_types.json')
corelex_raw = open_text('data/CoreLex/corelex_nouns.basictypes.synset.txt')
corelex_anchors = {}
for line in corelex_raw[10:]:
    line_split = line.split('\t')

    # Get synset
    synset_number = line_split[1]
    synset = wn.synset_from_pos_and_offset('n', int(wordnet_lookup[synset_number]))

    # Get corelex type
    corelex_type = line_split[0]
    corelex_type = type_names[corelex_type]

    assert synset not in corelex_anchors
    corelex_anchors[synset] = corelex_type

assert len(set(corelex_anchors.values())) == 39, 'There should be 39 Basic Types'
## bug fix for FOOD
## https://github.com/bond-lab/chainnet-xling/issues/3

corelex_anchors[wn.synset('food.n.02')] = 'FOOD'

info('Assigning each synset to its nearest anchor')
synset_to_type = {}
offset_to_type = {}
for i, synset in enumerate(wn.all_synsets('n')):
    if (i+1)%1000 == 0:
        info(f'On synset {i+1}')
    assert synset.name() not in synset_to_type
    similarities = [(wn.path_similarity(synset, other_synset), basic_type) for other_synset, basic_type in corelex_anchors.items()]
    best_type = max(similarities, key=lambda x: x[0])[1]
    synset_to_type[synset.name()] = best_type
    offset_to_type[f"{synset.offset():08d}-f{synset.pos()}"] = best_type

    
info('Saving')
save_json('data/synset_to_type.json', synset_to_type)
save_json('data/offset_to_type.json', offset_to_type)

info('Done')
