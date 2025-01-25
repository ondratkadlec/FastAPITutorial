from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import user, post
from app import models, database


# database.Base.metadata.drop_all(bind=database.engine)
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(post.router)

@app.get("/")
def root():
    return {"message": "Hello World"}