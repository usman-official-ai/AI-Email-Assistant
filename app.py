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

# ========== DARK THEME ==========
st.markdown("""
<style>
.stApp { background: #0e1117; }
.stSidebar { background: #1a1a2e; border-right: 1px solid #2a2a44; }

/* ALL TEXT WHITE */
h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, .stCaption,
.stTextInput > label, .stSelectbox > label, .stTextArea > label,
.stRadio > label { color: #ffffff !important; }

/* SIDEBAR */
.stSidebar .stMarkdown, .stSidebar .stText, .stSidebar label,
.stSidebar h1, .stSidebar h2, .stSidebar h3 { color: #ffffff !important; }

/* INPUT FIELDS */
.stTextArea > div > div > textarea {
    background: #1a1a2e !important;
    color: #ffffff !important;
    border: 1px solid #2a2a44 !important;
    border-radius: 10px !important;
    font-size: 14px !important;
}
.stTextArea > div > div > textarea::placeholder {
    color: #666 !important;
}
.stTextInput > div > div > input {
    background: #1a1a2e !important;
    color: #ffffff !important;
    border: 1px solid #2a2a44 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
}
.stSelectbox > div > div > select {
    background: #1a1a2e !important;
    color: #ffffff !important;
    border: 1px solid #2a2a44 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
}

/* RADIO BUTTONS */
.stRadio > div {
    display: flex !important;
    gap: 8px !important;
}
.stRadio > div > label {
    background: #1a1a2e !important;
    color: #ffffff !important;
    padding: 8px 20px !important;
    border-radius: 8px !important;
    border: 1px solid #2a2a44 !important;
    font-size: 13px !important;
}
.stRadio > div > label:hover {
    border-color: #ff4b4b !important;
}

/* PRIMARY BUTTONS */
.stButton > button {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 20px rgba(255, 75, 75, 0.25) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 30px rgba(255, 75, 75, 0.35) !important;
}

/* SIDEBAR BUTTONS */
.stSidebar .stButton > button {
    background: #2a2a44 !important;
    color: white !important;
    border: 1px solid #3a3a5c !important;
    box-shadow: none !important;
    padding: 10px 20px !important;
}
.stSidebar .stButton > button:hover {
    background: #3a3a5c !important;
    border-color: #ff4b4b !important;
    transform: none !important;
}

/* DOWNLOAD BUTTONS */
.stDownloadButton > button {
    background: #1a1a2e !important;
    color: white !important;
    border: 1px solid #2a2a44 !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
}

/* OUTPUT BOX */
.output-box {
    background: #1a1a2e;
    border: 1px solid #2a2a44;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    min-height: 200px;
}
.output-box .stMarkdown {
    color: #e0e0e0 !important;
}

/* DIVIDER */
hr { border-color: #2a2a44 !important; margin: 15px 0 !important; }

/* SCROLLBAR */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0e1117; }
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
    st.markdown("# 📧 AI Email Assistant")
    st.caption("Write, reply, correct, and polish your emails.")
    
    st.divider()
    
    st.markdown("### ⚙️ Settings")
    
    st.markdown("**Tone**")
    tone = st.selectbox("", ["Professional", "Friendly", "Formal", "Casual", "Persuasive", "Confident", "Apologetic"], label_visibility="collapsed")
    
    st.markdown("**Length**")
    length = st.selectbox("", ["Medium", "Short", "Detailed"], label_visibility="collapsed")
    
    st.divider()
    
    st.markdown("### 📝 Templates")
    
    if st.button("📧 Job", use_container_width=True):
        st.session_state.email_input = """Subject: Application for Position

Dear Hiring Manager,

I am writing to apply for the position at your company. With my experience and skills, I believe I would be a valuable addition to your team.

Best regards,
[Your Name]"""
        st.rerun()
    
    if st.button("🏖️ Leave", use_container_width=True):
        st.session_state.email_input = """Subject: Leave Request

Dear Manager,

I am writing to request leave from [start date] to [end date]. Please approve my request.

Regards,
[Your Name]"""
        st.rerun()
    
    if st.button("📄 Proposal", use_container_width=True):
        st.session_state.email_input = """Subject: Business Proposal

Dear [Name],

I hope this email finds you well. I am writing to propose a collaboration between our companies.

Best regards,
[Your Name]"""
        st.rerun()
    
    st.divider()
    
    st.markdown("### 🔑 API Status")
    if is_connected:
        st.success("✅ Connected")
    else:
        st.error("❌ Not Connected")
    
    st.divider()
    st.caption("Built with Streamlit + Groq")

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

# ========== LEFT COLUMN ==========
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
        
        st.markdown("**Reply Type**")
        reply_type = st.selectbox(
            "",
            ["General", "Accept Meeting", "Decline Politely", "Request More Info", "Thank You", "Follow-up"],
            label_visibility="collapsed"
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
            if st.button("✅ Fix Grammar", use_container_width=True):
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
            if st.button("🎭 Change Tone", use_container_width=True):
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
            if st.button("📏 Adjust Length", use_container_width=True):
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
            if st.button("💡 Improve", use_container_width=True):
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

# ========== RIGHT COLUMN ==========
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
                    st.success("✅ Copied to clipboard!")
                except:
                    st.warning("Please select and copy manually.")
        
        with col_b:
            st.download_button(
                label="📄 TXT",
                data=st.session_state.generated_email,
                file_name=f"email_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_c:
            try:
                from src.utils.pdf_export import create_pdf
                pdf_data = create_pdf(st.session_state.generated_email)
                st.download_button(
                    label="📑 PDF",
                    data=pdf_data,
                    file_name=f"email_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except:
                st.download_button(
                    label="📑 PDF",
                    data=st.session_state.generated_email,
                    file_name=f"email_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    disabled=True
                )
        
        if st.button("🔄 Clear Output", use_container_width=True):
            st.session_state.generated_email = ""
            st.rerun()
    else:
        st.info("Your generated or improved email will appear here.")

# ========== FOOTER ==========
st.divider()
st.caption("⚠️ Always review AI-generated content before sending. This tool assists — it doesn't replace your judgment.")
