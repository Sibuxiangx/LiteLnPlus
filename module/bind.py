from cocotst.app import Cocotst
from database.model import User
from cocotst.event.message import GroupMessage, C2CMessage
from cocotst.network.model.target import Target
from cocotst.network.model.event_element.normal import Member
from cocotst.network.model.webhook import Content
from cocotst.message.parser.base import QCommandMatcher
from graia.saya.builtins.broadcast.shortcut import listen
from loguru import logger


@listen(GroupMessage)
async def catch(
    app: Cocotst,
    target: Target,
    member: Member,
    content: Content = QCommandMatcher("绑定"),
):
    qq_number = content.content
    uuid = member.member_openid

    # 验证是否已注册
    if not (user := await User.find_one(User.uid == uuid)):
        await app.send_group_message(
            target,
            content="你还未注册小霖念俱乐部，请发送 /注册 【昵称】 来注册一个账号",
        )
        return

    # 验证QQ号格式
    if not qq_number.isdigit() or len(qq_number) < 5 or len(qq_number) > 11:
        await app.send_group_message(
            target,
            content="QQ号格式不正确，请输入5-11位数字",
        )
        return

    # 检查QQ号是否已被绑定
    if await User.find_one(User.qq_number == qq_number):
        await app.send_group_message(
            target,
            content="该QQ号已被绑定，请使用其他QQ号",
        )
        return

    # 更新用户QQ号
    user.qq_number = qq_number
    await user.save()
    
    logger.info(f"[Mod|Bind] QQ绑定详情\nUUID: {uuid}\nQQ: {qq_number}")
    await app.send_group_message(
        target,
        content=f"绑定成功！已将QQ号 {qq_number} 绑定到您的账号",
    )


@listen(C2CMessage)
async def catch(
    app: Cocotst,
    target: Target,
    content: Content = QCommandMatcher("绑定"),
):
    qq_number = content.content
    uuid = target.target_unit

    # 验证是否已注册
    if not (user := await User.find_one(User.uid == uuid)):
        await app.send_c2c_message(
            target,
            content="你还没有注册哦！请先发送 /注册 【昵称】 来注册一个账号",
        )
        return

    # 验证QQ号格式
    if not qq_number.isdigit() or len(qq_number) < 5 or len(qq_number) > 11:
        await app.send_c2c_message(
            target,
            content="QQ号格式不正确，请输入5-11位数字",
        )
        return

    # 检查QQ号是否已被绑定
    if await User.find_one(User.qq_number == qq_number):
        await app.send_c2c_message(
            target,
            content="该QQ号已被其他账号绑定",
        )
        return

    # 更新用户QQ号
    user.qq_number = qq_number
    await user.save()
    
    logger.info(f"[Mod|Bind] QQ绑定详情\nUUID: {uuid}\nQQ: {qq_number}")
    await app.send_c2c_message(
        target,
        content=f"QQ号绑定成功！已将QQ号 {qq_number} 与您的账号绑定",
    )