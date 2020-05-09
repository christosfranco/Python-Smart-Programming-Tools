import psycopg2
from psycopg2 import connect, extensions, sql, Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline

#number of articles used in total from dataset
ARTICLE_COUNT = 1000

#TEST
test_text = """
The failures of the intelligence community before the Iraq war the gullibility of much of the western media
as well as the cynical manipulation of both by the political class of the day, provide us with a stark reminder 
of what can go radically wrong On 8 September 2002 the New York Times published one of this century’s most
"""

test_label = 10
#TEST


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

conn, cursor = create_connection()


cursor.execute(f'''
SELECT content, type_id
FROM article
WHERE type_id IS NOT NULL
LIMIT {ARTICLE_COUNT};
''')

results = cursor.fetchall()

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
    reliable = [1, 3, 8] 
    fake = [0,1,4,5,6,7,9,10,11]
    return int(type_id in fake)

#Split the dataset into train and test here


#Text of train articles 
article_contents = [i[0] for i in results]
#label of train articles
article_labels = [type_mapping(i[1]) for i in results]

article_clf = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LinearSVC(random_state=0)), #maybe add more options here
])

#This fits a model
article_clf.fit(article_contents, article_labels)

#Print prediction of test
print(f"prediction :  {article_clf.predict([test_text])}")
print(f"True value : {type_mapping(test_label)}")
