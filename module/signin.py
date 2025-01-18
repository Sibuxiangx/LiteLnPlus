from cocotst.app import Cocotst
from database.model import User
from datetime import datetime
from toolkit.signin import generate_signin
from aiohttp import ClientSession
import random
from io import BytesIO
import asyncio
from cocotst.event.message import GroupMessage,C2CMessage
from cocotst.network.model import   Target, Member
from cocotst.message.parser.base import QCommandMatcher
from cocotst.message.element import Image
from graia.saya.builtins.broadcast.shortcut import listen, decorate
from loguru import logger
from kayaku import create
from config_model.qapi import QOpenAPI

QOPENID = create(QOpenAPI).AppID

@listen(GroupMessage)
@decorate(QCommandMatcher("签到"))
async def catch(app: Cocotst, target: Target,member: Member):
    uuid = member.member_openid
    user = await User.find_one(User.uid == uuid)
    if not user:
        await app.send_group_message(
            target,
            content="你好，你似乎没有注册过哦！请你发送 /注册 【昵称】来注册一个账号吧！",
        )
        user = User(
            uid="GUESTMODE_" + uuid,
            name="游 客 模 式",
            last_signed=datetime(1999, 1, 1),
            signed_days=0,
            favorability=0,
        )

    if user.last_signed.date() == datetime.now().date():
        await app.send_group_message(
            target,
            content="你好，你今天已经签到过了哦！",
        )
        return
    user.signed_days += 1
    user.last_signed = datetime.now()
    favorability = random.randint(10, 30)
    user.favorability += favorability
    await user.save()
    async with ClientSession() as session:
        async with session.get("https://v1.hitokoto.cn") as resp:
            hitokoto = (await resp.json())["hitokoto"]
    async with ClientSession() as session:
        async with session.get(f"https://q.qlogo.cn/qqapp/{QOPENID}/{uuid}/640") as resp:
            with BytesIO() as avatar:
                avatar.write(await resp.read())
                avatar.seek(0)
                result = await asyncio.to_thread(
                    generate_signin,
                    "resource/signin",
                    avatar,
                    user.name,
                    user.signed_days,
                    user.favorability,
                    hitokoto,
                )
    logger.info(f"[Mod|Signin] 用户签到详情\nUUID: {uuid}\n昵称: {user.name}\n好感度: {user.favorability}\n签到: {user.signed_days}天")
    await app.send_group_message(
        target, 
        content="你好，你已经成功签到！\n今日签到获得了"
        + str(favorability)
        + "点好感度！",
        element=Image(data=result),
    )

@listen(C2CMessage)
@decorate(QCommandMatcher("签到"))
async def catch(app: Cocotst, target: Target):
    uuid = target.target_unit
    user = await User.find_one(User.uid == uuid)
    if not user:
        await app.send_c2c_message(
            target,
            content="你好，你似乎没有注册过哦！请你发送 /注册 【昵称】来注册一个账号吧！",
        )
        user = User(
            uid="GUESTMODE_" + uuid,
            name="游 客 模 式",
            last_signed=datetime(1999, 1, 1),
            signed_days=0,
            favorability=0,
        )

    if user.last_signed.date() == datetime.now().date():
        await app.send_c2c_message(
            target,
            content="你好，你今天已经签到过了哦！",
        )
        return
    user.signed_days += 1
    user.last_signed = datetime.now()
    favorability = random.randint(10, 30)
    user.favorability += favorability
    await user.save()
    async with ClientSession() as session:
        async with session.get("https://v1.hitokoto.cn") as resp:
            hitokoto = (await resp.json())["hitokoto"]
    async with ClientSession() as session:
        async with session.get(f"https://q.qlogo.cn/qqapp/{QOPENID}/{uuid}/640") as resp:
            with BytesIO() as avatar:
                avatar.write(await resp.read())
                avatar.seek(0)
                result = await asyncio.to_thread(
                    generate_signin,
                    "resource/signin",
                    avatar,
                    user.name,
                    user.signed_days,
                    user.favorability,
                    hitokoto,
                )
    logger.info(f"[Mod|Signin] 用户签到详情\nUUID: {uuid}\n昵称: {user.name}\n好感度: {user.favorability}\n签到: {user.signed_days}天")
    await app.send_c2c_message(
        target,
        content="你好，你已经成功签到！\n今日签到获得了"
        + str(favorability)
        + "点好感度！",
        element=Image(data=result),
    )