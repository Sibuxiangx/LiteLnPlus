from io import BytesIO

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def imageRadiusProcessing(img: Image.Image, central_a: int, radius: int = 30):
    """处理图片四个圆角。
    :centralA: 中央区域的 A 通道值，当指定为 255 时全透，四角将使用 0 全不透
    """
    circle = Image.new("L", (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=central_a)
    w, h = img.size
    alpha = Image.new("L", img.size, central_a)
    upperLeft, lowerLeft = circle.crop((0, 0, radius, radius)), circle.crop(
        (0, radius, radius, radius * 2)
    )
    upperRight, lowerRight = (
        circle.crop((radius, 0, radius * 2, radius)),
        circle.crop((radius, radius, radius * 2, radius * 2)),
    )
    alpha.paste(upperLeft, (0, 0))
    alpha.paste(upperRight, (w - radius, 0))
    alpha.paste(lowerRight, (w - radius, h - radius))
    alpha.paste(lowerLeft, (0, h - radius))
    img.putalpha(alpha)
    return img


def write_text(
    img: Image.Image,
    text: str,
    position: tuple[int, int],
    font_path: str,
    font_size: int,
    color: tuple[int, int, int] = (255, 255, 255),
):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, font_size)
    min_font_limit = 10
    _text_size = font.getbbox(text)
    text_size = (_text_size[2] - _text_size[0], _text_size[3] - _text_size[1])
    x = int(position[0] - text_size[0] / 2)
    while x <= 50:
        font_size -= 2
        font = ImageFont.truetype(font_path, font_size)
        _text_size = font.getbbox(text)
        text_size = (_text_size[2] - _text_size[0], _text_size[3] - _text_size[1])
        x = int(position[0] - text_size[0] / 2)
    y = int(position[1] - text_size[1] / 2)
    draw.text((x, y), text, font=font, fill=color)
    return img


def generate_signin(
    res_path: str,
    avatar: BytesIO,
    nickname: str,
    signed_days: int,
    favorability: int,
    hitokoto: str,
):
    img = Image.open(avatar).convert("RGBA").resize((640, 640), Image.LANCZOS)
    mask = Image.new("L", (256, 256), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 256, 256), fill=255)
    round_img = img.resize((256, 256), Image.LANCZOS)
    round_img.putalpha(mask)
    canvas = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
    canvas.paste(img.copy().filter(ImageFilter.GaussianBlur(7)))
    _magic_circle = Image.open(f"{res_path}/magic_circle.png").convert("L")
    _magic_circle = _magic_circle.resize((286, 286), Image.LANCZOS)
    magic_circle = Image.new("RGBA", (286, 286), (0, 0, 0, 0))
    magic_circle.putalpha(_magic_circle)
    text_basemap = Image.new("RGBA", (540, 160), (0, 0, 0, 190))
    text_basemap = imageRadiusProcessing(text_basemap, 190)
    x = int((640 - 256 - 30) / 2)
    y = x - 50
    canvas.paste(magic_circle, (x, y), magic_circle)
    x = int((640 - 256) / 2)
    y = x - 50
    canvas.paste(round_img, (x, y), round_img)
    x = int((640 - 540) / 2)
    y = 425
    canvas.paste(text_basemap, (x, y), text_basemap)
    canvas = write_text(
        canvas,
        text=nickname,
        position=(320, 451),
        font_path=f"{res_path}/font/REEJI-HonghuangLiGB-SemiBold.ttf",
        font_size=28,
    )
    canvas = write_text(
        canvas,
        text="签 到 成 功 !",
        position=(320, 489),
        font_path=f"{res_path}/font/REEJI-HonghuangLiGB-SemiBold.ttf",
        font_size=25,
    )
    canvas = write_text(
        canvas,
        text=f"签到天数  {signed_days}   好感度  {favorability}",
        position=(320, 527),
        font_path=f"{res_path}/font/REEJI-HonghuangLiGB-SemiBold.ttf",
        font_size=20,
    )
    canvas = write_text(
        canvas,
        text=hitokoto,
        position=(320, 562),
        font_path=f"{res_path}/font/zhanku.ttf",
        font_size=20,
    )

    io = BytesIO()
    canvas.save(io, format="png")
    return io.getvalue()
