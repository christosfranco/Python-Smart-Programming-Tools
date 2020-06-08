# coding=<utf-8>
import psycopg2
from psycopg2 import connect, extensions, sql, Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import numpy as np
import pandas as pd
import itertools
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
import random
import pickle
import os
import sys
import csv

from gensim.utils import simple_preprocess
from gensim.corpora import Dictionary

#number of articles used in total from dataset
ARTICLE_COUNT = 1000000


def create_connection():
    # Establishing the connection
    conn = psycopg2.connect(
        database="fakenews", user='user123', password='pass123', host='127.0.0.1', port= '5432'
    )
    # Set the isolation level
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    return conn, cursor

def close_connection(conn, cursor):
    # Close the cursor to avoid memory leaks
    cursor.close()

    # Close the connection to avoid memory leaks
    conn.close()

def type_mapping(type_id):
    """
    0  | junkscience
    1  | reliable
    2  | hate
    3  | political
    4  | clickbait
    5  | unknown
    6  | fake
    7  | conspiracy
    8  | satire
    9  | unreliable
    10 | rumor
    11 | bias
    """
    #reliable = [1,3,8] 
    fake = [0,2,5,6,4,7,9,10,11]
    return int(type_id in fake)



conn, cursor = create_connection()

# py2 / py3 compatibility
try:
    # xrange is defined in py2 only
    xrange
except NameError:
    # py3 range is actually p2 xrange
    xrange = range

cursor.execute("SELECT count(*) FROM article")
count = cursor.fetchone()[0]
batch_size = 100000 # whatever

fake_labels = []
real_labels = []
fake_content = []
real_content = []
fakeCount = 0
realCount = 0
for offset in xrange(0, count, batch_size):
    cursor.execute(
        "SELECT content, type_id FROM article WHERE type_id IS NOT NULL LIMIT %s OFFSET %s", (batch_size, offset))
    print(offset)
    for row in cursor:
        typ = type_mapping(row[1])
        if (typ == 1):
            fake_content.append(row[0])
            fake_labels.append(typ)
            fakeCount += 1
        else:
            real_content.append(row[0])
            real_labels.append(typ)
            realCount += 1


close_connection(conn, cursor)

print("connection closed")

#Make sure we have an equal distrituion of Fake and non-fake in article_labels
#choose value that has the most quantity over label

print(f"real and fake divided")

k = 0
population = []
result_labels = []
result_content = []


if fakeCount > realCount*1.02:
    Content = fake_content
    Labels = fake_labels

    k = realCount
    population = fakeCount

    randomRows = np.random.randint(population,size=k)
    
    result_labels = real_labels
    result_content = real_content

    for i in randomRows:
        result_labels.append(Labels[i])
        result_content.append(Content[i])
elif realCount > fakeCount*1.02:
    Content = real_content
    Labels = real_labels

    k = fakeCount
    population = realCount

    randomRows = np.random.randint(population,size=k)
    
    result_labels = fake_labels
    result_content = fake_content

    for i in randomRows:
        result_labels.append(Labels[i])
        result_content.append(Content[i])
else:
    pass

fake_labels = []
real_labels = []
fake_content = []
real_content = []
print("fakecount: %i realcount %i resultcount: %i" % (fakeCount, realCount, resultcount))

#Split the dataset into train and test here
# create training and testing vars
#Stratify ensures equal distribution of fake/non-fake over test and train
VALIDATION_SET, TEST_SET = 0.1, 0.25
X_train, X_test, y_train, y_test = train_test_split(result_content, result_labels, test_size=TEST_SET, shuffle=True, stratify=result_labels)

result_labels = []
result_content = []
#X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=VALIDATION_SET, shuffle=False, stratify=y_train)


print("Data split")
print(len(X_train) , len(X_test), len(y_train),len(y_test))


#ignore vectors that are in more than 90% and less than 5% of articles
tfidf = TfidfVectorizer(stop_words='english',max_df =0.9,min_df=0.05)
print("vectorizer created")

tfidfXTrain = tfidf.fit_transform(X_train)
print("Xtrain transformed")

tfidfXTest = tfidf.transform(X_test)
print("xtest transformed")

# tfidfXVal = tfidf.transform(X_val)
# print("xval transformed")

fileXTrain = open('tfidfXTrain.p', 'wb')
print("fileXTrain openened")
pickle.dump(tfidfXTrain, fileXTrain, protocol=None)
fileXTrain.close()

fileYTrain = open('tfidfYTrain.p', 'wb')
print("fileYTrain openened")
pickle.dump(y_train, fileYTrain, protocol=None)
fileYTrain.close()

fileXTest = open('tfidfXTest.p', 'wb')
print("fileXTest openened")
pickle.dump(tfidfXTest, fileXTest, protocol=None)
fileXTest.close()

fileYTest = open('tfidfYTest.p', 'wb')
print("fileYTest openened")
pickle.dump(y_test, fileYTest, protocol=None)
fileYTest.close()

# fileXVal = open('tfidfXVal.p', 'wb')
# print("fileXVal openened")
# pickle.dump(tfidfXVal, fileXVal, protocol=None)
# fileXVal.close()

# fileYVal = open('tfidfYVal.p', 'wb')
# print("fileYVal openened")
# pickle.dump(y_Val, fileYVal, protocol=None)
# fileYVal.close()
