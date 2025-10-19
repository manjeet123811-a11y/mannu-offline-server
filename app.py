import streamlit as st
import time
from datetime import datetime

st.set_page_config(page_title="E2EE Automation Panel", layout="centered")
st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    ">
        <h1 style="margin-bottom: 10px;">MANJEET<br>E2EE FACEBOOK CONVO</h1>
        <h4>Created by MANJEET</h4>
    </div>
    """,
    unsafe_allow_html=True
)

# Initialize states
if "running" not in st.session_state:
    st.session_state.running = False
if "logs" not in st.session_state:
    st.session_state.logs = []
if "message_count" not in st.session_state:
    st.session_state.message_count = 0

# Sidebar Navigation
tabs = st.tabs(["⚙️ Configuration", "🚀 Automation"])

# ---------------- CONFIGURATION TAB ----------------
with tabs[0]:
    st.title("Your Configuration")

    chat_id = st.text_input("Chat/Conversation ID", placeholder="e.g., 1362400298935018")
    haters_name = st.text_input("Hatersname", placeholder="[END TO END MANJEET HERE]")
    delay = st.number_input("Delay (seconds)", min_value=1, max_value=300, value=30)
    fb_cookie = st.text_area("Facebook Cookies (optional - kept private)", 
                             placeholder="Paste your Facebook cookies here (will be encrypted)")
    messages = st.text_area("Messages (one per line)", 
                            placeholder="Write your messages here, one per line")

    if st.button("💾 Save Configuration"):
        st.session_state.config = {
            "chat_id": chat_id,
            "haters_name": haters_name,
            "delay": delay,
            "fb_cookie": fb_cookie,
            "messages": messages.splitlines()
        }
        st.success("✅ Configuration saved successfully!")


# ---------------- AUTOMATION TAB ----------------
with tabs[1]:
    st.title("Automation Control")

    st.write(f"**Messages Sent:** {st.session_state.message_count}")
    status = "🟢 Running" if st.session_state.running else "🔴 Stopped"
    st.write(f"**Status:** {status}")
    st.write(f"**Total Logs:** {len(st.session_state.logs)}")

    col1, col2 = st.columns(2)
    start_btn = col1.button("▶️ Start E2EE")
    stop_btn = col2.button("⏹️ Stop E2EE")

    if start_btn and not st.session_state.running:
        if "config" not in st.session_state:
            st.warning("⚠️ Please save your configuration first!")
        else:
            st.session_state.running = True
            st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Started automation.")
            st.success("Automation started!")

    if stop_btn and st.session_state.running:
        st.session_state.running = False
        st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Stopped automation.")
        st.warning("Automation stopped.")

    # Run simulation if running
    if st.session_state.running:
        st.info("Automation is running... check logs below.")
        config = st.session_state.config
        for msg in config["messages"]:
            if not st.session_state.running:
                break
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] Sent message: {msg}"
            st.session_state.logs.append(log_entry)
            st.session_state.message_count += 1
            time.sleep(config["delay"])
        st.session_state.running = False
        st.success("✅ All messages sent successfully!")

    # Live Logs Display
    st.subheader("📊 Live Logs")
    if st.session_state.logs:
        for log in reversed(st.session_state.logs[-10:]):
            st.code(log)
    else:
        st.info("No logs yet. Start automation to see logs here.")
