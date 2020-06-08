import csv
import datetime as dtime
from datetime import datetime

from cleantext import clean
import re
import numpy as np
import pandas as pd

import psycopg2
from psycopg2 import connect, extensions, sql, Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import scrapy
from scrapy.crawler import CrawlerProcess

import sys
import os

import nltk
from nltk.tokenize import word_tokenize
import string
from nltk.corpus import stopwords


# Sample
csv_in = './../WikinewsScraping/wiki.csv'


def create_empty_file_for_writing(filename):
    if os.path.exists(filename):
        file = open(filename)
        file.close()
        os.remove(filename)
    return open(filename, "w")


def simple_entity_to_CSV(filename, idName, keyName, dictionary):
    file = open(filename,"a",encoding='utf-8')
    for item in dictionary.items():
        file.write("%s<%s\n" %(str(item[1]), str(item[0])))
    file.close


def clean_text(content):

    # split into words
    tokens = word_tokenize(content)
    
    # convert to lower case
    tokens = [w.lower() for w in tokens]
    
    # remove punctuation from the end of words
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    
    # remove remaining tokens that are not alphabetic
    words = [word for word in stripped if word.isalpha()]
    
    # filter out stop words
    stop_words = set(stopwords.words('english'))
    words = [w for w in words if not w in stop_words]
    
    #Join to one string
    seperator = ' '
    clean_text = seperator.join(words)
    
    return clean_text

def isNaN(string):
    return string != string


def extract_and_put_in_csv_files(chunk):
    
    global ID_domain
    global ID_keyword
    global ID_type 
    global ID_article
    global ID_time
    global ID_source
    
    
    for index, row in chunk.iterrows():

        # Sources and References
        sources = row['sources']
        if(not isNaN(sources)):
            list_of_sources = list(dict.fromkeys(re.split(r'\", \"', sources[2:-2])))
            for source in list_of_sources:
                if(len(source) <= 128 and len(source) > 0): 
                    if (source not in source_dictionary):
                        source_dictionary[source] = ID_source
                        csv_references.write("%s,%s\n" % (ID_article, ID_source))
                        ID_source += 1
                    else:
                        csv_references.write("%s,%s\n" % (ID_article, source_dictionary.get(source)))            
        
        
        # Meta keywords and Tags
        keywords = row['keywords']
        if(not isNaN(keywords)):
            list_of_keywords = list(dict.fromkeys(re.split(r'\", \"', keywords[2:-2])))
            for keyword in list_of_keywords:
                if(len(keyword) <= 128 and len(keyword) > 0): 
                    keyword = keyword.lower()
                    if (keyword not in keyword_dictionary):
                        keyword_dictionary[keyword] = ID_keyword
                        csv_tags.write("%s,%s\n" % (ID_article, ID_keyword))
                        ID_keyword += 1
                    else:
                        csv_tags.write("%s,%s\n" % (ID_article, keyword_dictionary.get(keyword)))
        
        
        
        # Domain
        domain = row['domain']
        if(not isNaN(domain)):
            if(len(domain) <= 1024 and (domain not in domain_dictionary)):
                domain_dictionary[domain] = ID_domain
                ID_domain += 1
        
        
        
        # Type
        typ = row['type']
        if(not isNaN(typ)):
            if(len(typ) <= 64 and (typ not in type_dictionary)):
                type_dictionary[typ] = ID_type
                ID_type += 1
        
        
        
        # Time
        scraped_at_time_id = 0
        scraped_at = row['scraped_at']
        if(isNaN(scraped_at)):
            scraped_at = dtime.datetime(1000, 1, 1)
        if (scraped_at not in time_dictionary):
            time_dictionary[scraped_at] = ID_time
            scraped_at_time_id = ID_time
            ID_time += 1
        else:
            scraped_at_time_id = time_dictionary.get(scraped_at)    
            
        written_at_time_id = 0 
        written_at  = row['written_at']
        if(not isNaN(written_at) and written_at != 'Published'):
            written_at = datetime.strptime(written_at, '%B %d, %Y')     
        else:    
            written_at = dtime.datetime(1000, 1, 1)

        if (written_at not in time_dictionary):
            time_dictionary[written_at] = ID_time
            written_at_time_id = ID_time
            ID_time += 1
        else:
            written_at_time_id = time_dictionary.get(written_at)

        
        
        
        # Article
        title = row['title']
        if(title and (not isNaN(title)) and (len(title) <= 512)):
            title = clean_text(title)
        else:
            title = "NULL"
        
        content = row['content']
        if(not isNaN(content)):
            content = clean_text(content)
        else:
            content = "NULL"
        
        typ = row['type']
        if((not isNaN(typ)) and (len(typ) <= 64)):
            type_id = type_dictionary[typ]
        else:
            type_id = 0

        csv_article.write("%s^\"%s\"^\"%s\"^%s^%s^%s\n"%
            (ID_article
             , title
             , content
             , type_id
             , scraped_at_time_id
             , written_at_time_id))
        
        
        
        # Webpage
        url = row['url']
        domain = row['domain']
        if((not isNaN(url)) and (not isNaN(domain)) and (len(url) <= 1024) and (len(domain) <= 1024)):
            csv_webpage.write("%s^%s^%s\n" % (ID_article, url, domain_dictionary[domain]))
                    

        ID_article += 1


csv_source     = create_empty_file_for_writing('csv-files/source.csv')
csv_references = create_empty_file_for_writing('csv-files/references.csv')

csv_keyword    = create_empty_file_for_writing('csv-files/keyword.csv')
csv_tags       = create_empty_file_for_writing('csv-files/tags.csv')

csv_domain     = create_empty_file_for_writing('csv-files/domain.csv')
csv_webpage    = create_empty_file_for_writing('csv-files/webpage.csv')

csv_time       = create_empty_file_for_writing('csv-files/time.csv')

csv_type       = create_empty_file_for_writing('csv-files/type.csv')

csv_article    = create_empty_file_for_writing('csv-files/article.csv')

# Initialize the dictionaries
source_dictionary  = dict()
domain_dictionary  = dict() 
type_dictionary    = dict()
keyword_dictionary = dict()   
time_dictionary    = dict()

# Used to generate ID's in the csv files
ID_source = ID_domain = ID_keyword = ID_type = ID_article = ID_time = 0

# Process and store the stuff 
CHUNK_SIZE = 100000

with open(csv_in, 'r', newline='',encoding='utf-8', errors='replace') as csvfile:
    reader = pd.read_csv(csvfile, chunksize=CHUNK_SIZE,
                         encoding='utf-8',
                         parse_dates=['scraped_at','written_at'])
    chunk_idx = 1 # Used to see how far the reading process is
    for chunk in reader:
        extract_and_put_in_csv_files(chunk)
        print(str(CHUNK_SIZE * chunk_idx) + " rows have been read.")
        chunk_idx += 1
    
    simple_entity_to_CSV("csv-files/source.csv", "source_id", "source", source_dictionary)
    simple_entity_to_CSV("csv-files/keyword.csv", "keyword_id", "keyword_name", keyword_dictionary)
    simple_entity_to_CSV("csv-files/domain.csv", "domain_id", "domain_url", domain_dictionary)    
    simple_entity_to_CSV("csv-files/type.csv", "type_id", "type_name", type_dictionary)
    simple_entity_to_CSV("csv-files/time.csv", "time_id", "time", time_dictionary)
csvfile.close()