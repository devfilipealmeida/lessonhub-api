from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models, utils
from ..database import get_db
from passlib.context import CryptContext

router = APIRouter(tags=['Users'])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    
    # Create new user
    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password,
        credits=10
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.get('/me', response_model=schemas.User)
def get_me(current_user: models.User = Depends(utils.get_current_user)):
    return current_user

@router.patch('/me', response_model=schemas.User)
def update_me(
    update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(utils.get_current_user)
):
    if update.full_name is not None:
        current_user.full_name = update.full_name
    if update.email is not None:
        existing = db.query(models.User).filter(models.User.email == update.email, models.User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = update.email
    if update.password is not None:
        current_user.hashed_password = pwd_context.hash(update.password)
    db.commit()
    db.refresh(current_user)
    return current_user