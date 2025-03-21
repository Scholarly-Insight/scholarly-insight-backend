from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....core.database import get_db
from ....schemas.auth import SignUpRequest, SignInRequest, AuthResponse
from ....services import auth as auth_service
from ....api.deps import get_current_user
from ....models.user import User

router = APIRouter()

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    """
    Create a new user account using Firebase authentication.
    """
    try:
        return await auth_service.create_user_account(db, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/signin", response_model=AuthResponse)
async def signin(request: SignInRequest, db: Session = Depends(get_db)):
    """
    Sign in a user using Firebase authentication.
    """
    try:
        return await auth_service.sign_in_user(db, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/signout")
async def signout(current_user: User = Depends(get_current_user)):
    """
    Sign out the current user.
    """
    return {"message": "Successfully signed out"} 