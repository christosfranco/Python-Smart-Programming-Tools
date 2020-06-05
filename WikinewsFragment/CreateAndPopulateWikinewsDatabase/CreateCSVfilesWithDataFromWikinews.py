import csv
import datetime
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
        file.write("%s,%s\n" %(str(item[1]), str(item[0])))
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
    
    global ID_author
    global ID_domain
    global ID_keyword
    global ID_type 
    global ID_article
    global ID_time
    
    
    for index, row in chunk.iterrows():
        # Authors  
        authors = row['authors']
        if(not isNaN(authors)):
            list_of_authors = authors.split(", ")
            for author in list_of_authors:
                if(len(author) <= 64 and (author not in author_dictionary)):
                    author_dictionary[author] = ID_author
                    ID_author += 1
        
        
        
        # Meta keywords and Tags
        keywords = row['meta_keywords']
        if(not isNaN(keywords)):
            list_of_keywords = list(dict.fromkeys(re.split(r'[;,"\'\[\]]\s*', keywords)))
            for keyword in list_of_keywords:
                if(len(keyword) <= 128 and len(keyword) > 0): 
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
        scrapped_at_time_id = 0
        scrapped_at = row['scraped_at']
        if(isNaN(scrapped_at)):
            scrapped_at = datetime.datetime(1000, 1, 1)
        if (scrapped_at not in time_dictionary):
            time_dictionary[scrapped_at] = ID_time
            scrapped_at_time_id = ID_time
            ID_time += 1
        else:
            scrapped_at_time_id = time_dictionary.get(scrapped_at)
            
        inserted_at_time_id = 0    
        inserted_at = row['inserted_at']
        if(isNaN(inserted_at)):
            inserted_at = datetime.datetime(1000, 1, 1)
        if (inserted_at not in time_dictionary):
            time_dictionary[inserted_at] = ID_time
            inserted_at_time_id = ID_time
            ID_time += 1
        else:
            inserted_at_time_id = time_dictionary.get(inserted_at)    
            
        updated_at_time_id = 0 
        updated_at  = row['updated_at']
        if(isNaN(updated_at)):
            updated_at = datetime.datetime(1000, 1, 1)
        if (updated_at not in time_dictionary):
            time_dictionary[updated_at] = ID_time
            updated_at_time_id = ID_time
            ID_time += 1
        else:
            updated_at_time_id = time_dictionary.get(updated_at)    
        
        
        
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
        
        summary = row['summary']
        if(summary and (not isNaN(summary))):
            summary = clean_text(summary)
        else:
            summary = "NULL"
        
        meta_description = row['meta_description']
        if(meta_description and (not isNaN(meta_description))):
            meta_description = clean_text(meta_description)
        else:
            meta_description = "NULL"
        
        typ = row['type']
        if((not isNaN(typ)) and (len(typ) <= 64)):
            type_id = type_dictionary[typ]
        else:
            type_id = 0

        csv_article.write("%s^\"%s\"^\"%s\"^\"%s\"^\"%s\"^%s^%s^%s^%s\n"%
            (ID_article
             , title
             , content
             , summary
             , meta_description
             , type_id
             , scrapped_at_time_id
             , inserted_at_time_id
             , updated_at_time_id))
        
        
        
        # Webpage
        url = row['url']
        domain = row['domain']
        if((not isNaN(url)) and (not isNaN(domain)) and (len(url) <= 1024) and (len(domain) <= 1024)):
            csv_webpage.write("%s^%s^%s\n" % (ID_article, url, domain_dictionary[domain]))
        
        
        
        # Writen_by
        authors = row['authors']
        if(not isNaN(authors)):
            list_of_authors = authors.split(", ")
            for author in list_of_authors:
                if(len(author) <= 64):
                    csv_written_by.write("%s,%s\n" % (ID_article, author_dictionary[author]))
                    

        ID_article += 1


csv_author     = create_empty_file_for_writing('csv-files/author.csv')
csv_keyword    = create_empty_file_for_writing('csv-files/keyword.csv')
csv_domain     = create_empty_file_for_writing('csv-files/domain.csv')
csv_type       = create_empty_file_for_writing('csv-files/type.csv')
csv_article    = create_empty_file_for_writing('csv-files/article.csv')
csv_written_by = create_empty_file_for_writing('csv-files/written_by.csv')
csv_tags       = create_empty_file_for_writing('csv-files/tags.csv')
csv_webpage    = create_empty_file_for_writing('csv-files/webpage.csv')
csv_time       = create_empty_file_for_writing('csv-files/time.csv')

# Initialize the dictionaries
author_dictionary  = dict()
domain_dictionary  = dict() 
type_dictionary    = dict()
keyword_dictionary = dict()   
time_dictionary    = dict()

# Used to generate ID's in the csv files
ID_author = ID_domain = ID_keyword = ID_type = ID_article = ID_time = 0

# Process and store the stuff 
CHUNK_SIZE = 100000

with open(csv_in, 'r', newline='',encoding='utf-8', errors='replace') as csvfile:
    reader = pd.read_csv(csvfile, chunksize=CHUNK_SIZE,
                         encoding='utf-8',
                         parse_dates=['scraped_at','inserted_at','updated_at'])
    chunk_idx = 1 # Used to see how far the reading process is
    for chunk in reader:
        extract_and_put_in_csv_files(chunk)
        print(str(CHUNK_SIZE * chunk_idx) + " rows have been read.")
        chunk_idx += 1
    
    simple_entity_to_CSV("csv-files/author.csv", "author_id", "author_name", author_dictionary)
    simple_entity_to_CSV("csv-files/keyword.csv", "keyword_id", "keyword_name", keyword_dictionary)
    simple_entity_to_CSV("csv-files/domain.csv", "domain_id", "domain_url", domain_dictionary)    
    simple_entity_to_CSV("csv-files/type.csv", "type_id", "type_name", type_dictionary)
    simple_entity_to_CSV("csv-files/time.csv", "time_id", "time", time_dictionary)
csvfile.close()