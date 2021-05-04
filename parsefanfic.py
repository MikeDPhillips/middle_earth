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

with open("lotr_titles.txt") as inF:
    wiki_titles = [t.lower().strip() for t in inF.readlines()]

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
    
    if tags[0] == 'Crossover':
        tags.pop(0)
        meta['fandoms'] = [x.strip() for x in tags.pop(0).split('&', 1)]
    else:
        pass
        #print("Check on " + meta["title"])
        
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
                for f in b['fandoms']:
                    if f not in md[k]['fandoms']:
                        md[k]['fandoms'].append(f)
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
                    #else:
                    #    print(f"Key {key} not found.")
    return rels
        
def make_rel_json(edge_dict, names):
    nodes = []
    edges = []
    
    for i,name in enumerate(names):
        new_dict = {}
        new_dict['id'] = i
        new_dict['name'] = name
        nodes.append(new_dict)
    
    for k,v in edge_dict.items():
        if v == 0:
            continue
        new_dict = {}
        new_dict['source'] =k[0]
        new_dict['target'] = k[1]
        new_dict['weight'] = str(v)
        new_dict['source_index'] = names.index(k[0])
        new_dict['target_index'] = names.index(k[1])
        edges.append(new_dict)
        json_out = {}
        json_out['nodes'] = nodes
        json_out['edges'] = edges
        json.dumps(json_out)
        save_json(json_out, filename = "relationships.json")
        
        
    
    
        
def get_all_characters(li):
    chars = []
    for l in li:
        if l["characters"] == "NA" or len(l["characters"])==0:
            continue
        for r in l["characters"]:
            if r == "":
                continue
            chars.append(r)
    return chars

   
def remove_tags_matching(li, matches):
    return None


    
def dict_to_matrix(d, names):
    keys = []
    for a in names:
        for b in names:
            keys.append((a, b))
    matrix = np.array([d[i] for i in keys])
    print(matrix)
    return(matrix)
    
    
filename = "/Users/mdp38/outputS/*txt"
silm = parse_files(filename)
for s in silm:
    s['fandoms'] = ['The Silmarillion']
    
filename = "/Users/mdp38/output2/*txt"
lotr = parse_files(filename)
for s in lotr:
    s['fandoms'] = ['The Lord of the Rings']
    
filename = "/Users/mdp38/outputHobbit/*txt"
hobbit = parse_files(filename)
for s in hobbit:
    s['fandoms'] = ['The Hobbit']
    

lx_filename = 'outpuCrossoversLOTR/*txt'
lx = parse_files(lx_filename)
hx_filename = 'outpuCrossoversHobbit/*txt'
hx = parse_files(hx_filename)

dupes = []
merged = merge_blurbs(lotr, hobbit, silm, lx, hx, dupes = dupes)
raw = copy.deepcopy(merged)
li_merged = list(raw.values())


get_relationships(li_merged)
li_rs = get_all_relationships(li_merged)
rs_occ = collections.Counter(li_rs)


chars = get_all_characters(li_merged)
collections.Counter(chars).most_common(20)




all_rs = get_all_relationships(li_merged)
occurences = collections.Counter(all_rs)
occurences.most_common(20)




glob_pattern = "ao3_with_author/*.json"
ao3 = load_jsons(glob_pattern)
ao3_rs = get_all_relationships(ao3)
collections.Counter(ao3_rs).most_common(20)

def split_by_years(li):
    valid_list = [x for x in li if ','  in x["published"]]
    years = sorted(set([x["published"].split(',')[1].strip() for x in valid_list]))
    by_year = {}
    for y in years:
        by_year[y] = []
    for l in valid_list:
        year = l['published'].split(',')[1].strip()
        by_year[year].append(l)
    return by_year


    
def make_character_json(d):
    output = []
    keys = sorted(d.keys())[1:]
    for k in keys:
        year_dict = {}
        year_dict['year'] = k
        v = d[k]
        year_dict['total_tolkien'] = len(v)
        year_dict['characters'] = []
        chars = get_all_characters(v)
        occ = dict(collections.Counter(chars).most_common())
        for k2,v2 in occ.items():
            char_dict = {}
            char_dict['name'] = k2
            char_dict['appearances'] = v2
            year_dict['characters'].append(char_dict)
        output.append(year_dict)
    return output
            
        
def fix_characters(li, fix_dict):
    for old, new in fix_dict.items():
        for l in li:
            l["characters"] = [x.replace(old, new) for x in l["characters"]]
            for r in l["relationships"]:
                l["relationships"] = [x.replace(old, new) for x in r]
    
     








newp = []
for p in set(probs):
    #print(p)
    result = re.search(r'\(([^)]+)\)', p)
    if result:
        print(result[1])
        newp.append(p)


#search wiki titles for characters:
found = []
unfound = []  
idx = []
string_vals = []
wiki = [x.lower() for x in wiki_titles]
for i, line in enumerate(alts):
    foundMatch = False
    chars = [x.strip() for x in line.split("|")]
    found_str = ''
    for c in chars:
        if c.lower() in wiki:
            foundMatch = True
            found_str += 'T'
        else: 
            found_str += 'F'
            
    if foundMatch:        
        found.append(line)
        idx.append(i)
        string_vals.append(found_str)
    else:
        unfound.append(line)


changes = {}
for line in found:
    chars = [x.strip() for x in line.split("|")]
    
    

replacements = {}            
with open("replacements.txt") as inF:
   for line in inF.readlines():
       args = line.split(":")
       if args[0] in replacements:
           print("Problem with " + args[0])
       else:
           replacements[args[0].strip()] = args[1].strip()
       
        
def clean_up_ao3(list_to_copy):
    li = copy.deepcopy(list_to_copy)
    
    with  open("tags_to_remove.txt") as infile:
        tags_to_remove = infile.readlines()
    with open("replacements.txt") as inF:
       for line in inF.readlines():
           args = line.split(":")
           if args[0] in replacements:
               print("Problem with " + args[0])
           else:
               replacements[args[0].strip()] = args[1].strip()
               
    #simplify OCs
    for l in li:
        if l["characters"] == "NA" or len(l["characters"])==0: continue
        l["characters"] = [re.sub(r"- ?[Cc]haracter", "", x).strip() for x in l["characters"]]
        #remove parentheses from tags
        l["characters"] = [re.sub(r"\(([^)]+)\)", "", x).strip() for x in l["characters"]]
        
        for bad_value in tags_to_remove:
            l["characters"] = [x for x in l["characters"] if bad_value.lower() not in x.lower()]
        for i in range(0, len(l["characters"])):        
            elem = l["characters"][i].lower()
            if re.search(r"\boc", elem):
                l["characters"][i] = "OC"
            elif re.search(r"\bofc", elem):
                #print(f"{elem} is now OFC")
                l["characters"][i] = "OFC"
            elif re.search(r"\bomc", elem):
                #print(f"{elem} is now OMC")
                l["characters"][i] = "OMC"          
            elif re.search(r"original (\s*|.*)character", elem):
                if "female" in elem:
                    l["characters"][i] = "OFC"
                elif "male" in elem:
                    l["characters"][i] = "OMC"
                else:
                    l["characters"][i] = "OC"
            for old, new in replacements.items():
                if old.lower() in elem or new.lower() in elem:
                    l["characters"][i] = new
                    #print(f"Replacing {elem} with {new}")
        #print("After:" + str(len(l["characters"]))  )  
    return li 


def create_fandom_list(li):
    fandoms = []
    books = []
    for idx, a in enumerate(li):
        new_fandoms = []
        tolkien= []
        for f in li[idx]['fandoms']:
            f = re.sub(r'\(([^)]+)\)', '', f)
            f = f.split('-')[0].strip()
            f = f.replace('  ', ' ')
            f = f.replace('RPF', '').strip()
            if re.search(r'\s?[Ll]ord [Oo]f', f) or re.search(r'[Ll][Oo][[Tt][[Rr]', f):
                tolkien.append('The Lord of the Rings')
            elif re.search(r'\s?[Hh]obbit', f):
                tolkien.append('The Hobbit')
            elif 'silma' in f.lower():
                tolkien.append('The Silmarillion')
            elif 'middle' in f.lower():
                tolkien.append('The Silmarillion')
            elif 'tolkien' in f.lower() or 'thranduil' in f.lower():
                continue
            elif 'harry' in f.lower():
                new_fandoms.append('Harry Potter')
            elif re.search(r"[Mm]arvel(['\sv]|$)", f):
                new_fandoms.append('Marvel Universe')
            elif re.search(r"Thor([\s:]|$)", f):
                new_fandoms.append("Thor")
                new_fandoms.append("Marvel Universe")
            elif 'Captain America' in f:
                new_fandoms.append("Captain America")
                new_fandoms.append("Marvel Universe")
            elif 'Iron Man' in f or 'Ironman' in f:
                new_fandoms.append("Iron Man")
                new_fandoms.append("Marvel Universe")  
            elif 'sherlock' in f.lower():
                new_fandoms.append('Sherlock Holmes')
            elif 'buffy' in f.lower():
                new_fandoms.append('Buffy the Vampire Slayer')
            elif re.search(r'[Ss]tar\s?[Ww]ars', f):
                new_fandoms.append('Star Wars Universe')
            elif re.search('[Ss]tar\s?[Tt]rek', f):
                new_fandoms.append('Star Trek Universe')
            elif re.search(r'^[Dd][Cc]', f):
                new_fandoms.append("DC Universe")
            elif "Batman" in f:
                new_fandoms.append("Batman")
                new_fandoms.append("DC Universe")
            elif "Superman" in f:
                new_fandoms.append("Superman")
                new_fandoms.append("DC Universe")
            elif "Wonder Woman" in f:
                new_fandoms.append("Wonder Woman")
                new_fandoms.append("DC Universe")
            elif "Aquanman" in f:
                new_fandoms.append("Aquaman")
                new_fandoms.append("DC Universe")
            elif re.search(r"^Flash$", f) or re.search(r"^The Flash$", f):
                new_fandoms.append("The Flash")
                new_fandoms.append("DC Universe")
            elif 'ice and fire' in f.lower() or 'throne' in f.lower():
                new_fandoms.append("Game of Thrones")
            elif 'percy' in f.lower():
                new_fandoms.append('Percy Jackson and the Olympians')
            elif 'Hunger' in f:
                new_fandoms.append('The Hunger Games')
            elif f == 'Twilight':
                new_fandoms.append('Twilight')
            elif 'disney' in f.lower():
                new_fandoms.append('Disney Universe')
            elif 'shannara' in f.lower():
                new_fandoms.append('The Shannara Chronicles')
            elif 'pokemon' in f.lower():
                new_fandoms.append('Pokemon')
            elif 'doctor who' in f.lower():
                new_fandoms.append('Doctor Who')
            elif 'Actor' in f or 'Real Person' in f or 'thorin' in f or 'Multi' in f:
                continue
            elif 'vampire diaries' in f.lower():
                new_fandoms.append('The Vampire Diaries')
            elif 'Highlander' in f:
                new_fandoms.append('Highlander')
            elif 'Witcher' in f:
                new_fandoms.append('The Witcher')
            elif 'avengers' in f.lower():
                new_fandoms.append('The Avengers')
                new_fandoms.append('Marvel Universe')
            elif 'walking dead' in f.lower():
                new_fandoms.append('The Walking Dead')
            elif 'stargate' in f.lower():
                new_fandoms.append('Stargate')
            else:
                new_fandoms.append(f)

        li[idx]['fandoms'] = new_fandoms

        li[idx]['series'] = tolkien
        #fandoms += list(set(new_fandoms))
        #books += list(set(tolkien))
        fandoms += new_fandoms
        books += tolkien
        
    return fandoms, books
    #return fandoms + books

        
def make_fandom_json(d):
    output = []
    keys = sorted(d.keys())
    for k in keys:
        year_dict = {}
        year_dict['year'] = k
        v = d[k]
        (fandoms, books) = create_fandom_list(v)
        
        mc_f = dict(collections.Counter(fandoms).most_common(50))
        series = dict(collections.Counter(books).most_common())
        year_dict['fandoms'] = []
        year_dict['series'] = []

        for k2,v2 in mc_f.items():
            char_dict = {}
            char_dict['fandom'] = k2
            char_dict['count'] = v2
            year_dict['fandoms'].append(char_dict)
        for k2, v2 in series.items():
            char_dict = {}
            char_dict['series'] = k2
            char_dict['count'] = v2
            year_dict['series'].append(char_dict)
            
        output.append(year_dict)
    return output 
            
                

validated_chars = load_jsons("validated_characters2.json")
final_chars = [x['name'] for x in validated_chars]
for i in range(0, len(validated_chars)):
    if validated_chars[i]["gender"] == 'Males' or validated_chars[i]["gender"] == 'male':
        validated_chars[i]["gender"] = 'Male'
    elif validated_chars[i]["gender"] =='Other':
        validated_chars[i]["gender"] = 'NA'



ao3 = load_jsons("ao3_with_author/parsed*.json")


race_corrections = { 'Orc':'Orcs',
                     'Goblin':'Orcs',
                     'Man':'Men',
                     'Men':'Men',
                     'Half':'Elves',
                     'Elves':'Elves',
                     'Elven':'Elves',
                     'Elf':'Elves',
                     'Unknown':'Unknown',
                     'Ents':'Ents',
                     'Dwarf':'Dwarves',
                     'Hobbit':'Hobbits',
                     'Eagle':'Great Eagles',
                     'Balrog':'Balrog',
                     'Dwarven':'Dwarves',
                     'Horse':'Horses',
                     }

for i in range(0, len(validated_chars)):
    race = validated_chars[i]["race"]
    
    if re.search(r'Ent$', race):
        validated_chars[i]["race"] = 'Ents'
        continue
    
    for old, new in race_corrections.items():
        if old in race:
            validated_chars[i]["race"] = new
    
    
culture_corrections = {
    'Shire':'Shire-hobbits',
    'Hobbits of Bree':'Bree-hobbits',
    'Stoor':'Stoor-hobbits',
    'Took':'Shire-hobbits',
    'Brandybuck':'Shire-hobbits',
    'Ñoldor':'Ñoldor (Deep Elves)',
    'Noldor':'Ñoldor (Deep Elves)',
    'Tatyar':'Ñoldor (Deep Elves)',
    'Sindar':'Sindar (Grey Elves)',
    'Silvan':'Silvan (Wood Elves)',
    'Vanyar':'Vanyar (Light Elves)',
    'Minyar':'Vanyar (Light Elves)',
    'Gondolindrim':'Gondolindrim (Hidden Elves)',
    'Nandor':'Silvan (Wood Elves)',
    'Nelyar':'Teleri (Sea Elves)',
    'Teleri':'Teleri (Sea Elves)',
    'Falmari':'Teleri (Sea Elves)',
    'Elves of Rivendell':'Elves of Rivendell',
    'Rohirri':'Rohirrim',
    'Rohan':'Rohirrim',
    'Gondor':'Men of Gondor',
    'Númenórean':'Númenóreans',
    'Númenoreans': 'Númenóreans',
    'Bëor':'Edain',
    'Haleth':'Edain',
    'Durin':"Durin's Folk (Dwarves)",
    'Firebeards':'Dwarves of Nogrod',
    'Broadbeams':'Dwarves of Belegost',
    'Uruk':'Uruk-hai of Isengard',
    'Moria Orcs':'Orcs of Moria',
    'Lake-town':'Men of Dale',
    'Istari':'Istari (Wizards)',
    'Wizards':'Istari (Wizards)',
    'Maia':'Maiar',
    'Balrog':'Maiar',
    'Valar':'Valar',
    'Ringwraith':'Nazgûl',
    'Easterling':'Easterlings',
    'Eagles':'Great Eagles',
    'Galadhrim':'Tree Elves',
    'NA':"Unkown",
    'Edain':'Men of Edain'
    }

for i in range(0, len(validated_chars)):
    if 'culture' not in validated_chars[i]: continue

    culture = validated_chars[i]["culture"]
    
    if 'Dúnedain' in culture:
        if 'Gondor'in culture or 'Dol Amroth' in culture:
            validated_chars[i]["culture"] = 'Dúnedain of Gondor'
        else:
            validated_chars[i]["culture"] = 'Dúnedain of the North'
        
    # if re.search(r'Ent$', race):
    #     validated_chars[i]["race"] = 'Ents'
    #     continue
    
    for old, new in culture_corrections.items():
        if old in culture:
            validated_chars[i]["culture"] = new
            
cultures = [x["culture"] for x in validated_chars if 'culture' in x]
set(cultures)

collections.Counter(cultures).most_common()
