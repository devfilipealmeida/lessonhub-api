from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models, utils
from ..database import get_db
from passlib.context import CryptContext

router = APIRouter(tags=['Authentication'])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post('/login')
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid Credentials"
        )
    
    if not pwd_context.verify(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid Credentials"
        )
    
    access_token = utils.create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}