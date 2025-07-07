from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter()

@router.get("/", response_model=List[User])
async def get_users(skip: int = 0, limit: int = 100):
    """
    Retrieve users.
    """
    # This would be replaced with actual database query
    return [
        {
            "id": 1,
            "email": "user@example.com",
            "full_name": "Test User",
            "is_active": True,
            "is_superuser": False,
            "created_at": "2025-07-01T00:00:00"
        }
    ]

@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    """
    Create new user.
    """
    # This would be replaced with actual database insertion
    return {
        "id": 2,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": True,
        "is_superuser": False,
        "created_at": "2025-07-07T00:00:00"
    }

@router.get("/me", response_model=User)
async def get_current_user():
    """
    Get current user.
    """
    # This would be replaced with actual authentication logic
    return {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
        "created_at": "2025-07-01T00:00:00"
    }

@router.get("/{user_id}", response_model=User)
async def get_user_by_id(user_id: int):
    """
    Get specific user by ID.
    """
    # This would be replaced with actual database query
    if user_id != 1:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
        "created_at": "2025-07-01T00:00:00"
    }

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate):
    """
    Update user.
    """
    # This would be replaced with actual database update
    if user_id != 1:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user_id,
        "email": user.email or "user@example.com",
        "full_name": user.full_name or "Test User",
        "is_active": user.is_active if user.is_active is not None else True,
        "is_superuser": False,
        "created_at": "2025-07-01T00:00:00"
    }

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    """
    Delete user.
    """
    # This would be replaced with actual database deletion
    if user_id != 1:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}