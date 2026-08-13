from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.users.models import User
from app.shared.security.hashing import hash_password
from app.features.auth.schemas import RegisterRequest
from app.features.auth.schemas import LoginRequest
from app.shared.security.hashing import verify_password
from app.shared.enums.roles import UserRole


def register_user(
    data: RegisterRequest,
    db: Session,
) -> User:

    # Check whether the email already exists
    existing_user = db.scalar(
        select(User).where(User.email == data.email)
    )

    if existing_user:
        raise ValueError("Email already registered")

    # Hash the plain password
    hashed_password = hash_password(data.password)

    # Create the database user
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hashed_password,
        role=UserRole.RESEARCHER,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user





def authenticate_user(
    db: Session,
    data: LoginRequest
) -> User:

    # Find user by email
    user = db.scalar(
        select(User).where(User.email == data.email)
    )
    print("Login Email:", data.email)
    print("User Found:", user)

    # If user doesn't exist
    # Verify password
    
    print("Entered Password:", data.password)
    print("Stored Hash:", user.password_hash)

    result = verify_password(
        data.password,
        user.password_hash
    )

    print("Password Match:", result)
    
    if not result:
        raise ValueError("Invalid email or password")
        
    # Authentication successful
    return user

   
    
    
        
        
        
    
        
        
    
    
    