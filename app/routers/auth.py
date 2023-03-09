from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, utils, models, oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.TokenOut)
# def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    refresh_token = oauth2.create_refresh_token(data={"user_id": user.id})

    token = models.Tokens()
    token.refresh = refresh_token
    db.add(token)
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=schemas.Token)
def refresh(payload: schemas.RefreshTokenIn, db: Session = Depends(get_db)):
    if payload.refresh_token:
        query = db.query(models.Tokens).filter(
            models.Tokens.refresh == payload.refresh_token)
        token = query.first()
        if token:
            try:
                user = oauth2.get_refresh_user(token.refresh, db)

            except HTTPException as error:
                query.delete()
                db.commit()
                raise error
            access_token = oauth2.create_access_token(
                data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: schemas.RefreshTokenIn, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if payload.refresh_token and current_user.id:
        db.query(models.Tokens).filter(
            models.Tokens.refresh == payload.refresh_token).delete()
        db.commit()
