from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, utils, models
from app.database import get_db


router = APIRouter(prefix="/user", tags=["Users"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # check if exists
    user_found = db.query(models.User).filter(models.User.email == user.email).first()
    if user_found:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User with email {user.email} already exists.")
    # hash the password
    user.password = utils.hash_password(user.password)

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} doesn't exist.")

    return user