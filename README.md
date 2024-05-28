## Requirements

1. Install python>=3.9

2. Create the venv:

```shell
python -m venv $(pwd)/venv
source $(pwd)/venv/bin/activate    
```

3. Install requirements

```shell
pip install -r requirements.txt
```

## Prepare your adbpg instance

#### 1. Create an adbpg instance;
Refer to [common-by](https://common-buy.aliyun.com/?commodityCode=GreenplumPost&regionId=cn-beijing&request=%7B%7D), 
please select the EngineVersion as 6.0 and Vector Engine Optimization as enabled.

#### 2. Create an account;

Replace the `region` and `instance_id` of the url: https://gpdbnext.console.aliyun.com/gpdb/{region}/list/nav/{instance_id}/storageelastic/user and visit it, you can create an initial account.

#### 3. Get your ak and sk

Get your ak and sk refer to [doc](https://www.alibabacloud.com/help/en/analyticdb-for-postgresql/support/create-an-accesskey-pair?spm=a2c63.l28256.0.0.11ad2d176sqRw6).


## Start the app

```shell
export ALI_CLOUD_ACCESS_KEY_ID='YOUR_AK'       # aliyun ram ak
export ALI_CLOUD_ACCESS_KEY_SECRET='YOUR_SK'   # aliyun ram sk
export ADBPG_INSTANCE_ID='gp-test1234'         # your adbpg instance id
export ADBPG_INSTANCE_REGION='cn-hangzhou'     # region id of your adbpg instance

streamlit run Home.py
```


## Use cases

#### 1. Initialize the vector database

Visit http://localhost:8501/ and enter the account and password created before.

#### 2. Manage namespace

Visit http://localhost:8501/Namespace and create a namespace with a custom password.

#### 4. Manage document collections

Visit http://localhost:8501/KnowledgeBase and select the namespace created last step.

Click `Create document collection` button, then you can create a document collection.


#### 5. Manage documents

Visit http://localhost:8501/KnowledgeBase and enter the document collection created last step.

- Text Retrieval
- Image Retrieval
- Upload Document
- Upload Chunks
- Document List
