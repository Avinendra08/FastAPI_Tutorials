from fastapi import FastAPI
from . import models
from .database import  engine
from .routers import post,user


models.Base.metadata.create_all(bind = engine)
app = FastAPI()

@app.get("/")
def root():
    return {"message":"Hey!!"}

app.include_router(user.router)
app.include_router(post.router)