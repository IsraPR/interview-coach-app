from pydantic import BaseModel


class BasicChat(BaseModel):
    prompt: str
