from fastapi import FastAPI,HTTPException,Depends,status
from pydantic import BaseModel,EmailStr
from typing  import List,Annotated
import models
from database import engine,SessionLocal
from sqlalchemy.orm import Session
from models import Users,Profile
from passlib.context import CryptContext

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

SECRET_KEY = "eyJhbGciOIsInR5cCIiwiI6IkpXVCJ9eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9TJVA95OrM7E2cBab30RMHrHD"
ALGORITHM = 'HS256'


bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated = 'auto')


class CreateUserRequset(BaseModel):
    first_name: str
    last_name: str
    username : str
    email: EmailStr
    password: str
    phone: str


class ProfilePictureRequset(BaseModel):
    profile_picture: str
    user_id: int
    
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

db_dependency = Annotated[Session,Depends(get_db)]
    
   

@app.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequset):
    existing_email = db.query(Users).filter(Users.email == create_user_request.email).first()
    existing_phone = db.query(Users).filter(Users.Phone == create_user_request.phone).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Email already registered")
    if existing_phone:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Phone number already registered")
    create_user_model = Users(
        fullname=create_user_request.username,
        firstname=create_user_request.first_name,
        lastname=create_user_request.last_name,
        email=create_user_request.email,  
        password=bcrypt_context.hash(create_user_request.password),
        Phone=create_user_request.phone  
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return create_user_model

