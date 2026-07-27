import streamlit as st
import os
import time
from datetime import datetime
import requests
import pyperclip

# ========== SESSION STATE ==========
if 'generated_email' not in st.session_state:
    st.session_state.generated_email = ""
if 'groq_available' not in st.session_state:
    st.session_state.groq_available = False
if 'api_checked' not in st.session_state:
    st.session_state.api_checked = False

# ========== SECRETS + .ENV SUPPORT ==========
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

# ========== LIGHT THEME ==========
st.markdown("""
<style>
.stApp { background: #f5f5f7; }
.stSidebar { background: #ffffff; border-right: 1px solid #e0e0e0; }
h1, h2, h3, h4, h5, h6, .stTitle, .stHeader, .stSubheader { color: #1a1a1a !important; }
.stApp, .stMarkdown, .stText, .stCaption, .stInfo, .stSuccess, .stWarning, .stError,
.stTextInput > label, .stSelectbox > label, .stTextArea > label,
.stRadio > label, .stCheckbox > label { color: #1a1a1a !important; }
.stSidebar .stMarkdown, .stSidebar .stText, .stSidebar label { color: #1a1a1a !important; }
.stTextArea > div > div > textarea {
    background: #ffffff !important; color: #1a1a1a !important;
    border: 1px solid #d0d0d0 !important; border-radius: 12px !important;
}
.stTextArea > div > div > textarea::placeholder { color: #999 !important; }
.stButton > button {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; padding: 12px 28px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(255, 75, 75, 0.2) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 25px rgba(255, 75, 75, 0.3) !important;
}
.stSidebar .stButton > button {
    background: #f0f0f0 !important;
    color: #1a1a1a !important;
    border: 1px solid #d0d0d0 !important;
}
.stDownloadButton > button {
    background: #f0f0f0 !important; color: #1a1a1a !important;
    border: 1px solid #d0d0d0 !important; border-radius: 10px !important;
}
hr { border-color: #e0e0e0 !important; }
.stCaption { color: #888 !important; }
.output-box { 
    background: #ffffff; 
    border: 1px solid #e0e0e0; 
    border-radius: 12px; 
    padding: 20px; 
    margin: 10px 0; 
    min-height: 150px;
}
.output-box .stMarkdown { color: #1a1a1a !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f5f5f7; }
::-webkit-scrollbar-thumb { background: #d0d0d0; border-radius: 4px; }
.stRadio > div {
    display: flex !important;
    gap: 8px !important;
}
.stRadio > div > label {
    background: #f0f0f0 !important;
    color: #1a1a1a !important;
    padding: 8px 20px !important;
    border-radius: 8px !important;
    border: 1px solid #d0d0d0 !important;
    font-size: 13px !important;
}
.stRadio > div > label:hover { border-color: #ff4b4b !important; }
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

def generate_email(prompt):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        elif response.status_code == 429:
            return "⚠️ Rate limit. Please wait."
        else:
            return f"❌ Error: {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

is_connected = check_api()

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("# 📧 AI Email Assistant")
    st.caption("Write, reply, correct, and polish your emails.")
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

with left:
    if mode == "Write a new email":
        st.markdown("### ✍️ What's the email about?")
        input_text = st.text_area(
            "",
            height=150,
            placeholder="e.g. Ask my manager for 2 days of leave next week for a family event...",
            key="input_new",
            label_visibility="collapsed"
        )

        # ========== TONE (7 TYPES) ==========
        tone = st.selectbox(
            "Tone",
            ["Professional", "Formal", "Friendly", "Polite", "Confident", "Apologetic", "Persuasive"],
            index=0
        )
        
        # ========== LENGTH (3 TYPES) ==========
        length = st.selectbox(
            "Length",
            ["Short", "Medium", "Detailed"],
            index=1
        )

        if st.button("✨ Generate Email", type="primary", use_container_width=True):
            if not input_text.strip():
                st.warning("Please describe what the email should be about.")
            else:
                with st.spinner("Drafting your email..."):
                    prompt = f"Write a professional email with {tone} tone and {length} length about: {input_text}"
                    result = generate_email(prompt)
                    if not result.startswith("❌"):
                        st.session_state.generated_email = result
                        st.rerun()
                    else:
                        st.error(result)

    elif mode == "Reply to an email":
        st.markdown("### 📨 Paste the email you're replying to")
        input_text = st.text_area(
            "",
            height=150,
            placeholder="Paste the email you received here...",
            key="input_reply",
            label_visibility="collapsed"
        )

        # ========== REPLY TYPES (5 TYPES) ==========
        reply_type = st.selectbox(
            "Reply type",
            ["General", "Accept Meeting", "Decline Politely", "Request More Info", "Thank You", "Follow-up"],
            index=0
        )

        tone = st.selectbox(
            "Tone",
            ["Professional", "Formal", "Friendly", "Polite", "Confident", "Apologetic", "Persuasive"],
            index=0,
            key="reply_tone"
        )
        
        length = st.selectbox(
            "Length",
            ["Short", "Medium", "Detailed"],
            index=1,
            key="reply_length"
        )

        if st.button("↩️ Generate Reply", type="primary", use_container_width=True):
            if not input_text.strip():
                st.warning("Please paste the original email first.")
            else:
                with st.spinner("Writing your reply..."):
                    prompt = f"Write a {reply_type} reply with {tone} tone and {length} length for: {input_text}"
                    result = generate_email(prompt)
                    if not result.startswith("❌"):
                        st.session_state.generated_email = result
                        st.rerun()
                    else:
                        st.error(result)

    else:
        st.markdown("### 🛠️ Paste the email you want to improve")
        input_text = st.text_area(
            "",
            height=150,
            placeholder="Paste your draft email here...",
            key="input_edit",
            label_visibility="collapsed"
        )

        st.markdown("#### Actions")
        
        # ========== 4 ACTIONS ==========
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✅ Fix Grammar", use_container_width=True):
                if not input_text.strip():
                    st.warning("Please paste an email first.")
                else:
                    with st.spinner("Fixing grammar..."):
                        prompt = f"Fix all grammar errors in this email: {input_text}"
                        result = generate_email(prompt)
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
                        tone = st.selectbox("Tone", ["Professional", "Formal", "Friendly", "Polite", "Confident", "Apologetic", "Persuasive"], index=0, key="edit_tone")
                        prompt = f"Rewrite this email in {tone} tone: {input_text}"
                        result = generate_email(prompt)
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
                        length = st.selectbox("Length", ["Short", "Medium", "Detailed"], index=1, key="edit_length")
                        prompt = f"Rewrite this email in {length} length: {input_text}"
                        result = generate_email(prompt)
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
                        result = generate_email(prompt)
                        if not result.startswith("❌"):
                            st.session_state.generated_email = result
                            st.rerun()
                        else:
                            st.error(result)
    
    # ========== SUBJECT LINE GENERATOR ==========
    st.divider()
    st.markdown("### 🏷️ Subject Line Generator")
    if st.button("Generate Subject Lines (3-5)", use_container_width=True):
        source_text = st.session_state.generated_email or input_text if 'input_text' in locals() else ""
        if not source_text.strip():
            st.warning("Generate or paste an email first.")
        else:
            with st.spinner("Generating subject lines..."):
                prompt = f"Generate 5 professional subject lines for this email: {source_text}"
                result = generate_email(prompt)
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
        
        # ========== COPY FEATURE ==========
        with col_a:
            if st.button("📋 Copy", use_container_width=True):
                try:
                    pyperclip.copy(st.session_state.generated_email)
                    st.success("✅ Copied!")
                except:
                    st.warning("Please select and copy manually.")
        
        # ========== TXT EXPORT ==========
        with col_b:
            st.download_button(
                label="📄 TXT",
                data=st.session_state.generated_email,
                file_name=f"email_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        # ========== PDF EXPORT ==========
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
                st.button("📑 PDF", disabled=True, use_container_width=True)
        
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.generated_email = ""
            st.rerun()
    else:
        st.info("Your generated email will appear here.")

st.divider()
st.caption("⚠️ Always review AI-generated content before sending.")
