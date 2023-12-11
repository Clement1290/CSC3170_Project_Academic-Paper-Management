Create database GoogleScholar;
USE GoogleScholar;

CREATE TABLE Author (
author_link VARCHAR(100) PRIMARY KEY,
author_name VARCHAR(100),
h_index INT);

create TABLE Author_interests(
interest VARCHAR(1000),
author_link VARCHAR(100),
FOREIGN KEY (author_link) REFERENCES Author(author_link));


CREATE TABLE Paper(
ID VARCHAR(8) PRIMARY KEY,
title VARCHAR(1000),
paper_link VARCHAR(1000),
cited_number INT,
cited_link VARCHAR(1000),
related_paper_link VARCHAR(1000),
snippet VARCHAR(1000));

create table Paper_versions(
ID VARCHAR(8),
versions INT,
versions_link VARCHAR(1000),
FOREIGN KEY (ID) REFERENCES Paper(ID));

CREATE TABLE Organization(
org_name VARCHAR(100) PRIMARY KEY,
org_address VARCHAR(1000));

Create TABLE Journal(
journal_name VARCHAR(100) PRIMARY KEY);

Create TABLE Author_paper(
ID VARCHAR(8),
author_link VARCHAR(100),
FOREIGN KEY (ID) REFERENCES Paper(ID),
FOREIGN KEY (author_link) REFERENCES Author(author_link));

Create TABLE Related_paper(
ID VARCHAR(8),
related_ID VARCHAR(8),
FOREIGN KEY (ID) REFERENCES Paper(ID) ON DELETE CASCADE,
FOREIGN KEY (related_ID) REFERENCES Paper(ID) ON DELETE CASCADE) ;

Create TABLE Affiliate(
author_link VARCHAR(100),
org_name VARCHAR(100),
FOREIGN KEY (author_link) REFERENCES Author(author_link),
FOREIGN KEY (org_name) REFERENCES Organization(org_name));

Create TABLE Publishment(
ID VARCHAR(8),
journal_name VARCHAR(100),
publish_year year,
FOREIGN KEY (journal_name) REFERENCES Journal(journal_name),
FOREIGN KEY (ID) REFERENCES Paper(ID));


