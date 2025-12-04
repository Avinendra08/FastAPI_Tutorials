from datetime import datetime, timedelta
from jose import JWTError , jwt 

SECRET_KEY = "43434324324fsdfsdfdsds12124ewefrf34f34f3wf3f3f3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_Access_Token(data:dict):
    to_encode = data.copy()

    expire  = datetime.now() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})

    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

    return encoded_jwt