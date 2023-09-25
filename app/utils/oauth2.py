from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.utils import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail={'msg': 'Could not validate credentials'}, 
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    return jwt.verify_token(token, credentials_exception)

