import json

import streamlit as st
from alibabacloud_gpdb20160503 import models as gpdb_20160503_models
from streamlit_modal import Modal
from .delete import show_delete_document_collection_modal


def refresh_document_collections_in_session():
    st.session_state.collections = st.session_state.adbpg_client.list_collections(
        st.session_state.collection_namespace,
        st.session_state.namespace_password_cache[st.session_state.collection_namespace],
    )
    st.session_state.document_collections = st.session_state.adbpg_client.list_document_collections(
        st.session_state.collection_namespace,
        st.session_state.namespace_password_cache[st.session_state.collection_namespace],
    )


def check_in_document_collection(dc: gpdb_20160503_models.ListDocumentCollectionsResponseBodyItemsCollectionList):
    st.session_state.kb_code_content = ''
    st.session_state.selected_document_collection = dc


def show_document_collection_detail(dc: gpdb_20160503_models.ListDocumentCollectionsResponseBodyItemsCollectionList):
    dc_pydict = {
        'collection_name': dc.collection_name,
        'dimension': dc.dimension,
        'embedding_model': dc.embedding_model,
        'full_text_retrieval_fields': dc.full_text_retrieval_fields,
        'metadata': dc.metadata,
        'metrics': dc.metrics,
        'parser': dc.parser,
    }
    dc_json = json.dumps(dc_pydict)
    modal = Modal('', key=f"modal_detail_{dc.collection_name}", max_width=600)
    with modal.container():
        col, buf = st.columns((3, 1))
        col.json(dc_json)


def show_list_document_collections_table():
    colms = st.columns((1, 2, 2, 2, 2, 3))
    fields = ["序号", '名称', '向量模型', '维度', '距离算法', '操作']
    for col, field_name in zip(colms, fields):
        # header
        col.write(field_name)
    for i, dc in enumerate(st.session_state.document_collections):
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns((1, 2, 2, 2, 2, 1, 1, 1))
        col1.write(i)
        col2.write(dc.collection_name)
        col3.write(dc.embedding_model)
        col4.write(dc.dimension)
        col5.write(dc.metrics)
        col6.button('详情', key=f'detail_{i}_{st.session_state.page_index}',
                     on_click=show_document_collection_detail, args=[dc])
        col7.button('进入', key=f'in_{i}_{st.session_state.page_index}',
                     on_click=check_in_document_collection, args=[dc])
        col8.button('删除', key=f'delete_{i}_{st.session_state.page_index}',
                     on_click=show_delete_document_collection_modal, args=[dc])
