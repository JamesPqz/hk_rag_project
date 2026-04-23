import os
from time import sleep

import requests
import streamlit as st
# from agent.react_agent import ReactAgent

st.set_page_config(page_title='rag system', layout='wide')

st.title('rag service')
st.divider()

with st.sidebar:
    st.header('configuration')
    # api_base = os.getenv("API_BASE_URL", "http://localhost/api")
    if os.getenv("DOCKER_ENV"):
        api_base = "http://nginx/api"
    else:
        api_base = "http://localhost:8000"
    api_url = st.text_input('api address', value=api_base)
    session_id = st.text_input('session id', value='user123')

    st.header('document manager')
    upload_file = st.file_uploader('upload file', type=['docx','txt', 'md', 'csv', 'tsv'])
    if upload_file and st.button('upload'):
        files = {"file": upload_file}
        try:
            resp = requests.post(f"{api_url}/documents/upload", files= files)
            if resp.status_code == 200:
                st.success(f"upload success:{resp.json()['filename']}")
            else:
                st.error(f"upload fail:{resp.text}")
        except Exception as e:
            st.error(f"connect error:{e}")


# if 'agent' not in st.session_state:
#     st.session_state['agent'] = ReactAgent()
#
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
#
for msg in st.session_state['messages']:
    st.chat_message(msg['role']).write(msg['content'])
    if "sources" in msg and msg["sources"]:
        st.caption(f"来源：{', '.join(msg['sources'])}")

prompt = st.chat_input()

if prompt:
    st.chat_message('user').write(prompt)
    st.session_state['messages'].append({'role': 'user', 'content': prompt})

    res_list = []
    with st.spinner('ai thinking'):
        # res_stream = st.session_state['agent'].execute_stream(prompt)
        try:
            resp = requests.post(
                # f"{api_url}/chat/ask",
                # f"{api_url}/chat/ask/stream",
                f"{api_url}/agent/chat/stream",
                params={"session_id": session_id},
                json={"query": prompt, "k": 4},
                stream=True
            )
            if resp.status_code == 200:
                # 直接输出
                # data = resp.json()
                # answer = data["answer"]
                # sources = data.get("sources", [])
                # st.chat_message('assistant').write_stream(answer)
                # if sources:
                #     st.caption(f"来源：{', '.join(sources)}")
                # st.session_state.messages.append({
                #     "role": "assistant",
                #     "content": answer,
                #     "sources": sources
                # })

                #流输出
                # full_answer = ""
                # placeholder = st.empty()
                # for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
                #     if chunk:
                #         full_answer += chunk
                #         placeholder.markdown(full_answer + "▌")
                # placeholder.markdown(full_answer)

                answer = st.chat_message('assistant').write_stream(resp.iter_content(chunk_size=128, decode_unicode=True))

                # 从响应头获取 sources
                sources_header = resp.headers.get("X-Sources", "")
                sources = sources_header.split(",") if sources_header else []

                if sources:
                    st.caption(f"来源：{', '.join(sources)}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            else:
                st.error(f"request fail：{resp.text}")
        except Exception as e:
            st.error(f"connect fail:{e}")

        # def capture(generator, cache_list):
        #     for chunk in generator:
        #         cache_list.append(chunk)
        #         for char in chunk:
        #             sleep(0.01)
        #             yield char
        #
        # res = capture(res_stream, res_list)
        # st.chat_message('assistant').write_stream(res)
        # st.session_state['messages'].append({'role': 'assistant', 'content': res_list[-1]})
        # st.rerun()