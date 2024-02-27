import streamlit as st
import json
from alibabacloud_gpdb20160503 import models as gpdb_20160503_models
from utils.utils import write_error, write_info
from configs import *
from typing import List


def clear_msg():
    st.session_state.upsert_err_msg = ''
    st.session_state.upsert_info_msg = ''


def set_info_msg(msg):
    st.session_state.upsert_err_msg = ''
    st.session_state.upsert_info_msg = msg


def set_err_msg(msg):
    st.session_state.upsert_err_msg = msg
    st.session_state.upsert_info_msg = ''


def do_upsert_chunks(text_chunks, file_name, metadata_list: List[str] = None):
    if not text_chunks:
        set_err_msg('Chunks内容不能为空')
        st.session_state.disable_do_upsert_chunks_btn = False
        st.rerun()
    for i in text_chunks:
        if not i.content:
            set_err_msg('Content in Chunks不能为空')
            st.session_state.disable_do_upsert_chunks_btn = False
            st.rerun()
    if metadata_list:
        for index, metadata_str in enumerate(metadata_list):
            if not metadata_str:
                continue
            try:
                text_chunks[index].metadata = json.loads(metadata_str)
            except Exception as e:
                logger.error(e)
                set_err_msg(f'第{index+1}个Metadata非法：{str(e)}, 请重新输入')
                st.session_state.disable_do_upsert_chunks_btn = False
                st.rerun()
    st.session_state.upsert_err_msg = ''
    try:
        write_info('开始上传...')
        resp = st.session_state.adbpg_client.upsert_chunks(
            namespace=st.session_state.collection_namespace,
            namespace_password=st.session_state.namespace_password_cache[st.session_state.collection_namespace],
            collection=st.session_state.selected_document_collection.collection_name,
            text_chunks=text_chunks,
            file_name=file_name if file_name else None,
        )
        set_info_msg(f"上传成功: {resp}")
    except Exception as e:
        set_err_msg(str(e))
    finally:
        st.session_state.disable_do_upsert_chunks_btn = False
        st.rerun()


def upsert_chunks_page():
    if 'upsert_info_msg' not in st.session_state:
        st.session_state.upsert_info_msg = ''
    if 'upsert_err_msg' not in st.session_state:
        st.session_state.upsert_err_msg = ''
    if 'disable_do_upsert_chunks_btn' not in st.session_state:
        st.session_state.disable_do_upsert_chunks_btn = False

    def disable_do_upsert_chunks_btn():
        st.session_state.disable_do_upsert_chunks_btn = True

    text_chunks = None
    on = st.toggle('使用文件上传', on_change=clear_msg)
    if on:
        uploaded_file = st.file_uploader("选择文件",
                                         help='格式为[{"content":"your content","metadata":{"key": anyTypeValue }}]')
        if uploaded_file is not None:
            file_data = json.loads(uploaded_file.getvalue().decode('utf-8'))
            try:
                text_chunks = [gpdb_20160503_models.UpsertChunksRequestTextChunks(i.get('content'), i.get('metadata'))
                               for i in file_data]
            except Exception as e:
                logger.error(e)
                write_error(str(e))
        file_name = st.text_input('指定文件名（可选）：', help='如果指定文件名，会覆盖文档库之前相同文件名的内容')
        if st.button('确定上传', disabled=st.session_state.disable_do_upsert_chunks_btn,
                     on_click=disable_do_upsert_chunks_btn):
            do_upsert_chunks(text_chunks, file_name)
    else:
        col, buf = st.columns((1, 5))
        count = col.number_input('chunks数目:', value=1, min_value=1)
        text_chunks = [gpdb_20160503_models.UpsertChunksRequestTextChunks() for _ in range(count)]
        metadata_list = ["" for _ in range(count)]
        with st.form(key='form_chunks_input'):
            for i in range(count):
                chunk_col1, chunk_col2 = st.columns(2)
                text_chunks[i].content = chunk_col1.text_input('Content:', key=f'content_{i}')
                metadata_list[i] = chunk_col2.text_input('Metadata:', key=f'metadata_{i}', help='json格式map')
            file_name = st.text_input('指定文件名（可选）：', help='如果指定文件名，会覆盖文档库之前相同文件名的内容')
            if st.form_submit_button('确定上传', disabled=st.session_state.disable_do_upsert_chunks_btn,
                                     on_click=disable_do_upsert_chunks_btn):
                do_upsert_chunks(text_chunks, file_name, metadata_list)
    write_info(st.session_state.upsert_info_msg)
    write_error(st.session_state.upsert_err_msg)
