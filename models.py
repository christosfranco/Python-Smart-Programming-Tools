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

import pickle

fileXTrain = open('tfidfXTrain.p', 'rb')
fileYTrain = open('tfidfYTrain.p', 'rb')
fileXTest = open('tfidfXTest.p', 'rb')
fileYTest = open('tfidfYTest.p', 'rb')
# fileXVal = open('tfidfXVal.p', 'rb')
# fileYVal = open('tfidfYVal.p', 'rb')

print("files opened")

tfidfXTrain = pickle.load(fileXTrain)
tfidfYTrain = pickle.load(fileYTrain)
tfidfXTest = pickle.load(fileXTest)
tfidfYTest = pickle.load(fileYTest)
# tfidfXVal = pickle.load(fileXVal)
# tfidfYVal = pickle.load(fileYVal)

print("data loaded")


###LinearSVC######
clf = LinearSVC(random_state=0)
modelSVC = clf.fit(tfidfXTrain,tfidfYTrain)
print("model fitted")
predictionScore = modelSVC.score(tfidfXTest, tfidfYTest)
predict = modelSVC.predict(tfidfXTest)
print("predict calculated")
CM = metrics.confusion_matrix(tfidfYTest,predict)
NormalizedCM = CM.astype('float') / CM.sum(axis=1)[:, np.newaxis]
print("CM created")
#Print prediction of test
print(f"prediction : ", predictionScore)
print(f"Training Total: %s\n Non-Fake: %s\n Fake: %s" % (len(tfidfYTrain), tfidfYTrain.count(0), tfidfYTrain.count(1)))
print(f"Test Total: %s\n Non-Fake: %s\n Fake: %s" % (len(tfidfYTest), tfidfYTest.count(0), tfidfYTest.count(1)))
print(f"Non-normalized Confusion Matrix: \n%s" % CM)
print(f"normalized Confusion Matrix: \n%s" % NormalizedCM)
#print(f"True value : {type_mapping(y_test)}")
###LinearSVC######


###KNeighborsClassifier######
clf = KNeighborsClassifier(n_neighbors=5)
modelSVC = clf.fit(tfidfXTrain,tfidfYTrain)
print("model fitted")
predictionScore = modelSVC.score(tfidfXTest, tfidfYTest)
predict = modelSVC.predict(tfidfXTest)
print("predict calculated")
CM = metrics.confusion_matrix(tfidfYTest,predict)
NormalizedCM = CM.astype('float') / CM.sum(axis=1)[:, np.newaxis]
print("CM created")
#Print prediction of test
print(f"prediction : ", predictionScore)
print(f"Training Total: %s\n Non-Fake: %s\n Fake: %s" % (len(tfidfYTrain), tfidfYTrain.count(0), tfidfYTrain.count(1)))
print(f"Test Total: %s\n Non-Fake: %s\n Fake: %s" % (len(tfidfYTest), tfidfYTest.count(0), tfidfYTest.count(1)))

print(f"Non-normalized Confusion Matrix: \n%s" % CM)
print(f"normalized Confusion Matrix: \n%s" % NormalizedCM)
###KNeighborsClassifier######


###DecisionTreeClassifier######
clf = DecisionTreeClassifier(random_state=0)
decTree = clf.fit(tfidfXTrain,tfidfYTrain)
print("model fitted")
predictionScore = decTree.score(tfidfXTest, tfidfYTest)
predict = decTree.predict(tfidfXTest)
print("predict calculated")
CM = metrics.confusion_matrix(tfidfYTest,predict)
NormalizedCM = CM.astype('float') / CM.sum(axis=1)[:, np.newaxis]
print("CM created")
#Print prediction of test
print(f"prediction : ", predictionScore)
print(f"Training Total: %s\n Non-Fake: %s\n Fake: %s" % (len(tfidfYTrain), tfidfYTrain.count(0), tfidfYTrain.count(1)))
print(f"Test Total: %s\n Non-Fake: %s\n Fake: %s" % (len(tfidfYTest), tfidfYTest.count(0), tfidfYTest.count(1)))
print(f"Non-normalized Confusion Matrix: \n%s" % CM)
print(f"normalized Confusion Matrix: \n%s" % NormalizedCM)
###DecisionTreeClassifier######