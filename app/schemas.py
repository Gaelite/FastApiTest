from pydantic import BaseModel

class UserAuth(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

class infoInput(BaseModel):
    info: str

class infoOutput(BaseModel):
    info: str