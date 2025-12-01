from typing import Optional
from fastapi import Depends, FastAPI, HTTPException , Response , status
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
from sqlmodel import Session
from . import models
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
class Post(BaseModel):
    title: str
    content: str
    published: bool = True

    class Config:
        extra = "forbid"

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
        

@app.get("/posts")
def get_posts(db : Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data":posts}

@app.post("/posts",status_code = status.HTTP_201_CREATED)
def createPost(post : Post , db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # get newly created row with ID
    return {"data": new_post}

@app.get("/posts/latest")
def get_latest_post(db: Session = Depends(get_db)):
    latest_post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    return {"data": latest_post}

#in the route just above and just below, order matters

@app.get("/posts/{id}")
def get_post(id: int,response: Response, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    db_post = post_query.first()

    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found"
        )
    return {"post": db_post}
    # response.status_code = status.HTTP_404_NOT_FOUND
    


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


@app.put("/posts/{id}")
def update_post(id: int, post: Post , db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    db_post = post_query.first()

    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist"
        )

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return {"data": post_query.first()}