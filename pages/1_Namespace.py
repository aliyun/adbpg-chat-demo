import streamlit as st
import utils
from utils import namespace_utils
from configs import *

for k, v in st.session_state.to_dict().items():
    if "modal_" not in k:
        st.session_state[k] = v


def init():
    if 'page_index' not in st.session_state:
        st.session_state.page_index = 0
    st.session_state.page_index += 1
    if 'namespace_password_cache' not in st.session_state:
        st.session_state.namespace_password_cache = dict()


def main_show():
    if not utils.check_instance_initialized():
        return

    init()
    st.title(st.session_state.adbpg_instance_id)
    logger.info(f"namespaces: {st.session_state.all_namespaces}")

    col1, col2, buf = st.columns((1, 1, 1))
    namespace_utils.check_switch_document_collection()
    namespace_utils.create_namespace_div(col1)
    st.divider()
    namespace_utils.list_div(col2)
    namespace_utils.check_and_delete_namespace_div()


def main():
    st.set_page_config(layout="wide")
    main_col1, main_col2 = st.columns([3, 2])
    with main_col1:
        main_show()
    with main_col2:
        if 'namespace_code_content' not in st.session_state:
            st.session_state.namespace_code_content = ''
        st.markdown('### 调用代码示例：')
        st.code(st.session_state.namespace_code_content, language='python')


if __name__ == '__main__':
    main()
