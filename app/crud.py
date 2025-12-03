from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException , Response , status
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
from sqlmodel import Session
from .utils import hash
from . import models , schemas
from .database import  engine , get_db


models.Base.metadata.create_all(bind = engine)
app = FastAPI()


# @app.get("/hello")
# async def root():
#     return {"message":"hello world"}

# routes are sometimes called path ops in fastAPI
# decorators help in making a normal function to act like an api in on a specific path
# we define http method and path on our app , which is an instancce of FastAPI

# get,post,patch/delete methods

# @app.post("/createPost")
# def createPost(payload : dict = Body(...)):
#     print(payload)
#     return {"new post:": f"title: {payload['title']} content:{payload['content']}"}

#pydantic schema : basemodel
# title str , content str
# class Post(BaseModel):
#     title: str
#     content: str
#     published: bool = True

#     class Config:
#         extra = "forbid"

# my_posts = [{"id":1 , "title":"movie" , "content":"horror"},
#              {"id":2 , "title":"book" , "content":"biography"}]

# def find_post(id):
#     for p in my_posts:
#         if p['id'] == id:
#             return p

# def find_post_index(id):
#     for i,p in enumerate(my_posts):
#         if p['id'] == id:
#             return i
        
@app.get("/")
def root():
    return {"message":"Hey!!"}


#######   posts operations

##get all posts
@app.get("/posts" ,status_code = status.HTTP_200_OK , response_model= List[schemas.PostResponse])
def get_posts(db : Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


##create a post
@app.post("/posts",status_code = status.HTTP_201_CREATED , response_model= schemas.PostResponse)
def createPost(post : schemas.PostCreate , db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # get newly created row with ID
    return new_post


##get latest post
@app.get("/posts/latest" ,status_code = status.HTTP_200_OK, response_model= schemas.PostResponse)
def get_latest_post(db: Session = Depends(get_db)):
    latest_post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    return latest_post

#in the route just above and just below, order matters


##get a post by id
@app.get("/posts/{id}" ,status_code = status.HTTP_200_OK , response_model= schemas.PostResponse)
def get_post(id: int,response: Response, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    db_post = post_query.first()

    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found"
        )
    return db_post
    # response.status_code = status.HTTP_404_NOT_FOUND
    

##delete a post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    db_post = post_query.first()

    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist"
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


##update a post
@app.put("/posts/{id}" ,status_code = status.HTTP_200_OK , response_model= schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate , db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    db_post = post_query.first()

    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist"
        )

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()



##users operations

##create a user
@app.post("/users",status_code = status.HTTP_201_CREATED , response_model=schemas.UserOut)
def createUser(user : schemas.UserCreate , db: Session = Depends(get_db)):
    hashed_password = hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # get newly created row with ID
    return new_user 


##get user by id
@app.get("/users/{id}" ,status_code = status.HTTP_200_OK ,response_model=schemas.UserOut)
def get_posts(id:int , db : Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"user with id : {id} does not exist")
    
    return user