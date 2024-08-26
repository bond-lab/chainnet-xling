# chainnet-xling
Investigating metaphors cross-linguistically with ChainNet and OMW

Data in `data/CoreLex` is a copy from [here](https://www.cs.brandeis.edu/~paulb/CoreLex/corelex.html).
ChainNet data is a copy from [here](https://github.com/rowanhm/ChainNet).

To obtain the WordNet 1.5 to 3.0 mappings (needed for `synset_corelex.py`), download [mapp.tar](http://nlp.lsi.upc.edu/tools/mapp.tar.gz) and decompress the contents into `data`.


`03_get_related.py` look at synsets related by metaphor or metonomy and other senses they may have.

`03_get_translations.py` look at synsets related by metaphor or metonomy and how their translations overlap.
