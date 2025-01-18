from kayaku import config


@config("webdav")
class WebDAVConfig:
    host: str
    user: str
    password: str
    real_host: str
