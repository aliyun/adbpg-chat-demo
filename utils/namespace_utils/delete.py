import streamlit as st
from utils.utils import write_error, write_info
from configs import *


def show_delete_namespace_modal(namespace, modal):
    def set_delete_namespace(ns):
        st.session_state.need_to_delete_namespace = ns

    with modal.container():
        st.button("确认删除", on_click=set_delete_namespace, args=[namespace])


def check_and_delete_namespace_div():
    if "need_to_delete_namespace" not in st.session_state or not st.session_state.need_to_delete_namespace:
        return
    if st.session_state.need_to_delete_namespace in st.session_state.all_namespaces:
        st.session_state.all_namespaces.remove(st.session_state.need_to_delete_namespace)
        st.rerun()
    write_info(f"开始删除{st.session_state.need_to_delete_namespace}...")
    logger.info(f"starting to delete namespace: {st.session_state.need_to_delete_namespace}")
    try:
        st.session_state.adbpg_client.delete_namespace(
            manager_account=st.session_state.manager_account,
            manager_account_password=st.session_state.manager_password,
            namespace=st.session_state.need_to_delete_namespace)
        if 'namespace_password_cache' in st.session_state and \
                st.session_state.need_to_delete_namespace in st.session_state.namespace_password_cache:
            del st.session_state.namespace_password_cache[st.session_state.need_to_delete_namespace]
        if 'collection_namespace' in st.session_state and \
                st.session_state.collection_namespace == st.session_state.need_to_delete_namespace:
            del st.session_state['collection_namespace']
        write_info(f"删除{st.session_state.need_to_delete_namespace}成功")
    except Exception as e:
        st.session_state.all_namespaces.append(st.session_state.need_to_delete_namespace)
        logger.error(e)
        write_error(str(e))
        return
    finally:
        if 'need_to_delete_namespace' in st.session_state:
            del st.session_state['need_to_delete_namespace']
