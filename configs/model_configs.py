import os

DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY')
EAS_SERVICE_URL = os.environ.get('EAS_SERVICE_URL')
EAS_SERVICE_TOKEN = os.environ.get('EAS_SERVICE_TOKEN')

PROMPT_TEMPLATES = {
    "default":
        """
    <指令>根据已知信息，简洁和专业的来回答问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题”，不允许在答案中添加编造成分，答案请使用中文。 </指令>
    <已知信息>{context}</已知信息>、
    <问题>{question}</问题>
    """,

    "Empty":
        """
    <指令>请根据用户的问题，进行简洁明了的回答</指令>
    <问题>{question}</问题>
    """,
}
