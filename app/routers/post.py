from typing import List
from fastapi import Depends,HTTPException , Response , status , APIRouter
from sqlmodel import Session
from ..utils import hash
from .. import models , schemas
from ..database import get_db

router = APIRouter()

##get all posts
@router.get("/posts" ,status_code = status.HTTP_200_OK , response_model= List[schemas.PostResponse])
def get_posts(db : Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


##create a post
@router.post("/posts",status_code = status.HTTP_201_CREATED , response_model= schemas.PostResponse)
def createPost(post : schemas.PostCreate , db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # get newly created row with ID
    return new_post


##get latest post
@router.get("/posts/latest" ,status_code = status.HTTP_200_OK, response_model= schemas.PostResponse)
def get_latest_post(db: Session = Depends(get_db)):
    latest_post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    return latest_post

#in the route just above and just below, order matters


##get a post by id
@router.get("/posts/{id}" ,status_code = status.HTTP_200_OK , response_model= schemas.PostResponse)
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
@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
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
@router.put("/posts/{id}" ,status_code = status.HTTP_200_OK , response_model= schemas.PostResponse)
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

