#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 14:54:14 2021

@author: mdp38
"""

import undetected_chromedriver as uc
import time
import random


count = 0

def rip_pages():
    options = uc.ChromeOptions()
    options.headless=True
    options.add_argument('--headless')
    driver = uc.Chrome(options=options)
   
    #url = "https://www.fanfiction.net/book/Lord-of-the-Rings/?&srt=1&lan=1&r=10&p={}"
    url = "https://www.fanfiction.net/book/Hobbit/?&srt=1&lan=1&r=10&p={}"
    #url= "https://www.fanfiction.net/book/Silmarillion/?&srt=1&lan=1&r=10&p={}"
    first_page = 1
    #last_page = 2013
    last_page = 205
    all_blurbs = []
    try:
        for p in range(first_page, last_page):
            all_blurbs = []
            time.sleep(1)
            driver.get('https://distilnetworks.com')
            r = random.randint(4,10)
            time.sleep(r)
            driver.get(url.format(p))
            print(driver.title + f"   page  {p}")
            blurb = driver.find_elements_by_css_selector('.z-list.zhover.zpointer')
            all_blurbs = [b.get_attribute('innerHTML').replace('\n', '') for b in blurb]
            with open(f'outputHobbit/blurbs_{p}.txt', 'w') as outFile:
                outFile.write('\n'.join(all_blurbs))        
    except Exception as e:
        print(e.text)
        print("Found an error")
        




        
rip_pages()
