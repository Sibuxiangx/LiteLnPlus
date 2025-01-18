from kayaku import config


@config("llm")
class LLM:
    api_key: str = ""
    base_url: str = "https://ark.cn-beijing.volces.com/api/v3/"
    endpoint: str = ""