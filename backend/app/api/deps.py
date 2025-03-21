from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import logging
from ..core.database import get_db
from ..core.firebase import verify_firebase_token
from ..models.user import User

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    logger.info(f"Received token: {token[:20]}...")
    
    decoded_token = verify_firebase_token(token)
    
    if not decoded_token:
        logger.error("Token verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Firebase tokens can have the user ID in different keys depending on the token type
    # First try 'uid', then 'user_id', then 'sub'
    firebase_uid = decoded_token.get("uid") or decoded_token.get("user_id") or decoded_token.get("sub")
    logger.info(f"Extracted Firebase UID: {firebase_uid}")
    
    if not firebase_uid:
        logger.error(f"Could not extract UID from token: {decoded_token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token structure",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not user:
        logger.error(f"User not found for Firebase UID: {firebase_uid}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"User found: {user.id} ({user.email})")
    return user 