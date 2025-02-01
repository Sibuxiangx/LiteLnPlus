from beanie import Document
from datetime import datetime


class User(Document):
    uid: str
    name: str
    signed_days: int
    favorability: int
    last_signed: datetime
    qq_number: str = ""