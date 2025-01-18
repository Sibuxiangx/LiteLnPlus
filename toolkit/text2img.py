import re
import string

from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
import asyncio


font_file = "./resource/font/sarasa-mono-sc-semibold.ttf"
font = ImageFont.truetype(font_file, 22)


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


def _text(text: str,cut: int = 0):
    imageio = BytesIO()
    if cut:
        cut_strs = get_cut_str(text, cut)
    else:
        cut_strs = text.split("\n")
    textx = 0
    texty = 0
    for i in cut_strs:
        left,top,right,bottom = font.getbbox(i)
        length = right - left
        high = bottom - top
        texty += high
        if not i:
            texty += font.font.height
        textx = max(textx, length)
    image = Image.new("RGB", (int(textx) + 50, int(texty) + 100), (242, 242, 242))
    draw = ImageDraw.Draw(image)
    draw.text((20, 20),text, font=font, fill=(31, 31, 33))
    image.save(imageio, format="JPEG")
    return imageio


async def create_image(text: str, cut: int = 0):

    return (await asyncio.to_thread(_text, text, cut)).getvalue()

