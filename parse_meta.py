#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  2 12:12:12 2021

@author: mdp38
"""

import json
import re
import codecs
import copy
import collections




def parse_ff_meta(filename = "../ff_meta.json"):
    filename = "../ff_meta.json"
    with open(filename) as infile:
        ff_meta = json.load(infile)
    
    meta_rows = ff_meta['rows']
    
    for row in meta_rows:
        year = row[2].split('-')[0]
        row[2] = year
    

    ffm_objects = []
    for row in meta_rows:     
        meta_obj = {}
        vals = row[0].split(', ')
        meta_obj['year'] = row[2]
        meta_obj['genre'] = row[1]
        meta_obj['rating'] = row[3]
        meta_obj['wc'] = row[4]
        meta_obj['fandoms'] = []
        for v in vals:
            new_vals = translate_fandom(v)
            for x in new_vals:
                meta_obj['fandoms'].append(x)
        ffm_objects.append(meta_obj)
        


koi = ['Harry Potter', 'Twilight', 'Star Trek Universe', 'Star Wars Universe', 
       'Marvel Universe', 'DC Universe', 'Middle Earth Total', 'The Lord of the Rings', 
       'The Hobbit', 'Pokémon']

# koi = ['Harry Potter', 'Twilight', 'Star Trek Universe', 'Star Wars Universe', 
#        'Marvel Universe', 'DC Universe', 'Middle Earth Total',  
#        'Supernatural', 'Pokémon', 'Digimon', 'Sherlock Holmes',
#        'Percy Jackson and the Olympians', 'Naruto']

obj = {}
obj['Franchise'] = ''
obj['Year'] = ''
obj['Count'] = 0
obj['wc'] = 0

years = ['1998','1999','2000','2001', '2002', '2003', '2004', '2005',
 '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013',
 '2014', '2015', '2016', '2017']



all_obj = {}

for k in koi:
    for y in years:
        all_obj[(k, y)] = {}
        all_obj[(k, y)]['count'] = 0
        all_obj[(k, y)]['wc'] = 0
    for o in ffm_objects:
        if k in o['fandoms']:
            y = o['year']
            if y=='1969': continue
            all_obj[ (k, y) ]['count'] += 1
            all_obj[ (k, y) ]['wc'] += o['wc']

obj_list = []
for k, v in all_obj.items():
    obj = {}
    obj['Franchise'] = k[0]
    obj['Year'] = k[1]
    obj['Count'] = v['count']
    obj['WC'] = v['wc']
    obj_list.append(obj)

#add rankings to each object too
for y in years:
    tmp = sorted([a for a in obj_list if a['Year'] == y], key=lambda x: x['Count'], reverse=True)
    for i,t in enumerate(tmp):
        t['Rank'] = i+1
    tmp2 = sorted([a for a in obj_list if a['Year'] == y], key=lambda x: x['WC'], reverse=True)
    for i,t in enumerate(tmp2):
        t['WC_Rank'] = i+1
  

    
with open('franchises_small.csv', 'w') as outfile:
    outfile.write('Franchise,Year,Count,Rank,WC,WC_Rank\n')
    for val in obj_list:
        if val['Count']==0:
            val['Rank'] = 0
            val['WC_Rank'] = 0
            
        out_str = f"{val['Franchise']},{val['Year']},{val['Count']},{val['Rank']},{val['WC']},{val['WC_Rank']}\n"
        outfile.write(out_str)        

        




counts = {}

top_franchise = []
for y in years[2:]:
    top = list(counts[y])[0:10]
    for v in top:
        if v not in top_franchise:
            top_franchise.append(v)


for y in years:
    if y == '' or y == '1969':
        continue
    counts[y] = []
    
for y in years:
    fans, books = create_fandom_list([all_cats[y]])
    series_counter = collections.Counter(books)
    me_sum = sum([int(a[1]) for a in series_counter.most_common()])
    fans = fans + books + (['Middle Earth Total']*me_sum)
    fan_counter = dict(collections.Counter(fans).most_common())
    counts[y] = fan_counter
    print(y)
    print(fan_counter)


koi = ['Harry Potter', 'Twilight', 'Star Trek Universe', 'Star Wars Universe', 'Marvel Universe', 'Middle Earth Total', 'The Lord of the Rings', 'The Hobbit']

list_of_vals = [['Franchise'] + sorted(years)]
obj = {}
obj['Franchise'] = ''
obj['Year'] = ''
obj['Count'] = ''
obj['Words'] = ''



for k in koi:
    obj = {}
    obj['Franchise'] = k
    obj['Year'] = ''
    obj['Count'] = ''
    obj['Words'] = ''
    vals = [k]
    for y in years:
        
        if k not in counts[y]:
            vals.append(0)
        else:
            vals.append(counts[y][k])
    list_of_vals.append(vals)


"","AirportName","City","Country","Week","Percent.wk","Month","Percent.mo"



with open('franchises.csv', 'w') as outfile:
    for val in list_of_vals:
        outfile.write(','.join([str(v) for v in val]) + '\n')
     
    

tags = {}
with open("sorted_tags.txt") as tagfile:
    for line in tagfile.readlines():
        vals = line.strip().split(',')
        if vals[1] != "Fandom":
            print("Error found in file for " + line)
            continue
        name = vals[2]
        tag_id = vals[-1]
        if tag_id in tags:
            print(f"Error {tag_id} is already in ditionary.")
        else:
            tags[tag_id] = name

works = []
missing= []
with open("works-20210226.csv") as tagfile:
    for line in tagfile.readlines():
        w_dic = {}
        vals = line.strip().split(',')
        if vals[1] != 'en':
            continue
        year = vals[0].split('-')[0]
        w_dic['year'] = year
        tag_li= [v for v in vals[-1].split('+') if v in tags]
        w_dic['tags'] = tag_li
        fandoms = []
        for t in tag_li:
            tag_t = tags[t]
            if 'Redacted' in tag_t: continue
            if '我英' in tag_t: continue
            if '唐画' in tag_t: continue
            if 'Original Fiction' in tag_t: continue
            if 'Hs' in tag_t:continue
            if 'ハイキュー!!' in tag_t: continue
            fandoms.append(tags[t])

        w_dic['fandoms'] = list(set(fandoms))
        w_dic['word_count'] = vals[4]
        works.append(w_dic)
        
            

years = sorted(list(set([a['year'] for a in works])))
ma_by_year = {}
for y in years:
    ma_by_year[y] = []
    
for w in works:
    year = w['year']
    ma_by_year[year].append(w)
    
    
m_chars = {}
for y in years:
    fans, books = create_fandom_list(ma_by_year[y])
    series_counter = collections.Counter(books)
    me_sum = sum([int(a[1]) for a in series_counter.most_common()])
    fans = fans + books
    fan_counter = dict(collections.Counter(fans).most_common(40))
    fan_counter['Middle Earth Total'] = me_sum
    m_chars[y] = fan_counter
    print(y)
    print(fan_counter)
    
   

def translate_fandom(fan_str):
    new_fandoms = []
    f = fan_str
    f = re.sub(r'\(([^)]+)\)', '', f)
    f = f.split('-')[0].strip()
    f = f.replace('  ', ' ')
    f = f.replace('RPF', '').strip()
    if re.search(r'\s?[Ll]ord [Oo]f', f) or re.search(r'[Ll][Oo][[Tt][[Rr]', f):
        new_fandoms.append('The Lord of the Rings')
        new_fandoms.append('Middle Earth Total')
    elif re.search(r'\s?[Hh]obbit', f):
        new_fandoms.append('The Hobbit')
        new_fandoms.append('Middle Earth Total')
    elif 'silma' in f.lower():
        new_fandoms.append('The Silmarillion')
        new_fandoms.append('Middle Earth Total')
    elif 'middle' in f.lower():
        new_fandoms.append('The Silmarillion')
        new_fandoms.append('Middle Earth Total')
    elif 'tolkien' in f.lower() or 'thranduil' in f.lower():
        new_fandoms.append('Middle Earth Total')
    elif 'harry' in f.lower():
        new_fandoms.append('Harry Potter')
    elif 'final fantasy' in f.lower():
        new_fandoms.append("Final Fantasy Series")
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
    elif 'Actor' in f or 'Real Person' in f or 'thorin' in f or 'Multi' in f:
        pass
    else:
        new_fandoms.append(f)
    
    return new_fandoms

            
            