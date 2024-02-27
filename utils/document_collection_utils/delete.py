import streamlit as st
from alibabacloud_gpdb20160503 import models as gpdb_20160503_models
from utils.utils import write_error, write_info
from configs import *
from streamlit_modal import Modal


def set_delete_document_collection(dc):
    st.session_state.need_to_delete_document_collection = dc


def show_delete_document_collection_modal(
        dc: gpdb_20160503_models.ListDocumentCollectionsResponseBodyItemsCollectionList):
    delete_modal = Modal(f"是否删除:{dc.collection_name}", key=f"modal_del_{dc.collection_name}", max_width=400)
    with delete_modal.container():
        st.button("确认删除", on_click=set_delete_document_collection, args=[dc])


def check_and_delete_document_collection():
    if "need_to_delete_document_collection" not in st.session_state or \
            not st.session_state.need_to_delete_document_collection:
        return
    need_to_delete_dc: gpdb_20160503_models.ListDocumentCollectionsResponseBodyItemsCollectionList = \
        st.session_state.need_to_delete_document_collection
    if need_to_delete_dc in st.session_state.document_collections:
        st.session_state.document_collections.remove(need_to_delete_dc)
        st.session_state.collections.remove(need_to_delete_dc.collection_name)
        st.rerun()
    write_info(f"开始删除{need_to_delete_dc.collection_name}...")
    logger.info(f"starting to delete document collection: {need_to_delete_dc.collection_name}")
    try:
        st.session_state.adbpg_client.delete_document_collection(
            namespace=st.session_state.collection_namespace,
            namespace_password=st.session_state.namespace_password_cache[st.session_state.collection_namespace],
            collection=need_to_delete_dc.collection_name)
        write_info(f"删除{need_to_delete_dc.collection_name}成功")
    except Exception as e:
        st.session_state.document_collections.append(need_to_delete_dc)
        st.session_state.collections.append(need_to_delete_dc.collection_name)
        logger.error(e)
        write_error(str(e))
        return
    finally:
        if 'need_to_delete_document_collection' in st.session_state:
            del st.session_state['need_to_delete_document_collection']
