from fastapi import Depends, HTTPException, status

from app.features.users.models import User
from app.shared.enums.roles import UserRole
from app.features.auth.dependencies import get_current_user


def require_roles(*allowed_roles: UserRole):
    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return role_checker