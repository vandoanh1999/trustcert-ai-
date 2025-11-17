import streamlit as st
import httpx
import time

# Cấu hình client API
# Dùng tên service của Docker Compose làm hostname
API_GATEWAY_URL = "http://gateway:8000"
client = httpx.Client(base_url=API_GATEWAY_URL, timeout=60.0)

st.set_page_config(page_title="TWP-Ω V-Infinity", layout="wide")

st.title("🧠 TWP-Ω V-Infinity")
st.caption("The Perpetual AI Operating System")

# ---- Chức năng Tiếp thu (Assimilate) ----
st.header("1. Assimilate Knowledge")
with st.expander("Expand to add new information to the system"):
    user_id_assimilate = st.text_input("Enter your User ID", value="doanh", key="user_id_assimilate")
    source_id = st.text_input("Enter a Source ID (e.g., 'wikipedia_ai')", value=f"manual_{int(time.time())}", key="source_id")
    content = st.text_area("Paste the content you want the system to learn", height=200, key="content_area")

    if st.button("Assimilate"):
        if user_id_assimilate and source_id and content:
            with st.spinner("The system is learning... This may take a moment."):
                try:
                    response = client.post(
                        "/v_infinity/assimilate",
                        params={"source_id": source_id, "content": content, "user_id": user_id_assimilate}
                    )
                    if response.status_code == 200:
                        job_id = response.json().get("job_id")
                        st.success(f"Assimilation task queued successfully! Job ID: {job_id}")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except httpx.RequestError as e:
                    st.error(f"Connection Error: Could not connect to the Gateway API. Is the system running? Details: {e}")
        else:
            st.warning("Please fill in all fields.")

# ---- Chức năng Chat ----
st.header("2. Chat with the System")

user_id_chat = st.text_input("Enter your User ID", value="doanh", key="user_id_chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is your question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        with st.spinner("Thinking..."):
            try:
                response = client.post(
                    "/v_infinity/chat",
                    params={"query": prompt, "user_id": user_id_chat}
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
