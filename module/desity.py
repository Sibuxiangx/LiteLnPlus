from cocotst.app import Cocotst
from openai import AsyncOpenAI
from datetime import datetime
from cocotst.event.message import GroupMessage, C2CMessage
from cocotst.network.model.target import Target
from cocotst.network.model.event_element.normal import Member
from cocotst.message.parser.base import QCommandMatcher
from graia.saya.builtins.broadcast.shortcut import listen, decorate
from pathlib import Path
import aiofiles
from kayaku import create
from config_model.llm import LLM

PROMPT = """
假设你是一个能够预测个人运势的智能助手，这是今天的日期：{date} ，这是用户id {uid} 请根据以下结构随机生成今日运势报告,运势可以有好有坏，请简单明了的说明，字数控制在200字以内，必要时使用关键词而不是句子。

开场问候语：泥嚎啊

财运：

桃花：

特别运势：

选其一： 今日推荐诗歌一首（引用经典）或者 今日推荐阅读书籍一本（包括书名及简短推荐理由）：

对今天的总体点评与建议：

"""

CFG = create(LLM)

client = AsyncOpenAI(
    api_key=CFG.api_key,
    base_url=CFG.base_url,
)

@listen(GroupMessage)
@decorate(QCommandMatcher("运势"))
async def desity(app: Cocotst, target: Target,member: Member):
    date = datetime.now().strftime(r"%Y_%m_%d")
    cache_path = Path(f"cache/destiny/{date}_{member.member_openid}.ctxt")
    if cache_path.exists():
        async with aiofiles.open(cache_path, "r") as f:
            content = await f.read()
        await app.send_group_message(
            target,
            content=content,
        )
        return
    prompt = PROMPT.format(date=date, uid=member.member_openid)
    response = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "今日运势"},
        ],
        model=CFG.endpoint,
    )
    answer = response.choices[0].message.content
    async with aiofiles.open(cache_path, "w") as f:
        await f.write(answer)
    await app.send_group_message(
        target,
        content=answer,
    )

@listen(C2CMessage)
@decorate(QCommandMatcher("运势"))
async def desity(app: Cocotst, target: Target):
    date = datetime.now().strftime(r"%Y_%m_%d")
    cache_path = Path(f"cache/destiny/{date}_{target.target_unit}.ctxt")
    if cache_path.exists():
        async with aiofiles.open(cache_path, "r") as f:
            content = await f.read()
        await app.send_c2c_message(
            target,
            content=content,
        )
        return
    prompt = PROMPT.format(date=date, uid=target.target_unit)
    response = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "今日运势"},
        ],
        model=CFG.endpoint,
    )
    answer = response.choices[0].message.content
    async with aiofiles.open(cache_path, "w") as f:
        await f.write(answer)
    await app.send_c2c_message(
        target,
        content=answer,
    )