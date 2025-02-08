import csv
import json
from collections import defaultdict as dd
import sys, os
import sqlite3 

db = 'chainnet_plus.db'
scriptdir = os.path.dirname(sys.argv[0])

cn = '/home/bond/git/chainnet-viz/instance/chain-net-omw.json'

# download from https://github.com/kbatsuren/UniMet
uni_met = '/home/bond/git/UniMet/UniMet.v1.tsv'
log = open('related.log', 'w')

clf = '/home/bond/git/chainnet-xling/data/offset_to_type.json'


with open(clf) as fh:
    cl = json.load(fh)


def ss2omw(ss, lemma):
    """
    should load escaping from wn
    """
    return f"omw-en-{lemma}-{ss[1:]}-{ss[0]}"

def load_uni_met(path):
    um = []
    with open(path) as tsv:
        for l in tsv:
            if l.startswith('index'):
                continue
            um.append(l.strip().split('\t'))
    return um


def make_db(db, tables='tables.sql'):
    conn = sqlite3.connect(db)    # loads dbfile as con
    c = conn.cursor()
    with open(os.path.join(scriptdir, 'tables.sql'), 'r') as sql_file:
        sql_script = sql_file.read()
    c.executescript(sql_script)
    conn.commit()

def slurp(db, um):
    """
    add the data to the table
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    dom = dict()
    for r in um:
        if r[1] != 'eng' or r[7] == 'morphological':
            continue
        lems = r[6].split(' ; ')
        if len(lems) == 1:
            lems.append(None)
        src, tgt = ss2omw(r[8], lems[0]), ss2omw(r[9], lems[0])
        try:
            c.execute("""
            INSERT INTO links (lemma, tlemma, src, tgt, trop, utype)
            VALUES (?, ?, ?, ?, ?, ?)""",
                      (lems[0], lems[1],
                       src, tgt, 'metonymy', r[7]))
        except:
            print('NOT UNIQUE:', r)
    #     if src not in dom:            
    #         dom[src] = r[4]
    #     elif dom[src] != r[4]:
    #         print(f'Warning domain of {src} conflicts: {dom[src]} vs {r[4]} ({r[0]})')
    #     if tgt not in dom:            
    #         dom[tgt] = r[5]
    #     elif dom[tgt] != r[5]:
    #         print(f'Warning domain of {tgt} conflicts: {dom[tgt]} vs {r[5]} ({r[0]})')
    # for ss, udom in dom.items():
    #     c.execute("""
    #     INSERT INTO udom (ss, dom)
    #     VALUES (?, ?)""",
    #               (ss, udom))
    conn.commit() 


def load_chainnet(db, chainnet):
    """
    use the json version from chainnet-viz for now
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    d = conn.cursor()
    with open(chainnet) as f:
        cn = json.load(f)
    for lemma in cn:
        for src in cn[lemma]:
            for tgt in cn[lemma][src]:
                trope = cn[lemma][src][tgt]
                try:
                    c.execute("""
                    INSERT INTO links (lemma, src, tgt, trop, cn)
                    VALUES (?, ?, ?, ?, ?)""",
                              (lemma,
                               src, tgt,
                               trope, 1))
                except:
                    if trope == 'metaphor':
                        print(f'WARNING: meto/meta for {lemma} {src}, {tgt}')
                    else:
                      c.execute("""
                      UPDATE links SET cn = 1 
                      WHERE lemma = ? AND src = ? AND tgt = ?""", 
                                (lemma, src, tgt))    
                        
    conn.commit()
                

def add_corelex(db, cl):
    conn = sqlite3.connect(db)    # loads dbfile as con
    c = conn.cursor()
    c.execute("""SELECT src, tgt FROM links""")
    links = c.fetchall()
    ### could be more efficient by splitting, but not worth it
    for src, tgt in links:
        if src[-10:] in cl and tgt[-10:] in cl:
            c.execute("""UPDATE links SET scor = ?, tcor = ?
            WHERE src =? and tgt = ?""",
                      (cl[src[-10:]], cl[tgt[-10:]], src, tgt))      
    conn.commit()

   
make_db(db)
um =  load_uni_met(uni_met)
slurp(db, um)
load_chainnet(db, cn)
add_corelex(db, cl)

