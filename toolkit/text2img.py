import hashlib
import asyncio
from io import BytesIO
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta
from PIL import Image, ImageFont, ImageDraw
import string
import re


font_file = "./font/sarasa-mono-sc-semibold.ttf"
try:
    font = ImageFont.truetype(font_file, 22)
except OSError:
    logger.error(
        f"未找到字体文件：{font_file}，请前往 https://github.com/djkcyl/ABot-Resource/releases/tag/Font 进行下载后解压至 ABot 根目录"
    )
    exit(1)

cache = Path("./cache/t2i")
cache.mkdir(exist_ok=True, parents=True)


async def create_image(text: str, cut=64) -> bytes:
    return await asyncio.to_thread(_cache, text, cut)


def get_cut_str(str, cut):
    """
    自动断行，用于 Pillow 等不会自动换行的场景
    """
    punc = """，,、。.？?）》】“"‘'；;：:！!·`~%^& """
    si = 0
    i = 0
    next_str = str
    str_list = []

    while re.search(r"\n\n\n\n\n", next_str):
        next_str = re.sub(r"\n\n\n\n\n", "\n", next_str)
    for s in next_str:
        if s in string.printable:
            si += 1
        else:
            si += 2
        i += 1
        if next_str == "":
            break
        elif next_str[0] == "\n":
            next_str = next_str[1:]
        elif s == "\n":
            str_list.append(next_str[: i - 1])
            next_str = next_str[i - 1 :]
            si = 0
            i = 0
            continue
        if si > cut:
            try:
                if next_str[i] in punc:
                    i += 1
            except IndexError:
                str_list.append(next_str)
                return str_list
            str_list.append(next_str[:i])
            next_str = next_str[i:]
            si = 0
            i = 0
    str_list.append(next_str)
    i = 0
    non_wrap_str = []
    for p in str_list:
        if p == "":
            break
        elif p[-1] == "\n":
            p = p[:-1]
        non_wrap_str.append(p)
        i += 1
    return non_wrap_str


def _cache(text: str, cut: int) -> bytes:
    str_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
    cache.joinpath(str_hash[:2]).mkdir(exist_ok=True)
    cache_file = cache.joinpath(f"{str_hash}.jpg")
    if cache_file.exists():
        logger.info(f"T2I Cache hit: {str_hash}")
    else:
        cache_file.write_bytes(_create_image(text, cut))
    return cache_file.read_bytes()


def _create_image(text: str, cut: int) -> bytes:
    cut_str = "\n".join(get_cut_str(text, cut))

    # 使用 ImageDraw.Draw 创建临时图像来计算文本大小
    temp_image = Image.new("RGB", (1, 1))
    temp_draw = ImageDraw.Draw(temp_image)

    # 获取文本边界框
    bbox = temp_draw.multiline_textbbox((0, 0), cut_str, font=font)
    textx = bbox[2] - bbox[0]
    texty = bbox[3] - bbox[1]

    # 创建实际图像并绘制文本
    image = Image.new("RGB", (textx + 40, texty + 40), (235, 235, 235))
    draw = ImageDraw.Draw(image)
    draw.text((20, 20), cut_str, font=font, fill=(31, 31, 33))

    imageio = BytesIO()
    image.save(
        imageio,
        format="JPEG",
        quality=90,
        subsampling=2,
        qtables="web_high",
    )
    return imageio.getvalue()


def delete_old_cache():
    cache_files = cache.glob("*")
    i = 0
    r = 0
    for cache_file in cache_files:
        i += 1
        if (
            cache_file.stat().st_mtime
            < ((datetime.now() - timedelta(days=14)).timestamp())
            and cache_file.is_file()
        ):
            cache_file.unlink()
            r += 1
    return i, r


delete_old_cache()
