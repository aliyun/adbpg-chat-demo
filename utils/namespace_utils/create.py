import streamlit as st
from utils.utils import write_error, write_info
from configs import *


def create_namespace():
    if not st.session_state.namespace:
        write_error("项目空间不能为空")
        return
    if not st.session_state.namespace_password:
        write_error("项目空间密码不能为空")
        return
    if st.session_state.namespace_password != st.session_state.namespace_password_confirm:
        write_error("两次输入的密码不相同")
        return
    if st.session_state.namespace != "public" and st.session_state.namespace in st.session_state.all_namespaces:
        write_error(f"Namespace {st.session_state.namespace} 已经存在")
        return
    write_info(f"开始创建Namespace:{st.session_state.namespace}...")
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
    write_info("创建成功...")
    st.session_state.create_ns_btn = False


def create_namespace_div(col_outer):
    if col_outer.button("创建Namespace"):
        st.session_state.namespace_code_content = ''
        st.session_state.create_ns_btn = True
    if "create_ns_btn" in st.session_state and st.session_state.create_ns_btn:
        col, buff = st.columns([3, 1])
        col.text_input('项目空间:', key='namespace')
        col, buff = st.columns([3, 1])
        col.text_input('项目空间密码:', key='namespace_password', type='password')
        col, buff = st.columns([3, 1])
        col.text_input('再次确认密码:', key='namespace_password_confirm', type='password')
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
            if st.button("确认"):
                create_namespace()
        with c2:
            if st.button("取消"):
                st.session_state.namespace_code_content = ''
                del st.session_state["create_ns_btn"]
                st.rerun()
