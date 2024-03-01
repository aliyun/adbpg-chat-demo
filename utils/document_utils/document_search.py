import streamlit as st
import json
from utils.utils import write_error, write_info
from configs import *


def do_query_content(top_k, content, filter_str, metrics, use_full_text_retrieval, file_name=None, file_bytes_data=None):
    logger.info("query....")
    _, resp = st.session_state.adbpg_client.query_content(
        namespace=st.session_state.collection_namespace,
        namespace_password=st.session_state.namespace_password_cache[st.session_state.collection_namespace],
        collection=st.session_state.selected_document_collection.collection_name,
        top_k=top_k,
        content=content,
        filter_str=filter_str if filter_str else None,
        metrics=metrics,
        use_full_text_retrieval=use_full_text_retrieval,
        file_name=file_name,
        file_object_data=file_bytes_data
    )
    return resp


def show_search_result(top_k, content, filter_str, metrics, use_full_text_retrieval, only_show_content, show_ref_image,
                       file_name=None, file_bytes_data=None):
    write_info(f'检索内容:{content}, 参数：top_k:{top_k}, filter_str:{filter_str}, metrics:{metrics}, '
               f'use_full_text_retrieval:{use_full_text_retrieval}, only_show_content:{only_show_content}')
    try:
        resp = do_query_content(top_k=top_k, content=content, filter_str=filter_str, metrics=metrics,
                                use_full_text_retrieval=use_full_text_retrieval,
                                file_name=file_name, file_bytes_data=file_bytes_data)
        if only_show_content:
            resp_data = [i.content for i in resp]
        else:
            resp_data = [
                {"content": i.content, "file_name": i.file_name, "id": i.id, "loader_metadata": i.loader_metadata,
                 "metadata": i.metadata, "retrieval_source": i.retrieval_source, "score": i.score,
                 "vector": i.vector.vector_list if i.vector else None} for i in resp]
        if not show_ref_image:
            st.json(json.dumps(resp_data))
            return

        st.divider()
        st.markdown('### 检索结果: ')
        for data in resp:
            if not data.loader_metadata:
                st.write(data.content)
            else:
                loader_metadata = json.loads(data.loader_metadata)
                if 'image_refs' not in loader_metadata:
                    if data.content:
                        st.write(data.content)
                else:
                    for image_ref in loader_metadata['image_refs']:
                        if image_ref.get('img_pos') == 'front':
                            st.image(loader_metadata['image_ref_urls'][f'{image_ref["page_index"]}_{image_ref["img_index"]}'])
                    st.write(data.content)
                    for image_ref in loader_metadata['image_refs']:
                        if image_ref.get('img_pos') == 'behind':
                            st.image(loader_metadata['image_ref_urls'][f'{image_ref["page_index"]}_{image_ref["img_index"]}'])
            st.divider()
    except Exception as e:
        write_error(str(e))


def show_image_search_result(top_k, content, metrics, file_name=None, file_bytes_data=None):
    write_info(f'检索内容:{content}, 图片文件名:{file_name}, 参数：top_k:{top_k}, metrics:{metrics}')
    try:
        resp = do_query_content(top_k=top_k, content=content, filter_str="", metrics=metrics,
                                use_full_text_retrieval=False,
                                file_name=file_name, file_bytes_data=file_bytes_data)
        st.divider()
        st.markdown('### 检索结果: ')
        for data in resp:
            if not data.loader_metadata:
                st.write(data.content)
            else:
                if data.content:
                    st.write(data.content)
                if data.file_url:
                    st.write('Image Search Result: %s' % data.file_name)
                    st.image(data.file_url)
            st.divider()
    except Exception as e:
        write_error(str(e))


def retrieval_search_page():
    with st.expander('高级选项'):
        top_k = st.number_input('TopK:', value=10)
        filter_str = st.text_area('Filter:')
        metrics = st.selectbox('Metrics:', options=[None, 'cosine', 'l2', 'ip'])
        use_full_text_retrieval = st.toggle('是否全文检索')
        only_show_content = st.toggle('只显示Content内容', value=True)
        show_ref_image = st.toggle('搜索的文本显示关联图片', value=True)

    # 支持的检索项
    content = st.text_input('检索内容: ')
    if st.button('文档检索'):
        show_search_result(top_k, content, filter_str, metrics, use_full_text_retrieval, only_show_content, show_ref_image)


def retrieval_image_search_page():
    with st.expander('高级选项'):
        top_k = st.number_input('TopK:', value=10)
        metrics = st.selectbox('Metrics:', options=[None, 'cosine', 'l2', 'ip'])

    # 支持的检索项
    content = st.text_input('检索内容: ')
    uploaded_file = st.file_uploader("选择图片文件")
    file_bytes_data = None
    file_name = None
    if uploaded_file is not None:
        file_bytes_data = uploaded_file.read()
        file_name = uploaded_file.name

    if st.button('图片检索'):
        show_image_search_result(top_k, content, metrics, file_name, file_bytes_data)
