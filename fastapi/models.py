from database import Base
from sqlalchemy import Column,Integer,String,ForeignKey

class Users(Base):
    __tablename__ = "users"
    
    id = Column(Integer,primary_key=True,index=True)
    fullname = Column(String,unique=True)
    firstname = Column(String)
    lastname = Column(String)
    email = Column(String,unique=True,index=True)
    password = Column(String)
    Phone = Column(String,unique=True)
    


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    profile_picture = Column(String)
    user_id = Column(Integer,ForeignKey("users.id"))
    

