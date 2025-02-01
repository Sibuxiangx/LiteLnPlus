from beanie import Document, init_beanie
from cocotst.app import Cocotst, GroupMessage, C2CMessage
from cocotst.app import ApplicationReady
from cocotst.message.parser.base import QCommandMatcher
from cocotst.network.model.target import Target
from cocotst.network.model.webhook import Content
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.saya import Saya
from creart import it
import kayaku
from motor.motor_asyncio import AsyncIOMotorClient

from module_services.aichat import AichatS

kayaku.initialize({"{**}": "./config/{**}"})
from config_model.database import MongoDB
from config_model.qapi import QOpenAPI

appcfg = kayaku.create(QOpenAPI)
app = Cocotst(appid=appcfg.AppID, clientSecret=appcfg.AppSecret)
saya = it(Saya)
saya.install_behaviours(BroadcastBehaviour(broadcast=app.broadcast))


dbcfg = kayaku.create(MongoDB)

db = AsyncIOMotorClient(dbcfg.url)

app.mgr.add_component(AichatS())


@app.broadcast.receiver(ApplicationReady)
async def on_ready(event: ApplicationReady):
    await init_beanie(database=db.xlnbot, document_models=Document.__subclasses__())


@app.broadcast.receiver(GroupMessage, decorators=[QCommandMatcher("ping")])
async def catch(app: Cocotst, target: Target, content: Content):
    await app.send_group_message(
        target,
        content="🎉 Hello LiteLnPlus! 🎉\nPowered By Linota & Graia Toolchain",
    )


@app.broadcast.receiver(C2CMessage, decorators=[QCommandMatcher("ping")])
async def catch(app: Cocotst, target: Target, content: Content):
    await app.send_c2c_message(
        target,
        content="🎉 Hello LiteLnPlus! 🎉\nPowered By Linota & Graia Toolchain",
    )


with saya.module_context():
    saya.require("module.signin")
    saya.require("module.login")
    # saya.require("module.aichat")
    saya.require("module.desity")
    saya.require("module.rank")
    saya.require("module.bind")
    saya.require("module.b50")
    saya.require("module.ttgame")

kayaku.save_all()


if __name__ == "__main__":
    app.launch_blocking()
