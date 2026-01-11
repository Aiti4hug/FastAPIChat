from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import create_engine

DB_URL = 'postgresql://postgres::aiti4aiti4@localhost:5432/test_chat_db'
engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)




Base = declarative_base()
