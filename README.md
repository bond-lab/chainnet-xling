# chainnet-xling
Investigating metaphors cross-linguistically with ChainNet and OMW

Data in `data/CoreLex` is a copy from [here](https://www.cs.brandeis.edu/~paulb/CoreLex/corelex.html).
ChainNet data is a copy from [here](https://github.com/rowanhm/ChainNet).

To obtain the WordNet 1.5 to 3.0 mappings (needed for `synset_corelex.py`), download [mapp.tar](http://nlp.lsi.upc.edu/tools/mapp.tar.gz) and decompress the contents into `data`.


`03_get_related.py` look at synsets related by metaphor or metonomy and other senses they may have.

`03_get_translations.py` look at synsets related by metaphor or metonomy and how their translations overlap.


## References ##

* Francis Bond, & Maudslay, R. H. (2025) bond-lab/chainnet-xling: Data for GWC 2025 paper (v0.9). Zenodo. https://doi.org/10.5281/zenodo.14837329
* Francis Bond and Rowan Hall Maudslay (2025)  Metonymy is more multilingual than metaphor: Analysing tropes using ChainNet and the Open Multilingual Wordnet  In <i>Proceedings of the 13th International Global Wordnet Conference (GWC2025)</i>, Pavia
