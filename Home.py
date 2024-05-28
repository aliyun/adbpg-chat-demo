import streamlit as st
from configs import *
from adbpg.adbpg import AdbpgClient
from utils.utils import write_error, write_info
from utils import instance_utils


for k, v in st.session_state.to_dict().items():
    if "modal_" not in k and 'form_' not in k:
        st.session_state[k] = v


def init():
    if "disable_init" not in st.session_state:
        st.session_state.disable_init = False
    if 'click_init' not in st.session_state:
        st.session_state.click_init = False
    if 'init_success' not in st.session_state:
        st.session_state.init_success = False


def main_show():
    if 'adbpg_instance_id' not in st.session_state:
        if not ADBPG_INSTANCE_ID:
            st.title('Choose an instance')
            st.divider()
            instance_utils.list_div()
            return
        else:
            st.session_state.adbpg_instance_id = ADBPG_INSTANCE_ID
            if "adbpg_client" not in st.session_state:
                st.session_state.adbpg_client = AdbpgClient()

    st.title(f"Instance: {st.session_state.adbpg_instance_id}")
    if not ADBPG_INSTANCE_ID:
        if st.button('Choose other instances'):
            st.session_state.home_code_content = ''
            if 'all_namespaces' in st.session_state:
                del st.session_state['all_namespaces']
            del st.session_state['adbpg_instance_id']
            st.rerun()
    st.divider()

    init()
    col1, col2 = st.columns(2)
    with col1:
        manager_account = st.text_input('Manage Account', "", disabled=st.session_state.disable_init,
                                        key="manager_account")
    with col2:
        manager_password = st.text_input('Manage Account Password', "", type="password", disabled=st.session_state.disable_init,
                                         key="manager_password")
    if st.button("Initialize instance", disabled=st.session_state.disable_init):
        if manager_account == "" or manager_password == "":
            write_error('Please enter the account and password.')
            return
        write_info('Starting initialization...')
        st.session_state.disable_init = True
        st.session_state.click_init = True
        st.rerun()
    if "init_err_msg" in st.session_state:
        write_info('Starting initialization...')
        write_error(f'{st.session_state.init_err_msg}')
    if st.session_state.click_init:
        st.session_state.click_init = False
        write_info('Starting initialization...')
        try:
            st.session_state.adbpg_client.init_vector_database(manager_account, manager_password)
        except Exception as e:
            st.session_state.disable_init = False
            logger.info(f"failed to init_vector_database: {str(e)}")
            st.session_state.init_err_msg = str(e)
            st.rerun()
        try:
            st.session_state.all_namespaces = st.session_state.adbpg_client.list_namespaces(manager_account, manager_password)
        except Exception as e:
            st.session_state.disable_init = False
            logger.info(f"failed to list_namespaces: {str(e)}")
            st.session_state.init_err_msg = str(e)
            st.rerun()
        if "init_err_msg" in st.session_state:
            del st.session_state["init_err_msg"]
        st.session_state.init_success = True
        write_info('Initialization completed')
    elif st.session_state.init_success:
        write_info('Already initialized')


def main():
    st.set_page_config(layout="wide")
    main_col1, main_col2 = st.columns([3, 2])
    with main_col1:
        main_show()
    with main_col2:
        if 'home_code_content' not in st.session_state:
            st.session_state.home_code_content = ''
        st.markdown('### Code invocation example:')
        st.code(st.session_state.home_code_content, language='python')


if __name__ == '__main__':
    main()

