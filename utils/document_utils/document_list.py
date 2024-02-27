import streamlit as st
import json
from alibabacloud_gpdb20160503 import models as gpdb_20160503_models
from utils.utils import write_error, write_info
from configs import *
from typing import List
from streamlit_modal import Modal


def set_session_show_delete_document_modal(doc: gpdb_20160503_models.ListDocumentsResponseBodyItemsDocumentList):
    st.session_state.show_confirm_delete_modal = doc


def show_confirm_delete_modal():
    if 'show_confirm_delete_modal' in st.session_state and \
            f'modal_del_doc_{st.session_state.show_confirm_delete_modal.file_name}-close' in st.session_state and \
            st.session_state[f'modal_del_doc_{st.session_state.show_confirm_delete_modal.file_name}-close']:
        st.session_state.list_doc_info_msg = ''
        st.session_state.list_doc_err_msg = ''
        del st.session_state['show_confirm_delete_modal']

    def set_delete_document_session(d):
        st.session_state.need_to_delete_document = d

    if 'show_confirm_delete_modal' in st.session_state:
        delete_modal = Modal(f"是否删除:{st.session_state.show_confirm_delete_modal.file_name}",
                             key=f"modal_del_doc_{st.session_state.show_confirm_delete_modal.file_name}",
                             max_width=400)
        with delete_modal.container():
            st.button("确认删除", on_click=set_delete_document_session,
                      args=[st.session_state.show_confirm_delete_modal])


def set_session_show_document_detail(doc: gpdb_20160503_models.ListDocumentsResponseBodyItemsDocumentList):
    st.session_state.show_document_detail_modal = doc


def show_detail_modal():
    if 'show_document_detail_modal' in st.session_state and \
            f'modal_detail_{st.session_state.show_document_detail_modal.file_name}-close' in st.session_state and \
            st.session_state[f'modal_detail_{st.session_state.show_document_detail_modal.file_name}-close']:
        st.session_state.list_doc_info_msg = ''
        st.session_state.list_doc_err_msg = ''
        del st.session_state['show_document_detail_modal']

    if 'show_document_detail_modal' in st.session_state:
        doc = st.session_state.show_document_detail_modal
        err_msg = ''
        document_detail_json = ''
        try:
            resp: gpdb_20160503_models.DescribeDocumentResponseBody = st.session_state.adbpg_client.describe_document(
                namespace=st.session_state.collection_namespace,
                namespace_password=st.session_state.namespace_password_cache[st.session_state.collection_namespace],
                collection=st.session_state.selected_document_collection.collection_name,
                file_name=doc.file_name,
            )
            document_detail_pydic = {
                'file_name': resp.file_name,
                'source': resp.source,
                'docs_count': resp.docs_count,
                'document_loader': resp.document_loader,
                'file_ext': resp.file_ext,
                'file_md5': resp.file_md_5,
                'file_mtime': resp.file_mtime,
                'file_size': resp.file_size,
                'file_version': resp.file_version,
                'text_splitter': resp.text_splitter,
            }
            document_detail_json = json.dumps(document_detail_pydic)
        except Exception as e:
            err_msg = str(e)
        modal = Modal('', key=f"modal_detail_{doc.file_name}", max_width=600)
        with modal.container():
            col, buf = st.columns((3, 1))
            with col:
                if err_msg:
                    write_error(err_msg)
                else:
                    st.json(document_detail_json)


def check_and_delete_document():
    if "need_to_delete_document" not in st.session_state or not st.session_state.need_to_delete_document:
        return
    write_info(f"开始删除{st.session_state.need_to_delete_document.file_name}...")
    try:
        st.session_state.adbpg_client.delete_document(
            namespace=st.session_state.collection_namespace,
            namespace_password=st.session_state.namespace_password_cache[st.session_state.collection_namespace],
            collection=st.session_state.selected_document_collection.collection_name,
            file_name=st.session_state.need_to_delete_document.file_name,
        )
        st.session_state.list_doc_info_msg = f"删除{st.session_state.need_to_delete_document.file_name}成功"
        st.session_state.list_doc_err_msg = ''
    except Exception as e:
        logger.error(e)
        st.session_state.list_doc_info_msg = ''
        st.session_state.list_doc_err_msg = f'删除{st.session_state.need_to_delete_document.file_name}失败：{str(e)}'
    finally:
        if 'need_to_delete_document' in st.session_state:
            del st.session_state['need_to_delete_document']
        if 'show_confirm_delete_modal' in st.session_state:
            del st.session_state['show_confirm_delete_modal']
    st.rerun()


def list_documents_page():
    if 'list_doc_info_msg' not in st.session_state:
        st.session_state.list_doc_info_msg = ''
    if 'list_doc_err_msg' not in st.session_state:
        st.session_state.list_doc_err_msg = ''

    def do_list() -> List[gpdb_20160503_models.ListDocumentsResponseBodyItemsDocumentList]:
        return st.session_state.adbpg_client.list_documents(
            namespace=st.session_state.collection_namespace,
            namespace_password=st.session_state.namespace_password_cache[st.session_state.collection_namespace],
            collection=st.session_state.selected_document_collection.collection_name,
        )

    try:
        documents = do_list()
    except Exception as e:
        write_error(str(e))
        return
    colms = st.columns((1, 2, 2, 2))
    fields = ["序号", '名称', '来源', '操作']
    for col, field_name in zip(colms, fields):
        # header
        col.write(field_name)
    for i, doc in enumerate(documents):
        col1, col2, col3, col4, col5 = st.columns((1, 2, 2, 1, 1))
        col1.write(i)
        col2.write(doc.file_name)
        col3.write(doc.source)
        col4.button('详情', key=f'detail_doc_{i}_{st.session_state.page_index}',
                    on_click=set_session_show_document_detail, args=[doc])
        col5.button('删除', key=f'delete_doc_{i}_{st.session_state.page_index}',
                    on_click=set_session_show_delete_document_modal, args=[doc])
    check_and_delete_document()
    write_info(st.session_state.list_doc_info_msg)
    write_error(st.session_state.list_doc_err_msg)
    show_confirm_delete_modal()
    show_detail_modal()
