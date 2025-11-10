import io
import os
from distutils.util import strtobool
from http.client import responses

import uvicorn
import logging
from dotenv import load_dotenv
from fastapi import Request, HTTPException, UploadFile, File, Form
from fastapi.exceptions import RequestValidationError
from funasr.models.conformer.encoder import ChunkEncoderLayer
from pydantic import BaseModel
from alibabacloud_gpdb20160503.client import Client as gpdb20160503Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_gpdb20160503 import models as gpdb_20160503_models
# from alibabacloud_gpdb20160503_inner import models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional, Union
from typing import Optional
from fastapi import FastAPI, Depends, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests

load_dotenv()

app = FastAPI()
# 创建一个 HTTPBearer 实例
auth_scheme = HTTPBearer()

# 配置日志为DEBUG级别
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    expected_api_key = os.getenv("API_KEY") # TODO Your API key of this API
    # if credentials.scheme.lower() != "bearer" or credentials.credentials != expected_api_key:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.credentials

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    raw_body = await request.body()
    logger.error("Raw Body:", raw_body.decode("utf-8"))
    logger.error(f"Validation failed for request {request.url}: {str(request.body())}: {exc.errors()}")
    raise HTTPException(status_code=422, detail="Validation failed")

class ADBPGClient:
    def create_client(self) -> gpdb20160503Client:
        """
        使用AK&SK初始化账号Client
        @return: Client
        @throws Exception
        """
        # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考。
        # 建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html。
        config = open_api_models.Config(
        # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID。,
        access_key_id=os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
        # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_SECRET。,
        access_key_secret=os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'],
        # Endpoint 请参考 https://api.aliyun.com/product/gpdb
        endpoint=os.environ['ADBPG_ENDPOINT'],
        # 下沉版调用需要以下参数
        # protocol='http',
        # user_agent="Python Client",
        # region_id=os.getenv("ALIBABA_CLOUD_REGION_ID"),
        # max_idle_conns=200
        )
        return gpdb20160503Client(config)

    def create_namespace(self,
            namespace:str,
            namespacepassword:str,
    ) -> None:
        client = self.create_client()
        create_namespace_request = gpdb_20160503_models.CreateNamespaceRequest(
            region_id=os.getenv("ALIBABA_CLOUD_REGION_ID"),
            dbinstance_id=os.getenv("ADBPG_INSTANCE_ID"),
            manager_account=os.getenv("ADBPG_MANAGER_ACCOUNT"),
            manager_account_password= os.getenv("ADBPG_MANAGER_ACCOUNT_PASSWORD"),
            namespace=namespace,
            namespace_password=namespacepassword,
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            client.create_namespace_with_options(create_namespace_request, runtime)
            return Response(message="success", code=200)
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            # 诊断地址
            UtilClient.assert_as_string(error.message)
            return Response(message=error.message, code=400)

    def create_document_collection(self,
                                   namespace:str,
                                   col:str,
                                   metadata:str,
                                   enable_graph:bool,
                                   llm_model:str,
                                   language:str,
                                   entity_types:list[str],
                                   relationship_types:list[str]
    ) -> None:
        client = self.create_client()
        create_document_collection_request = gpdb_20160503_models.CreateDocumentCollectionRequest(
            region_id=os.getenv("ALIBABA_CLOUD_REGION_ID"),
            dbinstance_id=os.getenv("ADBPG_INSTANCE_ID"),
            manager_account=os.getenv("ADBPG_MANAGER_ACCOUNT"),
            manager_account_password=os.getenv("ADBPG_MANAGER_ACCOUNT_PASSWORD"),
            namespace=namespace,
            collection=col,
            metadata=metadata, #,'{"title":"text","page":"int"}'
            enable_graph=enable_graph,
            llmmodel=llm_model,
            language=language,
            entity_types=entity_types,
            relationship_types=relationship_types,
            # entity_types=["政策", "时间", "职务", "事件", "单位", "项目","人物","经历","地点","评价","背景"],
            # relationship_types=["支持", "导致", "发生", "影响", "关联", "隶属","使用"]
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            response = client.create_document_collection_with_options(create_document_collection_request, runtime)
            print(response.body)
            return Response(message=str(response.body), code=200)
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            if error.code == "Collection.AlreadyExists":
                return Response(message="success", code=200)
            else:
                print(error.message)
                # 诊断地址
                print(error.data.get("Recommend"))
                UtilClient.assert_as_string(error.message)
                return Response(message=error.message, code=400)

    def upload_document(self,
                       namespace:str,
                       namespace_password:str,
                       collection:str,
                       filename:str,
                       document:str,
                       chunk_size:int,
                       chunk_overlap: int,
                       text_spliter: str,
                       vl_enhance: bool
    ) -> None:
        client = self.create_client()
        gpdb_20160503_models.UploadDocumentAsyncRequest(

        )
        upload_document_async_request = gpdb_20160503_models.UploadDocumentAsyncRequest(
            region_id=os.getenv("ALIBABA_CLOUD_REGION_ID"),
            dbinstance_id=os.getenv("ADBPG_INSTANCE_ID"),
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            # file_url_object = io.BytesIO(self.get_file_bytes(document)),
            file_url = document,
            file_name=filename,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            document_loader_name='ADBPGLoader',
            text_splitter_name="RecursiveCharacterTextSplitter",
            vl_enhance=vl_enhance
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            response = client.upload_document_async(upload_document_async_request)
            return Response(message=str(response.body), code=200)
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print("upload_document:" + error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)
            return Response(message=error.message, code=200)

    def graph_retrieval(self,
                  namespace:str,
                  namespace_password:str,
                  col:str,
                  query:str,
                  top_k:int,
                  graph_enhance: bool
                  ):
        client = self.create_client()
        query_content_request = gpdb_20160503_models.QueryContentRequest(
            region_id=os.getenv("ALIBABA_CLOUD_REGION_ID"),
            dbinstance_id=os.getenv("ADBPG_INSTANCE_ID"),
            namespace=namespace,
            namespace_password=namespace_password,
            collection=col,
            content=query,
            top_k=top_k,
            use_full_text_retrieval=True,
            graph_enhance=graph_enhance,
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            res = client.query_content_with_options(query_content_request, runtime)
            # print("res.body:", res.body)
            return res.body
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            # 诊断地址
            UtilClient.assert_as_string(error.message)
            return Response(message=error.message, code=400)

    def retrieval(self,
                  namespace:str,
                  namespace_password:str,
                  col:str,
                  query:str,
                  top_k:int
                  ) -> list[dict]:
        client = self.create_client()
        hybrid_search_args = {
            "RRF": {
                "k": 60
            }
        }
        query_content_request = gpdb_20160503_models.QueryContentRequest(
            region_id=os.getenv("ALIBABA_CLOUD_REGION_ID"),
            dbinstance_id=os.getenv("ADBPG_INSTANCE_ID"),
            namespace=namespace,
            namespace_password=namespace_password,
            collection=col,
            content=query,
            top_k=top_k,
            use_full_text_retrieval=True,
            hybrid_search="RRF",
            hybrid_search_args=hybrid_search_args,
            recall_window=[0, 0],
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            res = client.query_content_with_options(query_content_request, runtime)
            # print("res.body:", res.body)

            merge_res = []
            for item in res.body.window_matches.window_matches:
               tmp_res = item.window_match.window_match[0]
               for i in range(1, len(item.window_match.window_match)):
                   tmp_res.content += item.window_match.window_match[i].content
               merge_res.append(tmp_res.to_map())
            return merge_res
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            # 诊断地址
            UtilClient.assert_as_string(error.message)
            return Response(message=error.message, code=400)

    def delete_document(self,
                       namespace:str,
                       namespace_password:str,
                       collection:str,
                       file_name:str
    ) -> None:
        """
        读取文件
        """
        client = self.create_client()

        delete_document_request = gpdb_20160503_models.DeleteDocumentRequest(
            region_id=os.getenv("ALIBABA_CLOUD_REGION_ID"),
            dbinstance_id=os.getenv("ADBPG_INSTANCE_ID"),
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            file_name=file_name
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            client.delete_document_with_options(delete_document_request, runtime)
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)

    def reranker(self,
                query:str,
                docs: list[dict]):
       client = self.create_client()
       rerank_request = gpdb_20160503_models.RerankRequest(
           region_id=os.getenv("ALIBABA_CLOUD_REGION_ID"),
           dbinstance_id=os.getenv("ADBPG_INSTANCE_ID"),
           query=query,
           documents=docs,
        #    model='bge-reranker-v2-minicpm-layerwise',
           return_documents=False
       )
       runtime = util_models.RuntimeOptions()
       try:
           # 复制代码运行请自行打印 API 的返回值
           res = client.rerank_with_options(rerank_request, runtime)
           return res.body.results.results
       except Exception as error:
           # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
           # 错误 message
           print(error.message)
           # 诊断地址
           print(error.data.get("Recommend"))
           UtilClient.assert_as_string(error.message)

    def upsert_chunks(self,
                      filename,
                      namespace,
                      namespace_password,
                      collection,
                      chunks: List[Dict]):
        client = self.create_client()
        upsert_chunks = []
        for chunk in chunks:
            content = chunk['content']
            metadata = chunk['metadata']
            upsert_chunk = gpdb_20160503_models.UpsertChunksRequest(
                metadata=metadata,
                content=content,
            )
            upsert_chunks.append(upsert_chunk)

        upsert_chunks_request = gpdb_20160503_models.UpsertChunksRequest(
            region_id=os.getenv("ALIBABA_CLOUD_REGION_ID"),
            dbinstance_id=os.getenv("ADBPG_INSTANCE_ID"),
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            file_name=filename,
            text_chunks=upsert_chunks,
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            client.upsert_chunks_with_options(upsert_chunks_request, runtime)
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)

    def get_upload_document_job(self,
                               namespace: str,
                               namespace_password: str,
                               collection: str,
                               job_id: str
    ) -> None:
        """
        获取文档上传任务状态
        """
        client = self.create_client()
        get_upload_document_job_request = gpdb_20160503_models.GetUploadDocumentJobRequest(
            region_id=os.getenv("ALIBABA_CLOUD_REGION_ID"),
            dbinstance_id=os.getenv("ADBPG_INSTANCE_ID"),
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            job_id=job_id,
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            response = client.get_upload_document_job_with_options(get_upload_document_job_request, runtime)
            return Response(message=str(response.body), code=200)
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print("get_upload_document_job:" + error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)
            return Response(message=error.message, code=400)

    def get_file_bytes(self, document):
    # 如果是以 http(s) 开头，认为是 URL
        if isinstance(document, str) and document.startswith("http"):
            response = requests.get(document)
            response.raise_for_status()
            return response.content
        # 如果是 str，转为 bytes
        elif isinstance(document, str):
            return document.encode("utf-8")
        # 如果已经是 bytes，直接返回
        elif isinstance(document, bytes):
            return document
        else:
            raise ValueError("Unsupported document type")


class Response(BaseModel):
    message: str
    code: int

class RetrivalResponse(BaseModel):
    records: list[dict]
    records_json: str


class NameSpace(BaseModel):
    namespace: str
    namespace_password: str

@app.post("/namespace/", response_model=Response)
def create_namespace(namespace: NameSpace):
    return ADBPGClient().create_namespace(namespace.namespace,
                                   namespace.namespace_password)

class Knowledge(BaseModel):
    knowledge_id: str
    metadata: str
    enable_graph: bool
    llm_model: Optional[str] = ""
    language: Optional[str] = ""
    entities: Optional[list[str]] = []
    relations: Optional[list[str]] = []


@app.post("/knowledge/", response_model=Response)
def create_collection(kb: Knowledge, api_key: str = Depends(verify_api_key)):
    ns = kb.knowledge_id.split("_")[0]
    col = kb.knowledge_id.split("_")[1]
    ns_pwd = api_key
    meta = kb.metadata
    
    # 处理可选字段
    llm_model = kb.llm_model if kb.llm_model else ""
    language = kb.language if kb.language else ""
    entities = kb.entities if kb.entities else []
    relations = kb.relations if kb.relations else []
    
    ADBPGClient().create_namespace(ns, ns_pwd)
    return ADBPGClient().create_document_collection(ns, col, meta,
                                                    kb.enable_graph,
                                                    llm_model,
                                                    language,
                                                    entities,
                                                    relations)


class UploadDocument(BaseModel):
    knowledge_id: str
    file_name: str
    metadata: str
    content: str
    chunk_size: int
    chunk_overlap: int
    text_spliter: str
    vl_enhance: bool

@app.post("/document/", response_model=Response)
def upload_document(document: UploadDocument, api_key: str = Depends(verify_api_key)):
    namespace = document.knowledge_id.split("_")[0]
    namespace_passwd = api_key
    col = document.knowledge_id.split("_")[1]
    content = document.content
    chunk_size = document.chunk_size
    chunk_overlap = document.chunk_overlap
    file_name = document.file_name
    text_spliter = document.text_spliter
    vl_enhance = document.vl_enhance

    return ADBPGClient().upload_document(namespace,
                                         namespace_passwd,
                                         col,
                                         file_name,
                                         content,
                                         chunk_size,
                                         chunk_overlap,
                                         text_spliter,
                                         vl_enhance)

class Retrieval(BaseModel):
    knowledge_id: str
    query: str
    retrieval_setting: dict
    graph_enhance: bool

@app.post("/retrieval/", response_model=RetrivalResponse)
def retrieval(retrival: Retrieval, api_key: str = Depends(verify_api_key)):
    namespace = retrival.knowledge_id.split("_")[0]
    col = retrival.knowledge_id.split("_")[1]
    query = retrival.query
    top_k = retrival.retrieval_setting.get("top_k", 2)
    namespace_password = api_key
    if retrival.graph_enhance:
        res = ADBPGClient().graph_retrieval(namespace,
                                            namespace_password,
                                            col,
                                            query,
                                            top_k,
                                            retrival.graph_enhance)
        print(res)
        return RetrivalResponse(records=[], records_json=str(res))

    res = ADBPGClient().retrieval(namespace,
                                  namespace_password,
                                  col,
                                  query,
                                  top_k)
    #处理window match内的内容，将content直接拼接，
    records = []
    reranker_req = []
    for item in res:
        record = dict()
        print(item)
        record["content"] = item.get("Content")
        reranker_req.append(item.get("Content"))
        record["title"] = item.get("FileName")
        record["metadata"] = item.get("Metadata")
        record["loadermetadata"] = item.get("LoaderMetadata")
        records.append(record)
    out_index = ADBPGClient().reranker(query, reranker_req)
    records_after_reranker = []
    for i in out_index:
        tmp_record = records[i.index]
        tmp_record["score"] = i.relevance_score
        records_after_reranker.append(tmp_record)

    return RetrivalResponse(records=records_after_reranker, records_json="")

# 定义 meta 字段的结构
class Meta(BaseModel):
    title: str
    title1: str

# 定义每个 item 的结构
class Chunk(BaseModel):
    content: str
    meta: Meta
@app.post("/chunks/", response_model=Response)
def upsert_chunks(knowledge_id: str,
                  filename: str,
                  kb_meta: List[Chunk],
                  api_key: str = Depends(verify_api_key)):
    namespace = knowledge_id.split("_")[0]
    namespace_passwd = api_key
    col = knowledge_id.split("_")[1]
    return ADBPGClient().upsert_chunks(filename,
                                       namespace,
                                       namespace_passwd,
                                       col,
                                       kb_meta)

class KbMeta(BaseModel):
    knowledge_id: str
    chunk_size: int
    chunk_overlap: int
    text_spliter: str

# 自定义响应状态类，类似于 ResponseState
class ResponseState:
    def __init__(self, success: bool, message: str, data: Optional[dict] = None):
        self.success = success
        self.message = message
        self.data = data

    def dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
        }
@app.post("/upload/{knowledge_id}/chunk/{chunk_size}/{chunk_overlap}/spliter/{text_spliter}", status_code=200)
@app.put("/upload/{knowledge_id}/chunk/{chunk_size}/{chunk_overlap}/spliter/{text_spliter}", status_code=200)
async def upload_file(knowledge_id: str = Path(..., description="知识库ID"),
                      chunk_size: int = Path(..., description="分块大小"),
                      chunk_overlap: int = Path(..., description="分块重叠度"),
                      text_spliter: str = Path(..., description="文本分割器"),
                      file: UploadFile = File(...)):
    """
    文件上传接口，支持 POST 和 PUT 方法。
    """
    namespace = knowledge_id.split("_")[0]
    # namespace_passwd = api_key
    col = knowledge_id.split("_")[1]
    chunk_size = chunk_size
    chunk_overlap = chunk_overlap

    try:
        # 读取文件内容
        file_content = await file.read()
        return ADBPGClient().upload_document(namespace,
                                             "Aa123456",
                                             col,
                                             file.filename,
                                             file_content,
                                             chunk_size,
                                             chunk_overlap,
                                             text_spliter)
    except Exception as e:
        # 处理异常
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")



class DeleteDocument(BaseModel):
    knowledge_id: str
    file_name: str

class GetUploadDocumentJob(BaseModel):
    knowledge_id: str
    job_id: str

@app.delete("/document", status_code=200)
async def delete_document(document: DeleteDocument, api_key: str = Depends(verify_api_key)):
    #api_key: str = Depends(verify_api_key)
    """
    读取文件
    """
    namespace = document.knowledge_id.split("_")[0]
    col = document.knowledge_id.split("_")[1]
    filename = document.file_name
    #namespace_passwd = api_key
    return ADBPGClient().delete_document(namespace,
                                         api_key,
                                         col,
                                         filename)

@app.post("/get-upload-job", response_model=Response)
async def get_upload_document_job(job_request: GetUploadDocumentJob, api_key: str = Depends(verify_api_key)):
    """
    获取文档上传任务状态
    """
    namespace = job_request.knowledge_id.split("_")[0]
    col = job_request.knowledge_id.split("_")[1]
    job_id = job_request.job_id
    namespace_password = api_key
    
    return ADBPGClient().get_upload_document_job(namespace,
                                                namespace_password,
                                                col,
                                                job_id)



if __name__ == '__main__':
    uvicorn.run(
        app="adbpg-graph:app",  # 指向 FastAPI 实例（main.py 中的 app）
        host="0.0.0.0",  # 监听所有网络接口（允许外部访问）
        port=8000,  # 端口号
        reload=True  # 开发时启用热重载（生产环境应关闭）
    )
