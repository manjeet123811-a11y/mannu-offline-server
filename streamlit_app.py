import streamlit as st
import threading, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import database as db

st.set_page_config(page_title="Automation", page_icon="🔥", layout="wide")

# ------------------------------------------------------------------------------------
# 🔥 NEW LIVE LOGS SYSTEM
# ------------------------------------------------------------------------------------
def init_live_logs(max_lines: int = 200):
    if "live_logs" not in st.session_state:
        st.session_state.live_logs = []
    if "live_logs_max" not in st.session_state:
        st.session_state.live_logs_max = max_lines

def live_log(msg: str):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"

    init_live_logs()
    st.session_state.live_logs.append(line)

    if len(st.session_state.live_logs) > st.session_state.live_logs_max:
        st.session_state.live_logs = st.session_state.live_logs[-st.session_state.live_logs_max:]

def render_live_console():
    st.markdown('<div class="logbox">', unsafe_allow_html=True)
    for line in st.session_state.live_logs[-100:]:
        st.markdown(line)
    st.markdown('</div>', unsafe_allow_html=True)
# ------------------------------------------------------------------------------------


# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp {
    background: url('https://iili.io/fK3pATQ.png') no-repeat center center fixed !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}
.stApp::before {
    content: "";
    position: fixed;
    top:0; left:0;
    width:100%; height:100%;
    background: rgba(0,0,0,0.10);
    z-index:0;
    pointer-events:none;
}
.stCard {background: rgba(255,255,255,0.02) !important;}
.logbox {
    background: rgba(0,0,0,0.55);
    color:#0ff;
    padding:15px;
    height:300px;
    overflow:auto;
    border-radius:20px;
    box-shadow:0 0 20px rgba(0,255,255,0.35);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center;">E23E FB</h1>', unsafe_allow_html=True)


# ---------------- SESSION ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "automation_running" not in st.session_state: st.session_state.automation_running = False
if "automation_state" not in st.session_state:
    st.session_state.automation_state = type('obj',(object,),{
        "running": False,
        "message_count": 0,
        "message_rotation_index": 0
    })()

init_live_logs()


# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            uid = db.verify_user(u, p)
            if uid:
                st.session_state.logged_in = True
                st.session_state.user_id = uid
                cfg = db.get_user_config(uid)

                st.session_state.chat_id = cfg.get("chat_id", "")
                st.session_state.chat_type = cfg.get("chat_type", "E2EE")
                st.session_state.delay = cfg.get("delay", 15)
                st.session_state.cookies = cfg.get("cookies", "")
                st.session_state.messages = cfg.get("messages", "").split("\n") if cfg.get("messages") else []

                if cfg.get("running", False):
                    st.session_state.automation_running = True
                    st.session_state.automation_state.running = True

                st.rerun()
            else:
                st.error("Invalid login")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        npc = st.text_input("Confirm Password", type="password")
        if st.button("Create User"):
            if np != npc:
                st.error("Passwords do not match")
            else:
                ok, msg = db.create_user(nu, np)
                if ok: st.success("User created!")
                else: st.error(msg)

    st.stop()


# ---------------- DASHBOARD ----------------
st.subheader(f"Dashboard — User {st.session_state.user_id}")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.automation_running = False
    st.session_state.automation_state.running = False
    st.rerun()


# ---------------- MESSAGE FILE ----------------
msg_file = st.file_uploader("Upload .txt messages", type=["txt"])
if msg_file:
    st.session_state.messages = msg_file.read().decode().split("\n")
    st.success("Messages Loaded")


# ---------------- CONFIG ----------------
chat_id = st.text_input("Chat ID", value=st.session_state.chat_id)
chat_type = st.selectbox("Chat Type", ["E2EE", "Non-E2EE"], index=0 if st.session_state.chat_type == "E2EE" else 1)
delay = st.number_input("Delay", 1, 300, value=st.session_state.delay)
cookies = st.text_area("Cookies", value=st.session_state.cookies)

if st.button("Save Config"):
    db.update_user_config(
        st.session_state.user_id,
        chat_id, chat_type, delay,
        cookies, "\n".join(st.session_state.messages),
        running=st.session_state.automation_running
    )
    st.success("Saved!")


# ---------------- AUTOMATION ENGINE ----------------
def setup_browser():
    opt = Options()
    opt.add_argument("--headless=new")
    opt.add_argument("--no-sandbox")
    opt.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=opt)

def find_input(driver, chat_type):
    sel = ["div[contenteditable='true']"] if chat_type == "E2EE" else ["div[contenteditable='true']", "textarea", "[role='textbox']"]
    for s in sel:
        try:
            return driver.find_element(By.CSS_SELECTOR, s)
        except: pass
    return None


def send_messages(cfg, stt):
    try:
        live_log("Starting browser...")
        d = setup_browser()
        d.get("https://www.facebook.com")
        time.sleep(8)
        live_log("Facebook loaded")

        for c in (cfg.get("cookies") or "").split(";"):
            if "=" in c:
                n, v = c.split("=", 1)
                try:
                    d.add_cookie({"name":n.strip(), "value":v.strip(), "domain":".facebook.com", "path":"/"})
                except:
                    live_log(f"Cookie failed: {c}")

        d.get(f"https://www.facebook.com/messages/t/{cfg.get('chat_id','')}")
        time.sleep(10)
        live_log("Chat opened")

        box = find_input(d, cfg.get("chat_type"))
        if not box:
            live_log("❌ Input box not found")
            stt.running = False
            return

        msgs = [m.strip() for m in (cfg.get("messages") or "").split("\n") if m.strip()]
        if not msgs: msgs = ["Hello!"]

        while stt.running:
            msg = msgs[stt.message_rotation_index % len(msgs)]
            stt.message_rotation_index += 1

            try:
                box.send_keys(msg)
                box.send_keys("\n")
                stt.message_count += 1
                live_log(f"Sent: {msg}")
            except Exception as e:
                live_log(f"Error: {e}")

            time.sleep(cfg.get("delay", 15))

        live_log("Automation stopped")
        d.quit()

    except Exception as e:
        live_log(f"Fatal Error: {e}")


# ---------------- CONTROLS ----------------
st.subheader("Automation Control")

col1, col2 = st.columns(2)

if col1.button("START", disabled=st.session_state.automation_running):
    cfg = db.get_user_config(st.session_state.user_id)
    cfg["running"] = True
    st.session_state.automation_running = True
    st.session_state.automation_state.running = True

    t = threading.Thread(target=send_messages, args=(cfg, st.session_state.automation_state))
    t.daemon = True
    t.start()

if col2.button("STOP", disabled=not st.session_state.automation_running):
    st.session_state.automation_state.running = False
    st.session_state.automation_running = False
    live_log("🛑 Stop pressed. Automation halting...")


# ---------------- LIVE LOGS DISPLAY ----------------
st.subheader("📡 Live Logs")
st.write(f"Messages Sent: {st.session_state.automation_state.message_count}")

render_live_console()

if st.session_state.automation_running:
    time.sleep(1)
    st.rerun()
