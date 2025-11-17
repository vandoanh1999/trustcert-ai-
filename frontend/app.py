import streamlit as st
import httpx
import time
import os
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- Cấu hình ---
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://gateway:8000")
client = httpx.Client(base_url=API_GATEWAY_URL, timeout=60.0)

# --- Kết nối Google Sheets ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Không thể kết nối đến Google Sheets. Vui lòng kiểm tra cấu hình secrets. Lỗi: {e}")
    conn = None

def record_feedback(question, incorrect_answer, correct_answer, feedback_type):
    """Ghi lại phản hồi vào Google Sheet."""
    if conn is None:
        st.error("Kết nối Google Sheets chưa được cấu hình, không thể ghi lại phản hồi.")
        return
    try:
        sheet = conn.read(worksheet="Feedback", usecols=list(range(4)), ttl=0)
        sheet = sheet.dropna(how="all")
        new_row = pd.DataFrame([{
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Question": question,
            "Incorrect Answer": incorrect_answer if feedback_type == "bad" else "N/A",
            "Correct Answer": correct_answer
        }])
        updated_df = pd.concat([sheet, new_row], ignore_index=True)
        conn.update(worksheet="Feedback", data=updated_df)
    except Exception as e:
        st.error(f"Gặp lỗi khi ghi phản hồi vào Google Sheet: {e}")

st.set_page_config(page_title="TWP-Ω V-Infinity", layout="wide")
st.title("🧠 TWP-Ω V-Infinity")
# ... (Phần Assimilate giữ nguyên) ...

# --- Chức năng Chat với Vòng lặp Phản hồi ---
# ... (Phần UI với các nút và form như đã thiết kế)
