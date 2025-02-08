import wn
import json
import itertools
from collections import defaultdict as dd
from itertools import combinations
from statistics import mean
from pathlib import Path

cndir = '.' #Chainnet directory
outdir = 'build'

ewn=wn.Wordnet(lexicon='omw-en:1.4')

log = open('related.log', 'w')


skey = dict()
for s in ewn.senses(pos='n'):
    #print (s.id, s.metadata()['identifier'])
    skey[s.metadata()['identifier']] = s.id

def skey2ili (key):
    """ give an ili from a sensekey """
    return ewn.sense(id=skey[key]).synset().ili.id
    
enouns = set()

# Read in metaphors
with open(f"{cndir}/data/chainnet_simple/chainnet_metaphor.json", "r") as fp:
    metaphor = json.load(fp)

print('Read Metaphors')
    
meta = dd(lambda: dd(list))

for e in metaphor['content']:
    w = e['wordform']
    enouns.add(w)
    fr_s = e['from_sense']
    to_s = e['to_sense']
    meta[skey2ili(fr_s)][skey2ili(to_s)].append(w)

###
### Synsets with more than two metaphorical relations linking them
###
### Or, why we need spelling variants!
###

stats = dd(int)
print('# More than two metaphor links between synsets', file=log)
for s in meta:
    for t in meta[s]:
        stats[len(meta[s][t])]+=1
        if len(meta[s][t]) > 1:
            print('METAPHOR',  s, t, meta[s][t], sep='\t', file=log)
print('Number of pairs linked by metaphor')
for s in stats:
    print(s, stats[s], sep='\t')

    
# Read in metonymy
with open(f"{cndir}/data/chainnet_simple/chainnet_metonymy.json", "r") as fp:
    metonymy = json.load(fp)
meto = dd(lambda: dd(list))
print('Read Metonymy')

for e in metonymy['content']:
    w = e['wordform']
    enouns.add(w)
    fr_s = e['from_sense']
    to_s = e['to_sense']
    meto[skey2ili(fr_s)][skey2ili(to_s)].append(w)

###
### Synsets with more than two metonymy relations linking them
###
### Or, why we need spelling variants!
###

stats = dd(int)
print('# More than two metonymy links between synsets', file=log)
for s in meto:
    for t in meto[s]:
        stats[len(meto[s][t])]+=1
        if len(meto[s][t]) > 2:
              print('METONOMY',  s, t, meta[s][t], sep='\t', file=log)
print('Number of linked pairs')
for s in stats:
    print(s, stats[s], sep='\t')


##
## Calculate derivational links between other senses
##

drvdir = Path(outdir) / 'deriv-links.tsv'
drv = open(drvdir, 'w')

print("rel", "src", "tgt", "wn", "link", "src-lem", "tgt=lem",
      sep = '\t', file=drv)


for rel, name in [(meto, 'Meto'), (meta, 'Meta')]:
    for wnet in  wn.lexicons():
        if wnet.version !='1.4':
            continue
        wnlabel = f'{wnet.id}:1.4'
        print(f'Processing {name} derivations with {wnlabel}')

        
        twn = wn.Wordnet(lexicon=wnlabel)    
        labels = dd(list)
        for i1 in rel:
            for i2 in rel[i1]:
                if twn.synsets(ili=i1):
                    ll1 = twn.synsets(ili=i1)[0].lemmas()
                else:
                    ll1 = []
                if twn.synsets(ili=i2):
                    ll2 = twn.synsets(ili=i2)[0].lemmas()
                else:
                    ll2 = []
                for l1 in ll1:
                    for l2 in ll2:
                        label = ''
                        if l1==l2: ### ignore identical ones
                            continue
                        if l1.startswith(l2):
                            label = wnet.id + '+' +  l1[len(l2):]
                            labels[label].append((i1, l1, i2, l2))
                        elif  l2.startswith(l1):
                            label = wnet.id + '-' + l2[len(l1):]
                            labels[label].append((i1, l1, i2, l2))

                        if label:
                            print(name, i1, i2, wnet.id,
                                  label, l1, l2,
                                  sep = '\t', file=drv)
                            
        for l in sorted(labels, key=lambda x: -len(labels[x])):
            print(f'{name}-dif:', len(labels[l]), l, labels[l], sep='\t')

    


        
