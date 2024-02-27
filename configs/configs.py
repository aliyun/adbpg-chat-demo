import os

# ak sk:
ALI_CLOUD_ACCESS_KEY_ID = os.environ['ALI_CLOUD_ACCESS_KEY_ID']
ALI_CLOUD_ACCESS_KEY_SECRET = os.environ['ALI_CLOUD_ACCESS_KEY_SECRET']

# 实例信息，可选：
ADBPG_INSTANCE_ID = os.environ.get('ADBPG_INSTANCE_ID')
ADBPG_INSTANCE_REGION = os.environ.get('ADBPG_INSTANCE_REGION')

# 预发绑定hosts，并指定gpdb.cn-beijing.aliyuncs.com：
ALI_CLOUD_ENDPOINT = os.environ.get('ALI_CLOUD_ENDPOINT')
