from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import authenticate_user, build_token_pair, decode_token
from app.schemas.auth_schema import LoginRequest, RefreshRequest, TokenPair

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/token", response_model=TokenPair)
async def login(credentials: OAuth2PasswordRequestForm = Depends()) -> TokenPair:
    if not authenticate_user(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenPair(**build_token_pair(credentials.username))


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(refresh_request: RefreshRequest) -> TokenPair:
    decoded = decode_token(refresh_request.refresh_token, expected_type="refresh")
    return TokenPair(**build_token_pair(str(decoded["sub"])))
