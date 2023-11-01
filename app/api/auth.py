from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.utils import jwt
from app.utils.hashing import hash, verify
from app.api.user import userTable
from app.utils.response_utils import response
from app.serializer import user_serializer

router = APIRouter(
    tags=['Authentication'],
    prefix='/auth'
)

@router.post('/login')
async def login(req: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await userTable.find_one({'username': req.username})
        if not user:
            return response(status_code=404, message='Account not found!')

        if not verify(req.password, user['password']):
            return response(status_code=400, message='Incorrect password!')
        
        access_token = jwt.create_access_token(data={'user_data': user_serializer(user)})
        
        data = {
            'access_token': access_token,
            'token_type': 'bearer'
        }   

        #return response(status.HTTP_200_OK, "Authentication accomplised!", data)
        # I must to return a dict with exact strucure as the data dict above because that is what...
        # ...the OAuthPasswordBearer extract and pass on subsequent request headers
        return data
    except Exception as e:
        return response(status_code=500, message=str(e))


