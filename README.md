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

如果使用百炼作为LLM：

准备AK，SK，百炼api-key，然后执行:

```shell
export ALI_CLOUD_ACCESS_KEY_ID='AK' 
export ALI_CLOUD_ACCESS_KEY_SECRET='SK'
export DASHSCOPE_API_KEY='API_KEY'
export DASHSCOPE_LLM_NAME='qwen-turbo'  # 模型名称，可选列表：https://help.aliyun.com/zh/model-studio/developer-reference/what-is-qwen-llm?spm=a2c4g.11186623.0.0.6f41528arzsTD9

streamlit run Home.py
```

如果使用PAI EAS作为LLM：

准备AK，SK，PAI的Endpoint和Token，然后执行:

```shell
export ALI_CLOUD_ACCESS_KEY_ID='AK' 
export ALI_CLOUD_ACCESS_KEY_SECRET='SK'
export EAS_SERVICE_URL='EAS_SERVICE_URL'
export EAS_SERVICE_TOKEN='EAS_SERVICE_TOKEN'

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
