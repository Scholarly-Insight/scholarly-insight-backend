from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from firebase_admin import auth
import requests
from ..schemas.auth import SignUpRequest, SignInRequest, AuthResponse
from ..models.user import User
from ..core.firebase import get_firebase_app
from ..core.config import settings

FIREBASE_AUTH_ENDPOINT = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
FIREBASE_SIGNUP_ENDPOINT = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"

async def create_user_account(db: Session, request: SignUpRequest) -> AuthResponse:
    """Create a new user account using Firebase Authentication and store in database."""
    try:
        # Ensure Firebase is initialized
        get_firebase_app()
        
        # Create user in Firebase
        firebase_user = auth.create_user(
            email=request.email,
            password=request.password,
            display_name=request.full_name
        )
        
        # Create user in database
        db_user = User(
            firebase_uid=firebase_user.uid,
            email=request.email,
            full_name=request.full_name,
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create a custom token
        custom_token = auth.create_custom_token(firebase_user.uid)
        
        return AuthResponse(
            access_token=custom_token.decode('utf-8'),
            user_id=db_user.id
        )
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")

async def sign_in_user(db: Session, request: SignInRequest) -> Optional[AuthResponse]:
    """Sign in a user using Firebase Authentication."""
    try:
        # Get the Firebase Web API key from settings
        web_api_key = settings.FIREBASE_WEB_API_KEY
        if not web_api_key:
            raise ValueError("Firebase Web API key not found in settings")
            
        # Sign in with Firebase using REST API
        response = requests.post(
            f"{FIREBASE_AUTH_ENDPOINT}?key={web_api_key}",
            json={
                "email": request.email,
                "password": request.password,
                "returnSecureToken": True
            }
        )
        
        if response.status_code != 200:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', 'Unknown error')
            raise HTTPException(status_code=401, detail=f"Authentication failed: {error_message}")
            
        auth_data = response.json()
        firebase_uid = auth_data['localId']
        id_token = auth_data['idToken']
        
        # Get or create user in database
        user = get_user_by_firebase_uid(db, firebase_uid)
        if not user:
            # Get user info from Firebase
            firebase_user = auth.get_user(firebase_uid)
            user = User(
                firebase_uid=firebase_uid,
                email=request.email,
                full_name=firebase_user.display_name or "",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return AuthResponse(
            access_token=id_token,
            user_id=user.id
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

def get_user_by_firebase_uid(db: Session, firebase_uid: str) -> Optional[User]:
    """Get a user by their Firebase UID."""
    return db.query(User).filter(User.firebase_uid == firebase_uid).first() 