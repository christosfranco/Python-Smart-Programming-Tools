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
from sklearn.dummy import DummyClassifier

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
print('\nLINEARSVC')
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
print(f"prediction score : ", predictionScore)
print(f"Training Total: %s\n Non-Fake: %s\n Fake: %s" % (len(tfidfYTrain), tfidfYTrain.count(0), tfidfYTrain.count(1)))
print(f"Test Total: %s\n Non-Fake: %s\n Fake: %s" % (len(tfidfYTest), tfidfYTest.count(0), tfidfYTest.count(1)))
print(f"Non-normalized Confusion Matrix: \n%s" % CM)
print(f"normalized Confusion Matrix: \n%s" % NormalizedCM)
###LinearSVC######


###KNeighborsClassifier######
# print(f'\nKNN')
# clf2 = KNeighborsClassifier(n_neighbors=1)
# modelKNN = clf2.fit(tfidfXTrain,tfidfYTrain)
# print("model fitted")
# predictionScore = modelKNN.score(tfidfXTest, tfidfYTest)
# predict = modelKNN.predict(tfidfXTest)
# print("predict calculated")
# CM = metrics.confusion_matrix(tfidfYTest,predict)
# NormalizedCM = CM.astype('float') / CM.sum(axis=1)[:, np.newaxis]
# print("CM created")
# #Print prediction of test
# print(f"prediction : ", predictionScore)
# print(f"Training Total: %s\n Non-Fake: %s\n Fake: %s" % (len(tfidfYTrain), tfidfYTrain.count(0), tfidfYTrain.count(1)))
# print(f"Test Total: %s\n Non-Fake: %s\n Fake: %s" % (len(tfidfYTest), tfidfYTest.count(0), tfidfYTest.count(1)))
# print(f"Non-normalized Confusion Matrix: \n%s" % CM)
# print(f"normalized Confusion Matrix: \n%s" % NormalizedCM)
###KNeighborsClassifier######


###Dummy######
print(f'\nDummy')
clf3 = DummyClassifier(random_state=0)
print(f'fitting')
modelTree = clf3.fit(tfidfXTrain,tfidfYTrain)
print("model fitted")
predictionScore = modelTree.score(tfidfXTest, tfidfYTest)
predict = modelTree.predict(tfidfXTest)
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
###dummy######

###DecisionTreeClassifier######
# print(f'\nTree')
# clf3 = DecisionTreeClassifier(random_state=0)
# print(f'fitting')
# modelTree = clf3.fit(tfidfXTrain,tfidfYTrain)
# print("model fitted")
# predictionScore = modelTree.score(tfidfXTest, tfidfYTest)
# predict = modelTree.predict(tfidfXTest)
# print("predict calculated")
# CM = metrics.confusion_matrix(tfidfYTest,predict)
# NormalizedCM = CM.astype('float') / CM.sum(axis=1)[:, np.newaxis]
# print("CM created")
# #Print prediction of test
# print(f"prediction : ", predictionScore)
# print(f"Training Total: %s\n Non-Fake: %s\n Fake: %s" % (len(tfidfYTrain), tfidfYTrain.count(0), tfidfYTrain.count(1)))
# print(f"Test Total: %s\n Non-Fake: %s\n Fake: %s" % (len(tfidfYTest), tfidfYTest.count(0), tfidfYTest.count(1)))
# print(f"Non-normalized Confusion Matrix: \n%s" % CM)
# print(f"normalized Confusion Matrix: \n%s" % NormalizedCM)
###DecisionTreeClassifier######