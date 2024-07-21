import streamlit as st
from chat import *
from utils.utils import write_error


def parse_question_from_qa_history(content: str):
    if '<问题>' not in content:
        return content
    return content[content.index('<问题>')+4:content.index('</问题>')]


def do_qa(question_content):
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
        answer = call_with_messages([], question_content)
        with st.chat_message("assistant"):
            st.write(answer)
    except Exception as e:
        write_error(str(e))


def main():
    if 'pre_page' in st.session_state and st.session_state.pre_page != '3_Chat':
        st.session_state.qa_history = []
    if 'qa_history' not in st.session_state:
        st.session_state.qa_history = []
    st.session_state.pre_page = '3_Chat'
    question = st.chat_input('请输入问题, 按回车确认')
    if question:
        do_qa(question)


if __name__ == '__main__':
    main()