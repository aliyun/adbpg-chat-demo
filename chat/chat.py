import random
from http import HTTPStatus
import dashscope
from configs.model_configs import PROMPT_TEMPLATES, EAS_SERVICE_URL, EAS_SERVICE_TOKEN, DASHSCOPE_LLM_NAME
from configs import logger
from typing import List
from dashscope.api_entities.dashscope_response import (Message, Role)
import streamlit as st
from langchain_community.llms.pai_eas_endpoint import PaiEasEndpoint
from langchain_core.prompts import PromptTemplate


def call_pai_eas(retrieval_contents: List[str], question: str) -> str:
    if retrieval_contents:
        prompt = PromptTemplate.from_template(PROMPT_TEMPLATES.get('default'))
        msg_content = PROMPT_TEMPLATES.get('default').replace('{context}', '\n'.join(retrieval_contents)).replace('{question}', question)
    else:
        prompt = PromptTemplate.from_template(PROMPT_TEMPLATES.get('Empty'))
        msg_content = PROMPT_TEMPLATES.get('Empty').replace('{question}', question)
    messages = [Message(role=Role.SYSTEM, content='You are a helpful assistant.'),
                Message(role=Role.USER, content=msg_content)]
    if len(st.session_state.qa_history) == 0:
        st.session_state.qa_history = messages.copy()
    else:
        st.session_state.qa_history.append(Message(role=Role.USER, content=msg_content))
    llm = PaiEasEndpoint(
        eas_service_url=EAS_SERVICE_URL,
        eas_service_token=EAS_SERVICE_TOKEN,
        version='1.0',
    )
    llm_chain = prompt | llm
    if retrieval_contents:
        output = llm_chain.invoke({"context": '\n'.join(retrieval_contents), "question": question})
    else:
        output = llm_chain.invoke({"question": question})
    logger.info(f"llm response: {output}")
    st.session_state.qa_history.append(
        Message(role='assistant',
                content=str(output),
                image_urls=None)
    )
    return str(output)


def call_dashscope(retrieval_contents: List[str], question: str) -> str:
    if retrieval_contents:
        msg_content = PROMPT_TEMPLATES.get('default').replace('{context}', '\n'.join(retrieval_contents)).replace('{question}', question)
    else:
        msg_content = PROMPT_TEMPLATES.get('Empty').replace('{question}', question)

    messages = [Message(role=Role.SYSTEM, content='You are a helpful assistant.'),
                Message(role=Role.USER, content=msg_content)]
    if len(st.session_state.qa_history) == 0:
        st.session_state.qa_history = messages.copy()
    else:
        st.session_state.qa_history.append(Message(role=Role.USER, content=msg_content))
    response = dashscope.Generation.call(
        DASHSCOPE_LLM_NAME,
        messages=messages,
        seed=random.randint(1, 10000),
        result_format='message',  # set the result to be "message" format.
    )
    if response.status_code == HTTPStatus.OK:
        print(response)
        # append result to history.
        st.session_state.qa_history.append(
            Message(role=response.output.choices[0]['message']['role'],
                    content=response.output.choices[0]['message']['content'],
                    image_urls=None)
        )
        return '\n\n'.join([i.message.content for i in response.output.choices])
    else:
        raise ValueError('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))


def call_with_messages(retrieval_contents: List[str], question: str) -> str:
    if EAS_SERVICE_URL:
        return call_pai_eas(retrieval_contents, question)
    return call_dashscope(retrieval_contents, question)


if __name__ == '__main__':
    call_with_messages([], "hello")
