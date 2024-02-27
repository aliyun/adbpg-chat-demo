from configs import *
import streamlit as st
from adbpg.adbpg import AdbpgClient
from utils.utils import write_error, write_info


def clear_instance_session_state():
    st.session_state.disable_init = False
    st.session_state.click_init = False
    st.session_state.init_success = False

    if 'init_err_msg' in st.session_state:
        del st.session_state['init_err_msg']
    if 'all_namespaces' in st.session_state:
        del st.session_state['all_namespaces']

    if 'selected_document_collection' in st.session_state:
        del st.session_state['selected_document_collection']
    if 'keep_show_select_namespace' in st.session_state:
        del st.session_state['keep_show_select_namespace']
    if 'show_checkin_namespace_password_modal' in st.session_state:
        del st.session_state['show_checkin_namespace_password_modal']
    if 'namespace_password_cache' in st.session_state:
        st.session_state.namespace_password_cache = {}

    if 'collections' in st.session_state:
        del st.session_state['collections']
    if 'document_collections' in st.session_state:
        del st.session_state['document_collections']
    if 'collection_namespace' in st.session_state:
        del st.session_state['collection_namespace']
    if 'need_to_delete_namespace' in st.session_state:
        del st.session_state['need_to_delete_namespace']
    if 'selected_document_collection' in st.session_state:
        del st.session_state['selected_document_collection']


def choose_instance(region, ins):
    st.session_state.adbpg_instance_id = ins.dbinstance_id
    st.session_state.adbpg_client = AdbpgClient(region=region, instance=ins.dbinstance_id)
    clear_instance_session_state()
    st.session_state.click_instance_btn = False
    st.rerun()


def click_instance_btn():
    st.session_state.home_code_content = ''
    st.session_state.click_instance_btn = True


def get_instance_list(region):
    write_info(f'获取Region（{region}）实例...')
    if 'click_instance_btn' in st.session_state and st.session_state.click_instance_btn:
        return
    adbpg_client = AdbpgClient(region=region)
    try:
        st.session_state.instance_list = adbpg_client.list_vector_db_instances()
    except Exception as e:
        write_error(str(e))
        st.session_state.instance_list = []
        return
    if len(st.session_state.instance_list) == 0:
        write_info(f'当前Region（{region}）不存在开启向量引擎优化的实例')
    else:
        write_info(f'获取Region（{region}）实例成功。')


def list_div():
    region_options = ['']
    for i in regions_cn_map.keys():
        region_options.append(i)

    col1, col2, _ = st.columns([1, 3, 5])
    col1.markdown('Region:')
    region_cn = col2.selectbox('', options=region_options, label_visibility='collapsed')
    if not region_cn:
        return
    region = regions_cn_map[region_cn]
    logger.info(f'choose region: {region}')
    get_instance_list(region)

    colms = st.columns((1, 3, 3, 2))
    fields = ["序号", '名称', '版本', '状态']
    for col, field_name in zip(colms, fields):
        # header
        col.write(field_name)

    for i, ins in enumerate(st.session_state.instance_list):
        col1, col2, col3, col4 = st.columns((1, 3, 3, 2))
        col1.write(i)
        if col2.button(ins.dbinstance_id, on_click=click_instance_btn, disabled=(ins.dbinstance_status != 'Running')):
            choose_instance(region, ins)
        col3.write(ins.core_version.lstrip('mm.'))
        col4.write(ins.dbinstance_status)

