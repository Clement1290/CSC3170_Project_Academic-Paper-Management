from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import pymysql
import pandas as pd


DB_PASSWARD = "YOUR DATABASE PASSWARD"
app = FastAPI()

# 创建数据库连接
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:PASSWARD@USERNAME/googlescholar"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Author(Base):
    __tablename__ = "Author"

    author_link = Column(String(100), primary_key=True)
    author_name = Column(String(100))
    h_index = Column(Integer)

    interests = relationship("AuthorInterests", back_populates="author",cascade="all, delete")
    papers = relationship("Paper", secondary="Author_paper",cascade="all, delete")
    #organization = relationship("Orgnization", secondary="Affiliate")

class AuthorInterests(Base):
    __tablename__ = "Author_interests"
    #id = Column(Integer, primary_key=True, autoincrement=True)
    interest = Column(String(1000), primary_key= True)
    author_link = Column(String(100), ForeignKey("Author.author_link", ondelete="CASCADE"))

    author = relationship("Author", back_populates="interests")

class Paper(Base):
    __tablename__ = 'Paper'

    ID = Column(String(8), primary_key=True)
    title = Column(String(1000))
    paper_link = Column(String(1000))
    cited_number = Column(Integer)
    cited_link = Column(String(1000))
    related_paper_link = Column(String(1000))
    snippet = Column(String(1000))

    versions = relationship("Paper_versions", back_populates="paper", cascade="all, delete")
    authors = relationship("Author", secondary="Author_paper", back_populates="papers")
    publications = relationship("Publishment", back_populates="paper", cascade="all, delete")
    #related_papers = relationship("Related_paper", back_populates="paper",cascade="all, delete")
    

    

    
    

    

class Paper_versions(Base):
    __tablename__ = 'Paper_versions'

    ID = Column(String(8), ForeignKey('Paper.ID'), primary_key=True)
    versions = Column(Integer)
    versions_link = Column(String(1000))
    
    paper = relationship("Paper", back_populates="versions")

class Organization(Base):
    __tablename__ = 'Organization'

    org_name = Column(String(100), primary_key=True)
    org_address = Column(String(1000))


class Journal(Base):
    __tablename__ = 'Journal'

    journal_name = Column(String(100), primary_key=True)


class Author_paper(Base):
    __tablename__ = 'Author_paper'

    ID = Column(String(8), ForeignKey('Paper.ID',ondelete="CASCADE"), primary_key=True)
    author_link = Column(String(100), ForeignKey('Author.author_link',ondelete="CASCADE"), primary_key=True)
    
class Related_paper(Base):
    __tablename__ = 'Related_paper'

    ID = Column(String(8), ForeignKey('Paper.ID', ondelete="CASCADE"), primary_key=True)
    related_ID = Column(String(8), ForeignKey('Paper.ID',ondelete="CASCADE"), primary_key=True)


class Affiliate(Base):
    __tablename__ = 'Affiliate'

    author_link = Column(String(100), ForeignKey('Author.author_link'), primary_key=True)
    org_name = Column(String(100), ForeignKey('Organization.org_name'), primary_key=True)


class Publishment(Base):
    __tablename__ = 'Publishment'

    ID = Column(String(8), ForeignKey('Paper.ID'), primary_key=True)
    journal_name = Column(String(100), ForeignKey('Journal.journal_name'), primary_key=True)
    publish_year = Column(Integer)
    paper = relationship("Paper", cascade="all, delete")

def insert_author(data,cur):
    #1. author
    for index, row in data.iterrows():
        insert_query = '''
        INSERT INTO author (author_link, author_name, h_index)
        VALUES (%s, %s, %s);
        '''
        cur.execute(insert_query, (row['author_link'], row['author_name'], row['author_h_index']))

def insert_author_interests(data,cur):
    #2. Author_interests
    for index, row in data.iterrows():
        insert_query = '''
        INSERT INTO author_interests (author_link, interest)
        VALUES (%s, %s);
        '''
        cur.execute(insert_query, (row['author_link'], row['interests']))

def insert_paper(data,cur):
    for index, row in data.iterrows():
        insert_query = '''
        INSERT INTO Paper (ID, title, paper_link, cited_number, cited_link, related_paper_link, snippet)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        '''

        cur.execute(insert_query, (row['ID'], row['title'], row['link'], row['cited_number'], row['cited_papers_link'], row['related_papers_link'], row['snippet']))

def insert_paper_version(data,cur):
    for index, row in data.iterrows():
        insert_query = '''
        INSERT INTO Paper_versions (ID, versions, versions_link)
        VALUES (%s, %s, %s);
        '''
        cur.execute(insert_query, (row['ID'], row['versions'], row['versions_link']))

def insert_organization(data,cur):
    for index, row in data.iterrows():
        insert_query = '''
        INSERT INTO Organization (org_name, org_address)
        VALUES (%s, %s);
        '''
        cur.execute(insert_query, (row['org_name'], row['org_address']))


def insert_journal(data,cur):
    for index, row in data.iterrows():
        insert_query = '''
        INSERT INTO Journal (journal_name)
        VALUES (%s);
        '''
        cur.execute(insert_query, (row['journal_name']))


def insert_author_paper(data,cur):
    for index, row in data.iterrows():
        insert_query = '''
        INSERT INTO Author_paper (ID, author_link)
        VALUES (%s, %s);
        '''

        cur.execute(insert_query, (row['ID'], row['author_link']))

def insert_related_paper(data,cur):
    for index, row in data.iterrows():
        insert_query = '''
        INSERT INTO Related_paper (ID, related_ID)
        VALUES (%s, %s);
        '''

        cur.execute(insert_query, (row['ID'], row['related_ID']))

def insert_affiliate(data,cur):
    for index, row in data.iterrows():
        insert_query = '''
        INSERT INTO Affiliate (author_link, org_name)
        VALUES (%s, %s);
        '''

        cur.execute(insert_query, (row['author_link'], row['org_name']))

def insert_publishment(data,cur):
    for index, row in data.iterrows():
        insert_query = '''
        INSERT INTO Publishment (ID, journal_name, publish_year)
        VALUES (%s, %s, %s);
        '''

        cur.execute(insert_query, (row['ID'], row['journal_name'], row['publish_date']))

def insert(dataframe,cur):
    Author = dataframe[["author_name","author_link","author_h_index"]]
    Paper = dataframe[["title","link","cited_number","cited_papers_link","related_papers_link","snippet","versions","versions_link","ID","related_ID"]]
    Author_Paper = dataframe[["author_link","ID"]]
    Author_intersts = dataframe[["author_link","interests"]]
    Paper_versions = dataframe[["ID","versions","versions_link"]]
    Organization = dataframe[["org_name","org_address"]]
    Journal = dataframe[["journal_name"]]
    Affiliate = dataframe[["author_link","org_name"]]
    Related_paper = dataframe[["ID","related_ID"]]
    Publishment = dataframe[["publish_date","ID","journal_name"]]
    insert_author(Author,cur)
    insert_author_interests(Author_intersts,cur)
    insert_paper(Paper,cur)
    insert_paper_version(Paper_versions,cur)
    insert_author_paper(Author_Paper,cur)
    insert_organization(Organization,cur)
    insert_journal(Journal,cur)
    insert_affiliate(Affiliate,cur)
    insert_publishment(Publishment,cur)
    insert_related_paper(Related_paper,cur)



# 添加中间件来允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中，这里应指定允许的来源，例如 ["http://localhost", "http://example.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#查询papers
@app.get("/search_paper_id/")
async def search_paper_id(paper_id: str):
    db = SessionLocal()
    paper = db.query(Paper).filter(Paper.ID == paper_id).first()
    paper_info = {
            "ID": paper.ID,
            "title": paper.title,
            "paper_link": paper.paper_link,
            "cited_number": paper.cited_number,
            "cited_link": paper.cited_link,
            "related_paper_link": paper.related_paper_link,
            "snippet": paper.snippet
            # 添加其他文章信息字段
        }
    return paper_info

# 查询作者名
@app.get("/search_author/")
async def search_author(author_name: str):
    db = SessionLocal()
    author = db.query(Author).filter(Author.author_name == author_name).first()
    link = author.author_link
    
    #intersts
    interests = db.query(AuthorInterests).filter(AuthorInterests.author_link == link).all()
    interest_list = []
    for interest in interests:
        field = interest.interest
        interest_list.append(eval(field)["title"])

    print(len(interests))  # 输出匹配的兴趣数量

    #papers
    papers_list = []
    for paper in author.papers:
        paper_info = {
            "ID": paper.ID,
            "title": paper.title,
            "paper_link": paper.paper_link,
            "cited_number": paper.cited_number,
            "cited_link": paper.cited_link,
            "related_paper_link": paper.related_paper_link,
            "snippet": paper.snippet
            # 添加其他文章信息字段
        }
        papers_list.append(paper_info)
    
    #organization
    author_affiliations = db.query(Affiliate).filter(Affiliate.author_link == link).all()
    organization = [affiliation.org_name for affiliation in author_affiliations]
    db.close()
    if not author:
        raise HTTPException(status_code=404, detail="Sorry, No information!")
    return {
        "author_name": author.author_name,
        "organization":organization,
        "h_index": author.h_index,
        "interest":interest_list,
        "papers":papers_list
    }

@app.delete("/papers/{paper_id}")
async def delete_paper(paper_id: str):
    # 创建数据库会话
    db = SessionLocal()

    # 查找要删除的论文
    paper = db.query(Paper).filter(Paper.ID == paper_id).first()
    related_papers = db.query(Related_paper).filter(Related_paper.ID == paper_id or Related_paper.related_ID == paper_id).all() 
    for related_paper in related_papers:
        db.delete(related_paper)
    
    # 如果论文不存在，则抛出 HTTP 异常
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")

    # 删除论文
    db.delete(paper)
    db.commit()
    
    return {"message": "Paper deleted"}

@app.post("/receive")
async def insert_data(data: dict):
    json_data = data.get("data")
    print(json_data)
    df = pd.read_json(json_data, orient='split')
    con = pymysql.connect(user="root",
                      passwd=DB_PASSWARD,
                      db="GoogleScholar",
                      host="127.0.0.1",
                      charset='utf8mb4')
    cur = con.cursor()
    insert(df,cur)
    con.commit()
    cur.close()
    cur.close()
    return {"message": "Successfully inserted!"}

# 文章
from typing import List

@app.get("/search_paper/")
async def search_paper(title_keyword: str):
    db = SessionLocal()

    # 查询包含标题关键字的文章，并按照 site_number 排序
    matching_papers = (
        db.query(Paper)
        .filter(Paper.title.ilike(f"%{title_keyword}%"))
        .order_by(Paper.cited_number.desc())
        .all()
    )

    papers_info = []
    for paper in matching_papers:
        paper_info = {
            "ID": paper.ID,
            "title": paper.title,
            "paper_link": paper.paper_link,
            "cited_number": paper.cited_number,
            "cited_link": paper.cited_link,
            "related_paper_link": paper.related_paper_link,
            "snippet": paper.snippet
            # 添加其他文章信息字段
        }
        papers_info.append(paper_info)

    db.close()

    if not papers_info:
        raise HTTPException(status_code=404, detail="No matching papers found!")

    return {"matching_papers": papers_info}

