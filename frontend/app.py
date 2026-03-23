"""
Genesis Core V7: The Portal Pillar (Genesis Hub)

A user-friendly Streamlit interface for non-technical users to interact
with the Genesis ecosystem.
"""
import streamlit as st
import requests
import time

# --- Configuration ---
API_URL = "http://127.0.0.1:8000"  # The URL of our FastAPI backend


# --- Helper Functions ---
def query_genesis_backend(instruction, experts):
    """
    Simulates a query to the backend. In a real V7 system, this would
    call a dispatch endpoint that uses the Chimera Core. For this PoC,
    we'll simulate the response and get a dispatch_id.
    """
    # This is a simulation. The real Chimera Core would be running this.
    # We are directly using the feedback endpoint's recording function
    # via a temporary, simulated "dispatch" endpoint we might add for the UI.

    # Let's assume a simple dispatch simulation endpoint exists for the UI
    try:
        # In a real scenario, you'd have a /dispatch endpoint that returns this
        # For now, we simulate by calling the feedback service to log the event
        # and get an ID back, which is close enough for our UI test.
        # This part is a placeholder for the actual inference call.

        # Let's just mock the backend call for now.
        time.sleep(2)
        mock_dispatch_id = f"dispatch_{int(time.time())}"
        mock_response_text = (
            f"This is a simulated response for your query about "
            f"'{instruction[:30]}...' using experts {experts}."
        )

        # We need to store this mapping locally in the session state for the UI
        if 'dispatch_history' not in st.session_state:
            st.session_state.dispatch_history = {}
        # Store which experts were used
        st.session_state.dispatch_history[mock_dispatch_id] = experts

        return mock_dispatch_id, mock_response_text
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the backend: {e}")
        return None, None


def send_feedback_to_backend(dispatch_id, score):
    """Sends the user's feedback score to the backend API."""
    try:
        feedback_url = f"{API_URL}/feedback/{dispatch_id}"
        response = requests.post(feedback_url, json={"score": score})
        if response.status_code == 200:
            st.toast(f"Feedback ({score}/1.0) submitted successfully! 🚀")
            # Clear the last response to be ready for the next query
            st.session_state.last_response = None
            time.sleep(1)
            st.rerun()
        else:
            st.error(
                f"Failed to submit feedback. "
                f"Server responded with: {response.status_code}"
            )
            st.json(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the backend: {e}")


# --- Streamlit UI ---
st.set_page_config(page_title="Genesis Hub", layout="wide")

# --- Sidebar Controls ---
with st.sidebar:
    st.title("⚙️ System Controls")
    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.clear()
        # To clear widget state, we can use a key-prefix or this trick:
        if "query_input_key" not in st.session_state:
            st.session_state.query_input_key = 0
        st.session_state.query_input_key += 1
        st.toast("Session reset successfully!")
        time.sleep(0.5)
        st.rerun()
    st.divider()
    st.info("Genesis Hub V8 - UX Enhanced")

st.title("🌌 Genesis Hub")
st.caption("The Portal to the Genesis Symbiotic Network")

# --- Initialization ---
if 'last_response' not in st.session_state:
    st.session_state.last_response = None
if "query_input_key" not in st.session_state:
    st.session_state.query_input_key = 0

# --- Main Interaction Panel ---
st.header("1. Submit a Query")

# For this demo, we'll let the user "choose" the experts.
# In a real system, the Oracle Brain would do this automatically.
available_experts = [
    "dummy_adapters/expert_A/adapter_model.bin",
    "dummy_adapters/expert_B/adapter_model.bin",
    "dummy_adapters/expert_C/adapter_model.bin"  # A hypothetical new expert
]
selected_experts = st.multiselect(
    "Select Experts to Consult (simulation):",
    options=available_experts,
    default=available_experts[:2]
)

user_instruction = st.text_area(
    "Enter your instruction or question:",
    key=f"user_instruction_{st.session_state.query_input_key}"
)

query_disabled = not user_instruction or not selected_experts
if st.button("Query Genesis", disabled=query_disabled):
    with st.status("Dispatching query to the expert network...") as status:
        st.write("🔍 Identifying relevant expert adapters...")
        time.sleep(0.5)
        st.write("📡 Routing query through decentralized P2P nodes...")
        dispatch_id, response_text = query_genesis_backend(
            user_instruction, selected_experts
        )
        if dispatch_id and response_text:
            st.session_state.last_response = {
                "dispatch_id": dispatch_id,
                "text": response_text,
                "experts": selected_experts
            }
            status.update(label="✅ Query successful!", state="complete")
        else:
            status.update(label="❌ Query failed.", state="error")

# --- Feedback Panel ---
if st.session_state.last_response:
    st.divider()
    st.header("2. Provide Feedback")

    response_data = st.session_state.last_response

    st.subheader("Generated Response:")
    st.code(response_data["text"], language="markdown")
    st.caption(f"Generated by: {', '.join(response_data['experts'])}")
    st.caption(f"Dispatch ID: {response_data['dispatch_id']}")

    st.write("How would you rate this response?")

    feedback_score = st.slider(
        "Rating (0.0 = Bad, 1.0 = Perfect)", 0.0, 1.0, 0.75, 0.05
    )

    if st.button("Submit Feedback"):
        # This is a slight hack for the demo. Since the backend isn't *really*
        # tracking our mocked dispatch IDs, we'll quickly register it
        # *just before* sending feedback. This simulates the real flow where
        # the ID would already exist from the inference step.
        try:
            # We need to create this endpoint
            register_url = f"{API_URL}/feedback/register_mock_dispatch"
            requests.post(register_url, json={
                "dispatch_id": response_data['dispatch_id'],
                "experts": response_data['experts']
            })
        except Exception:
            # Ignore if it fails, the main feedback call is important to test
            pass

        send_feedback_to_backend(response_data["dispatch_id"], feedback_score)
