import datetime

import jwt
from jwt import InvalidTokenError

from api.exceptions import JWTHTTPExceptions


class JWTService:
    
    def __init__(self, secret: str, audience: str):
        self.secret = secret
        self.audience = audience
    
    async def generate_jwt(self,
                           data: dict,
                           lifetime_seconds: int,
                           ) -> str:
        payload = data.copy()
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=lifetime_seconds)
        payload["exp"] = expire
        return jwt.encode(payload, self.secret)
    
    async def read_jwt(self, token: str) -> dict:
        try:
            payload = jwt.decode(token,
                                 self.secret,
                                 algorithms=["HS256"],
                                 audience=self.audience
                                 )
        except InvalidTokenError:
            raise JWTHTTPExceptions.InvalidJWTException()
        return payload
