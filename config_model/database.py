from kayaku import config


@config("mongo")
class MongoDB:
    url: str
