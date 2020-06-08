#====================================================================================#
#    Remeber to run the following commands in the terminal to create the database    #
#====================================================================================#

# sudo -u postgres psql

# CREATE DATABASE WikinewsFragment;

# CREATE USER user123 WITH ENCRYPTED PASSWORD 'pass123';

# GRANT ALL PRIVILEGES ON DATABASE WikinewsFragment TO user123;

# GRANT pg_read_server_files TO user123;





import psycopg2
from psycopg2 import connect, extensions, sql, Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


sql_query_create_and_load_database = """
DROP TABLE IF EXISTS Time, References_sources, Tags, Webpage, Article, Typ, Domain, Source, Keyword CASCADE;


CREATE TABLE Time
(
  time_id serial NOT NULL,
  time timestamp NOT NULL,
  PRIMARY KEY (time_id)
);

CREATE TABLE Typ
(
  type_id serial NOT NULL,
  type_name varchar(64) NOT NULL,
  PRIMARY KEY (type_id),
  UNIQUE (type_name)
);

CREATE TABLE Keyword
(
  keyword_id serial NOT NULL,
  keyword_name varchar(128),
  PRIMARY KEY (keyword_id),
  UNIQUE (keyword_name)
);

CREATE TABLE Source
(
  source_id serial NOT NULL,
  source varchar(128) NOT NULL,
  PRIMARY KEY (source_id),
  UNIQUE (source)
);

CREATE TABLE Domain
(
  domain_id serial NOT NULL,
  domain_url varchar(1024) NOT NULL,
  PRIMARY KEY (domain_id)
);

CREATE TABLE Article
(
  article_id serial NOT NULL,
  title text NOT NULL,
  content text NOT NULL,
  type_id integer NOT NULL,
  written_at_time_id  integer NOT NULL,
  scraped_at_time_id integer NOT NULL,
  PRIMARY KEY (article_id),
  FOREIGN KEY (written_at_time_id)  REFERENCES Time(time_id),
  FOREIGN KEY (scraped_at_time_id) REFERENCES Time(time_id),
  FOREIGN KEY (type_id) REFERENCES Typ(type_id)
);

CREATE TABLE Webpage 
(
  article_id integer REFERENCES Article(article_id),
  url varchar(1024),
  domain_id integer REFERENCES Domain(domain_id)
);

CREATE TABLE Tags
(
  article_id integer NOT NULL,
  keyword_id integer NOT NULL,
  PRIMARY KEY (article_id, keyword_id),
  FOREIGN KEY (article_id) REFERENCES Article(article_id),
  FOREIGN KEY (keyword_id) REFERENCES Keyword(keyword_id)
);

CREATE TABLE References_sources
(
  article_id integer NOT NULL,
  source_id integer NOT NULL,
  PRIMARY KEY (article_id, source_id),
  FOREIGN KEY (article_id) REFERENCES Article(article_id),
  FOREIGN KEY (source_id) REFERENCES Source(source_id)
);



COPY time               FROM '/home/marcus/Desktop/Studie/Data Science/Project_Data_Science/WikinewsFragment/CreateAndPopulateWikinewsDatabase/csv-files/time.csv'        DELIMITER '<' CSV;
COPY keyword            FROM '/home/marcus/Desktop/Studie/Data Science/Project_Data_Science/WikinewsFragment/CreateAndPopulateWikinewsDatabase/csv-files/keyword.csv'     DELIMITER '<' CSV;
COPY source             FROM '/home/marcus/Desktop/Studie/Data Science/Project_Data_Science/WikinewsFragment/CreateAndPopulateWikinewsDatabase/csv-files/source.csv'      DELIMITER '<' CSV;
COPY typ                FROM '/home/marcus/Desktop/Studie/Data Science/Project_Data_Science/WikinewsFragment/CreateAndPopulateWikinewsDatabase/csv-files/type.csv'        DELIMITER '<' CSV;
COPY domain             FROM '/home/marcus/Desktop/Studie/Data Science/Project_Data_Science/WikinewsFragment/CreateAndPopulateWikinewsDatabase/csv-files/domain.csv'      DELIMITER '<' CSV;
COPY article            FROM '/home/marcus/Desktop/Studie/Data Science/Project_Data_Science/WikinewsFragment/CreateAndPopulateWikinewsDatabase/csv-files/article.csv'     DELIMITER '^' QUOTE '}' CSV ;
COPY tags               FROM '/home/marcus/Desktop/Studie/Data Science/Project_Data_Science/WikinewsFragment/CreateAndPopulateWikinewsDatabase/csv-files/tags.csv'        DELIMITER ',' CSV;
COPY References_sources FROM '/home/marcus/Desktop/Studie/Data Science/Project_Data_Science/WikinewsFragment/CreateAndPopulateWikinewsDatabase/csv-files/references.csv'  DELIMITER ',' CSV;
COPY webpage            FROM '/home/marcus/Desktop/Studie/Data Science/Project_Data_Science/WikinewsFragment/CreateAndPopulateWikinewsDatabase/csv-files/webpage.csv'     DELIMITER '^' CSV;"""


# Establishing the connection
conn = psycopg2.connect(
   database="wikinewsfragment", user='user123', password='pass123', host='127.0.0.1', port= '5432'
)

# Set the isolation level
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Creating a cursor object using the cursor() method
cursor = conn.cursor()

# Execute SQL commands
cursor.execute(sql_query_create_and_load_database)

# Close the cursor to avoid memory leaks
cursor.close()

# Close the connection to avoid memory leaks
conn.close()