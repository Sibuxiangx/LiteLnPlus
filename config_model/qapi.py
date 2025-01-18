import kayaku
from kayaku import config


@config("qqapi")
class QOpenAPI:
    AppID: str
    Token: str
    AppSecret: str
