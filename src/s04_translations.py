import wn
import json
import itertools
from collections import defaultdict as dd
from itertools import combinations
from statistics import mean
import langcodes
import language_data
### should remove pairs with no translations
from pathlib import Path


cndir = '.' #Chainnet directory
outdir = 'build'

wn.config.data_directory = ".wn_data"
wn.download('omw:2.0')

ewn=wn.Wordnet(lexicon='omw-en:2.0')

log = open('related.log', 'w')


skey = dict()
for s in ewn.senses(pos='n'):
    #print (s.id, s.metadata()['identifier'])
    skey[s.metadata()['identifier']] = s.id

def skey2ili (key):
    """ give an ili from a sensekey """
    return ewn.sense(id=skey[key]).synset().ili
    
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
    if len(s1.union(s2)) == 0:
        #print ("union is zero")
        return 0
    return len(s1.intersection(s2))/len(s1.union(s2))
    
# def tscore(ili1, ili2, twn):
#     """
#     Look up all translations of ili1 and ili2 in twn
#     return the jacaard distance
#     """
#     lem1 = twn.synsets(ili=ili1)
#     lem2 = twn.synsets(ili=ili2)
#     ### FIXME use metric library
    
#     #print(lem1, lem2)
#     return ratio(lem1,lem2)
 


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
    if wnet.version !='2.0':
        continue
    wnlabel = f'{wnet.id}:2.0'
    if wnet.id == 'omw-en':
        continue
    # if wnet.id != 'omw-ja':  ## debug, just look at Japanese
    #     continue
    print(f'Processing {wnet.id}')
    twn = wn.Wordnet(lexicon=wnlabel)
    for n in enouns:
        sss = ewn.synsets(n, pos = 'n')
        for (ss1, ss2) in combinations(sss, 2):
            ### assume there is no overlap between metaphor and metonymy
            ### FIXME should check
            ili1, ili2  = ss1.ili, ss2.ili
            ts = tscore(ili1, ili2, twn)
            if meto[ili1][ili2] or meto[ili1][ili2]:
                sims[wnlabel]['meto'].append(ts)
            elif meta[ili1][ili2] or meta[ili1][ili2]:
                sims[wnlabel]['meta'].append(ts)
            else:
                sims[wnlabel]['xlnk'].append(ts)
            sims[wnlabel]['all'].append(ts)

outdir = Path(outdir) / 'trope-translation.tex'
out = open(outdir, 'w')
       
for w in sims:
    for t in ['all', 'xlnk', 'meta', 'meto']:
        print ('%', w, t, mean(sims[w][t]), len(sims[w][t]),
               sep='\t', file=out)

        
print("\n\n\n", file=out)

total = dd(float)
print("""  \\textbf{Language} & \\textbf{Code} & \\textbf{Unlinked} & \\textbf{Metaphor} & \\textbf{Metonomy} & \\textbf{All} & \\textbf{Translated} & \\\\ \\midrule""",
      file=out)
for w in sims:
    lname = langcodes.get(w[4:-4]).language_name()
    print(lname,
          w[4:-4],
          f"{mean(sims[w]['xlnk'])/mean(sims[w]['all']):.2f}",
          f"{mean(sims[w]['meta'])/mean(sims[w]['all']):.2f}",
          f"{mean(sims[w]['meto'])/mean(sims[w]['all']):.2f}",
          f"{mean(sims[w]['all']):.3f}",
          f"{len([x for x in sims[w]['all'] if x > 0.0]):,d}",
          sep = ' & ', end = ' \\\\\n', file=out) 
    total['xlnk'] += mean(sims[w]['xlnk'])/mean(sims[w]['all'])
    total['meta'] += mean(sims[w]['meta'])/mean(sims[w]['all'])
    total['meto'] += mean(sims[w]['meto'])/mean(sims[w]['all'])
    total['all'] += mean(sims[w]['all'])
    total['nonzero'] += len([x for x in sims[w]['all'] if x > 0.0])

print ('\\hline', file=out)
print('Mean', '',
      f"{total['xlnk']/len(sims):.2f}",  f"{total['meta']/len(sims):.2f}",
      f"{total['meto']/len(sims):.2f}",  f"{total['all']/len(sims):.3f}",
      f"{total['nonzero']/len(sims):,.1f}", 
      sep = ' & ', end = ' \\\\\n', file=out) 

print("""   \\caption{Differences in the translation overlap by language}
    \\label{tab:overlap}
""", file=out)
