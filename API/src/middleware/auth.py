from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
## @BEN put auth function import here; use relative importing (..->go one path down): import auth_user

async def auth_user(uid: str, jwt: str):
    return True ## @BEN delete this instead use import

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        ## grab from auth headers
        uid = request.headers.get("X-UID")
        jwt = request.headers.get("X-JWT")

        ## un-comment when auth is working
        """if not uid or not jwt: ## reject if no auth headers
            return JSONResponse(status_code=401, content={"error": "Missing Authentication Headers"})"""
        if not await auth_user(uid, jwt): ## reject on failed auth
            return JSONResponse(status_code=403, content={"error": "Invalid Authentication"})
        
        request.state.uid = uid ## add uid for get_uid

        ## call next step
        return await super().dispatch(request, call_next)

async def get_uid(request: Request):
    """Returns uid from injected request param"""
    return request.state.uid
