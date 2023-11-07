from fastapi import FastAPI,HTTPException,Depends,status,UploadFile
from pydantic import BaseModel,EmailStr,validator
from typing  import List,Annotated,Union
import models
from database import engine,SessionLocal
from sqlalchemy.orm import Session
from models import Users,Profile
from passlib.context import CryptContext
import os
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
    
class getresponce(BaseModel):
    first_name: str
    last_name: str
    username : str
    email: EmailStr
    phone: str
    
    @validator('phone')
    def validate_phone(cls, phone):
        if len(phone) != 10 or not phone.isdigit():
            raise ValueError("Invalid phone number. Please enter a 10-digit numeric phone number.")
        return phone



class ProfilePictureRequset(BaseModel):
    profile_picture: UploadFile
    user_id: int
    

    
class UserResponce(getresponce):
    profile_picture_path: str 
    
     
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


@app.get("/users/{user_id}",response_model=UserResponce)
async def get_user(user_id:int,db: db_dependency):
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    print("profile cheking",profile)
    profile_picture_path = profile.profile_picture if profile else None
    print("path",profile_picture_path)
    user_d = {
        "id": db_user.id,
        "first_name": db_user.firstname,
        "last_name": db_user.lastname,
        "username": db_user.fullname,
        "email": db_user.email,
        "phone": db_user.Phone,
        "password":db_user.password,
        "profile_picture_path": profile_picture_path
    }
    print("data cheking",user_d)
    return  UserResponce(**user_d)

@app.post("/upload-profile-picture/")
async def upload_profile_picture(user_id: int,profile_picture: UploadFile,db: db_dependency):
    db_user = db.query(Users).filter(Users.id == user_id).first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    upload_dir = "profile_pictures"

    # Create the directory if it doesn't exist
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_extension = profile_picture.filename.split(".")[-1]
    file_path = f"profile_pictures/{user_id}.{file_extension}"
    
    with open(file_path, "wb") as f:
        f.write(profile_picture.file.read())

    # Save the file path to the database
    new_profile = Profile(profile_picture=file_path, user_id=user_id)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {"message": "Profile picture uploaded successfully"}

