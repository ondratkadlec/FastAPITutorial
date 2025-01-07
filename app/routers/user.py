from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from app import schemas, utils, models
from app.database import get_db

router = APIRouter(prefix="/user", tags=["Users"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # hash the password
    user.password = utils.hash_password(user.password)

    new_user = models.User(**user.model_dump())
    print(new_user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(new_user)

    return new_user
