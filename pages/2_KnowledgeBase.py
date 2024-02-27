import streamlit as st
from configs import *
import utils
from utils import document_utils, document_collection_utils


for k, v in st.session_state.to_dict().items():
    if "modal_" not in k and 'form_' not in k:
        st.session_state[k] = v


def show_select_namespace():
    st.session_state.keep_show_select_namespace = True
    st.markdown("**请选择:**")
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Namespace：", options=st.session_state.all_namespaces, key="collection_namespace")
    with col2:
        st.text_input("NamespacePassword：", type="password",
                      disabled=st.session_state.collection_namespace in st.session_state.namespace_password_cache,
                      key="namespace_password")
    if st.session_state.collection_namespace in st.session_state.namespace_password_cache:
        st.session_state.collection_namespace_password = \
            st.session_state.namespace_password_cache[st.session_state.collection_namespace]
        utils.write_info(f'{st.session_state.collection_namespace} 密码已缓存，无需再次输入')
    else:
        st.session_state.collection_namespace_password = st.session_state.namespace_password
    if st.button("确定"):
        if not st.session_state.collection_namespace_password:
            utils.write_error("Password不能为空")
        logger.info(f"check password with namespace: {st.session_state.collection_namespace}")
        try:
            st.session_state.collections = st.session_state.adbpg_client.list_collections(
                st.session_state.collection_namespace,
                st.session_state.collection_namespace_password,
            )
            st.session_state.document_collections = st.session_state.adbpg_client.list_document_collections(
                st.session_state.collection_namespace,
                st.session_state.collection_namespace_password,
            )
            st.session_state.namespace_password_cache[st.session_state.collection_namespace] = \
                st.session_state.collection_namespace_password
            del st.session_state['keep_show_select_namespace']
            st.rerun()
        except Exception as e:
            logger.error(e)
            utils.write_error(str(e))
            return


def default_set():
    #     st.markdown('''<style>div[data-modal-container='true'][key='modal_create_document_collection'] {
    #     overflow-y: auto;
    # }</style>''', unsafe_allow_html=True)
    pass


def clear_pre_page_kb_code_content(page):
    if 'pre_page' in st.session_state and st.session_state.pre_page != page:
        st.session_state.kb_code_content = ''
        st.session_state.qa_history = []
    st.session_state.pre_page = page


def show_specific_document_collection_header():
    st.title(f'{st.session_state.adbpg_instance_id}/'
             f'{st.session_state.collection_namespace}/'
             f'{st.session_state.selected_document_collection.collection_name}')
    col1, col2, buf = st.columns((1, 1, 3))
    if col1.button("切换Namespace"):
        st.session_state.kb_code_content = ''
        del st.session_state['selected_document_collection']
        del st.session_state['collection_namespace']
        st.rerun()
    if col2.button('切换知识库'):
        st.session_state.kb_code_content = ''
        del st.session_state['selected_document_collection']
        st.rerun()


def show_specific_document_collection():
    page = st.sidebar.radio('', ['问答', '文档检索', '上传文档', '上传chunks', '文档列表'])
    if page in ('上传文档', '上传chunks', '文档列表'):
        main_col1, main_col2 = st.columns([3, 2])
        with main_col1:
            show_specific_document_collection_header()
            st.divider()
            if page == '上传文档':
                clear_pre_page_kb_code_content('上传文档')
                document_utils.upload_document_page()
            elif page == '上传chunks':
                clear_pre_page_kb_code_content('上传chunks')
                document_utils.upsert_chunks_page()
            else:
                clear_pre_page_kb_code_content('文档列表')
                document_utils.list_documents_page()
        with main_col2:
            st.markdown('### 调用代码示例：')
            st.code(st.session_state.kb_code_content, language='python')
        return
    if page == '问答':
        clear_pre_page_kb_code_content('问答')
        question = st.chat_input('请输入问题, 按回车确认')
        main_col1, main_col2 = st.columns([3, 2])
        with main_col1:
            show_specific_document_collection_header()
            document_utils.qa_page(question)
        with main_col2:
            st.markdown('### 调用代码示例：')
            st.code(st.session_state.kb_code_content, language='python')
    else:
        clear_pre_page_kb_code_content('文档检索')
        main_col1, main_col2 = st.columns([3, 2])
        with main_col1:
            show_specific_document_collection_header()
            document_utils.retrieval_search_page()
        with main_col2:
            st.markdown('### 调用代码示例：')
            st.code(st.session_state.kb_code_content, language='python')


def init():
    if 'namespace_password_cache' not in st.session_state:
        st.session_state.namespace_password_cache = dict()
    if 'page_index' not in st.session_state:
        st.session_state.page_index = 0
    if 'kb_code_content' not in st.session_state:
        st.session_state.kb_code_content = ''
    if 'qa_history' not in st.session_state:
        st.session_state.qa_history = []
    st.session_state.page_index += 1


def show_document_collections():
    st.title(f'{st.session_state.adbpg_instance_id}/{st.session_state.collection_namespace}')
    if st.button("切换Namespace"):
        st.session_state.kb_code_content = ''
        del st.session_state['collection_namespace']
        st.rerun()
    st.divider()

    # header:
    st.markdown("##### 文档库列表")

    col1, col2, buf = st.columns((1, 1, 1))
    document_collection_utils.show_create_document_collection_div(col1)
    if col2.button("刷新列表"):
        try:
            document_collection_utils.refresh_document_collections_in_session()
            utils.write_info("刷新列表成功")
        except Exception as e:
            logger.info(f"failed to list collections: {str(e)}")
            utils.write_error(str(e))
    document_collection_utils.show_list_document_collections_table()
    document_collection_utils.check_and_delete_document_collection()


def main():
    st.set_page_config(layout="wide")
    default_set()
    if not utils.check_instance_initialized():
        return

    init()
    if 'keep_show_select_namespace' in st.session_state or \
            'collection_namespace' not in st.session_state or \
            st.session_state.collection_namespace not in st.session_state.namespace_password_cache:
        main_col1, main_col2 = st.columns([3, 2])
        with main_col1:
            st.title(st.session_state.adbpg_instance_id)
            st.divider()
            show_select_namespace()
        with main_col2:
            st.markdown('### 调用代码示例：')
            st.code(st.session_state.kb_code_content, language='python')
        return
    if 'selected_document_collection' in st.session_state:
        show_specific_document_collection()
        return
    main_col1, main_col2 = st.columns([3, 2])
    with main_col1:
        show_document_collections()
    with main_col2:
        st.markdown('### 调用代码示例：')
        st.code(st.session_state.kb_code_content, language='python')


if __name__ == '__main__':
    main()
