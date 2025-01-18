from cocotst.app import Cocotst
from database.model import User
from datetime import datetime
from cocotst.event.message import GroupMessage,C2CMessage
from cocotst.network.model import Target, Member, Content
from cocotst.message.parser.base import QCommandMatcher
from graia.saya.builtins.broadcast.shortcut import listen
from toolkit.textsafe import verify_nickname
from loguru import logger


@listen(GroupMessage)
async def catch(
    app: Cocotst,
    target: Target,
    member: Member,
    content: Content = QCommandMatcher("注册"),
):
    nickname = content.content
    uuid = member.member_openid
    if await User.find_one(User.uid == uuid):
        await app.send_group_message(
            target,
            content="你好，你似乎已经注册过了哦！",
        )
        return
    if not nickname:
        await app.send_group_message(
            target,
            content="你好，你似乎没有输入名字哦！",
        )
        return
    if user := await User.find_one(User.uid == "GUESTMODE_" + uuid):
        result = await verify_nickname(nickname)
        if not result.verified:
            await app.send_group_message(
                target,
                content=f"注册失败，{result.msg}",
            )
            return
        await app.send_group_message(
            target,
            content=f"欢迎您正式注册！\n您将继承以下游客模式的数据：\n签到天数：{user.signed_days}\n好感度：{user.favorability}\n\n",
        )
        user.name = nickname
        user.uid = uuid
        await user.save()
        return
    result = await verify_nickname(nickname)
    if result.verified:
        await app.send_group_message(
            target,
            content=f"欢迎您加入小霖念俱乐部！注册成功",
        )
        logger.info(f"[Mod|Login] 用户注册详情\nUUID: {uuid}\n昵称: {nickname}")
        await User(
            uid=uuid,
            name=nickname,
            last_signed=datetime(1999, 1, 1),
            signed_days=0,
            favorability=0,
        ).save()
    else:
        await app.send_group_message(
            target,
            content=f"注册失败，{result.msg}",
        )

@listen(C2CMessage)
async def catch(
    app: Cocotst,
    target: Target,
    content: Content = QCommandMatcher("注册"),
):
    nickname = content.content
    uuid = target.target_unit
    if await User.find_one(User.uid == uuid):
        await app.send_c2c_message(
            target,
            content="你好，你似乎已经注册过了哦！",
        )
        return
    if not nickname:
        await app.send_c2c_message(
            target,
            content="你好，你似乎没有输入名字哦！",
        )
        return
    if user := await User.find_one(User.uid == "GUESTMODE_" + uuid):
        result = await verify_nickname(nickname)
        if not result.verified:
            await app.send_c2c_message(
                target,
                content=f"注册失败，{result.msg}",
            )
            return
        await app.send_c2c_message(
            target,
            content=f"欢迎您正式注册！\n您将继承以下游客模式的数据：\n签到天数：{user.signed_days}\n好感度：{user.favorability}\n\n",
        )
        user.name = nickname
        user.uid = uuid
        await user.save()
        return
    result = await verify_nickname(nickname)
    if result.verified:
        await app.send_c2c_message(
            target,
            content=f"欢迎您加入小霖念俱乐部！注册成功",
        )
        logger.info(f"[Mod|Login] 用户注册详情\nUUID: {uuid}\n昵称: {nickname}")
        await User(
            uid=uuid,
            name=nickname,
            last_signed=datetime(1999, 1, 1),
            signed_days=0,
            favorability=0,
        ).save()
    else:
        await app.send_c2c_message(
            target,
            content=f"注册失败，{result.msg}",
        )