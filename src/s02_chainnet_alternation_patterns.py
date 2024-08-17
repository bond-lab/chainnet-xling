import random
from collections import defaultdict

import numpy as np
from matplotlib.colors import PowerNorm

from src.common.common import open_json, info, save_json, save_csv
from nltk.corpus import wordnet as wn

assert wn.get_version() == '3.0'

info('Aligning ChainNet with CoreLex types')
synset_to_type = open_json('data/synset_to_type.json')
alternation_to_examples = defaultdict(list)
for relation in ['metaphor', 'metonymy']:

    data = open_json(f'data/chainnet_simple/chainnet_{relation}.json')['content']
    for datapoint in data:
        word = datapoint['wordform']
        from_synset = wn.lemma_from_key(datapoint['from_sense']).synset().name()
        to_synset = wn.lemma_from_key(datapoint['to_sense']).synset().name()

        from_type = synset_to_type[from_synset]
        to_type = synset_to_type[to_synset]

        alternation_to_examples[(relation, from_type, to_type)].append((word, from_synset, to_synset))

info('Saving JSON/TSV')
output = []
for ((relation, from_type, to_type), examples) in alternation_to_examples.items():
    for (word, from_synset, to_synset) in examples:
        from_definition = wn.synset(from_synset).definition()
        to_definition = wn.synset(to_synset).definition()
        output.append({
            'relation': relation,
            'from_type': from_type,
            'to_type': to_type,
            'wordform': word,
            'from_synset': from_synset,
            'to_synset': to_synset,
            'from_definition': from_definition,
            'to_definition': to_definition
        })
save_json('data/chainnet_corelex.json', output)
save_csv('data/chainnet_corelex.tsv', output)

info('Printing examples')
for ((relation, from_type, to_type), examples) in sorted(alternation_to_examples.items(), key=lambda x: len(x[1]), reverse=True):
    print(f'{relation} from {from_type} to {to_type} ({len(examples)})')
    if len(examples) <= 3:
        print_examples = examples
    else:
        print_examples = random.sample(examples, 3)
    for (word, from_synset, to_synset) in print_examples:
        print(f'e.g. {word}: {wn.synset(from_synset).definition()} -> {wn.synset(to_synset).definition()}')

info('Plotting heatmap')
import seaborn as sns
import matplotlib.pyplot as plt
basic_types = sorted(list(set(synset_to_type.values())))
for relation in ['metaphor', 'metonymy']:
    counts = defaultdict(int)
    # Get counts of types
    for ((r, from_type, to_type), examples) in alternation_to_examples.items():
        if r == relation:
            counts[(from_type, to_type)] = len(examples)

    heats = np.array([[counts[(from_type, to_type)] for to_type in basic_types] for from_type in basic_types])
    mask = heats == 0

    cmap = sns.color_palette("magma_r", as_cmap=True)
    # cmap.set_under('white')

    # Create the heatmap
    plt.figure(figsize=(18, 16))
    sns.heatmap(heats,  annot=np.where(heats == 0, np.nan, heats), fmt="g", cmap=cmap, xticklabels=basic_types, yticklabels=basic_types,
                mask=mask, linewidths=0.5, linecolor='black', norm=PowerNorm(gamma=0.2),)
    plt.title(relation.upper(), fontsize=30)
    plt.ylabel('From Domain', fontsize=30)
    plt.xlabel('To Domain', fontsize=30)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    plt.tight_layout()
    plt.show()




