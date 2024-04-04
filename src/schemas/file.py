from pydantic import BaseModel


class FileBase(BaseModel):
    file_name: str


class FileCreate(FileBase):
    pass


class FileInDBBase(FileBase):

    class Config:
        from_attributes = True


class File(FileInDBBase):
    pass
