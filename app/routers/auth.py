from fastapi import APIRouter , Depends , status , HTTPException , Response
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app import oauth2

from ..database import get_db
from .. import models , schemas , utils

router = APIRouter(
    tags=["Auth"]
)

@router.post('/login')
def login(user_credentials : OAuth2PasswordRequestForm = Depends() , db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user : 
        raise HTTPException(status_code=404 , detail=f"Invalid credentials")
    
    if not utils.verify(user_credentials.password , user.password):
        return HTTPException(status_code=404 , details=f'invalid credentials')
    
    access_token = oauth2.create_Access_Token({"data":user.id})

    return {"access_token":access_token , "token_type":"bearer"}