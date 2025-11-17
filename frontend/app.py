import streamlit as st
import httpx
import time
import os

# --- Cấu hình ---
# Sử dụng biến môi trường hoặc giá trị mặc định
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://gateway:8000")
client = httpx.Client(base_url=API_GATEWAY_URL, timeout=60.0)

st.set_page_config(page_title="TWP-Ω V-Infinity", layout="wide")

st.title("🧠 TWP-Ω V-Infinity")
st.caption("The Perpetual AI Operating System")

# ---- Chức năng Tiếp thu (Assimilate) ----
st.header("1. Assimilate Knowledge")
with st.expander("Expand to add new information to the system"):
    # API Key input
    api_key_assimilate = st.text_input("Enter your API Key", type="password", key="api_key_assimilate")
    user_id_assimilate = st.text_input("Enter your User ID", value="doanh", key="user_id_assimilate")
    source_id = st.text_input("Enter a Source ID", value=f"manual_{int(time.time())}", key="source_id")
    content = st.text_area("Paste the content you want the system to learn", height=200, key="content_area")

    if st.button("Assimilate"):
        if user_id_assimilate and source_id and content and api_key_assimilate:
            with st.spinner("The system is learning... This may take a moment."):
                try:
                    headers = {"X-API-Key": api_key_assimilate}
                    response = client.post(
                        "/v_infinity/assimilate",
                        params={"source_id": source_id, "content": content, "user_id": user_id_assimilate},
                        headers=headers
                    )
                    if response.status_code == 200:
                        job_id = response.json().get("job_id")
                        st.success(f"Assimilation task queued successfully! Job ID: {job_id}")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except httpx.RequestError as e:
                    st.error(f"Connection Error: Could not connect to the Gateway API. Is it running? Details: {e}")
        else:
            st.warning("Please fill in all fields, including the API Key.")

# ---- Chức năng Chat ----
st.header("2. Chat with the System")

api_key_chat = st.text_input("Enter your API Key", type="password", key="api_key_chat")
user_id_chat = st.text_input("Enter your User ID", value="doanh", key="user_id_chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is your question?"):
    if not api_key_chat:
        st.warning("Please enter your API Key to chat.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Thinking..."):
                try:
                    headers = {"X-API-Key": api_key_chat}
                    response = client.post(
                        "/v_infinity/chat",
                        params={"query": prompt, "user_id": user_id_chat},
                        headers=headers
                    )
                    if response.status_code == 200:
                        full_response = response.json().get("answer", "Sorry, I couldn't find an answer.")
                        loras_used = response.json().get("loras_used", 0)
                        full_response += f"\\n\\n*LoRAs used: {loras_used}*"
                    else:
                        full_response = f"Error: {response.status_code} - {response.text}"
                except httpx.RequestError as e:
                    full_response = f"Connection Error: Could not connect to the Gateway API. Details: {e}"

            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
