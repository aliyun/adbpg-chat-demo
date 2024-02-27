from alibabacloud_gpdb20160503.client import Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_gpdb20160503 import models as gpdb_20160503_models
from configs import *
import streamlit as st
from typing import List, Dict, Any
from alibabacloud_tea_util import models as util_models
import time
import io


class AdbpgClient:
    def __init__(self, region=None, instance=None):
        config = open_api_models.Config(access_key_id=ALI_CLOUD_ACCESS_KEY_ID,
                                        access_key_secret=ALI_CLOUD_ACCESS_KEY_SECRET)
        if region:
            self.region = region
        else:
            self.region = ADBPG_INSTANCE_REGION
        if instance:
            self.instance = instance
        else:
            self.instance = ADBPG_INSTANCE_ID

        if ALI_CLOUD_ENDPOINT:
            self.endpoint = ALI_CLOUD_ENDPOINT
        else:
            # https://api.aliyun.com/product/gpdb
            if self.region in ("cn-beijing", "cn-hangzhou", "cn-shanghai", "cn-shenzhen", "cn-hongkong",
                                         "ap-southeast-1", "cn-hangzhou-finance", "cn-shanghai-finance-1",
                                         "cn-shenzhen-finance-1", "cn-beijing-finance-1"):
                self.endpoint = "gpdb.aliyuncs.com"
            else:
                self.endpoint = f'gpdb.{self.region}.aliyuncs.com'
        config.endpoint = self.endpoint
        config.region_id = self.region
        self.client = Client(config)
        self.get_client_code_str = f'''
from alibabacloud_gpdb20160503.client import Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_gpdb20160503 import models as gpdb_20160503_models

def get_client():
    config = open_api_models.Config(access_key_id='{ALI_CLOUD_ACCESS_KEY_ID}', access_key_secret='****')
    config.endpoint = '{self.endpoint}'
    config.region_id = '{self.region}'
    return Client(config)
'''

    def describe_dbinstance_attribute(self, dbinstance_id) -> \
            gpdb_20160503_models.DescribeDBInstanceAttributeResponseBodyItemsDBInstanceAttribute:
        request = gpdb_20160503_models.DescribeDBInstanceAttributeRequest(
            dbinstance_id=dbinstance_id,
        )
        response = self.client.describe_dbinstance_attribute(request)
        logger.info(f"describe_dbinstance_attribute response code: {response.status_code}, body:{response.body}")
        return response.body.items.dbinstance_attribute[0]

    def list_vector_db_instances(self) -> \
            List[gpdb_20160503_models.DescribeDBInstanceAttributeResponseBodyItemsDBInstanceAttribute]:
        st.session_state.home_code_content = self.get_client_code_str + f'''

def describe_dbinstance_attribute(dbinstance_id):
    request = gpdb_20160503_models.DescribeDBInstanceAttributeRequest(
        dbinstance_id=dbinstance_id,
    )
    response = get_client.describe_dbinstance_attribute(request)
    return response.body.items.dbinstance_attribute[0]

def list_vector_db_instances():
    request = gpdb_20160503_models.DescribeDBInstancesRequest(
        region_id='{self.region}',
        dbinstance_modes=['StorageElastic'],
    )
    response = get_client().describe_dbinstances(request)
    version6_instances = [i for i in response.body.items.dbinstance if i.dbinstance_status != 'LOCKED'
                              and i.engine_version == '6.0']
    result = []
    for i in version6_instances:
        atr = describe_dbinstance_attribute(i.dbinstance_id)
        if atr.vector_configuration_status == 'enabled':
            result.append(atr)
    return result

list_vector_db_instances()
'''

        request = gpdb_20160503_models.DescribeDBInstancesRequest(
            region_id=self.region,
            dbinstance_modes=['StorageElastic'],
        )
        response = self.client.describe_dbinstances(request)
        logger.info(f"describe_dbinstances response code: {response.status_code}, body:{response.body}")
        version6_instances = [i for i in response.body.items.dbinstance if i.dbinstance_status != 'LOCKED'
                              and i.engine_version == '6.0']
        result = []
        for i in version6_instances:
            atr = self.describe_dbinstance_attribute(i.dbinstance_id)
            if atr.vector_configuration_status == 'enabled':
                result.append(atr)
        return result

    def describe_account(self) -> List[str]:
        request = gpdb_20160503_models.DescribeAccountsRequest(dbinstance_id=self.instance)
        response = self.client.describe_accounts(request)
        logger.info(f"describe_account response code: {response.status_code}, body:{response.body}")
        return [i.account_name for i in response.body.accounts.dbinstance_account]

    def init_vector_database(self, manager_account, manager_account_password):
        st.session_state.home_code_content = self.get_client_code_str + f'''
def init_vector_database():
    request = gpdb_20160503_models.InitVectorDatabaseRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        manager_account='{manager_account}',
        manager_account_password='{manager_account_password}'
    )
    response = get_client().init_vector_database(request)
'''
        request = gpdb_20160503_models.InitVectorDatabaseRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            manager_account=manager_account,
            manager_account_password=manager_account_password
        )
        response = self.client.init_vector_database(request)
        logger.info(f"init_vector_database response code: {response.status_code}, body:{response.body}")
        st.session_state.home_code_content += f'''
# output：
# response.status_code: {response.status_code}
# response.body: {response.body}
'''

    def create_namespace(self, manager_account, manager_account_password, namespace, namespace_password):
        st.session_state.namespace_code_content = self.get_client_code_str + f'''
def create_namespace():
    request = gpdb_20160503_models.CreateNamespaceRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        manager_account='{manager_account}',
        manager_account_password='{manager_account_password}',
        namespace='{namespace}',
        namespace_password='{namespace_password}'
    )
    response = get_client().create_namespace(request)
'''
        request = gpdb_20160503_models.CreateNamespaceRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            manager_account=manager_account,
            manager_account_password=manager_account_password,
            namespace=namespace,
            namespace_password=namespace_password
        )
        response = self.client.create_namespace(request)
        logger.info(f"create_namespace response code: {response.status_code}, body:{response.body}")
        st.session_state.namespace_code_content += f'''
# output：
# response.status_code: {response.status_code}
# response.body: {response.body}    
'''

    def list_namespaces(self, manager_account, manager_account_password) -> List[str]:
        st.session_state.namespace_code_content = self.get_client_code_str + f'''
def list_namespaces():
    request = gpdb_20160503_models.ListNamespacesRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        manager_account='{manager_account}',
        manager_account_password='{manager_account_password}',
    )
    response = get_client().list_namespaces(request)
    return response.body.namespaces.namespace
'''
        request = gpdb_20160503_models.ListNamespacesRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            manager_account=manager_account,
            manager_account_password=manager_account_password,
        )
        response = self.client.list_namespaces(request)
        logger.info(f"list_namespaces response code: {response.status_code}, body:{response.body}")
        st.session_state.namespace_code_content += f'''
# output:
# response.status_code: {response.status_code}
# namespaces: {response.body.namespaces.namespace}
'''
        return response.body.namespaces.namespace

    def delete_namespace(self, manager_account, manager_account_password, namespace):
        st.session_state.namespace_code_content = self.get_client_code_str + f'''
def delete_namespace():
    request = gpdb_20160503_models.DeleteNamespaceRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        manager_account='{manager_account}',
        manager_account_password='{manager_account_password}',
        namespace='{namespace}',
    )
    response = get_client().delete_namespace(request)
'''
        request = gpdb_20160503_models.DeleteNamespaceRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            manager_account=manager_account,
            manager_account_password=manager_account_password,
            namespace=namespace,
        )
        response = self.client.delete_namespace(request)
        logger.info(f"delete_namespace response code: {response.status_code}, body:{response.body}")
        st.session_state.namespace_code_content += f'''
# output:
# response.status_code: {response.status_code}
# body: {response.body}
'''

    def create_collection(self,
                          manager_account,
                          manager_account_password,
                          namespace,
                          collection,
                          dimension: int = None,
                          full_text_retrieval_fields: str = None,
                          hnsw_m: int = None,
                          pq_enable: int = None,
                          metadata: str = None,
                          metrics: str = None,
                          parser: str = None):
        request = gpdb_20160503_models.CreateCollectionRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            manager_account=manager_account,
            manager_account_password=manager_account_password,
            namespace=namespace,
            collection=collection,
            dimension=dimension,
            full_text_retrieval_fields=full_text_retrieval_fields,
            hnsw_m=hnsw_m,
            metadata=metadata,
            metrics=metrics,
            parser=parser,
            pq_enable=pq_enable,
        )
        response = self.client.create_collection(request)
        logger.info(f"create_namespace response code: {response.status_code}, body:{response.body}")

    def list_collections(self, namespace, namespace_password) -> List[str]:
        request = gpdb_20160503_models.ListCollectionsRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
        )
        response = self.client.list_collections(request)
        logger.info(f"list_collections response code: {response.status_code}, body:{response.body}")
        if response.body.count == 0:
            return []
        return response.body.collections.collection

    def describe_collection(self, namespace, namespace_password,
                            collection) -> gpdb_20160503_models.DescribeCollectionResponseBody:
        request = gpdb_20160503_models.DescribeCollectionRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
        )
        response = self.client.describe_collection(request)
        logger.info(f"describe_collection response code: {response.status_code}, body:{response.body}")
        return response.body

    def delete_collection(self, namespace, namespace_password, collection):
        request = gpdb_20160503_models.DeleteCollectionRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
        )
        response = self.client.delete_collection(request)
        logger.info(f"delete_collection response code: {response.status_code}, body:{response.body}")

    def upsert_collection_data(self, namespace, namespace_password, collection,
                               rows: List[gpdb_20160503_models.UpsertCollectionDataRequestRows]):
        request = gpdb_20160503_models.UpsertCollectionDataRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            rows=rows,
        )
        response = self.client.upsert_collection_data(request)
        logger.info(f"upsert_collection_data response code: {response.status_code}, body:{response.body}")

    def update_collection_data_metadata(self, namespace, namespace_password, collection,
                                        filter_str: str = None,
                                        ids: List[str] = None,
                                        metadata: Dict[str, Any] = None):
        request = gpdb_20160503_models.UpdateCollectionDataMetadataRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            filter=filter_str,
            ids=ids,
            metadata=metadata,
        )
        response = self.client.update_collection_data_metadata(request)
        logger.info(f"update_collection_data_metadata response code: {response.status_code}, body:{response.body}")

    def query_collection_data(self, namespace, namespace_password, collection, top_k,
                              content: str = None,
                              filter_str: str = None,
                              include_values: bool = None,
                              metrics: str = None,
                              vector: List[float] = None,
                              ) -> List[gpdb_20160503_models.QueryCollectionDataResponseBodyMatchesMatch]:
        request = gpdb_20160503_models.QueryCollectionDataRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            top_k=top_k,
            content=content,
            filter=filter_str,
            include_values=include_values,
            metrics=metrics,
            vector=vector,
        )
        response = self.client.query_collection_data(request)
        logger.info(f"query_collection_data response code: {response.status_code}, body:{response.body}")
        return response.body.matches.match

    def delete_collection_data(self, namespace, namespace_password, collection,
                               collection_data: str = None,
                               collection_data_filter: str = None) -> int:
        request = gpdb_20160503_models.DeleteCollectionDataRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            collection_data=collection_data,
            collection_data_filter=collection_data_filter,
        )
        response = self.client.delete_collection_data(request)
        logger.info(f"delete_collection_data response code: {response.status_code}, body:{response.body}")
        return response.body.applied_rows

    def create_document_collection(self, manager_account, manager_account_password, namespace, collection,
                                   embedding_model: str = None,
                                   full_text_retrieval_fields: str = None,
                                   hnsw_m: int = None,
                                   metadata: str = None,
                                   metrics: str = None,
                                   parser: str = None,
                                   pq_enable: int = None,
                                   external_storage: int = None):
        st.session_state.kb_code_content = self.get_client_code_str + f'''
def create_document_collection():
    request = gpdb_20160503_models.CreateDocumentCollectionRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        manager_account='{manager_account}',
        manager_account_password='{manager_account_password}',
        namespace='{namespace}',
        collection='{collection}',
        embedding_model='{embedding_model}',
        full_text_retrieval_fields='{full_text_retrieval_fields}',
        hnsw_m={hnsw_m},
        metadata='{metadata}',
        metrics='{metrics}',
        parser='{parser}',
        pq_enable={pq_enable},
        external_storage={external_storage},
    )
    response = get_client().create_document_collection(request)
'''
        request = gpdb_20160503_models.CreateDocumentCollectionRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            manager_account=manager_account,
            manager_account_password=manager_account_password,
            namespace=namespace,
            collection=collection,
            embedding_model=embedding_model,
            full_text_retrieval_fields=full_text_retrieval_fields,
            hnsw_m=hnsw_m,
            metadata=metadata,
            metrics=metrics,
            parser=parser,
            pq_enable=pq_enable,
            external_storage=external_storage,
        )
        response = self.client.create_document_collection(request)
        logger.info(f"create_document_collection response code: {response.status_code}, body:{response.body}")
        st.session_state.kb_code_content += f'''
# output:
# response.status_code: {response.status_code}
# body: {response.body}
'''

    def list_document_collections(self, namespace, namespace_password) -> \
            List[gpdb_20160503_models.ListDocumentCollectionsResponseBodyItemsCollectionList]:
        st.session_state.kb_code_content = self.get_client_code_str + f'''
def list_document_collections():
    request = gpdb_20160503_models.ListDocumentCollectionsRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        namespace='{namespace}',
        namespace_password='{namespace_password}',
    )
    response = get_client().list_document_collections(request)
'''
        request = gpdb_20160503_models.ListDocumentCollectionsRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
        )
        response = self.client.list_document_collections(request)
        logger.info(f"list_document_collections response code: {response.status_code}, body:{response.body}")
        st.session_state.kb_code_content += f'''
# output:
# response.status_code: {response.status_code}
# body: {response.body}
'''
        if response.body.count == 0:
            return []
        return response.body.items.collection_list

    def delete_document_collection(self, namespace, namespace_password, collection):
        st.session_state.kb_code_content = self.get_client_code_str + f'''
def delete_document_collection():
    request = gpdb_20160503_models.DeleteDocumentCollectionRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        namespace='{namespace}',
        namespace_password='{namespace_password}',
        collection='{collection}',
    )
    response = get_client().delete_document_collection(request)
'''
        request = gpdb_20160503_models.DeleteDocumentCollectionRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
        )
        response = self.client.delete_document_collection(request)
        logger.info(f"delete_document_collection response code: {response.status_code}, body:{response.body}")
        st.session_state.kb_code_content += f'''
# output:
# response.status_code: {response.status_code}
# body: {response.body}
'''

    def list_documents(self, namespace, namespace_password, collection) -> \
            List[gpdb_20160503_models.ListDocumentsResponseBodyItemsDocumentList]:
        pre_kb_code_content = self.get_client_code_str
        if 'pre_kb_code_content' in st.session_state and st.session_state.pre_kb_code_content:
            pre_kb_code_content = st.session_state.pre_kb_code_content
        st.session_state.kb_code_content = pre_kb_code_content + f'''
def list_documents():
    request = gpdb_20160503_models.ListDocumentsRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        namespace='{namespace}',
        namespace_password='{namespace_password}',
        collection='{collection}',
    )
    response = get_client().list_documents(request)
'''
        request = gpdb_20160503_models.ListDocumentsRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
        )
        response = self.client.list_documents(request)
        logger.info(f"list_documents response code: {response.status_code}, body:{response.body}")
        st.session_state.kb_code_content += f'''
# output:
# response.status_code: {response.status_code}
# body: {response.body}
'''
        st.session_state.pre_kb_code_content = ''
        return response.body.items.document_list

    def describe_document(self, namespace, namespace_password, collection, file_name) -> \
            gpdb_20160503_models.DescribeDocumentResponseBody:
        st.session_state.pre_kb_code_content = self.get_client_code_str + f'''
def describe_document():
    request = gpdb_20160503_models.DescribeDocumentRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        namespace='{namespace}',
        namespace_password='{namespace_password}',
        collection='{collection}',
        file_name='{file_name}',
    )
    response = get_client().describe_document(request)
'''
        request = gpdb_20160503_models.DescribeDocumentRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            file_name=file_name
        )
        response = self.client.describe_document(request)
        logger.info(f"describe_document response code: {response.status_code}, body:{response.body}")
        st.session_state.pre_kb_code_content += f'''
# output:
# response.status_code: {response.status_code}
# body: {response.body}
'''
        return response.body

    def delete_document(self, namespace, namespace_password, collection, file_name):
        st.session_state.pre_kb_code_content = self.get_client_code_str + f'''
def delete_document():
    request = gpdb_20160503_models.DeleteDocumentRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        namespace='{namespace}',
        namespace_password='{namespace_password}',
        collection='{collection}',
        file_name='{file_name}',
    )
    response = get_client().delete_document(request)
'''
        request = gpdb_20160503_models.DeleteDocumentRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            file_name=file_name
        )
        response = self.client.delete_document(request)
        logger.info(f"delete_document response code: {response.status_code}, body:{response.body}")
        st.session_state.pre_kb_code_content += f'''
# output:
# response.status_code: {response.status_code}
# body: {response.body}
'''

    def upsert_chunks(self, namespace, namespace_password, collection,
                      text_chunks: List[gpdb_20160503_models.UpsertChunksRequestTextChunks],
                      file_name: str = None) -> gpdb_20160503_models.UpsertChunksResponseBody:
        st.session_state.kb_code_content = self.get_client_code_str + f'''
def upsert_chunks():
    text_chunks: List[gpdb_20160503_models.UpsertChunksRequestTextChunks] = list()
    # e.g. append only one item：
    text_chunks.append(
        gpdb_20160503_models.UpsertChunksRequestTextChunks('{text_chunks[0].content}', {text_chunks[0].metadata})
    )
    file_name = {f"'{file_name}'" if file_name else None}
    request = gpdb_20160503_models.UpsertChunksRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        namespace='{namespace}',
        namespace_password='{namespace_password}',
        collection='{collection}',
        text_chunks=text_chunks,
        file_name=file_name,
    )
    response = get_client().upsert_chunks(request)
'''
        request = gpdb_20160503_models.UpsertChunksRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            text_chunks=text_chunks,
            file_name=file_name,
        )
        response = self.client.upsert_chunks(request)
        logger.info(f"upsert_chunks response code: {response.status_code}, body:{response.body}")
        st.session_state.kb_code_content += f'''
# output:
# response.status_code: {response.status_code}
# body: {response.body}
'''
        return response.body

    def upload_document_async(self, namespace, namespace_password, collection,
                              file_name,
                              file_object_bytes,
                              metadata: Dict[str, Any] = None,
                              chunk_overlap: int = None,
                              chunk_size: int = None,
                              document_loader_name: str = None,
                              text_splitter_name: str = None,
                              dry_run: bool = None,
                              zh_title_enhance: bool = None,
                              separators: List[str] = None):
        st.session_state.pre_kb_code_content = self.get_client_code_str + f'''
def upload_document_async():
    request = gpdb_20160503_models.UploadDocumentAsyncAdvanceRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        namespace='{namespace}',
        namespace_password='{namespace_password}',
        collection='{collection}',
        file_name='{file_name}',
        metadata={metadata},
        chunk_overlap={chunk_overlap},
        chunk_size={chunk_size},
        document_loader_name={"'"+document_loader_name+"'" if document_loader_name else None},
        file_url_object=io.BytesIO(b'{str(file_object_bytes)}'),
        text_splitter_name={"'"+text_splitter_name+"'" if text_splitter_name else None},
        dry_run={dry_run},
        zh_title_enhance={zh_title_enhance},
        separators={separators},
    )
    response = get_client().upsert_chunks(request)
'''
        request = gpdb_20160503_models.UploadDocumentAsyncAdvanceRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            file_name=file_name,
            metadata=metadata,
            chunk_overlap=chunk_overlap,
            chunk_size=chunk_size,
            document_loader_name=document_loader_name,
            file_url_object=io.BytesIO(file_object_bytes),
            text_splitter_name=text_splitter_name,
            dry_run=dry_run,
            zh_title_enhance=zh_title_enhance,
            separators=separators,
        )
        response = self.client.upload_document_async_advance(request, util_models.RuntimeOptions())
        logger.info(f"upload_document_async response code: {response.status_code}, body:{response.body}")
        st.session_state.pre_kb_code_content += f'''
# output:
# response.status_code: {response.status_code}
# body: {response.body}
'''
        return response.body.job_id

    def get_upload_document_job(self, namespace, namespace_password, collection, job_id):
        st.session_state.kb_code_content = st.session_state.pre_kb_code_content + f'''
def get_upload_document_job():
    request = gpdb_20160503_models.GetUploadDocumentJobRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        namespace='{namespace}',
        namespace_password='{namespace_password}',
        collection='{collection}',
        job_id='{job_id}',
    )
    response = get_client().get_upload_document_job(request)
'''
        request = gpdb_20160503_models.GetUploadDocumentJobRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            job_id=job_id,
        )
        response = self.client.get_upload_document_job(request)
        logger.info(f"get_upload_document_job response code: {response.status_code}, body:{response.body}")
        st.session_state.kb_code_content += f'''
# output:
# response.status_code: {response.status_code}
# body: {response.body}
'''
        return response.body

    def cancel_upload_document_job(self, namespace, namespace_password, collection, job_id):
        st.session_state.kb_code_content = self.get_client_code_str + f'''
def cancel_upload_document_job():
    request = gpdb_20160503_models.CancelUploadDocumentJobRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        namespace='{namespace}',
        namespace_password='{namespace_password}',
        collection='{collection}',
        job_id='{job_id}',
    )
    response = get_client().cancel_upload_document_job(request)
'''
        request = gpdb_20160503_models.CancelUploadDocumentJobRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            job_id=job_id,
        )
        response = self.client.cancel_upload_document_job(request)
        logger.info(f"cancel_upload_document_job response code: {response.status_code}, body:{response.body}")
        st.session_state.kb_code_content += f'''
# output:
# response.status_code: {response.status_code}
# body: {response.body}
'''

    def wait_upload_document_job(self, namespace, namespace_password, collection, job_id):
        def job_ready():
            request = gpdb_20160503_models.GetUploadDocumentJobRequest(
                region_id=self.region,
                dbinstance_id=self.instance,
                namespace=namespace,
                namespace_password=namespace_password,
                collection=collection,
                job_id=job_id,
            )
            response = self.client.get_upload_document_job(request)
            print(f"get_upload_document_job response code: {response.status_code}, body:{response.body}")
            return response.body.job.completed
        while True:
            if job_ready():
                print("successfully load document")
                break
            time.sleep(2)

    def query_content(self, namespace, namespace_password, collection, top_k,
                      content,
                      file_object_data,
                      file_name: str = None,
                      filter_str: str = None,
                      metrics: str = None,
                      use_full_text_retrieval: bool = None) -> \
            (gpdb_20160503_models.QueryContentResponseBodyUsage, List[gpdb_20160503_models.QueryContentResponseBodyMatchesMatchList]):
        st.session_state.kb_code_content = self.get_client_code_str + f'''
def query_content():
    request = gpdb_20160503_models.QueryContentAdvanceRequest(
        region_id='{self.region}',
        dbinstance_id='{self.instance}',
        namespace='{namespace}',
        namespace_password='{namespace_password}',
        collection='{collection}',
        content='{content}',
        filter={"'" + filter_str + "'" if filter_str else None},
        top_k={top_k},
        metrics={"'" + metrics + "'" if metrics else None},
        use_full_text_retrieval={use_full_text_retrieval},
'''
        request = gpdb_20160503_models.QueryContentAdvanceRequest(
            region_id=self.region,
            dbinstance_id=self.instance,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            content=content,
            filter=filter_str,
            top_k=top_k,
            metrics=metrics,
            use_full_text_retrieval=use_full_text_retrieval,
        )

        if file_name and file_object_data:
            request.file_name = file_name
            request.file_url_object = io.BytesIO(file_object_data)
            st.session_state.kb_code_content += f'''        file_name = '{file_name}',
        file_url_object = io.BytesIO(b'{str(file_object_data)}'),
    )
    runtime = util_models.RuntimeOptions()
    response = self.client.query_content_advance(request, runtime)
'''
        else:
            st.session_state.kb_code_content += f'''    )
    runtime = util_models.RuntimeOptions()
    response = self.client.query_content_advance(request, runtime)
'''

        runtime = util_models.RuntimeOptions()
        response = self.client.query_content_advance(request, runtime)
        logger.info(f"query_content response code: {response.status_code}, body:{response.body}")
        st.session_state.kb_code_content += f'''
# output:
# response.status_code: {response.status_code}
# body: {response.body}
'''
        return response.body.usage, response.body.matches.match_list
