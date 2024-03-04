import streamlit as st
import json
from utils.utils import write_error, write_info, horizontal_input
from configs import *


def check_create_metadata():
    if 'metadata' not in st.session_state or not st.session_state.metadata:
        if 'metadata_invalid' in st.session_state:
            del st.session_state['metadata_invalid']
        st.session_state.create_dc_metadata_err_msg = ''
        return
    try:
        py_metadata = json.loads(st.session_state.metadata)
    except Exception as e:
        logger.error(e)
        st.session_state.metadata_invalid = True
        st.session_state.create_dc_metadata_err_msg = f'Metadata字段不是json格式map：{str(e)}'
        return
    if 'metadata_invalid' in st.session_state:
        del st.session_state['metadata_invalid']
    st.session_state.create_dc_metadata_err_msg = ''
    st.session_state.full_text_retrieval_fields_opts = py_metadata.keys()


def do_create_document_collection():
    logger.info(f'starting to create {st.session_state.collection}')
    if not st.session_state.collection:
        st.session_state.create_dc_err_msg = '名称不能为空'
        return
    if st.session_state.collection in st.session_state.collections:
        st.session_state.create_dc_err_msg = f'Collection：{st.session_state.collection} 已经存在'
        return
    if 'metadata_invalid' in st.session_state:
        return
    st.session_state.create_dc_err_msg = ''
    try:
        st.session_state.create_dc_info_msg = f'开始创建{st.session_state.collection}...'
        full_text_retrieval_fields_str = ",".join(st.session_state.full_text_retrieval_fields) \
            if st.session_state.full_text_retrieval_fields else None
        st.session_state.adbpg_client.create_document_collection(
            manager_account=st.session_state.manager_account,
            manager_account_password=st.session_state.manager_password,
            namespace=st.session_state.collection_namespace,
            collection=st.session_state.collection,
            embedding_model=st.session_state.embedding_model,
            full_text_retrieval_fields=full_text_retrieval_fields_str,
            hnsw_m=st.session_state.hnsw_m,
            metadata=st.session_state.metadata if st.session_state.metadata else None,
            metrics=st.session_state.metrics,
            parser=st.session_state.parser if st.session_state.parser else None,
            pq_enable=st.session_state.pq_enable,
            external_storage=st.session_state.external_storage,
        )
        st.session_state.create_dc_info_msg = f'{st.session_state.collection}创建成功'
        st.session_state.collections.append(st.session_state.collection)
        st.session_state.document_collections = st.session_state.adbpg_client.list_document_collections(
            st.session_state.collection_namespace,
            st.session_state.namespace_password_cache[st.session_state.collection_namespace],
        )
        st.rerun()
    except Exception as e:
        logger.error(e)
        st.session_state.create_dc_err_msg = str(e)


def show_create_document_collection_div(col_outer):
    if col_outer.button("创建文档库"):
        st.session_state.kb_code_content = ''
        if 'full_text_retrieval_fields_opts' not in st.session_state:
            st.session_state.full_text_retrieval_fields_opts = ['']
        if 'create_dc_metadata_err_msg' not in st.session_state:
            st.session_state.create_dc_metadata_err_msg = ''
        if 'create_dc_info_msg' not in st.session_state:
            st.session_state.create_dc_info_msg = ''
        if 'create_dc_err_msg' not in st.session_state:
            st.session_state.create_dc_err_msg = ''
        st.session_state.create_kb_btn = True
    if "create_kb_btn" in st.session_state and st.session_state.create_kb_btn:
        horizontal_input('名称:').text_input(
            '', key='collection', max_chars=64, placeholder="不能为空", label_visibility='collapsed',
            help='只允许字母、数字和下划线_, 且以字母开头')
        horizontal_input('EmbeddingModel:').selectbox(
            '', key='embedding_model', options=['text-embedding-v1', 'text-embedding-v2', 'm3e-base', 'm3e-small',
                                                'text2vec', 'multimodal-embedding-one-peace-v1', 'clip-vit-b-32',
                                                'clip-vit-b-16', 'clip-vit-l-14', 'clip-vit-l-14-336px',
                                                'clip-rn50', 'clip-rn101', 'clip-rn50x4', 'clip-rn50x16',
                                                'clip-rn50x64', ], label_visibility='collapsed')
        horizontal_input('Metadata:').text_area(
            '', key='metadata', placeholder='json格式', label_visibility='collapsed', on_change=check_create_metadata,
            help='元数据定义，格式为map json字符串，其中key为字段名，value为字段类型')
        write_error(st.session_state.create_dc_metadata_err_msg)
        horizontal_input('全文检索字段:').multiselect(
            '', key='full_text_retrieval_fields', label_visibility='collapsed',
            options=st.session_state.full_text_retrieval_fields_opts)
        horizontal_input('分词器:').text_input(
            '', key='parser', value='zh_cn', label_visibility='collapsed', help='分词器， 默认zh_cn')
        horizontal_input('Metrics:').selectbox(
            '', key='metrics', label_visibility='collapsed', options=['cosine', 'ip', 'l2'],
            help='索引和查询使用的距离算法')
        horizontal_input('Hnsw_M:').number_input(
            '', value=64, key='hnsw_m', label_visibility='collapsed', help='建立索引时邻居数，默认64')
        horizontal_input('PQ Enable:').selectbox('', key='pq_enable', label_visibility='collapsed', options=[0, 1])
        horizontal_input('ExternalStorage').selectbox('', key='external_storage', label_visibility='collapsed', options=[0, 1])
        st.session_state.kb_code_content = st.session_state.adbpg_client.get_client_code_str + f'''
def create_document_collection():
    request = gpdb_20160503_models.CreateDocumentCollectionRequest(
        region_id='{st.session_state.adbpg_client.region}',
        dbinstance_id='{st.session_state.adbpg_client.instance}',
        manager_account='{st.session_state.manager_account}',
        manager_account_password='{st.session_state.manager_password}',
        namespace='{st.session_state.collection_namespace}',
        collection='{st.session_state.collection}',
        embedding_model='{st.session_state.embedding_model}',
        full_text_retrieval_fields={"'"+",".join(st.session_state.full_text_retrieval_fields) + "'" if st.session_state.full_text_retrieval_fields else None},
        hnsw_m={st.session_state.hnsw_m},
        metadata='{st.session_state.metadata}',
        metrics='{st.session_state.metrics}',
        parser='{st.session_state.parser}',
        pq_enable={st.session_state.pq_enable},
        external_storage={st.session_state.external_storage},
    )
    response = get_client().create_document_collection(request)
'''
        c1, c2 = st.columns(2)
        with c1:
            if st.button("确认"):
                do_create_document_collection()
        with c2:
            if st.button("取消"):
                st.session_state.kb_code_content = ''
                st.session_state.create_dc_info_msg = ''
                st.session_state.create_dc_err_msg = ''
                st.session_state.create_dc_metadata_err_msg = ''
                del st.session_state["create_kb_btn"]
                st.rerun()
        write_info(st.session_state.create_dc_info_msg)
        write_error(st.session_state.create_dc_err_msg)
        st.divider()
