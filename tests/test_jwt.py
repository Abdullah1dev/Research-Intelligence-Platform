from app.shared.security.jwt import create_access_token
token = create_access_token({"sub": "ali@test.com"})

print(token)

