from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.websockets import WebSocket
from starlette.responses import JSONResponse
from starlette.datastructures import State
import logging
## @BEN put auth function import here; use relative importing (..->go one path down): import auth_user

log = logging.getLogger("uvicorn.error")
log.setLevel(logging.INFO)

async def auth_user(uid: str, jwt: str):
    return True ## @BEN delete this instead use import

class AuthMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            # HTTP requests
            headers = {k.decode(): v.decode() for k, v in scope["headers"]}
            uid = headers.get("x-uid")
            jwt = headers.get("x-jwt")

            """if not uid or not jwt:
                response = JSONResponse({"error": "Unauthorized"}, status_code=401)
                await response(scope, receive, send)
                return""" ## uncomment when auth is in
            if not await auth_user(uid, jwt):
                response = JSONResponse({"error": "Unauthorized"}, status_code=401)
                await response(scope, receive, send)
                return

            scope["state"] = State(scope)
            scope["state"].uid = uid  # attach to request.state

            log.info("[HTTP-UAUTH] UID:%s passed uauth", uid)
            await self.app(scope, receive, send)

        elif scope["type"] == "websocket":
            # WebSocket requests
            headers = {k.decode(): v.decode() for k, v in scope["headers"]}
            uid = headers.get("x-uid")
            jwt = headers.get("x-jwt")

            """if not uid or not jwt:
                response = JSONResponse({"error": "Unauthorized"}, status_code=401)
                await response(scope, receive, send)
                return""" ## un comment when auth is in
            if not await auth_user(uid, jwt):
                ws = WebSocket(scope, receive=receive, send=send)
                await ws.close(code=1008)
                return

            scope["state"] = State(scope)
            scope["state"].uid = uid  # attach to ws.state
            
            log.info("[WS-UAUTH] UID:%s passed uauth", uid)
            await self.app(scope, receive, send)

        else:
            await self.app(scope, receive, send)

async def get_uid(request):
    """Returns uid from injected request param"""
    return request.state.uid
