import streamlit as st
import os
import time
from datetime import datetime
import requests
import pyperclip

# ========== SESSION STATE ==========
if 'generated_email' not in st.session_state:
    st.session_state.generated_email = ""
if 'email_input' not in st.session_state:
    st.session_state.email_input = ""
if 'groq_available' not in st.session_state:
    st.session_state.groq_available = False
if 'api_checked' not in st.session_state:
    st.session_state.api_checked = False

# ========== SECRETS + .ENV ==========
def get_api_key():
    try:
        if hasattr(st, 'secrets') and st.secrets:
            if "GROQ_API_KEY" in st.secrets:
                return st.secrets["GROQ_API_KEY"]
    except:
        pass
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("GROQ_API_KEY")
    except:
        pass
    return None

GROQ_API_KEY = get_api_key()

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found! Add to .env or Secrets.")
    st.stop()

st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="📧",
    layout="wide"
)

# ========== CLEAN CSS ==========
st.markdown("""
<style>
/* Main */
.stApp { background: #0a0a0f; }
.stSidebar { background: #111118; border-right: 1px solid #1a1a2e; }

/* All Text White */
h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, .stCaption,
.stTextInput > label, .stSelectbox > label, .stTextArea > label,
.stRadio > label { color: #ffffff !important; }

/* Sidebar Text */
.stSidebar .stMarkdown, .stSidebar .stText, .stSidebar label { color: #ffffff !important; }

/* Input Fields */
.stTextArea > div > div > textarea {
    background: #1a1a2e !important;
    color: #ffffff !important;
    border: 1px solid #2a2a44 !important;
    border-radius: 12px !important;
}
.stTextInput > div > div > input {
    background: #1a1a2e !important;
    color: #ffffff !important;
    border: 1px solid #2a2a44 !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
}
.stSelectbox > div > div > select {
    background: #1a1a2e !important;
    color: #ffffff !important;
    border: 1px solid #2a2a44 !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 28px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 20px rgba(255, 75, 75, 0.25) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 30px rgba(255, 75, 75, 0.35) !important;
}

/* Radio Buttons - Horizontal */
.stRadio > div {
    display: flex !important;
    gap: 10px !important;
}
.stRadio > div > label {
    background: #1a1a2e !important;
    color: #ffffff !important;
    padding: 8px 20px !important;
    border-radius: 10px !important;
    border: 1px solid #2a2a44 !important;
    font-size: 14px !important;
}
.stRadio > div > label:hover {
    border-color: #ff4b4b !important;
}
.stRadio > div > label[data-baseweb="radio"] input:checked + div {
    background: #ff4b4b !important;
    border-color: #ff4b4b !important;
}

/* Download Buttons */
.stDownloadButton > button {
    background: #1a1a2e !important;
    color: white !important;
    border: 1px solid #2a2a44 !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
}

/* Divider */
hr { border-color: #1a1a2e !important; margin: 15px 0 !important; }

/* Output Box */
.output-box {
    background: #111118;
    border: 1px solid #1a1a2e;
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    min-height: 150px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a44; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ========== API SETUP ==========
def check_api():
    if st.session_state.api_checked:
        return st.session_state.groq_available
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "OK"}], "max_tokens": 5}
        response = requests.post(url, headers=headers, json=data, timeout=10)
        st.session_state.groq_available = response.status_code == 200
    except:
        st.session_state.groq_available = False
    st.session_state.api_checked = True
    return st.session_state.groq_available

def call_groq(prompt):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "system", "content": "You are a professional email assistant."}, {"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"❌ Error: {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

is_connected = check_api()

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")
    
    st.markdown("**Tone**")
    tone = st.selectbox("", ["Professional", "Friendly", "Formal", "Casual", "Persuasive"], label_visibility="collapsed")
    
    st.markdown("**Length**")
    length = st.selectbox("", ["Medium", "Short", "Detailed"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 📝 Templates")
    
    templates = {
        "📧 Job": """Subject: Application for Position\n\nDear Hiring Manager,\n\nI am writing to apply for the position at your company. With my experience and skills, I believe I would be a valuable addition to your team.\n\nBest regards,\n[Your Name]""",
        "🏖️ Leave": """Subject: Leave Request\n\nDear Manager,\n\nI am writing to request leave from [start date] to [end date]. Please approve my request.\n\nRegards,\n[Your Name]""",
        "📄 Proposal": """Subject: Business Proposal\n\nDear [Name],\n\nI hope this email finds you well. I am writing to propose a collaboration between our companies.\n\nBest regards,\n[Your Name]"""
    }
    
    for name, content in templates.items():
        if st.button(name, use_container_width=True):
            st.session_state.email_input = content
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔑 API Status")
    if is_connected:
        st.success("✅ Connected")
    else:
        st.error("❌ Not Connected")

# ========== MAIN CONTENT ==========
st.markdown("# 📧 AI Email Assistant")
st.markdown("Write, reply, correct, and polish your emails in seconds.")

if not is_connected:
    st.warning("⚠️ API not connected. Please check your GROQ_API_KEY.")

# ========== MODE SELECTION ==========
mode = st.radio(
    "What do you want to do?",
    ["Write a new email", "Reply to an email", "Improve / edit an existing email"],
    horizontal=True,
)

left, right = st.columns([1, 1])

with left:
    if mode == "Write a new email":
        st.markdown("### ✍️ What's the email about?")
        input_text = st.text_area(
            "",
            height=180,
            placeholder="e.g. Ask my manager for 2 days of leave next week for a family event...",
            key="input_new",
            value=st.session_state.email_input if st.session_state.email_input else "",
            label_visibility="collapsed"
        )
        
        if st.button("✨ Generate Email", type="primary"):
            if not input_text.strip():
                st.warning("Please describe what the email should be about.")
            else:
                with st.spinner("Drafting your email..."):
                    prompt = f"Write a professional email with {tone} tone and {length} length about: {input_text}"
                    result = call_groq(prompt)
                    if not result.startswith("❌"):
                        st.session_state.generated_email = result
                        st.rerun()
                    else:
                        st.error(result)

    elif mode == "Reply to an email":
        st.markdown("### 📨 Paste the email you're replying to")
        input_text = st.text_area(
            "",
            height=180,
            placeholder="Paste the email you received here...",
            key="input_reply",
            value=st.session_state.email_input if st.session_state.email_input else "",
            label_visibility="collapsed"
        )
        
        reply_type = st.selectbox(
            "Reply type",
            ["General", "Accept Meeting", "Decline Politely", "Request More Info", "Thank You", "Follow-up"],
            index=0
        )
        
        if st.button("↩️ Generate Reply", type="primary"):
            if not input_text.strip():
                st.warning("Please paste the original email first.")
            else:
                with st.spinner("Writing your reply..."):
                    prompt = f"Write a {reply_type} reply with {tone} tone and {length} length for: {input_text}"
                    result = call_groq(prompt)
                    if not result.startswith("❌"):
                        st.session_state.generated_email = result
                        st.rerun()
                    else:
                        st.error(result)

    else:
        st.markdown("### 🛠️ Paste the email you want to improve")
        input_text = st.text_area(
            "",
            height=180,
            placeholder="Paste your draft email here...",
            key="input_edit",
            value=st.session_state.email_input if st.session_state.email_input else "",
            label_visibility="collapsed"
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✅ Fix Grammar"):
                if not input_text.strip():
                    st.warning("Please paste an email first.")
                else:
                    with st.spinner("Fixing grammar..."):
                        prompt = f"Fix all grammar errors in this email. Return only corrected version: {input_text}"
                        result = call_groq(prompt)
                        if not result.startswith("❌"):
                            st.session_state.generated_email = result
                            st.rerun()
                        else:
                            st.error(result)
        
        with col2:
            if st.button("🎭 Change Tone"):
                if not input_text.strip():
                    st.warning("Please paste an email first.")
                else:
                    with st.spinner("Changing tone..."):
                        prompt = f"Rewrite this email in {tone} tone: {input_text}"
                        result = call_groq(prompt)
                        if not result.startswith("❌"):
                            st.session_state.generated_email = result
                            st.rerun()
                        else:
                            st.error(result)
        
        with col3:
            if st.button("📏 Adjust Length"):
                if not input_text.strip():
                    st.warning("Please paste an email first.")
                else:
                    with st.spinner("Adjusting length..."):
                        prompt = f"Rewrite this email in {length} length: {input_text}"
                        result = call_groq(prompt)
                        if not result.startswith("❌"):
                            st.session_state.generated_email = result
                            st.rerun()
                        else:
                            st.error(result)
        
        with col4:
            if st.button("💡 Improve"):
                if not input_text.strip():
                    st.warning("Please paste an email first.")
                else:
                    with st.spinner("Analyzing..."):
                        prompt = f"Suggest improvements for this email: {input_text}"
                        result = call_groq(prompt)
                        if not result.startswith("❌"):
                            st.session_state.generated_email = result
                            st.rerun()
                        else:
                            st.error(result)

with right:
    st.markdown("### 📤 Output")
    
    if st.session_state.generated_email:
        st.markdown('<div class="output-box">', unsafe_allow_html=True)
        st.markdown(st.session_state.generated_email)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("📋 Copy", use_container_width=True):
                try:
                    pyperclip.copy(st.session_state.generated_email)
                    st.success("✅ Copied!")
                except:
                    st.warning("Select and copy manually.")
        
        with col_b:
            st.download_button(
                label="📄 TXT",
                data=st.session_state.generated_email,
                file_name=f"email_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_c:
            st.download_button(
                label="📑 PDF",
                data=st.session_state.generated_email,
                file_name=f"email_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.generated_email = ""
            st.rerun()
    else:
        st.info("Your generated or improved email will appear here.")

st.divider()
st.caption("⚠️ Always review AI-generated content before sending.")
