import wn
import json
import itertools
from collections import defaultdict as dd
from itertools import combinations
from statistics import mean

cndir = '../' #Chainnet directory

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
### Now, when our troubles begin!
###

def tscore(ili1, ili2, twn):
    """
    Look up all translations of ili1 and ili2 in twn
    return the jacaard distance
    """
    lem1 = twn.synsets(ili=ili1)
    lem2 = twn.synsets(ili=ili2)
    ### FIXME use metric library
    
    #print(lem1, lem2)
    if lem1:  
        s1 = set(lem1[0].lemmas())
    else:
        return 0  ## if one has no lemmas, similarity is 0
    if lem2:
        s2 = set(lem2[0].lemmas())
    else:
        return 0  ## if one has no lemmas, similarity is 0
    #print(s1,s2)
    return len(s1.intersection(s2))/len(s1.union(s2))
    

###
### Go through the nouns, look up the senses:
###  * check each pair
###  * save translation score as either
###  * unlinked, metaphor link, metonymy link
###  report on the average
###

# sims[wnlabel][relationship] = [score, score, score, ...]
sims = dd(lambda: dd(list))

for wnet in  wn.lexicons():
    if wnet.version !='1.4':
        continue
    wnlabel = f'{wnet.id}:1.4'

    twn = wn.Wordnet(lexicon=wnlabel)
    for n in enouns:
        sss = ewn.synsets(n, pos = 'n')
        for (ss1, ss2) in combinations(sss, 2):
            ### assume there is no overlap between metaphor and metonymy
            ### FIXME should check
            ili1, ili2  = ss1.ili.id, ss2.ili.id
            ts = tscore(ili1, ili2, twn)
            if meto[ili1][ili2] or meto[ili1][ili2]:
                sims[wnlabel]['meto'].append(ts)
            elif meta[ili1][ili2] or meta[ili1][ili2]:
                sims[wnlabel]['meta'].append(ts)
            else:
                sims[wnlabel]['xlnk'].append(ts)
            sims[wnlabel]['all'].append(ts)
        
for w in sims:
    for t in ['all', 'xlnk', 'meta', 'meto']:
        print (w, t, mean(sims[w][t]), len(sims[w][t]), sep='\t')

        
print("\n\n\n")
print('Wordnet\txlnk\tmeta\tmeto\tnon-zero\tall')
for w in sims:
    print(f"""{w}\t{mean(sims[w]['xlnk'])/mean(sims[w]['all']):.2f}\t{mean(sims[w]['meta'])/mean(sims[w]['all']):.2f}\t{mean(sims[w]['meto'])/mean(sims[w]['all']):.2f}\t({len([x for x in sims[w]['all'] if x > 0.0])})\t{mean(sims[w]['all'])}""")

        
