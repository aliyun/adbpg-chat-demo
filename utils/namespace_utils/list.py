import streamlit as st
from utils.utils import write_error, write_info
from configs import *
from streamlit_modal import Modal
from .check_in_collections import check_in_document_collection
from .delete import show_delete_namespace_modal


def list_div(col_outer):
    # col1, col2 = st.columns((1, 5))
    # with col1:
    #     st.markdown("##### Namespace列表")
    # with col2:
    if col_outer.button('Flush Namespace List'):
        try:
            st.session_state.all_namespaces = st.session_state.adbpg_client.list_namespaces(
                st.session_state.manager_account,
                st.session_state.manager_password)
            write_info("Flush namespace successfully.")
        except Exception as e:
            logger.info(f"failed to list_namespaces: {str(e)}")
            write_error(str(e))

    colms = st.columns((1, 2, 2))
    fields = ["Index", 'Name', 'Ops']
    for col, field_name in zip(colms, fields):
        # header
        col.write(field_name)

    for i, ns in enumerate(st.session_state.all_namespaces):
        col1, col2, col3, col4 = st.columns((1, 2, 1, 1))
        col1.write(i)
        col2.write(ns)
        delete_modal = Modal(f"ToDelete:{ns}", key=f"del_modal_{ns}", max_width=400)

        col3.button("Enter KnowledgeBase", key=f"checkin_{i}_{ns}_{st.session_state.page_index}",
                  on_click=check_in_document_collection, args=[ns])
        col4.button("Delete", key=f"delete_{i}_{ns}_{st.session_state.page_index}",
                  on_click=show_delete_namespace_modal,
                  disabled=(ns == "public"),
                  args=[ns, delete_modal])
            # col31, col32 = st.columns((1, 1))
            # with col31:
            #     st.button("进入文档库", key=f"checkin_{i}_{ns}_{st.session_state.page_index}",
            #               on_click=check_in_document_collection, args=[ns])
            # with col32:
            #     st.button("删除", key=f"delete_{i}_{ns}_{st.session_state.page_index}",
            #               on_click=show_delete_namespace_modal,
            #               disabled=(ns == "public"),
            #               args=[ns, delete_modal])
