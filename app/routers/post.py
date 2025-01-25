from typing import List, Optional

from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app import schemas, models, oauth2
from app.database import get_db


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostOut)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    new_post = models.Post(**post.model_dump(), owner_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user), search: Optional[str] = "", limit: int = 10, skip: int = 0):
    user_posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return user_posts


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {id} not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not the owner of the post {id}")

    return post


@router.put("/{id}", response_model=schemas.PostOut)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {id} not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not the owner of the post {id}")

    db.query(models.Post).filter(models.Post.id == id).update(updated_post.model_dump(), synchronize_session=False)
    db.commit()

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {id} not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not the owner of the post {id}")

    db.query(models.Post).filter(models.Post.id == id).delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
