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
    #reliable = [1] 
    fake = [0,2,3,4,5,6,7,8,9,10,11]
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

article_contents = []
article_labels = []
# fake = np.array([[],[]])
# real = np.array([[],[]])
fakeCount = 0
realCount = 0
for offset in xrange(0, count, batch_size):
    cursor.execute(
        "SELECT content, type_id FROM article WHERE type_id IS NOT NULL LIMIT %s OFFSET %s", (batch_size, offset))
    print(offset)
    for row in cursor:
        # if type_mapping(row[1]):
        #     np.concatenate(fake[0], row[0])
        #     np.concatenate(fake[1],(type_mapping(row[1])))
        #     fakeCount += 1
        # else:
        #     np.concatenate(real[0],row[0])
        #     np.concatenate(real[1],(type_mapping(row[1])))
        #     realCount += 1
        article_contents.append(row[0])
        article_labels.append(type_mapping(row[1]))


close_connection(conn, cursor)

print("connection closed")

#Make sure we have an equal distrituion of Fake and non-fake in article_labels
#choose value that has the most quantity over label

fake_labels = []
real_labels = []
fake_content = []
real_content = []
for i in range(len(article_labels)):
    if article_labels[i] == 1:
        fakeCount += 1
        fake_labels.append(article_labels[i])
        fake_content.append(article_contents[i])
    else:
        realCount += 1
        real_labels.append(article_labels[i])
        real_content.append(article_contents[i])

print(f"real and fake divided")

k = 0
# population = np.array([[],[]])
# result = np.array([[],[]])
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
    # for i in randomRows:
    #     np.concatenate(result,(population[i,:]))
    # np.concatenate(result,lessAttribute)
else:
    pass


#print("fakecount: %i realcount %i lessAttribute %s" % (fakeCount, realCount, lessAttribute, ))
#print(len(result))
#make list that contains all with the lesser quantity and equal/near equal amount from the opposite

tokens = list()
for text in result_content:
  tokens.append(simple_preprocess(text))

MAX_NUM_WORDS = 10000
MAX_SEQUENCE_LENGTH = 1000

dictionary = Dictionary(tokens)
dictionary.filter_extremes(no_below=0.05, no_above=0.95,
                           keep_n=MAX_NUM_WORDS-2)

word_index = dictionary.token2id
print('found %s unique tokens.' % len(word_index))

data = [dictonary.doc2idx(t) for t in tokens]

#concatenate and pad sequences
data = [i[MAX_SEQUENCE_LENGTH] for i in data]
data = np.array([np.pad(i,(0, MAX_SEQUENCE_LENGTH-len(i)),
                        mode='constant', constant_values=-2)
                for i in data], dtype=int)
data = data + 2

print('shape of data tensor ', data_shape)
print('length of label vector ', len(result_labels))



#Split the dataset into train and test here
# create training and testing vars
#Stratify ensures equal distribution of fake/non-fake over test and train
VALIDATION_SET, TEST_SET = 0.1, 0.25
X_train, X_test, y_train, y_test = train_test_split(data, result_labels, test_size=TEST_SET, shuffle=True, stratify=result_labels)

X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=VALIDATION_SET, shuffle=False, stratify=y_train)

print("Data split")
print(len(X_train) , len(X_test), len(y_train),len(y_test))

fileXTrain = open('XTrain.p', 'wb')
print("fileXTrain openened")
pickle.dump(X_Train, fileXTrain, protocol=None)
fileXTrain.close()

fileYTrain = open('YTrain.p', 'wb')
print("fileYTrain openened")
pickle.dump(y_train, fileYTrain, protocol=None)
fileYTrain.close()

fileXTest = open('XTest.p', 'wb')
print("fileXTest openened")
pickle.dump(X_Test, fileXTest, protocol=None)
fileXTest.close()

fileYTest = open('YTest.p', 'wb')
print("fileYTest openened")
pickle.dump(y_test, fileYTest, protocol=None)
fileYTest.close()

fileXVal = open('XVal.p', 'wb')
print("fileXVal openened")
pickle.dump(X_Val, fileXVal, protocol=None)
fileXVal.close()

fileYVal = open('YVal.p', 'wb')
print("fileYVal openened")
pickle.dump(y_Val, fileYVal, protocol=None)
fileYVal.close()