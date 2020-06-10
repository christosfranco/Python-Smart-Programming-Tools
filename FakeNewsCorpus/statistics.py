import psycopg2
from psycopg2 import connect, extensions, sql, Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
import pandas.io.sql as sqlio
import matplotlib.pyplot as plt

sql_number_of_articles = """
SELECT count(*)
FROM fakenewscorpus.article;
"""

sql_type_distribution = """
SELECT count(*),
       type_name
FROM fakenewscorpus.article
NATURAL JOIN fakenewscorpus.typ
GROUP BY type_name
ORDER BY COUNT DESC;"""

sql_domain_distribution = """
SELECT count(*),
       domain_url,
       type_name
FROM fakenewscorpus.article
NATURAL JOIN fakenewscorpus.webpage
NATURAL JOIN fakenewscorpus.domain
NATURAL JOIN fakenewscorpus.typ
GROUP BY domain_url,
         type_name
ORDER BY COUNT DESC
LIMIT 20;"""

sql_type_and_content_length_distribution = """
SELECT type_name,
       avg(content_length) AS avg_content_length
FROM
  (SELECT article_id,
          title,
          length(content) AS content_length,
          type_id
   FROM fakenewscorpus.Article) AS tmpTable
NATURAL JOIN fakenewscorpus.typ
GROUP BY type_name
ORDER BY avg_content_length DESC;"""

sql_type_word_count_distribution = """
SELECT type_name,
       avg(word_count) AS avg_word_count
FROM
  (SELECT article_id,
          length(replace(content, ' ', '')) AS content_length_no_spaces,
          length(content) - length(replace(content, ' ', '')) AS word_count,
          type_id
   FROM fakenewscorpus.Article) AS tmpTable
NATURAL JOIN fakenewscorpus.typ
GROUP BY type_name
ORDER BY avg_word_count DESC;"""

sql_type_word_length_distribution = """
SELECT type_name,
       avg(content_length_no_spaces) / avg(word_count) AS avg_word_length
FROM
  (SELECT article_id,
          length(replace(content, ' ', '')) AS content_length_no_spaces,
          length(content) - length(replace(content, ' ', '')) AS word_count,
          type_id
   FROM fakenewscorpus.Article) AS tmpTable
NATURAL JOIN fakenewscorpus.typ
GROUP BY type_name
ORDER BY avg_word_length DESC;"""

sql_type_keyword_distribution = """
SELECT type_name, 
       Avg(keyword_count) AS avg_keyword_count 
FROM   (SELECT article_id, 
               Count(*) AS keyword_count 
        FROM   fakenewscorpus.tags 
        GROUP  BY article_id) AS tmpTable 
       natural JOIN fakenewscorpus.article 
       natural JOIN fakenewscorpus.typ 
GROUP  BY type_name 
ORDER  BY avg_keyword_count DESC;"""


# Establishing the connection
conn = psycopg2.connect(
   database="fakenewsproject", user='user123', password='pass123', host='127.0.0.1', port= '5432'
)

df0 = sqlio.read_sql_query(sql_number_of_articles, conn)

df1 = sqlio.read_sql_query(sql_type_distribution, conn)

df2 = sqlio.read_sql_query(sql_domain_distribution, conn)

# Averages: Content length, word count, word length, and keyword count
df3 = sqlio.read_sql_query(sql_type_and_content_length_distribution, conn)
df4 = sqlio.read_sql_query(sql_type_word_count_distribution, conn)
df5 = sqlio.read_sql_query(sql_type_word_length_distribution, conn)
df6 = sqlio.read_sql_query(sql_type_keyword_distribution, conn)



# Close the connection to avoid memory leaks
conn.close()

print(df0)

df1.plot(kind='bar', x='type_name',y='count', color=(0.2, 0.4, 0.6, 0.6), legend=False, title='The distribution of the number of articles for each type')
plt.ylabel('Number of articles')
plt.xlabel('Types')

df2["label"] = df2["domain_url"] + "\n" +  df2["type_name"]
df2.plot(kind='bar', x='label',y='count', color=(0.2, 0.4, 0.6, 0.6), legend=False, title='The distribution of the number of articles of from the 20 domains with the most articles')
plt.ylabel('Number of articles')
plt.xlabel('The 20 domains with most articles and each domain\'s type')

df3.plot(kind='bar', x='type_name',y='avg_content_length', color=(0.2, 0.4, 0.6, 0.6), legend=False, title='The distribution of the average content length for each type')
plt.ylabel('Average content length')
plt.xlabel('Types')

df4.plot(kind='bar', x='type_name',y='avg_word_count', color=(0.2, 0.4, 0.6, 0.6), legend=False, title='The distribution of the average number of words for each type')
plt.ylabel('Average number of words')
plt.xlabel('Types')

df5.plot(kind='bar', x='type_name',y='avg_word_length', color=(0.2, 0.4, 0.6, 0.6), legend=False, title='The distribution of the average word length for each type')
plt.ylabel('Average word length')
plt.xlabel('Types')

df6.plot(kind='bar', x='type_name',y='avg_keyword_count', color=(0.2, 0.4, 0.6, 0.6), legend=False, title='The distribution of the average number of keywords for each type')
plt.ylabel('Average number of keywords')
plt.xlabel('Types')

plt.show()
