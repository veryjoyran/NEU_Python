# database.py
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class House(Base):
    __tablename__ = 'houses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_type = Column(String)
    area = Column(String)
    floor = Column(String)
    orientation = Column(String)
    build_year = Column(String)
    owner_name = Column(String)
    address = Column(String)
    description = Column(String)
    price = Column(String)

engine = create_engine('sqlite:///houses.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
