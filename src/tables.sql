-- Information about the names


CREATE TABLE links (
       lemma TEXT,      -- lemma (src)
       tlemma TEXT defualt NULL, -- lemma (tgt, if different, else none)
       src TEXT,      -- src synset (wn 3.0 id)
       tgt TEXT,      -- tgt synset (wn 3.0 id)
       trop TEXT,      -- metaphor|metonymy
       cn INTEGER CHECK (cn IN (0, 1)),    -- 1 if in CN, 0 otherwise
       utype TEXT,      -- lexical|morphological
       scor,            -- corelex type for src
       tcor,           -- corelex type for tgt
       UNIQUE(lemma, src, tgt)
);


-- create TABLE udom(	
--        ss TEXT,      --  synset
--        dom TEXT,     --  domain from uniMet
--        UNIQUE(ss, dom)	
--        )

create TABLE tdiff(
       src TEXT,    --- src synset
       tgt TEXT,    --- tgt synset
       trop TEXT,   --- trope:  metaphor|metonymy
       lang TEXT,   --- language
       wn TEXT,    --- which wn
       slemma TEXT, --- src lemma
       tlemma TEXT, --- tgt lemma
       diff TEXT   --- diff (suffix)
       );
       

