#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 01:35:05 2021

@author: mdp38
"""

import undetected_chromedriver as uc
import time
import random
import json
import codecs
from bs4 import BeautifulSoup

chars = []
with open("ff_chars.txt", 'r') as infile:
    chars = infile.readlines()
chars = [x.strip() for x in chars] 


options = uc.ChromeOptions()
options.headless=True
options.add_argument('--headless')
driver = uc.Chrome(options=options)

url = "https://lotr.fandom.com/wiki/{}"
valid_chars = []
outputs = []
invalid_chars = []


loop_through = sorted(list(set(chars)))
n = len(loop_through)


for i, char in enumerate(loop_through):
    if char in valid_chars or char in invalid_chars:
        continue
    if (i % 50 == 0):
        print(f"Parsing file {i} of {n}. Remaining:  {n-i}")
    time.sleep(1)
    driver.get('https://distilnetworks.com')
    char_dict = {}
    char_dict['name'] = char
    time.sleep(random.randint(2, 7))
    driver.get(url.format(char))
    time.sleep(0.5)
        
    source = driver.page_source
    soup = BeautifulSoup(source,"html.parser")
    #race
    race_tag = soup.find('div', attrs={'data-source' : "race"})
    if race_tag is None:
        print(f"{char} race not found.")
        if char not in invalid_chars: 
            invalid_chars.append(char)
        continue
    else:
        race = race_tag.find("div").text
        char_dict['race'] = race
        if char not in valid_chars: valid_chars.append(char)
    
    #culture
    culture_tag = soup.find('div', attrs={'data-source' : "culture"})
    if culture_tag is not None:
        culture = culture_tag.find("div").text
        char_dict['culture'] = culture
    gender_tag = soup.find('div', attrs={'data-source' : "gender"})
    if gender_tag is None:
        gender = "Other"
    else:
        gender = gender_tag.find("div").text
    char_dict['gender'] = gender
    
    #Was in a film?
    if soup.find('div', attrs={'data-source' : "actor"}) is None:
        char_dict['in_film'] = False
    else:
        char_dict['in_film'] = True
    outputs.append(char_dict)
    print(f"Successfully parsed file {i} of {n}: {char}")

    


#switch true and false from earlier error (now fixed)

        