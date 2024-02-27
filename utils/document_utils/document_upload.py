import json
import streamlit as st
import utils
import time

from alibabacloud_gpdb20160503 import models as gpdb_20160503_models


def cancel_job():
    try:
        utils.write_info(f'取消任务:{st.session_state.upload_doc_job_id}...')
        st.session_state.adbpg_client.cancel_upload_document_job(
            namespace=st.session_state.collection_namespace,
            namespace_password=st.session_state.namespace_password_cache[st.session_state.collection_namespace],
            collection=st.session_state.selected_document_collection.collection_name,
            job_id=st.session_state.upload_doc_job_id)
        utils.write_info(f'任务:{st.session_state.upload_doc_job_id}取消成功')
        del st.session_state['upload_doc_job_id']
    except Exception as e:
        utils.write_error(str(e))


def get_upload_do_job():
    utils.write_info(f"上传成功, JobId: {st.session_state.upload_doc_job_id}")
    st.divider()
    st.session_state.disabled_cancel_upload_doc_job = False
    if st.button('取消任务', disabled=st.session_state.disabled_cancel_upload_doc_job):
        cancel_job()
        return

    progress_text = f"等待任务({st.session_state.upload_doc_job_id})成功..."
    job_bar = st.progress(0, text=progress_text)
    while True:
        if 'upload_doc_job_id' not in st.session_state:
            break
        try:
            resp: gpdb_20160503_models.GetUploadDocumentJobResponseBody = st.session_state.adbpg_client.get_upload_document_job(
                namespace=st.session_state.collection_namespace,
                namespace_password=st.session_state.namespace_password_cache[st.session_state.collection_namespace],
                collection=st.session_state.selected_document_collection.collection_name,
                job_id=st.session_state.upload_doc_job_id)
        except Exception as e:
            utils.write_error(str(e))
            time.sleep(10)
            continue
        if resp.job.status == 'Running':
            job_bar.progress(resp.job.progress, text=progress_text)
        elif resp.job.status == 'Failed':
            utils.write_error(str(resp))
            del st.session_state['upload_doc_job_id']
            st.session_state.disabled_cancel_upload_doc_job = True
            break
        elif resp.job.completed:
            st.progress(resp.job.progress)
            utils.write_info("上传任务执行成功")
            if hasattr(resp.chunk_result, 'chunk_file_url') and resp.chunk_result.chunk_file_url:
                st.link_button('Download ChunkFile', resp.chunk_result.chunk_file_url)
            del st.session_state['upload_doc_job_id']
            st.session_state.disabled_cancel_upload_doc_job = True
            break
        time.sleep(5)
    time.sleep(1)
    job_bar.empty()


def do_upload_document(file_name, bytes_data,
                       metadata_str: str = None,
                       chunk_overlap: int = None,
                       chunk_size: int = None,
                       document_loader_name: str = None,
                       text_splitter_name: str = None,
                       dry_run: bool = None,
                       zh_title_enhance: bool = None,
                       separators_str: str = None):
    if not file_name:
        utils.write_error("文件名不能为空")
        return
    if not bytes_data:
        utils.write_error("上传文件不能为空")
        return
    metadata = None
    if metadata_str:
        metadata = json.loads(metadata_str)
    separators = None
    if separators_str:
        separators = [value.strip() for value in separators_str.split(',')]
    try:
        utils.write_info('开始上传...')
        resp = st.session_state.adbpg_client.upload_document_async(
            namespace=st.session_state.collection_namespace,
            namespace_password=st.session_state.namespace_password_cache[st.session_state.collection_namespace],
            collection=st.session_state.selected_document_collection.collection_name,
            file_name=file_name,
            file_object_bytes=bytes_data,
            metadata=metadata,
            chunk_overlap=chunk_overlap,
            chunk_size=chunk_size,
            document_loader_name=document_loader_name,
            text_splitter_name=text_splitter_name,
            dry_run=dry_run,
            zh_title_enhance=zh_title_enhance,
            separators=separators,
        )
        st.session_state.upload_doc_job_id = resp
        st.session_state.adbpg_client.get_upload_document_job(
            namespace=st.session_state.collection_namespace,
            namespace_password=st.session_state.namespace_password_cache[st.session_state.collection_namespace],
            collection=st.session_state.selected_document_collection.collection_name,
            job_id=st.session_state.upload_doc_job_id)
        st.rerun()
    except Exception as e:
        utils.write_error(str(e))


def upload_document_page():
    file_name = st.text_input('文件名：')
    uploaded_file = st.file_uploader("选择文件")
    bytes_data = None
    if uploaded_file is not None:
        bytes_data = uploaded_file.read()
    metadata = st.text_input('Metadata:', help='json string')
    chunk_size = st.slider("Chunk Size:", 1, 2048, value=250)
    default_chunk_overlap = 0
    if chunk_size > 50:
        default_chunk_overlap = 50
    chunk_overlap = st.slider("Chunk Overlap:", 0, chunk_size-1, value=default_chunk_overlap)
    document_loader_name = st.text_input('Document Loader Name')
    text_splitter_name = st.text_input('Text Splitter Name')
    dry_run = st.toggle('Dry Run:', value=False)
    zh_title_enhance = st.toggle('ZH Title Enhance', value=False)
    separators = st.text_input('separators')
    st.session_state.kb_code_content = st.session_state.adbpg_client.get_client_code_str + f'''
def upload_document_async():
    metadata = {metadata if metadata else ""}
    separators = {"[value.strip() for value in '"+separators+"'.split(',')]" if separators else None}
    with open("/local/path/to/file", "rb") as f:
        file_object_bytes = f.read()
    request = gpdb_20160503_models.UploadDocumentAsyncAdvanceRequest(
        region_id='{st.session_state.adbpg_client.region}',
        dbinstance_id='{st.session_state.adbpg_client.instance}',
        namespace='{st.session_state.collection_namespace}',
        namespace_password='{st.session_state.namespace_password_cache[st.session_state.collection_namespace]}',
        collection='{st.session_state.selected_document_collection.collection_name}',
        file_name='{file_name}',
        metadata=metadata,
        chunk_overlap={chunk_overlap},
        chunk_size={chunk_size},
        document_loader_name={"'" + document_loader_name + "'" if document_loader_name else None},
        file_url_object=io.BytesIO(file_object_bytes),
        text_splitter_name={"'" + text_splitter_name + "'" if text_splitter_name else None},
        dry_run={dry_run},
        zh_title_enhance={zh_title_enhance},
        separators=separators,
    )
    response = get_client().upsert_chunks(request)
'''
    if st.button('上传文档'):
        do_upload_document(file_name, bytes_data, metadata, chunk_overlap, chunk_size, document_loader_name,
                           text_splitter_name, dry_run, zh_title_enhance, separators)
    if 'upload_doc_job_id' in st.session_state:
        get_upload_do_job()
