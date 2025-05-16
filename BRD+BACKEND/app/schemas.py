from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None


class GroupCreate(BaseModel):
    name: str

class GroupOut(BaseModel):
    id: int
    name: str
    created_by: int

    class Config:
        orm_mode = True
class ProjectCreate(BaseModel):
    name: str
    description: str

class ProjectOut(BaseModel):
    id: int
    name: str
    description: str
    group_id: int
    created_by: int

    class Config:
        orm_mode = True

class DocumentOut(BaseModel):
    id: int
    filename: str
    path: str
    description: str
    summary_title: Optional[str]
    summary_description: Optional[str]
    project_id: int

    class Config:
        orm_mode = True
