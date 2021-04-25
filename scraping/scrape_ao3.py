# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import codecs
import re 
import time
import json
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import random 
import os


#get the page
def make_url(page=1, langu="en", rating_key="",
                    fandom="TOLKIEN+J.+R.+R.+-+Works+%26+Related+Fandoms"):
    rating = {
        "": "",
        "Not_Rated": 9,
        "General_Audiences": 10,  
        "Teen_And_Up_Audiences": 11,  
        "Mature": 12, 
        "Explicit": 13,  
    }

    base_loc = "https://archiveofourown.org/works/"

    base_loc += "search?commit=Search&page=" + str(page) + "&utf8=%E2%9C%93"
    #base_loc += "&work_search%5Bbookmarks_count%5D="
    #base_loc += "&work_search%5Bcharacter_names%5D="
    #base_loc += "&work_search%5Bcomments_count%5D="
    #base_loc += "&work_search%5Bcomplete%5D="
    #base_loc += "&work_search%5Bcreators%5D="
    #base_loc += "&work_search%5Bcrossover%5D="
    base_loc += "&work_search%5Bfandom_names%5D="+fandom
    #base_loc += "&work_search%5Bfreeform_names%5D="
    #base_loc += "&work_search%5Bhits%5D="
    #base_loc += "&work_search%5Bkudos_count%5D="
    base_loc += "&work_search%5Blanguage_id%5D=" + langu  
    #base_loc += "&work_search%5Bquery%5D="
    base_loc += "&work_search%5Brating_ids%5D=" + rating[rating_key]  
    #base_loc += "&work_search%5Brelationship_names%5D="
    #base_loc += "&work_search%5Brevised_at%5D="
    #base_loc += "&work_search%5Bsingle_chapter%5D=0"
    #base_loc += "&work_search%5Bsort_column%5D=_score"
    #base_loc += "&work_search%5Bsort_direction%5D=desc"
    #base_loc += "&work_search%5Btitle%5D="
    #base_loc += "&work_search%5Bword_count%5D="

    return base_loc


    
  
    
def parse_search(html):
    soup = BeautifulSoup(html,"html.parser") 
    ol = soup.find("ol",attrs={"class":"work index group"})
    li = ol.findAll("li",attrs={"role":"article"})
    
    
    list_of_dic = []
    
    for article in li:
        #create a dictionary
        thisdict= {}
        
        #get title
        thisdict['title'] = article.find('h4', class_ = "heading").find('a').text
       
        #get author
        aut = article.find('a', {"rel":"author"})
        if aut == None:
            "Found an error for " + thisdict['title']
            thisdict['author'] = "NA"
        else:
            thisdict['author'] = aut.text

        #get publication date in usa ordering
        pdate = article.find('p', class_="datetime").text.split()
        thisdict['published'] = f"{pdate[1]} {pdate[0]}, {pdate[2]}"
        
        #get fandoms
        thisdict['fandoms'] = [t.text for t in article.find("h5", class_="fandoms heading").findAll("a")]
        
        #get ratings
        thisdict['rating'] = article.find('span',class_=re.compile(r'rating\-.*rating')).text
        
        #get category
        thisdict['category'] = article.find('span',class_=re.compile(r'category\-.*category')).text
        
        #get word count
        count = article.find('dd', class_="words").text
        if len(count) > 0:
            thisdict['count'] = count
        else:
            thisdict['count'] = "NA"
        
        #get hit count
        hits = article.find('dd', class_="hits").text
        if len(count) > 0:
            thisdict['hits'] = hits
        else:
            thisdict['hits'] = "NA"
        #characters
        char = article.findAll('li',class_="characters")
        #if len(char)==0:
        #    thisdict["characters"] = "NA"
        #else:
        #thisdict["characters"] = [t.text.split("|", 1)[0].strip() for t in char]
        thisdict["characters"] = [t.text for t in char]
        #relationships
        relation = article.findAll('li',attrs={"class":"relationships"})
        #if len(relation)==0:
            #thisdict["relationships"] = "NA"
        #else:
        thisdict["relationships"] = []
        for r in relation:
            rel = [a.strip() for a in r.text.split('&')]
            #thisdict["relationships"].append([s.split("|", 1)[0].strip() for s in rel])
            thisdict["relationships"].append(rel)
        list_of_dic.append(thisdict)

    return list_of_dic
    
#web scraping starts here  
    
save_path = "ao3_with_author/" # this is where we store the file
if not os.path.exists(save_path):
    os.makedirs(save_path)


options = uc.ChromeOptions()
options.headless=True
options.add_argument('--headless')
browser = uc.Chrome(options=options)
    
#c_service = webdriver.chrome.service.Service("/Users/yidanxu/chromedriver")
#c_service.command_line_args()
#c_service.start()

#chrome_options = webdriver.ChromeOptions()
#browser = webdriver.Chrome(executable_path=path, chrome_options=chrome_options)

time.sleep(1)
browser.get('https://distilnetworks.com')
time.sleep(1)
browser.get("https://archiveofourown.org/")

time.sleep(3)
browser.find_element_by_id("tos_agree").click()
time.sleep(1)
browser.find_element_by_id("accept_tos").click()
time.sleep(1)

start_p = 316 
end_p = 3359

#work_list = [12, 39, 49 ]
work_list = range(start_p, end_p)
for page in work_list:
    work_url = make_url(page)
    browser.get(work_url)
    html_text = browser.page_source
    
    #handle errors
    if (
        'If you accept cookies from our site and you choose "Proceed"'
        in html_text
    ):  
        print("handling a cookie error!")       
        browser.find_element_by_link_text("Proceed").click()
        time.sleep(1)
        browser.get(work_url)
        html_text = browser.page_source
    if "Retry later" in html_text:
        print("handling a retry later error!")  
        while "Retry later" in html_text:
            print(f"Retrying for{page}")
            time.sleep(3)
            browser.get('https://distilnetworks.com')
            time.sleep(3)
            browser.quit()
            time.sleep(60)
            browser = uc.Chrome(options=options)
            browser.get("https://archiveofourown.org/")
            time.sleep(5)
            browser.find_element_by_id("tos_agree").click()
            time.sleep(2)
            browser.find_element_by_id("accept_tos").click()
            time.sleep(3)
            browser.get(work_url)
            html_text = browser.page_source
    
            if (
                'If you accept cookies from our site and you choose "Proceed"'
                in html_text
            ):  
                browser.find_element_by_link_text("Proceed").click()
                time.sleep(1)
                browser.get(work_url)
                html_text = browser.page_source
    
    
    try:
        work_list = parse_search(html_text)
    
        with codecs.open(f'{save_path}parsed_{page}.json', 'w', encoding="utf-8") as fout:
            json.dump(work_list, fout, ensure_ascii=False)

        print(f"Scraped page # {page}: {browser.title}")
        time.sleep(random.randint(4000, 7000)/1000)
    
    except:
        print(f"Found an error with page number {page}")
        print(html_text)
        exit(1)
        