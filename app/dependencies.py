from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> UUID:
    # In a real application, you would validate the token and retrieve the user
    # For this example, we'll just return a dummy UUID
    return UUID('12345678-1234-5678-1234-567812345678')