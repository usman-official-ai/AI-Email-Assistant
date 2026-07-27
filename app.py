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
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = 0

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
    st.error("""
    ❌ **GROQ_API_KEY not found!**
    
    **For Cloud:** Add secrets in Streamlit Cloud dashboard
    **For Local:** Create `.env` file with `GROQ_API_KEY=your_key_here`
    
    Get API key from: [console.groq.com](https://console.groq.com)
    """)
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
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 25px rgba(255, 75, 75, 0.3) !important;
}
.stSidebar .stButton > button {
    background: #f0f0f0 !important;
    color: #1a1a1a !important;
    border: 1px solid #d0d0d0 !important;
    box-shadow: none !important;
}
.stSidebar .stButton > button:hover {
    background: #e0e0e0 !important;
    border-color: #ff4b4b !important;
}
.stDownloadButton > button {
    background: #f0f0f0 !important; color: #1a1a1a !important;
    border: 1px solid #d0d0d0 !important; border-radius: 10px !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #f0f0f0 !important; border-radius: 12px !important;
    padding: 4px !important; border: 1px solid #e0e0e0 !important;
}
.stTabs [data-baseweb="tab"] { color: #666 !important; border-radius: 8px !important; padding: 10px 20px !important; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b) !important;
    color: #ffffff !important;
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
.stRadio > div > label[data-baseweb="radio"] input:checked + div {
    background: #ff4b4b !important;
    border-color: #ff4b4b !important;
}
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

def call_groq_api(prompt, model="llama-3.1-8b-instant", retry_count=0):
    try:
        current_time = time.time()
        time_since_last = current_time - st.session_state.last_request_time
        if time_since_last < 1.0:
            time.sleep(1.0 - time_since_last)
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional email assistant with expertise in business communication, grammar, and writing styles. Respond with clear, well-formatted emails."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 1
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        st.session_state.last_request_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        elif response.status_code == 429 and retry_count < 2:
            wait_time = (retry_count + 1) * 3
            time.sleep(wait_time)
            return call_groq_api(prompt, model, retry_count + 1)
            
        elif response.status_code == 401:
            return "❌ Invalid API Key! Please check your GROQ_API_KEY."
            
        elif response.status_code == 429:
            return "⚠️ Rate limit exceeded! Please wait 2-3 minutes and try again."
            
        else:
            return f"❌ API Error: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "❌ Request timeout! Please try again."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def generate_email(prompt):
    if not st.session_state.groq_available:
        return "❌ API not connected. Please check your GROQ_API_KEY."
    
    model_to_use = "llama-3.1-8b-instant"
    if not prompt or not prompt.strip():
        return "❌ Please provide a valid prompt."
    
    return call_groq_api(prompt, model_to_use)

is_connected = check_api()

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("# 📧 AI Email Assistant")
    st.caption("Write, reply, correct, and polish your emails.")
    
    st.divider()
    
    st.markdown("### 🎯 Features")
    st.markdown("""
    - ✍️ Write Email
    - ↩️ Reply (5 Types)
    - ✅ Grammar Fix
    - 🎭 Tone (7 Types)
    - 📏 Length (Short/Medium/Detailed)
    - 🏷️ Subject Lines
    - 💡 Improvement Tips
    - 📋 Copy
    - 📄 TXT/PDF Export
    """)
    
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
    st.warning("""
    ⚠️ **API not connected!**
    
    Please check your `GROQ_API_KEY` in:
    - **Cloud:** Streamlit Secrets
    - **Local:** `.env` file
    """)

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
            "Describe the topic, purpose, or bullet points for your email",
            height=150,
            placeholder="e.g. Ask my manager for 2 days of leave next week for a family event...",
            key="input_new"
        )

        col_tone, col_length = st.columns(2)
        with col_tone:
            tone = st.selectbox(
                "Tone",
                ["Professional", "Formal", "Friendly", "Polite", "Confident", "Apologetic", "Persuasive"],
                index=0
            )
        with col_length:
            length = st.selectbox(
                "Length",
                ["Short", "Medium", "Detailed"],
                index=1
            )

        if st.button("✨ Generate Email", type="primary"):
            if not input_text.strip():
                st.warning("Please describe what the email should be about.")
            else:
                with st.spinner("Drafting your email..."):
                    prompt = f"""Write a professional email based on the following description.

Topic: {input_text}
Tone: {tone}
Length: {length}

Write a complete email with subject line, greeting, body, and sign-off.

Email:"""
                    result = generate_email(prompt)
                    if result.startswith("❌") or result.startswith("⚠️"):
                        st.error(result)
                    else:
                        st.session_state.generated_email = result
                        st.rerun()

    elif mode == "Reply to an email":
        st.markdown("### 📨 Paste the email you're replying to")
        input_text = st.text_area(
            "Original email",
            height=150,
            placeholder="Paste the email you received here...",
            key="input_reply"
        )

        reply_type = st.selectbox(
            "Reply type",
            ["General", "Accept Meeting", "Decline Politely", "Request More Info", "Thank You", "Follow-up"],
            index=0
        )

        col_tone, col_length = st.columns(2)
        with col_tone:
            tone = st.selectbox(
                "Tone",
                ["Professional", "Formal", "Friendly", "Polite", "Confident", "Apologetic", "Persuasive"],
                index=0,
                key="reply_tone"
            )
        with col_length:
            length = st.selectbox(
                "Length",
                ["Short", "Medium", "Detailed"],
                index=1,
                key="reply_length"
            )

        if st.button("↩️ Generate Reply", type="primary"):
            if not input_text.strip():
                st.warning("Please paste the original email first.")
            else:
                with st.spinner("Writing your reply..."):
                    prompt = f"""Write a reply to the following email.

Original email:
{input_text}

Reply type: {reply_type}
Tone: {tone}
Length: {length}

Write a complete email reply.

Reply:"""
                    result = generate_email(prompt)
                    if result.startswith("❌") or result.startswith("⚠️"):
                        st.error(result)
                    else:
                        st.session_state.generated_email = result
                        st.rerun()

    else:
        st.markdown("### 🛠️ Paste the email you want to improve")
        input_text = st.text_area(
            "Your email draft",
            height=150,
            placeholder="Paste your draft email here...",
            key="input_edit"
        )

        st.markdown("#### Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✅ Fix Grammar", use_container_width=True):
                if not input_text.strip():
                    st.warning("Please paste an email first.")
                else:
                    with st.spinner("Fixing grammar..."):
                        prompt = f"Fix all grammar, spelling, and punctuation errors in this email. Return only the corrected version:\n\n{input_text}"
                        result = generate_email(prompt)
                        if result.startswith("❌") or result.startswith("⚠️"):
                            st.error(result)
                        else:
                            st.session_state.generated_email = result
                            st.rerun()
        
        with col2:
            if st.button("🎭 Change Tone", use_container_width=True):
                if not input_text.strip():
                    st.warning("Please paste an email first.")
                else:
                    with st.spinner("Changing tone..."):
                        tone = st.selectbox("Tone", ["Professional", "Formal", "Friendly", "Polite", "Confident", "Apologetic", "Persuasive"], index=0, key="edit_tone")
                        prompt = f"Rewrite this email in a {tone} tone. Keep the core message but adjust the language:\n\n{input_text}"
                        result = generate_email(prompt)
                        if result.startswith("❌") or result.startswith("⚠️"):
                            st.error(result)
                        else:
                            st.session_state.generated_email = result
                            st.rerun()
        
        with col3:
            if st.button("📏 Adjust Length", use_container_width=True):
                if not input_text.strip():
                    st.warning("Please paste an email first.")
                else:
                    with st.spinner("Adjusting length..."):
                        length = st.selectbox("Length", ["Short", "Medium", "Detailed"], index=1, key="edit_length")
                        prompt = f"Create a {length} version of this email. Keep the same meaning and tone:\n\n{input_text}"
                        result = generate_email(prompt)
                        if result.startswith("❌") or result.startswith("⚠️"):
                            st.error(result)
                        else:
                            st.session_state.generated_email = result
                            st.rerun()
        
        with col4:
            if st.button("💡 Improve", use_container_width=True):
                if not input_text.strip():
                    st.warning("Please paste an email first.")
                else:
                    with st.spinner("Analyzing..."):
                        prompt = f"""Provide improvement suggestions for this email including:
1. Grammar and spelling
2. Readability and clarity
3. Tone appropriateness
4. Missing information
5. Professional wording recommendations

Email:
{input_text}

Suggestions:"""
                        result = generate_email(prompt)
                        if result.startswith("❌") or result.startswith("⚠️"):
                            st.error(result)
                        else:
                            st.session_state.generated_email = result
                            st.rerun()
    
    # ========== SUBJECT LINE GENERATOR ==========
    st.divider()
    st.markdown("### 🏷️ Subject Line Generator")
    if st.button("Generate Subject Lines (3-5)", use_container_width=True):
        source_text = st.session_state.generated_email or input_text if 'input_text' in locals() else ""
        if not source_text.strip():
            st.warning("Generate or paste an email first.")
        else:
            with st.spinner("Generating subject lines..."):
                prompt = f"Generate 5 professional subject lines for this email. Return only the subject lines, one per line:\n\n{source_text}"
                result = generate_email(prompt)
                if result.startswith("❌") or result.startswith("⚠️"):
                    st.error(result)
                else:
                    st.session_state.generated_email = result
                    st.rerun()

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
                    st.code(st.session_state.generated_email, language="text")
        
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
                st.button("📑 PDF", disabled=True, use_container_width=True)
        
        if st.button("🔄 Clear Output", use_container_width=True):
            st.session_state.generated_email = ""
            st.rerun()
    else:
        st.info("Your generated email will appear here.")

# ========== FOOTER ==========
st.divider()
st.caption("⚠️ Always review AI-generated content before sending. This tool assists — it doesn't replace your judgment.")
