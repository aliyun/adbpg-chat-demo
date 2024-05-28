import streamlit as st
from utils.utils import write_error, write_info
from configs import *


def create_namespace():
    if not st.session_state.namespace:
        write_error("Namespace can not be empty")
        return
    if not st.session_state.namespace_password:
        write_error("Namespace Password can not be empty")
        return
    if st.session_state.namespace_password != st.session_state.namespace_password_confirm:
        write_error("The passwords entered do not match")
        return
    if st.session_state.namespace != "public" and st.session_state.namespace in st.session_state.all_namespaces:
        write_error(f"Namespace {st.session_state.namespace} already exists")
        return
    write_info(f"Start creating the Namespace:{st.session_state.namespace}...")
    try:
        st.session_state.adbpg_client.create_namespace(
            st.session_state.manager_account,
            st.session_state.manager_password,
            st.session_state.namespace,
            st.session_state.namespace_password)
    except Exception as e:
        logger.info(f"failed to create_namespace: {str(e)}")
        write_error(str(e))
        return
    st.session_state.all_namespaces.append(st.session_state.namespace)
    st.session_state.namespace_password_cache[st.session_state.namespace] = st.session_state.namespace_password
    write_info("Create successfully...")
    st.session_state.create_ns_btn = False


def create_namespace_div(col_outer):
    if col_outer.button("Create Namespace"):
        st.session_state.namespace_code_content = ''
        st.session_state.create_ns_btn = True
    if "create_ns_btn" in st.session_state and st.session_state.create_ns_btn:
        col, buff = st.columns([3, 1])
        col.text_input('Namespace:', key='namespace')
        col, buff = st.columns([3, 1])
        col.text_input('Namespace Password:', key='namespace_password', type='password')
        col, buff = st.columns([3, 1])
        col.text_input('Confirm Password:', key='namespace_password_confirm', type='password')
        st.session_state.namespace_code_content = st.session_state.adbpg_client.get_client_code_str + f'''
def create_namespace():
    request = gpdb_20160503_models.CreateNamespaceRequest(
        region_id='{st.session_state.adbpg_client.region}',
        dbinstance_id='{st.session_state.adbpg_client.instance}',
        manager_account='{st.session_state.manager_account}',
        manager_account_password='{st.session_state.manager_password}',
        namespace='{st.session_state.namespace}',
        namespace_password='{st.session_state.namespace_password}'
    )
    response = get_client().create_namespace(request)
'''
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Confirm"):
                create_namespace()
        with c2:
            if st.button("Cancel"):
                st.session_state.namespace_code_content = ''
                del st.session_state["create_ns_btn"]
                st.rerun()
