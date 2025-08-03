import streamlit as st
import requests
from PIL import Image

# 页面配置
st.set_page_config(
    page_title="智能聊天助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if "history" not in st.session_state:
    st.session_state.history = []

# 侧边栏设置
with st.sidebar:
    sys_prompt = st.text_input("系统提示词", value="你是一个有用的小助手")
    temperature = st.slider("温度", min_value=0.1, max_value=2.0, step=0.1, value=0.7)
    top_p = st.slider("采样率", min_value=0.0, max_value=1.0, step=0.1, value=0.5)
    max_tokens = st.slider("最大分词量", min_value=100, max_value=2048, step=100, value=1024)
    history_len = st.slider("保留历史聊天长度", min_value=2, max_value=20, step=1, value=5)
    model = st.radio("选择模型", ("deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", "Qwen/Qwen3-8B", "THUDM/GLM-Z1-9B-0414"))
    stream = st.checkbox("流式输出", value=True)

    # 清空聊天记录
    if st.button("清空聊天记录"):
        st.session_state.history = []
        st.success("聊天记录已清空")

# 显示历史聊天
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 输入框
if prompt := st.chat_input("请输入您的问题..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)

    # 准备请求数据
    data = {
        "query": prompt,
        "sys_prompt": sys_prompt,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "history_len": history_len,
        "history": st.session_state.history,
        "model": model,
    }

    backend_url = "http://127.0.0.1:1234/chat"

    # 创建一个占位符来显示助手的回复
    assistant_placeholder = st.chat_message("assistant")
    assistant_text = assistant_placeholder.markdown("正在响应中，请稍等...")

    try:
        # 发送请求到后端
        response = requests.post(backend_url, json=data, stream=True)

        if response.status_code == 200:
            full_response = ""

            # 处理流式响应
            if stream:
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        full_response += chunk
                        assistant_text.markdown(full_response)
            else:
                # 获取完整响应
                full_response = response.text
                assistant_text.markdown(full_response)

            # 更新历史记录
            st.session_state.history.append({"role": "user", "content": prompt})
            st.session_state.history.append({"role": "assistant", "content": full_response})
        else:
            assistant_text.markdown(f"错误: 服务器返回状态码 {response.status_code}")
    except Exception as e:
        assistant_text.markdown(f"错误: {str(e)}")
