from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)


class RegisterResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    
    
class LoginRequest(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8 , max_length=128)
    


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    
    