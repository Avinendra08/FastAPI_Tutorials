from fastapi import Depends, HTTPException ,status , APIRouter
from sqlmodel import Session
from ..utils import hash
from .. import models , schemas
from ..database import get_db

router = APIRouter()

##create a user
@router.post("/users",status_code = status.HTTP_201_CREATED , response_model=schemas.UserOut)
def createUser(user : schemas.UserCreate , db: Session = Depends(get_db)):
    hashed_password = hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # get newly created row with ID
    return new_user 


##get user by id
@router.get("/users/{id}" ,status_code = status.HTTP_200_OK ,response_model=schemas.UserOut)
def get_posts(id:int , db : Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"user with id : {id} does not exist")
    
    return user