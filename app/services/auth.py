import time
import jwt
import json
import httpx
from app.config import settings as global_settings
import os
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


async def get_from_redis(request: Request, key: str):
    return await request.app.state.redis.get(key)


async def set_to_redis(request: Request, key: str, value: str, ex: int):
    return await request.app.state.redis.set(key, value, ex=ex)


async def verify_jwt(request: Request, token: str) -> bool:
    # Check if token is already verified and stored in Redis
    cached_user = await get_from_redis(request, f"verified_{token}")
    if cached_user:
        request.state.user = json.loads(cached_user)
        return True

    # If not in Redis, call the Django validate endpoint
    app_host = os.getenv('APP_SERVER_HOST')  # Replace with your Django app's URL
    headers = {"Authorization": f"{token}"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(app_host+'/api/auth/validate', headers=headers)
            response.raise_for_status()
            user_data = response.json()
            if user_data:
                # Store the validated token in Redis with an expiration of 1 hour (3600 seconds)
                await set_to_redis(request, f"verified_{token}", json.dumps(user_data), ex=3600)
                request.state.user = user_data
                return True
        except (httpx.HTTPError, KeyError) as e:
            # If validation fails, ensure Redis entry is cleared
            print(e)
            await request.app.state.redis.delete(f"verified_{token}")
            raise HTTPException(status_code=403, detail="Invalid token or expired token.")

    return False


class AuthBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
        if not await verify_jwt(request, credentials.credentials):
            raise HTTPException(status_code=403, detail="Invalid token or expired token.")
        return credentials.credentials
