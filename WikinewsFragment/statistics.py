import psycopg2
from psycopg2 import connect, extensions, sql, Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
import pandas.io.sql as sqlio
import matplotlib.pyplot as plt
import numpy as np

sql_number_or_articles = """
SELECT count(*)
FROM wikinewsfragment.article;"""

sql_dates_distribution = """
SELECT count(*),
       time
FROM wikinewsfragment.article
INNER JOIN wikinewsfragment.time ON wikinewsfragment.article.written_at_time_id = wikinewsfragment.time.time_id
GROUP BY time
ORDER BY COUNT DESC;"""

sql_avg_min_max_number_of_keywords = """
SELECT Avg(keyword_count) AS avg_keyword_count,
       Min(keyword_count) AS min_keyword_count,
       Max(keyword_count) AS max_keyword_count
FROM
  (SELECT article_id,
          Count(*) AS keyword_count
   FROM wikinewsfragment.tags GROUP  BY article_id) AS tmpTable
NATURAL JOIN wikinewsfragment.article;"""

sql_distribution_of_word_count = """
SELECT word_count,
       count(*)
FROM
  (SELECT length(content) - length(replace(content, ' ', '')) AS word_count
   FROM wikinewsfragment.article) AS tmpTable
GROUP BY word_count
ORDER BY word_count;"""

sql_avg_min_max_number_of_words = """
SELECT avg(word_count) AS avg_word_count,
       min(word_count) AS min_word_count,
       max(word_count) AS max_word_count
FROM
  (SELECT length(content) - length(replace(content, ' ', '')) AS word_count
   FROM wikinewsfragment.article) AS tmpTable;"""


# Establishing the connection
conn = psycopg2.connect(
   database="fakenewsproject", user='user123', password='pass123', host='127.0.0.1', port= '5432'
)

df1 = sqlio.read_sql_query(sql_number_or_articles, conn)

df2 = sqlio.read_sql_query(sql_dates_distribution, conn)

df3 = sqlio.read_sql_query(sql_avg_min_max_number_of_keywords, conn)

df4 = sqlio.read_sql_query(sql_distribution_of_word_count, conn)

df5 = sqlio.read_sql_query(sql_avg_min_max_number_of_words, conn)


# Close the connection to avoid memory leaks
conn.close()

print(df1)

df2 = df2.groupby(pd.DatetimeIndex(df2['time']).year).sum()
df2['time'] = df2.index
df2.plot(kind='bar', x='time',y='count', color=(0.2, 0.4, 0.6, 0.6), title='The number of articles per year')
plt.xlabel('Years (The year 1677 is a default that is used for articles with no dates)')
plt.ylabel('Number of articles')

print(df3)

plt.figure()
plt.hist(df4['word_count'], 
         range=(0, df4['word_count'].max()+1), 
         bins=200)       
plt.xticks(np.arange(0, df4['word_count'].max()+1, 200.0))
plt.xlabel('Number of words')
plt.ylabel('Number of articles')
plt.title('The distribution of the number of articles containing a specific number of words')
print(df5)

plt.show()