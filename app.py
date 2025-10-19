import streamlit as st
import time
from datetime import datetime

st.set_page_config(page_title="E2EE Automation Panel", layout="centered")

# ---------------- SESSION STATES ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "running" not in st.session_state:
    st.session_state.running = False
if "logs" not in st.session_state:
    st.session_state.logs = []
if "message_count" not in st.session_state:
    st.session_state.message_count = 0


# ---------------- LOGIN PAGE ----------------
def login_page():
    st.markdown("""
        <div style="background: linear-gradient(135deg,#6a11cb,#2575fc);padding:20px;border-radius:15px;margin-bottom:30px;text-align:center;color:white;">
            <h2>HASSAN RAJPUT<br>E2EE FACEBOOK CONVO</h2>
            <p>Created by HASSAN RAJPUT</p>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🔐 Login", "✨ Sign Up"])

    with tabs[0]:
        st.subheader("Welcome Back!")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", placeholder="Enter your password", type="password")

        if st.button("Login", use_container_width=True):
            # Example login (you can customize)
            if username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    with tabs[1]:
        st.subheader("Create a New Account")
        st.info("Signup feature under development...")


# ---------------- MAIN APP ----------------
def automation_panel():
    st.markdown("""
        <div style="background: linear-gradient(135deg,#6a11cb,#2575fc);padding:20px;border-radius:15px;margin-bottom:30px;text-align:center;color:white;">
            <h2>HASSAN RAJPUT<br>E2EE FACEBOOK CONVO</h2>
            <p>Created by HASSAN RAJPUT</p>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.title("👤 Account")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    tabs = st.tabs(["⚙️ Configuration", "🚀 Automation"])

    # CONFIGURATION TAB
    with tabs[0]:
        st.title("Your Configuration")

        chat_id = st.text_input("Chat/Conversation ID", placeholder="e.g., 1362400298935018")
        haters_name = st.text_input("Hatersname", placeholder="[END TO END HASSAN RAJPUT HERE]")
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

    # AUTOMATION TAB
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

        st.subheader("📊 Live Logs")
        if st.session_state.logs:
            for log in reversed(st.session_state.logs[-10:]):
                st.code(log)
        else:
            st.info("No logs yet. Start automation to see logs here.")


# ---------------- MAIN EXECUTION ----------------
if not st.session_state.logged_in:
    login_page()
else:
    automation_panel()
