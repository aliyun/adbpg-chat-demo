import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from configs import *
from utils.utils import write_error, write_info
from streamlit_modal import Modal


def check_password(namespace, password):
    try:
        logger.info(f"get collections of {namespace}")
        st.session_state.collections = st.session_state.adbpg_client.list_collections(
            namespace,
            password,
        )
        st.session_state.document_collections = st.session_state.adbpg_client.list_document_collections(
            namespace,
            password,
        )
        st.session_state.collection_namespace = namespace
        st.session_state.switch_document_collection = True
        if 'namespace_password_cache' not in st.session_state:
            st.session_state.namespace_password_cache = dict()
        st.session_state.namespace_password_cache[namespace] = password
        st.session_state.checkin_err_msg = ''
        del st.session_state['show_checkin_namespace_password_modal']
    except Exception as e:
        logger.error(e)
        st.session_state.checkin_err_msg = str(e)


def show_checkin_namespace_password_modal():
    ns = st.session_state.show_checkin_namespace_password_modal
    if f'modal_in_{ns}-close' in st.session_state and st.session_state[f'modal_in_{ns}-close']:
        del st.session_state['show_checkin_namespace_password_modal']
        st.session_state.checkin_err_msg = ''
        st.rerun()
    modal = Modal(f"Enter {ns}", key=f"modal_in_{ns}", max_width=400)
    with modal.container():
        col, buf = st.columns([4, 1])
        with col:
            password = st.text_input('NamespacePassword:', key=f'namespace_password_{ns}', type='password')
            st.button('Confirm', on_click=check_password, args=[ns, password])
        write_error(st.session_state.checkin_err_msg)


def check_in_document_collection(namespace):
    logger.info(f'checkin {namespace}....')
    if namespace in st.session_state.namespace_password_cache:
        try:
            logger.info(f"get collections of {namespace}")
            st.session_state.collections = st.session_state.adbpg_client.list_collections(
                namespace,
                st.session_state.namespace_password_cache[namespace],
            )
            st.session_state.document_collections = st.session_state.adbpg_client.list_document_collections(
                namespace,
                st.session_state.namespace_password_cache[namespace],
            )
            st.session_state.collection_namespace = namespace
            st.session_state.switch_document_collection = True
        except Exception as e:
            logger.error(e)
            write_error(str(e))
    else:
        st.session_state.show_checkin_namespace_password_modal = namespace


def check_switch_document_collection():
    if 'switch_document_collection' in st.session_state and st.session_state.switch_document_collection:
        del st.session_state['switch_document_collection']
        if 'selected_document_collection' in st.session_state:
            del st.session_state['selected_document_collection']
        if 'keep_show_select_namespace' in st.session_state:
            del st.session_state['keep_show_select_namespace']
        switch_page('KnowledgeBase')
    if 'show_checkin_namespace_password_modal' in st.session_state:
        if 'checkin_err_msg' not in st.session_state:
            st.session_state.checkin_err_msg = ''
        show_checkin_namespace_password_modal()
