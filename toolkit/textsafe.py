import kayaku
import os
import sys

from typing import List

from alibabacloud_green20220302.client import Client as Green20220302Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_green20220302 import models as green_20220302_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

from config_model.aliyun import Aliyun

import ujson

class Status:
    verified: bool = False
    msg: str = ""

    def __init__(self, verified: bool = True, msg: str = ""):
        self.verified = verified
        self.msg = msg


def create_client() -> Green20220302Client:
    """
    使用AK&SK初始化账号Client
    @return: Client
    @throws Exception
    """
    cfgbasic = kayaku.create(Aliyun)
    config = open_api_models.Config(
        access_key_id=cfgbasic.access_key_id,
        access_key_secret=cfgbasic.access_key_secret,
    )

    config.endpoint = f"green-cip.cn-shenzhen.aliyuncs.com"
    return Green20220302Client(config)


async def verify_nickname(
    nickname: str,
):
    client = create_client()
    text_moderation_plus_request = green_20220302_models.TextModerationRequest(
        service="nickname_detection",
        service_parameters=str(
            {
                "content": nickname,
            }
        ),
    )
    runtime = util_models.RuntimeOptions()
    try:
        result = await client.text_moderation_with_options_async(
            text_moderation_plus_request, runtime
        )
        if result.body.data.reason == "":
            return Status(verified=True, msg="昵称正常")
        else:
            return Status(verified=False, msg="昵称违规警告⚠️")
    except Exception as error:
        return Status(verified=False, msg="服务出错了哦！")
