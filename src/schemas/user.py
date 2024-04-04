from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserAuth(UserBase):
    username: str
    password: str


class UserCreate(UserAuth):
    pass


class UserInDBBase(UserBase):
    id: int
    username: str
    token: str

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass
