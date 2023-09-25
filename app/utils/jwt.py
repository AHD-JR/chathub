from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int (os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))

def create_access_token(data: dict):
    data_to_encode = data.copy()
    expiry_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data_to_encode.update({'exp': expiry_time})
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str, credentials_exception):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except JWTError as e:
        raise credentials_exception
    
def verify_token(token: str, credentials_exception):
    payload = decode_token(token, credentials_exception)
    user = payload.get('user_data')
    user_id: str = user['id']
    username: str = user['username']
    if (user_id is None) or (username is None):
        raise credentials_exception
    return user