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

# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# import torch.optim as optim
# from torch.utils.data import TensorDataset, DataLoader

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
batch_size = 10000 # whatever

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

print(f"real and fake divided")

close_connection(conn, cursor)
print("connection closed")

#Make sure we have an equal distrituion of Fake and non-fake in article_labels
#choose value that has the most quantity over label

k = 0
population = []
result_labels = []
result_content = []

#make list that contains randomrows from the lesser type
if fakeCount > realCount*1.02:
    Content = fake_content
    Labels = fake_labels

    k = realCount
    population = fakeCount

    randomRows = np.random.randint(population,size=k)
    
    result_labels = real_labels
    result_content = real_content
elif realCount > fakeCount*1.02:
    Content = real_content
    Labels = real_labels

    k = fakeCount
    population = realCount

    randomRows = np.random.randint(population,size=k)
    
    result_labels = fake_labels
    result_content = fake_content
else:
    pass

resultcount = 0
#Append to result
for i in randomRows:
    resultcount += 1
    result_labels.append(Labels[i])
    result_content.append(Content[i])
#reset arrays
fake_labels = []
real_labels = []
fake_content = []
real_content = []
print(fake_labels)

print("fakecount: %i realcount %i resultcount: %i" % (fakeCount, realCount, resultcount))

labels = open('labels.p', 'wb')
print("labels openened")
pickle.dump(result_labels, labels, protocol=None)
labels.close()

content = open('content.p', 'wb')
print("content openened")
pickle.dump(result_content, content, protocol=None)
content.close()

#Here do something with GENSIM TENSOR DATA
# MAX_NUM_WORDS = 10000
# MAX_SEQUENCE_LENGTH = 1000

# tokens = list()
# dataArr = np.empty((9999,MAX_SEQUENCE_LENGTH),dtype=int)
# #for offset in xrange(0, resultcount, batch_size):
# #result_content[offset:offset+batch_size-1].copy()
# for text in result_content:
#     tokens.append(simple_preprocess(text))

# dictionary = Dictionary(tokens)
# dictionary.filter_extremes(no_below=0.05, no_above=0.95,
#                         keep_n=MAX_NUM_WORDS-2)

# word_index = dictionary.token2id
# print('found %s unique tokens.' % len(word_index))

# data = [dictionary.doc2idx(t) for t in tokens]

# #concatenate and pad sequences
# data = [i[:MAX_SEQUENCE_LENGTH] for i in data]
# data = np.array([np.pad(i,(0, MAX_SEQUENCE_LENGTH-len(i)), mode='constant', constant_values=-2) for i in data], dtype=int)
# print('shape of conc', data.shape)
# #print('shape of Arr', dataArr.shape)

# #np.append(dataArr, data ,axis =0)
# #dataArr = dataArr + 2
# data = data + 2

# print('shape of data tensor ', data.shape)
# print('length of label vector ', len(result_labels))



# #Split the dataset into train and test here
# # create training and testing vars
# #Stratify ensures equal distribution of fake/non-fake over test and train
# VALIDATION_SET, TEST_SET = 0.1, 0.25
# X_Train, X_Test, y_train, y_test = train_test_split(data, result_labels, test_size=TEST_SET, shuffle=True, stratify=result_labels)

# data = []

# X_Train, X_Val, y_train, y_Val = train_test_split(X_Train, y_train, test_size=VALIDATION_SET, shuffle=True, stratify=y_train)

# print("Data split")
# print(len(X_Train) , len(X_Test), len(y_train),len(y_test))

# fileXTrain = open('XTrain.p', 'wb')
# print("fileXTrain openened")
# pickle.dump(X_Train, fileXTrain, protocol=None)
# fileXTrain.close()

# fileYTrain = open('YTrain.p', 'wb')
# print("fileYTrain openened")
# pickle.dump(y_train, fileYTrain, protocol=None)
# fileYTrain.close()

# fileXTest = open('XTest.p', 'wb')
# print("fileXTest openened")
# pickle.dump(X_Test, fileXTest, protocol=None)
# fileXTest.close()

# fileYTest = open('YTest.p', 'wb')
# print("fileYTest openened")
# pickle.dump(y_test, fileYTest, protocol=None)
# fileYTest.close()

# fileXVal = open('XVal.p', 'wb')
# print("fileXVal openened")
# pickle.dump(X_Val, fileXVal, protocol=None)
# fileXVal.close()

# fileYVal = open('YVal.p', 'wb')
# print("fileYVal openened")
# pickle.dump(y_Val, fileYVal, protocol=None)
# fileYVal.close()