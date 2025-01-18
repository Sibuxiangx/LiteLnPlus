from aiowebdav.client import Client
from config_model.webdav import WebDAVConfig
import aiofiles
import kayaku
from pathlib import Path


async def upload_img(name: str, data: bytes, dir: str = ""):
    config = kayaku.create(WebDAVConfig)
    options = {
        "webdav_hostname": "https://webdav.server.ru",
        "webdav_login": "login",
        "webdav_password": "password",
        "disable_check": True,
    }
    options["webdav_hostname"] = config.host
    options["webdav_login"] = config.user
    options["webdav_password"] = config.password
    client = Client(options)
    if not await client.check("imgupload"):
        client.mkdir("imgupload")
    if not Path("cache/uploader").exists():
        Path("cache/uploader").mkdir()
    if dir:
        if not Path(f"cache/uploader/{dir}").exists():
            Path(f"cache/uploader/{dir}").mkdir()
        async with aiofiles.open(f"cache/uploader/{dir}/{name}", "wb") as f:
            await f.write(data)
        await client.upload(
            f"imgupload/{dir}/{name}",
            f"cache/uploader/{dir}/{name}",
        )
        return f"{config.real_host}/imgupload/{dir}/{name}"
    async with aiofiles.open(f"cache/uploader/{name}", "wb") as f:
        await f.write(data)
    await client.upload(
        f"imgupload/{name}",
        f"cache/uploader/{name}",
    )
    return f"{config.real_host}/imgupload/{name}"
