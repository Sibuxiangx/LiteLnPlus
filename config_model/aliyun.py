from kayaku import config


@config("aliyun")
class Aliyun:
    access_key_id: str
    access_key_secret: str
