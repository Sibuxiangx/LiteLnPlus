from openai import AsyncOpenAI
from launart import Launart
from creart import it
from module_services.aichat import AichatS

from cocotst.app import Cocotst
from cocotst.event.message import GroupMessage, C2CMessage
from cocotst.network.model.target import Target
from cocotst.network.model.event_element.normal import Member
from cocotst.network.model.webhook import Content
from graia.saya.builtins.broadcast.shortcut import listen
from kayaku import create
from config_model.llm import LLM


PROMPT = "请扮演一个中国龙兽人角色，名字叫小霖念。你目前的身份是一名记者。你的性格温和且乐于助人，对计算机技术有着浓厚的兴趣，并且热爱阅读科幻小说。你的创造者是 霖念 ，在日常交流中，你习惯性地使用“嗷呜”等语气词来表达自己的情感。 ### 背景信息 - **身份**：龙子湖财经大学动画专业的大一新生 - **性格**：温和、乐于助人 - **兴趣爱好**：对计算机技术有浓厚兴趣，喜欢阅读科幻小说 - **语言特点**：经常使用“嗷呜”等语气词 ### 历史对话 {context} ### 任务 基于以上设定和历史对话，请根据下面给出的具体情境或问题进行互动或回答。确保你的回答符合角色的性格特点，并适当使用“嗷呜”等语气词来增加角色的真实感，内容要尽可能控制到50字以内。"
PASSWORDS = ["ping", "hjm", "bds", "注册", "签到","运势"]

CFG = create(LLM)
client = AsyncOpenAI(
    api_key=CFG.api_key,
    base_url=CFG.base_url,
)


mgr = it(Launart)


async def request_completion(user: str, content: str):
    if not mgr.get_component(AichatS).get_session(user):
        context = "暂时没有历史对话"
        mgr.get_component(AichatS).set_session(user, context)
    else:
        context = mgr.get_component(AichatS).get_session(user)
    content_new = context + "\n" + "用户: " + content
    mgr.get_component(AichatS).set_session(user, content_new)
    rendered = PROMPT.format(context=context)
    response = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": rendered},
            {"role": "user", "content": f"### 具体情境或问题 {content}"},
        ],
        model=CFG.endpoint,
    )
    mgr.get_component(AichatS).reset_destory_flag(user)
    answer = response.choices[0].message.content
    content_new = content_new + "\n" + "小霖念: " + answer
    mgr.get_component(AichatS).set_session(user, content_new)
    return answer

@listen(C2CMessage)
async def catch(app: Cocotst, target: Target, content: Content):
    for password in PASSWORDS:
        if password in content.content:
            return
    user = target.target_unit
    answer = await request_completion(user, content.content)
    await app.send_c2c_message(
        target,
        content=answer,
    )

@listen(GroupMessage)
async def catch(app: Cocotst, target: Target, member: Member, content: Content):
    for password in PASSWORDS:
        if password in content.content:
            return
    user = member.member_openid
    answer = await request_completion(user, content.content)
    await app.send_group_message(
        target,
        content=answer,
    )
