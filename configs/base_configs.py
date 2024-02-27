import logging

log_verbose = True

# 日志格式
LOG_FORMAT = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.basicConfig(format=LOG_FORMAT)

# https://api.aliyun.com/product/gpdb
regions_cn_map = {
    '北京': 'cn-beijing',
    '张家口': 'cn-zhangjiakou',
    '呼和浩特': 'cn-huhehaote',
    '杭州': 'cn-hangzhou',
    '上海': 'cn-shanghai',
    '深圳': 'cn-shenzhen',
    '成都': 'cn-chengdu',
    '香港': 'cn-hongkong',
    '日本（东京）': 'ap-northeast-1',
    '韩国（首尔）': 'ap-northeast-2',
    '新加坡': 'ap-southeast-1',
    '澳大利亚（悉尼）': 'ap-southeast-2',
    '马来西亚（吉隆坡）': 'ap-southeast-3',
    '印度尼西亚（雅加达）': 'ap-southeast-5',
    '泰国（曼谷）': 'ap-southeast-7',
    '美国（弗吉尼亚）': 'us-east-1',
    '美国（硅谷）': 'us-west-1',
    '英国（伦敦）': 'eu-west-1',
    '德国（法兰克福）': 'eu-central-1',
    '印度（孟买）': 'ap-south-1',
    '沙特（利雅得）': 'me-central-1',
    '华东1 金融云': 'cn-hangzhou-finance',
    '华东2 金融云': 'cn-shanghai-finance-1',
    '华南1 金融云': 'cn-shenzhen-finance-1',
}
