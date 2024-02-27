import streamlit as st
from chat import *
from .document_search import do_query_content
from utils.utils import write_error


def parse_question_from_qa_history(content: str):
    if '<问题>' not in content:
        return content
    return content[content.index('<问题>')+4:content.index('</问题>')]


def do_qa(question_content, top_k, filter_str, metrics, use_full_text_retrieval):
    for h in st.session_state.qa_history:
        if h.role in ('user', 'assistant'):
            with st.chat_message(h.role):
                if h.role == 'user':
                    st.write(parse_question_from_qa_history(h.content))
                else:
                    st.write(h.content)
    with st.chat_message("user"):
        st.write(question_content)
    try:
        retrieval_contents = do_query_content(top_k, question_content, filter_str, metrics, use_full_text_retrieval)
        answer = call_with_messages([i.content for i in retrieval_contents], question_content)
        with st.chat_message("assistant"):
            st.write(answer)
    except Exception as e:
        write_error(str(e))


def qa_page(question):
    with st.expander('高级选项'):
        top_k = st.number_input('TopK:', value=10)
        filter_str = st.text_area('Filter:')
        metrics = st.selectbox('Metrics:', options=[None, 'cosine', 'l2', 'ip'])
        use_full_text_retrieval = st.toggle('是否全文检索', value=True)
    if question:
        do_qa(question, top_k, filter_str, metrics, use_full_text_retrieval)

