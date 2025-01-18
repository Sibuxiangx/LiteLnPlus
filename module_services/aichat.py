import asyncio
import contextlib
from typing import Dict
from launart import Service
from asyncio import sleep
from loguru import logger


class AichatS(Service):
    id = "aichat"
    context: Dict = {}
    destory_flag: Dict = {}

    @property
    def stages(self):
        return {"preparing", "blocking", "cleanup"}

    @property
    def required(self):
        return set()

    def set_session(self, user_id: str, context: str):
        self.context[user_id] = context

    def get_session(self, user_id: str) -> str:
        if not user_id in self.context:
            return ""
        return self.context[user_id]

    def reset_destory_flag(self, user_id: str):
        self.destory_flag[user_id] = 180

    async def check_destory_flag(self):
        while True:
            for user_id in self.destory_flag:
                self.destory_flag[user_id] -= 3
                if self.destory_flag[user_id] <= 0:
                    self.context.pop(user_id)
                    self.destory_flag.pop(user_id)
                    logger.info(f"Session for {user_id} has been destoryed.")
            await sleep(3)

    async def launch(self, manager):
        async with self.stage("preparing"):
            pass
        async with self.stage("blocking"):
            query_tsk = asyncio.create_task(self.check_destory_flag())
            await manager.status.wait_for_sigexit()
        async with self.stage("cleanup"):
            query_tsk.cancel()
            with contextlib.suppress(asyncio.CancelledError):  #
                await query_tsk
