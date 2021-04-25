#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 14:54:14 2021

@author: mdp38
"""

import glob
import re
from bs4 import BeautifulSoup
import json
import codecs
import copy
import collections
import numpy as np

count = 0
wk = re.compile('Witch-King$')
wk2 = re.compile('Witch-King,')

fix_dict = {'Elvenking Thranduil':'Thranduil',
            'The Necromancer/Sauron': 'Sauron',
            re.compile('Witch-King(,|$)'): r'Witch-King of Angmar\1'}



with open("genres.txt") as inF:
    genres = [t.strip() for t in inF.readlines()]



def parse_files(filename):
    langs = []
    files = glob.glob(filename)
    n = len(files)
    print(f"Parsing {n} total files.")
    for i,f in enumerate(files):
        if (i % 200 == 0):
            print(f"Parsing file {i} of {n}. Remaining:  {n-i}")
        with open(f) as infile:
            for line in infile.readlines():
                res = parse_blurb(line)
                if res:
                    langs.append(res)
    return langs
                
            

def parse_blurb(b):
    meta = {}
    soup = BeautifulSoup(b, "html.parser")
    t_block = soup.findAll("a", class_="stitle")
    if (len(t_block) != 1 ):
        print ("We have an error title not right!")
        print(b)
    meta["title"] = t_block[0].text
    a_block = [a.text for a in soup.findAll("a", class_="") if a.text != '']
    if  len(a_block) != 1:
        print ("We have an error author not right!")
        print(b)
    meta["author"] = a_block[0]
    
    t_block =  [x.text for  x in soup.findAll("div", class_="z-padtop2") if x.text != '']
    tags = re.split(r"\s-\s", t_block[0])
    params = [x for x in tags if x.find(":") < 0]
    pairs = [x for x in tags if x.find(":") >= 0]
    if 'Complete' in params:
        params.remove('Complete')
    if 'English' in params:
        params.remove('English')
    for p in params:
        if p in genres:
            meta["genre"] = p
        else:
            meta["characters"] = p
            for old, new in fix_dict.items():
                meta["characters"] = re.sub(old, new, meta["characters"])
        
    for pair in pairs:
        k = pair.split(":")[0].lower()
        v = pair.split(":")[1]
        if k in ("rated", "words", "reviews", "favs", "follows", "published"):
            meta[k]= v
            
    return meta
 


def save_json(li, filename = "lotr.json"):
    with codecs.open(filename, 'w', encoding="utf-8") as fout:
        json.dump(li, fout, ensure_ascii=False)
    
  

def load_jsons(glob_pattern):
    data = []
    files = glob.glob(glob_pattern)
    n = len(files)
    print(f"Parsing {n} total files.")
    
    for i,f in enumerate(files):
        if (i % 200 == 0):
            print(f"Parsing file {i} of {n}. Remaining:  {n-i}")
        with open(f) as infile:
            d = json.load(infile)
            if d is None:
                print(f"Error in file {f}")
            else:
                data = data + d
    return data
            

def ao3_fix_relationships(li):
    for blurb in li:
        tmp = []
        for r in blurb["relationships"]:
            
            if len(r) == 1:
                new_r = r[0].split('/')
                if new_r not in tmp:
                    tmp.append(sorted(new_r))
            else:
                if r not in tmp:
                    tmp.append(sorted(r))
                
        blurb["relationships"] = sorted(tmp)




            
            
def merge_blurbs(*lists, dupes):
    md = {}
    for li in lists:
        for b in li:
            k = (b["title"], b["author"])
            if k in md:
                print(f'Found a dupe for {b["title"]} by {b["author"]}')
                dupes.append(b)
            else:
                md[k] = b
    return md



def get_relationships(li):
    for l in li:
        if "characters" not in l:
            l["characters"] = "NA"
            l["relationships"] = "NA"
            continue
        
        if "[" not in l["characters"]:
            #now also clean up the characters list
            l["characters"] = [x.strip().replace(',','') for x in l["characters"].split(',')]
            l["relationships"] = "NA"
            continue

        #Find the relationships (between [])
        res = re.findall(r'\[.*?\]', l['characters'])
        #Turn each relationship into a list
        relationships =[]
        for x in res:
            new_r = []
            parts = x.split(',')
            for y in parts:
                y = y.strip().replace("[", '').replace("]", '')
                new_r.append(y)
            relationships.append(new_r)
                
            
        #now also clean up the characters list
        l["characters"] = l["characters"].replace("[",'').replace("]", ',')
        l["characters"] = [x.strip() for x in l["characters"].split(',') if x.strip() != ""]
        
        if len(relationships) > 0:
            l["relationships"] = relationships
        else:
            l["relationsips"] = "NA"

def get_all_relationships(li):
    rels = []
    for l in li:
        if l["relationships"] == "NA":
            continue
        for r in l["relationships"]:
            for s in r:
                rels.append(s)
    return rels


def has_relationship(li, match):
    for i, blurb in enumerate(li):
        for r in blurb["relationships"]:
            for elem in r:
                if match in elem:
                    print(f"Found {match} in index {i}")
                    print(r)
                    

def get_all_r_containing(li, match):
    blurbs = []
    for i, blurb in enumerate(li):
        for r in blurb["relationships"]:
            for elem in r:
                if match.lower() in elem.lower():
                    blurbs.append(blurb)
    return(blurbs)    

def get_all_c_containing(li, match):
    blurbs = []
    idx = []
    for i, blurb in enumerate(li):
        for r in blurb["characters"]:
                if match.lower() in r.lower():
                    blurbs.append(blurb)
                    idx.append(i)
    return(idx)             

def count_relationships(li, names):
    rels = {}
    for a in names:
        for b in names:
            key = (a, b)
            rels[key] = 0
            
    for l in li:
        for groups in l["relationships"]:
            for i,r in enumerate(groups):
                for j,s in enumerate(groups):
                    if r==s: continue
                    key = (r, s)
                    if key in rels:
                        rels[key] += 1
                    else:
                        print(f"Key {key} not found.")
    return rels
        
def get_all_characters(li):
    chars = []
    for l in li:
        if l["characters"] == "NA":
            continue
        for r in l["characters"]:
            if r == "":
                print(l)
            chars.append(r)
    return chars

   
def remove_tags_matching(li, matches):
    return None

def clean_up_ao3(list_to_copy):
    li = copy.deepcopy(list_to_copy)
    
    #remove mention* from all tags
    tags_to_remove["mention"]
    
    #simplify OCs
    for l in li:
        for i in range(0, len(l["characters"])):        
            elem = l["characters"][i]
            print("Testing " + elem)
            if re.search(r" oc", elem.lower()):
                print(str(i )+ "  " + l["characters"][i])
                li["characters"][i] = "OC"
                print(str(i )+ "  " + l["characters"][i])
            
    changes = {"omc":"OMC",
               "ofc":"OFC",
               "oc": "OC"}
    
    return None
    
def dict_to_matrix(d, names):
    keys = []
    for a in names:
        for b in names:
            keys.append((a, b))
    matrix = np.array([d[i] for i in keys])
    print(matrix)
    return(matrix)
    
    
filename = "outputS/*txt"
silm = parse_files(filename)
filename = "output2/*txt"
lotr = parse_files(filename)
filename = "outputHobbit/*txt"
hobbit = parse_files(filename)
dupes = []
merged = merge_blurbs(lotr, hobbit, silm, dupes = dupes)
raw = copy.deepcopy(merged)
li_merged = list(raw.values())

get_relationships(li_merged)
chars = get_all_characters(li_merged)
collections.Counter(chars).most_common(20)


collections.Counter(get_all_characters(ao3)).most_common(20)
all_rs = get_all_relationships(li_merged)
occurences = collections.Counter(all_rs)
occurences.most_common(20)

ao3_rs = get_all_relationships(ao3)
collections.Counter(ao3_rs).most_common(20)


glob_pattern = "/Users/mdp38/ao3/fulltext/*.json"
ao3 = load_jsons(glob_pattern)




def fix_characters(li, fix_dict):
    for old, new in fix_dict.items():
        for l in li:
            l["characters"] = [x.replace(old, new) for x in l["characters"]]
            for r in l["relationships"]:
                l["relationships"] = [x.replace(old, new) for x in r]
    
     

li = test2
    
test2 = copy.deepcopy(li_merged)
fix_characters(li_merged, fix_dict)   


langs# =============================================================================  
#    bio = re.split(r"\breviews", b)[0]
#    bio2 = [tmp.strip() for tmp in re.split(r"\bby\b", bio)]  
#    bio =[tmp.strip() for tmp in  b.split("reviews")[0].split("by")]

#     if len(bio2) > 3:
#         print(b)
#         count += 1
#         return None
#     #summary = b.split("Rated")[0]
#     #meta = "Rated" + b.split("Rated")[1].strip()
#     return None
# =============================================================================


filename = "output2/blurbs_114.txt"
filename = "output2/*txt"

# =============================================================================
with open("output2/blurbs_114.txt") as inF:
    data = inF.readlines()


        
    