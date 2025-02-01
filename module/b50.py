from typing import Dict, List, Tuple
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import asyncio
from io import BytesIO
from database.model import User
from cocotst.message.element import Image as MessageImage
from cocotst.event.message import GroupMessage
from cocotst.network.model.target import Target
from cocotst.network.model.event_element.normal import Member
from cocotst.message.parser.base import QCommandMatcher
from graia.saya.builtins.broadcast.shortcut import listen, decorate
from cocotst.network.model.webhook import Content
from cocotst.app import Cocotst
from cocotst.event.message import C2CMessage
from loguru import logger

MONO_FONT = "resource/font/sarasa-mono-sc-semibold.ttf"
TITLE_FONT = "resource/signin/font/REEJI-HonghuangLiGB-SemiBold.ttf"


async def fetch_player_data(qq_number: str) -> Dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://www.diving-fish.com/api/maimaidxprober/query/player",
            json={"qq": qq_number, "b50": True},
        ) as response:
            return await response.json()


def calculate_potential_score(achievements: float, ds: float) -> float:
    if achievements >= 100.5:
        return ds * 22.4 * 1.005
    elif achievements >= 100:
        return ds * 22.4
    elif achievements >= 99.5:
        return ds * 21.6
    elif achievements >= 99:
        return ds * 21.1
    elif achievements >= 98:
        return ds * 20.8
    elif achievements >= 97:
        return ds * 20.3
    elif achievements >= 94:
        return ds * 20.0
    else:
        return ds * 19.5


async def generate_analysis_image(qq_number: str) -> Tuple[Image.Image, List]:
    data = await fetch_player_data(qq_number)

    items_count = len(data["charts"]["dx"] + data["charts"]["sd"])
    row_height = 60
    total_height = 100 + (items_count * row_height)

    width = 2400
    img = Image.new("RGB", (width, total_height), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(MONO_FONT, 20)
    title_font = ImageFont.truetype(TITLE_FONT, 28)

    draw.text(
        (30, 20),
        f"玩家：{data['nickname']} - Rating: {data['rating']}",
        fill=(255, 255, 255),
        font=title_font,
    )

    all_charts = data["charts"]["dx"] + data["charts"]["sd"]
    all_charts.sort(key=lambda x: x["ra"], reverse=True)

    y_pos = 80
    for idx, chart in enumerate(all_charts):
        max_potential = calculate_potential_score(100.5, chart["ds"])
        current_potential = chart["ra"]
        improvement = max_potential - current_potential

        bg_color = (40, 40, 40) if idx % 2 == 0 else (50, 50, 50)
        draw.rectangle([(20, y_pos), (width - 20, y_pos + 50)], fill=bg_color)

        song_info = f"{chart['title']} [{chart['level']}] - {chart['achievements']}% (DS:{chart['ds']})"
        draw.text((30, y_pos + 10), song_info, fill=(255, 255, 255), font=font)

        potential_text = (
            f"潜力：+{improvement:.1f} ({current_potential:.1f} → {max_potential:.1f})"
        )
        potential_x = width - 400
        draw.text(
            (potential_x, y_pos + 10), potential_text, fill=(200, 200, 200), font=font
        )

        y_pos += 60

    return img, all_charts


@listen(GroupMessage)
@decorate(QCommandMatcher("b50"))
async def analyze_player(
    app: Cocotst, target: Target, member: Member, content: Content
):

    user = await User.find_one(User.uid == member.member_openid)
    if not user or not user.qq_number:
        await app.send_group_message(
            target,
            content="请先绑定QQ号或在指令后提供QQ号",
        )
        return
    qq_number = user.qq_number

    await app.send_group_message(
        target,
        content="正在查询中，请稍等片刻...",
    )

    result,charts = await generate_analysis_image(qq_number)
    buffer = BytesIO()
    result.save(buffer, format="PNG")
    buffer.seek(0)
    logger.info(f"[Mod|B50] 查分详情\nQQ: {qq_number}")
    await app.send_group_message(
        target,
        content=f"为你查询到的b50数据：",
        element=MessageImage(data=buffer.getvalue()),
    )
    suggestion_text = "建议提升曲目：\n"
    for chart in charts[:5]:  # 取前5首
        suggestion_text += f"{chart['title']} [{chart['level']}]\n"
    await app.send_group_message(
        target,
        content=suggestion_text,
    )


@listen(C2CMessage)
@decorate(QCommandMatcher("b50"))
async def analyze_player_c2c(app: Cocotst, target: Target, content: Content):

    user = await User.find_one(User.uid == target.target_unit)
    if not user or not user.qq_number:
        await app.send_c2c_message(
            target,
            content="请先绑定QQ号或在指令后提供QQ号",
        )
        return
    qq_number = user.qq_number

    await app.send_c2c_message(
        target,
        content="正在查询中，请稍等片刻...",
    )

    result,charts = await generate_analysis_image(qq_number)
    buffer = BytesIO()
    result.save(buffer, format="PNG")
    buffer.seek(0)
    logger.info(f"[Mod|B50] 查分详情\nQQ: {qq_number}")
    await app.send_c2c_message(
        target,
        content=f"为你查询到的b50数据：",
        element=MessageImage(data=buffer.getvalue()),
    )
    suggestion_text = "建议提升曲目：\n"
    for chart in charts[:5]:
        suggestion_text += f"{chart['title']} [{chart['level']}]\n"
    await app.send_c2c_message(
        target,
        content=suggestion_text,
    ) 
