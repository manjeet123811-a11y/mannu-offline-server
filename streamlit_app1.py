import streamlit as st
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import database as db

st.set_page_config(page_title="Automation", page_icon="🔥", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>  
.stApp{background:#0d0d0d;} 
.title{font-size:2.5rem;font-weight:900;text-align:center;background:linear-gradient(90deg,#00eaff,#ff00d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;} 
.stButton>button{background:linear-gradient(45deg,#00eaff,#ff00d4);color:#fff;border:none;border-radius:10px;padding:10px 25px;font-weight:700;}  
.logbox{background:#111;color:#0ff;padding:10px;height:200px;overflow:auto;border-radius:10px;margin-top:10px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">⚡ AUTOMATION</div>', unsafe_allow_html=True)

# ---------------- SESSION VARS ----------------
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_id' not in st.session_state: st.session_state.user_id = None
if 'automation_running' not in st.session_state: st.session_state.automation_running = False
if 'automation_state' not in st.session_state:
    st.session_state.automation_state = type('obj',(object,),{
        "running":False,
        "message_count":0,
        "message_rotation_index":0,
        "logs":[]
    })()

# ---------------- LOGIN / CREATE USER ----------------
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["User Login", "Create Account"])  

    # USER LOGIN  
    with tab1:  
        u = st.text_input("Username")  
        p = st.text_input("Password", type="password")  
        if st.button("Login"):  
            uid = db.verify_user(u, p)  
            if uid:  
                st.session_state.logged_in = True  
                st.session_state.user_id = uid  
                st.rerun()  
            else:  
                st.error("Invalid username/password")  

    # CREATE ACCOUNT  
    with tab2:  
        nu = st.text_input("New Username")  
        np = st.text_input("New Password", type="password")  
        npc = st.text_input("Confirm Password", type="password")  
        if st.button("Create User"):  
            if np != npc:  
                st.error("Passwords do not match!")  
            else:  
                ok, msg = db.create_user(nu, np)  
                if ok: st.success("User Created! You can now login.")  
                else: st.error(msg)  

    st.stop()

# ---------------- USER DASHBOARD ----------------
st.subheader("👤 User Dashboard")

# ---------------- MESSAGE FILE UPLOAD ----------------
st.markdown("### 📂 Upload .txt Messages File")
msg_file = st.file_uploader("Upload messages", type=["txt"])
msgs = []
if msg_file:
    msgs = msg_file.read().decode("utf-8").split("\n")
    st.success("Messages loaded!")

# ---------------- CONFIG ----------------
chat_id = st.text_input("Chat ID")
chat_type = st.selectbox("Chat Type", ["E2EE", "Non-E2EE"])
delay = st.number_input("Delay (sec)", 1, 300, 15)
cookies = st.text_area("Cookies")

if st.button("Save Config"):
    db.update_user_config(
        st.session_state.user_id, chat_id, chat_type, delay, cookies, "\n".join(msgs)
    )
    st.success("Saved!")

# ---------------- AUTOMATION ENGINE ----------------
def setup_browser():
    opt = Options()
    opt.add_argument('--headless=new')
    opt.add_argument('--no-sandbox')
    opt.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=opt)

def find_input(driver, chat_type):
    if chat_type == "E2EE":
        selectors = ["div[contenteditable='true']"]
    else:
        selectors = ["div[contenteditable='true']", "textarea", "[role='textbox']"]
    for s in selectors:
        try: 
            return driver.find_element(By.CSS_SELECTOR, s)
        except: 
            pass
    return None

def send_messages(cfg, stt):
    stt.logs.append("Starting browser...")
    d = setup_browser()
    d.get("https://www.facebook.com")
    time.sleep(8)
    stt.logs.append("Browser loaded Facebook")

    # set cookies
    for c in (cfg.get('cookies') or "").split(';'):  
        if '=' in c:  
            n,v = c.split('=',1)  
            try: 
                d.add_cookie({"name":n.strip(),"value":v.strip(),"domain":".facebook.com","path":"/"})  
            except: 
                stt.logs.append(f"Failed to add cookie: {c}")

    d.get(f"https://www.facebook.com/messages/t/{cfg.get('chat_id','')}")  
    time.sleep(10)  
    stt.logs.append(f"Opened chat: {cfg.get('chat_id','')}")

    box = find_input(d, cfg.get('chat_type','E2EE'))  
    if not box:  
        stt.logs.append("Input box not found!")
        stt.running = False  
        return  

    msgs = [m for m in (cfg.get('messages') or "").split("\n") if m.strip()]  
    if not msgs:  
        msgs = ["Hello!"]  

    while stt.running:  
        m = msgs[stt.message_rotation_index % len(msgs)]  
        stt.message_rotation_index += 1  
        try:  
            box.send_keys(m)
            box.send_keys("\n")  
            stt.message_count += 1
            stt.logs.append(f"Sent message: {m}")
        except Exception as e:  
            stt.logs.append(f"Error sending message: {e}")
        time.sleep(int(cfg.get('delay',15)))  

    d.quit()
    stt.logs.append("Browser closed, automation stopped")

# ---------------- AUTOMATION UI ----------------
st.subheader("🚀 Automation Control")
col1, col2 = st.columns(2)

if col1.button("▶️ START", disabled=st.session_state.automation_running):
    cfg = db.get_user_config(st.session_state.user_id)
    if not cfg or not cfg.get('chat_id'):
        st.error("Please save a Chat ID in config first.")
    else:
        st.session_state.automation_state.running = True
        st.session_state.automation_running = True
        t = threading.Thread(target=send_messages, args=(cfg, st.session_state.automation_state))
        t.daemon = True
        t.start()
        st.rerun()

if col2.button("⏹️ STOP", disabled=not st.session_state.automation_running):
    st.session_state.automation_state.running = False
    st.session_state.automation_running = False
    st.rerun()

# ---------------- LIVE LOGS ----------------
st.subheader("📡 Live Logs & Messages Sent")
st.write(f"Messages Sent: {st.session_state.automation_state.message_count}")
st.markdown('<div class="logbox">', unsafe_allow_html=True)
for log in st.session_state.automation_state.logs[-50:]:
    st.markdown(log)
st.markdown('</div>', unsafe_allow_html=True)
