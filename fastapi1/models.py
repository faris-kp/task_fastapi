from database import Base
from sqlalchemy import Column,Integer,String,ForeignKey
class Users(Base):
    __tablename__ = "users"
    
    id = Column(Integer,primary_key=True,index=True)
    fullname = Column(String,unique=True)
    email = Column(String,unique=True,index=True)
    password = Column(String)
    Phone = Column(String,unique=True)
    
    

    

