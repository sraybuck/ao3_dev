import requests
import bs4
import pandas as pd
import nltk
import csv
import time
from nltk.corpus import stopwords

def get_first_soup(headers, url):
    r = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(r.text, 'lxml')
    return soup

def get_title(soup):
    # get title as string
    title = ""
    title_html = soup.select("div.preface h2")
    for row in title_html:
        title += row.text.lower().strip()
    return title

def get_chap(soup):
    # get chapter
    chapter = ""
    chapter_html = soup.select("div.chapter h3 a")
    for row in chapter_html:
        chapter += row.text.lower()
    return chapter

def clean_html(soup):
    # select for the body of the fic
    base = soup.select("div.userstuff p")
    
    # create clean string to store stripped text
    clean = ""
    
    # strip html tags
    for row in base:
        clean += row.text.lower()

    # tokenize
    tokens = nltk.word_tokenize(clean)
    return tokens

def log_text_feature(tokens, output_file, chapter, thing_total):
    # iterate over entire fic
    for token_index, token in enumerate(tokens):
        # look for instances of voice or tone
        if token == "voice" or token == "tone":
            # update total
            thing_total += 1

            #create index trackers
            back_iterator = token_index
            front_iterator = token_index

            # get index of first word of sentence or clause
            while(tokens[back_iterator] != "\"" and tokens[back_iterator] != "."):
                back_iterator -=1
            
            # get index of last word of sentence
            while(tokens[front_iterator] != "."):
                front_iterator +=1
            
            # init/clear context
            context = ""

            # loop over tokens to get all the words in sentence or clause
            for i in range(back_iterator + 1, front_iterator):
                context += tokens[i]
                context += " "
            # write output to file
            output_string = chapter + ", \"" + context + "\"\n"
            output_file.write(output_string)
    
    return thing_total

def is_there_another_chapter(soup):
    another_chapter = False

    links = soup.select("div.feedback ul.actions li a")
    for link_index, link in enumerate(links):
        if link.text == "Next Chapter →":
            another_chapter = True

    return another_chapter

def get_next_chapter_url(soup):
    links = soup.select("div.feedback ul.actions li a")
    for link_index, link in enumerate(links):
        if link.text == "Next Chapter →":
            url_slug = links[link_index].get('href')
        
    next_url = "https://archiveofourown.org" + url_slug

    return next_url

def main():
    # declare headers for request
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"}
    
    # accumulator for text feature total
    feature_total = 0

    # flag for end of fic
    notAtEndOfFic = True
    
    url = input("Please enter the url of the first chapter of the fic: ")

    # get BS object base html
    soup = get_first_soup(headers, url)
    
    # get fic title
    title = get_title(soup)
        
    # generate output file name
    output_file_name = title.replace(" ", "_") + "_features.txt"

    # create/open output file
    output_file = open( output_file_name, "a")
    output_file.write("chapter, text\n")

    while notAtEndOfFic == True:
        # sleep
        time.sleep(5)

        # get chapter for output
        chapter = get_chap(soup)
    
        # get list for tokenized fic
        tokens = clean_html(soup)

        # log instances of text feature and get total
        feature_total = log_text_feature(tokens, output_file, chapter, feature_total)
        
        # print thing total to screen
        print(feature_total)

        if is_there_another_chapter(soup) == True :
            url = get_next_chapter_url(soup)
            r = requests.get(url, headers=headers)
            soup = bs4.BeautifulSoup(r.text, 'lxml')
        else:
            output_file.close()
            notAtEndOfFic = False
            
    



main()