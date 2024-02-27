## 安装依赖

1.安装python>=3.9

2.使用venv:

```shell
python -m venv $(pwd)/venv
source $(pwd)/venv/bin/activate    
```

3.安装依赖

```shell
pip install -r requirements.txt
```

## 启动服务：

准备AK，SK，灵积api-key，然后执行:

```shell
export ALI_CLOUD_ACCESS_KEY_ID='AK' 
export ALI_CLOUD_ACCESS_KEY_SECRET='SK'
export DASHSCOPE_API_KEY='API_KEY'

streamlit run Home.py
```

#### 如果要指定实例：

启动时添加环境变量：

```shell
export ADBPG_INSTANCE_ID='实例名' 
export ADBPG_INSTANCE_REGION='地域'
export DASHSCOPE_API_KEY='API_KEY'
export ALI_CLOUD_ACCESS_KEY_ID='YOUR_AK'
export ALI_CLOUD_ACCESS_KEY_SECRET='YOUR_SK'

streamlit run Home.py
```
