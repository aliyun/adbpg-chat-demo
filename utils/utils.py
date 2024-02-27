import streamlit as st


def write_error(msg):
    st.markdown(f'<p style="font-family:Courier; color:Red; font-size: 10px;">{msg}</p>',
                unsafe_allow_html=True)


def write_info(msg):
    st.markdown(f'<p style="font-family:Courier; color:Blue; font-size: 10px;">{msg}</p>',
                unsafe_allow_html=True)


def horizontal_input(label, columns=None):
    c1, c2 = st.columns(columns or [2, 5])
    c1.markdown(label)
    return c2


def check_instance_initialized() -> bool:
    if 'all_namespaces' not in st.session_state:
        if 'adbpg_instance_id' in st.session_state:
            st.title(st.session_state.adbpg_instance_id)
        write_error("实例未初始化，请返回主页初始化。")
        return False
    return True
