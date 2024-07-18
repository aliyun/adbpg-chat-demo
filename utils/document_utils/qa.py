import streamlit as st
from chat import *
from .document_search import do_query_content
from utils.utils import write_error
import json


def parse_question_from_qa_history(content: str):
    if '<问题>' not in content:
        return content
    return content[content.index('<问题>')+4:content.index('</问题>')]

def get_image_urls(retrieval_contents):
    image_urls = []
    for data in retrieval_contents:
        if data.loader_metadata:
            loader_metadata = json.loads(data.loader_metadata)
            if 'image_refs' in loader_metadata:
                for image_ref in loader_metadata['image_refs']:
                    if image_ref.get('img_pos') == 'front':
                        image_urls.append(loader_metadata['image_ref_urls'][
                                     f'{image_ref["page_index"]}_{image_ref["img_index"]}'])
                for image_ref in loader_metadata['image_refs']:
                    if image_ref.get('img_pos') == 'behind':
                        image_urls.append(loader_metadata['image_ref_urls'][
                                     f'{image_ref["page_index"]}_{image_ref["img_index"]}'])
    return list(set(image_urls))


def do_qa(question_content, top_k, filter_str, metrics, use_full_text_retrieval):
    for h in st.session_state.qa_history:
        if h.role in ('user', 'assistant'):
            with st.chat_message(h.role):
                if h.role == 'user':
                    st.write(parse_question_from_qa_history(h.content))
                else:
                    st.write(h.content)
                    if h.image_urls:
                        for u in h.image_urls:
                            st.image(u)
    with st.chat_message("user"):
        st.write(question_content)
    try:
        retrieval_contents = do_query_content(top_k, question_content, filter_str, metrics, use_full_text_retrieval)
        answer = call_with_messages([i.content for i in retrieval_contents], question_content)
        with st.chat_message("assistant"):
            st.write(answer)
            image_urls = get_image_urls(retrieval_contents)
            if len(image_urls) > 0:
                for u in image_urls:
                    st.image(u)
                st.session_state.qa_history[-1].image_urls = image_urls
    except Exception as e:
        write_error(str(e))


def qa_page(question):
    with st.expander('高级选项'):
        top_k = st.number_input('TopK:', value=3)
        filter_str = st.text_area('Filter:')
        metrics = st.selectbox('Metrics:', options=[None, 'cosine', 'l2', 'ip'])
        use_full_text_retrieval = st.toggle('是否全文检索', value=True)
    if question:
        do_qa(question, top_k, filter_str, metrics, use_full_text_retrieval)

