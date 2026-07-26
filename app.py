import streamlit as st
import os
import time
import json
from datetime import datetime
from io import BytesIO
import requests

# ========== SECRETS + .ENV SUPPORT ==========
def get_api_key():
    try:
        if hasattr(st, 'secrets') and st.secrets:
            if "GROQ_API_KEY" in st.secrets:
                key = st.secrets["GROQ_API_KEY"]
                if key:
                    return key
    except:
        pass
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        key = os.getenv("GROQ_API_KEY")
        if key:
            return key
    except:
        pass
    
    return None

GROQ_API_KEY = get_api_key()

if not GROQ_API_KEY:
    st.error("""
    ❌ **GROQ_API_KEY not found!**
    
    **For Cloud:** Add secrets in Streamlit Cloud dashboard
    1. Go to App Settings → Secrets
    2. Add: `GROQ_API_KEY = "your_key_here"`
    3. Save and Reboot
    """)
    st.stop()

st.set_page_config(
    page_title="AI Email Assistant Pro",
    page_icon="✉️",
    layout="wide"
)

# ========== DARK THEME ==========
st.markdown("""
<style>
.stApp { background: #0e1117; }
.stSidebar { background: #1a1a2e; }
.stSidebar .stMarkdown, .stSidebar .stText, 
.stSidebar label, .stSidebar h1, .stSidebar h2, .stSidebar h3, 
.stSidebar h4, .stSidebar .stCaption, .stSidebar p,
.stSidebar .stTextInput > label, .stSidebar .stSelectbox > label,
.stSidebar .stRadio > label, .stSidebar .stCheckbox > label {
    color: #ffffff !important;
}
.stSidebar .stTextInput > div > div > input {
    background: #2d2d44 !important;
    color: #ffffff !important;
    border: 1px solid #444 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
}
.stSidebar .stSelectbox > div > div > select {
    background: #2d2d44 !important;
    color: #ffffff !important;
    border: 1px solid #444 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
}
.stSidebar .stButton > button {
    background: #2d2d44 !important;
    color: #ffffff !important;
    border: 1px solid #444 !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
}
.stSidebar .stButton > button:hover {
    background: #3d3d5c !important;
    border-color: #ff4b4b !important;
}
.stSidebar hr { border-color: #444 !important; margin: 15px 0 !important; }
.stApp, .stApp viewport, .stApp .main,
.stMarkdown, .stText, .stCaption, .stInfo, .stSuccess, .stWarning, .stError,
.stTextInput > label, .stSelectbox > label, .stTextArea > label,
.stRadio > label, .stCheckbox > label,
h1, h2, h3, h4, h5, h6, .stTitle, .stHeader, .stSubheader {
    color: #ffffff !important;
}
.stTextInput > div > div > input {
    background: #2d2d44 !important;
    color: #ffffff !important;
    border: 1px solid #444 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
}
.stTextArea > div > div > textarea {
    background: #2d2d44 !important;
    color: #ffffff !important;
    border: 1px solid #444 !important;
    border-radius: 10px !important;
}
.stSelectbox > div > div > select {
    background: #2d2d44 !important;
    color: #ffffff !important;
    border: 1px solid #444 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
}
.stRadio > div > label { color: #ffffff !important; }
.stCheckbox > label { color: #ffffff !important; }
.stButton > button {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255, 75, 75, 0.4) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #2d6a4f, #40916c) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #1a1a2e !important;
    border-radius: 12px !important;
    padding: 6px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #8899aa !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    font-weight: 500 !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(255, 75, 75, 0.1) !important;
    color: #ffffff !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3) !important;
}
.stExpander {
    background: #1a1a2e !important;
    border: 1px solid #333 !important;
    border-radius: 12px !important;
}
.stExpander .streamlit-expanderHeader { color: #ffffff !important; font-weight: 500 !important; }
.stMetric {
    background: #1a1a2e !important;
    border-radius: 12px !important;
    padding: 16px !important;
    border: 1px solid #333 !important;
}
.stMetric label { color: #ffffff !important; font-weight: 500 !important; }
.stMetric .stMarkdown { color: #ff4b4b !important; font-size: 24px !important; font-weight: 700 !important; }
.api-status {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
}
.api-status.connected {
    background: rgba(0, 200, 0, 0.15);
    color: #00cc00;
    border: 1px solid #00cc00;
}
.api-status.disconnected {
    background: rgba(255, 0, 0, 0.15);
    color: #ff4444;
    border: 1px solid #ff4444;
}
.stSuccess { background: rgba(0, 200, 0, 0.1) !important; border: 1px solid #00cc00 !important; border-radius: 10px !important; padding: 16px !important; }
.stSuccess .stMarkdown { color: #00cc00 !important; }
.stError { background: rgba(255, 0, 0, 0.1) !important; border: 1px solid #ff4444 !important; border-radius: 10px !important; padding: 16px !important; }
.stError .stMarkdown { color: #ff4444 !important; }
.stWarning { background: rgba(255, 200, 0, 0.1) !important; border: 1px solid #ffcc00 !important; border-radius: 10px !important; padding: 16px !important; }
.stWarning .stMarkdown { color: #ffcc00 !important; }
hr { border-color: #333 !important; margin: 20px 0 !important; }
.stCaption { color: #888 !important; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #1a1a2e; }
::-webkit-scrollbar-thumb { background: #444; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if 'email_content' not in st.session_state:
    st.session_state.email_content = ""
if 'generated_email' not in st.session_state:
    st.session_state.generated_email = ""
if 'current_action' not in st.session_state:
    st.session_state.current_action = ""
if 'selected_model_id' not in st.session_state:
    st.session_state.selected_model_id = "llama-3.3-70b-versatile"
if 'groq_available' not in st.session_state:
    st.session_state.groq_available = False
if 'api_error' not in st.session_state:
    st.session_state.api_error = None
if 'api_checked' not in st.session_state:
    st.session_state.api_checked = False
if 'template_clicked' not in st.session_state:
    st.session_state.template_clicked = False

# ========== API CONNECTION CHECK - ONLY ONCE ==========
def check_api_connection():
    if st.session_state.api_checked:
        return st.session_state.groq_available
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": "OK"}],
            "max_tokens": 5
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            st.session_state.groq_available = True
            st.session_state.api_error = None
        else:
            st.session_state.groq_available = False
            st.session_state.api_error = f"API Error: {response.status_code}"
            
    except Exception as e:
        st.session_state.groq_available = False
        st.session_state.api_error = str(e)
    
    st.session_state.api_checked = True
    return st.session_state.groq_available

# ========== API CALL FUNCTION ==========
def call_groq_api(prompt, model="llama-3.3-70b-versatile"):
    try:
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
                    "content": "You are a professional email assistant with expertise in business communication, grammar, and writing styles."
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
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "❌ Invalid API Key! Please check your GROQ_API_KEY in Secrets."
        elif response.status_code == 429:
            return "❌ Rate limit exceeded! Please wait a moment and try again."
        else:
            return f"❌ API Error: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "❌ Request timeout! Please try again."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ========== FIX: generate_with_groq WITH PROPER PROMPT ==========
def generate_with_groq(prompt):
    """Generate response using Groq API"""
    if not st.session_state.groq_available:
        return "❌ API not connected. Please check your GROQ_API_KEY in Secrets."
    
    model_to_use = st.session_state.get('selected_model_id', 'llama-3.3-70b-versatile')
    
    # ========== FIX: Make sure prompt is properly formatted ==========
    if not prompt or not prompt.strip():
        return "❌ Please provide a valid prompt."
    
    return call_groq_api(prompt, model_to_use)

# ========== CHECK API CONNECTION ==========
is_connected = check_api_connection()

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")
    
    st.markdown("### 🤖 Model Selection")
    
    model_options = {
        "Llama 3.3 70B (Best Quality)": "llama-3.3-70b-versatile",
        "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant",
        "Llama 3 70B": "llama3-70b-8192",
        "Llama 3 8B (Fastest)": "llama3-8b-8192",
        "Gemma 2 9B": "gemma2-9b-it"
    }
    
    selected_model_name = st.selectbox(
        "Choose AI Model:",
        list(model_options.keys()),
        key="model_select"
    )
    st.session_state.selected_model_id = model_options[selected_model_name]
    
    st.markdown("---")
    
    st.markdown("### ✉️ Email Settings")
    sender_name = st.text_input("Your Name", placeholder="e.g., John Doe")
    default_tone = st.selectbox("Default Tone", ["Professional", "Formal", "Friendly", "Polite", "Confident", "Apologetic", "Persuasive"])
    
    st.markdown("---")
    
    st.markdown("### 🔑 API Status")
    if is_connected:
        st.success("✅ Connected to Groq API")
        st.caption(f"Key: {GROQ_API_KEY[:8]}...{GROQ_API_KEY[-4:]}")
        st.caption(f"Model: {selected_model_name}")
    else:
        st.error("❌ API Not Connected")
        if st.session_state.api_error:
            st.caption(f"Error: {st.session_state.api_error}")
        st.caption("Check your GROQ_API_KEY in Secrets")
    
    st.markdown("---")
    
    st.markdown("### 📝 Quick Templates")
    
    templates = {
        "📧 Job Application": """Subject: Application for Position

Dear Hiring Manager,

I am writing to apply for the position at your company. With my experience and skills, I believe I would be a valuable addition to your team.

Best regards,
[Your Name]""",
        "🏖️ Leave Request": """Subject: Leave Request

Dear Manager,

I am writing to request leave from [start date] to [end date]. Please approve my request.

Regards,
[Your Name]""",
        "📄 Business Proposal": """Subject: Business Proposal

Dear [Name],

I hope this email finds you well. I am writing to propose a collaboration between our companies.

Best regards,
[Your Name]"""
    }
    
    for name, content in templates.items():
        if st.button(name, use_container_width=True):
            st.session_state.email_content = content
            st.session_state.template_clicked = True
            st.rerun()

# ========== MAIN CONTENT ==========
st.markdown("# ✉️ AI Email Assistant Pro")
st.markdown("Write, improve, and reply to emails professionally using AI")

if not is_connected:
    st.warning("""
    ⚠️ **API Not Connected**
    
    Please check your `GROQ_API_KEY` in Streamlit Cloud Secrets.
    
    1. Go to App Settings → Secrets
    2. Verify key is correct: `GROQ_API_KEY = "gsk_..."`
    3. Save and Reboot
    """)

# ========== TABS ==========
t1, t2, t3, t4, t5 = st.tabs(["📝 Write & Reply", "🔧 Grammar", "🎭 Tone", "📏 Length", "📌 More"])

# ========== TAB 1: Write & Reply ==========
with t1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Input Email")
        
        input_method = st.radio("Choose:", ["📋 Paste Email", "✍️ Write New"], horizontal=True)
        
        if input_method == "📋 Paste Email":
            email_input = st.text_area(
                "Paste your email:",
                height=250,
                placeholder="Paste the email content here...",
                key="tab1_paste",
                value=st.session_state.email_content if st.session_state.template_clicked else ""
            )
        else:
            email_input = st.text_area(
                "Write your email:",
                height=250,
                placeholder="Write your email content here...",
                key="tab1_write",
                value=st.session_state.email_content if st.session_state.template_clicked else ""
            )
        
        reply_type = st.selectbox(
            "Reply Type:",
            ["general", "accept_meeting", "decline_politely", "request_info", "thank_you", "follow_up"],
            key="tab1_reply"
        )
        
        # ========== FIX: Generate Reply Button with Debug ==========
        if st.button("🚀 Generate Reply", use_container_width=True, type="primary"):
            if not email_input.strip():
                st.warning("⚠️ Please enter or paste an email first!")
            else:
                if not is_connected:
                    st.error("❌ API not connected. Please check your GROQ_API_KEY in Secrets.")
                else:
                    with st.spinner(f"Generating reply with {selected_model_name}..."):
                        # ========== FIX: Proper prompt building ==========
                        prompt = f"""Generate a professional {reply_type} reply for the following email.

Original Email:
{email_input}

Instructions:
- Reply type: {reply_type}
- Keep it professional and concise
- Be polite and respectful
- Include appropriate subject line

Reply:"""
                        
                        result = generate_with_groq(prompt)
                        
                        # Check if result is error
                        if result.startswith("❌"):
                            st.error(result)
                        else:
                            st.session_state.generated_email = result
                            st.session_state.current_action = "reply"
                            st.rerun()
    
    with col2:
        st.markdown("### 📤 Generated Reply")
        if st.session_state.generated_email and st.session_state.current_action == "reply":
            st.markdown("---")
            st.markdown(st.session_state.generated_email)
            st.markdown("---")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("📋 Copy", use_container_width=True):
                    try:
                        import pyperclip
                        pyperclip.copy(st.session_state.generated_email)
                        st.success("✅ Copied!")
                    except:
                        st.error("Copy not available")
            with col_b:
                st.download_button(
                    label="📄 TXT",
                    data=st.session_state.generated_email,
                    file_name=f"email_reply_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
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
                        file_name=f"email_reply_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except:
                    st.button("📑 PDF", disabled=True, use_container_width=True)
        else:
            st.info("👈 Generate a reply to see it here")

# ========== TAB 2: Grammar ==========
with t2:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔧 Email to Correct")
        grammar_input = st.text_area(
            "Paste email with errors:",
            height=250,
            placeholder="Paste email with grammar, spelling, or punctuation errors...",
            key="tab2_input"
        )
        
        if st.button("✅ Correct Grammar", use_container_width=True, type="primary"):
            if not grammar_input.strip():
                st.warning("⚠️ Please enter an email!")
            else:
                if not is_connected:
                    st.error("❌ API not connected. Please check your GROQ_API_KEY in Secrets.")
                else:
                    with st.spinner(f"Correcting grammar with {selected_model_name}..."):
                        prompt = f"Fix all grammar, spelling, and punctuation errors in this email. Return only the corrected version:\n\n{grammar_input}"
                        result = generate_with_groq(prompt)
                        if result.startswith("❌"):
                            st.error(result)
                        else:
                            st.session_state.generated_email = result
                            st.session_state.current_action = "grammar"
                            st.rerun()
    
    with col2:
        st.markdown("### 📤 Corrected Email")
        if st.session_state.generated_email and st.session_state.current_action == "grammar":
            st.markdown("---")
            st.markdown(st.session_state.generated_email)
            st.markdown("---")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("📋 Copy", use_container_width=True):
                    try:
                        import pyperclip
                        pyperclip.copy(st.session_state.generated_email)
                        st.success("✅ Copied!")
                    except:
                        st.error("Copy not available")
            with col_b:
                st.download_button(label="📄 TXT", data=st.session_state.generated_email, file_name=f"corrected_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", mime="text/plain", use_container_width=True)
            with col_c:
                try:
                    from src.utils.pdf_export import create_pdf
                    pdf_data = create_pdf(st.session_state.generated_email)
                    st.download_button(label="📑 PDF", data=pdf_data, file_name=f"corrected_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf", use_container_width=True)
                except:
                    st.button("📑 PDF", disabled=True, use_container_width=True)
        else:
            st.info("👈 Correct grammar to see it here")

# ========== TAB 3: Tone ==========
with t3:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎭 Email to Transform")
        tone_input = st.text_area(
            "Paste email:",
            height=200,
            placeholder="Paste email to change tone...",
            key="tab3_input"
        )
        
        tone_options = ["Professional", "Formal", "Friendly", "Polite", "Confident", "Apologetic", "Persuasive"]
        selected_tone = st.selectbox("Select Tone:", tone_options, key="tab3_tone")
        
        if st.button("🎭 Change Tone", use_container_width=True, type="primary"):
            if not tone_input.strip():
                st.warning("⚠️ Please enter an email!")
            else:
                if not is_connected:
                    st.error("❌ API not connected. Please check your GROQ_API_KEY in Secrets.")
                else:
                    with st.spinner(f"Changing tone with {selected_model_name}..."):
                        prompt = f"Rewrite this email in a {selected_tone} tone. Keep the core message but adjust the language:\n\n{tone_input}"
                        result = generate_with_groq(prompt)
                        if result.startswith("❌"):
                            st.error(result)
                        else:
                            st.session_state.generated_email = result
                            st.session_state.current_action = "tone"
                            st.rerun()
    
    with col2:
        st.markdown("### 📤 Transformed Email")
        if st.session_state.generated_email and st.session_state.current_action == "tone":
            st.markdown("---")
            st.markdown(st.session_state.generated_email)
            st.markdown("---")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("📋 Copy", use_container_width=True):
                    try:
                        import pyperclip
                        pyperclip.copy(st.session_state.generated_email)
                        st.success("✅ Copied!")
                    except:
                        st.error("Copy not available")
            with col_b:
                st.download_button(label="📄 TXT", data=st.session_state.generated_email, file_name=f"tone_changed_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", mime="text/plain", use_container_width=True)
            with col_c:
                try:
                    from src.utils.pdf_export import create_pdf
                    pdf_data = create_pdf(st.session_state.generated_email)
                    st.download_button(label="📑 PDF", data=pdf_data, file_name=f"tone_changed_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf", use_container_width=True)
                except:
                    st.button("📑 PDF", disabled=True, use_container_width=True)
        else:
            st.info("👈 Change tone to see it here")

# ========== TAB 4: Length ==========
with t4:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📏 Email to Adjust")
        length_input = st.text_area(
            "Paste email:",
            height=200,
            placeholder="Paste email to adjust length...",
            key="tab4_input"
        )
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("📏 Short", use_container_width=True):
                if not length_input.strip():
                    st.warning("⚠️ Please enter an email!")
                else:
                    if not is_connected:
                        st.error("❌ API not connected. Please check your GROQ_API_KEY in Secrets.")
                    else:
                        with st.spinner(f"Shortening with {selected_model_name}..."):
                            prompt = f"Create a short, concise version of this email. Keep only the essential information:\n\n{length_input}"
                            result = generate_with_groq(prompt)
                            if result.startswith("❌"):
                                st.error(result)
                            else:
                                st.session_state.generated_email = result
                                st.session_state.current_action = "shorten"
                                st.rerun()
        with col_b:
            if st.button("📐 Medium", use_container_width=True):
                if not length_input.strip():
                    st.warning("⚠️ Please enter an email!")
                else:
                    if not is_connected:
                        st.error("❌ API not connected. Please check your GROQ_API_KEY in Secrets.")
                    else:
                        with st.spinner(f"Creating medium version with {selected_model_name}..."):
                            prompt = f"Create a medium-length version of this email. Keep it balanced (about 60-70% of original):\n\n{length_input}"
                            result = generate_with_groq(prompt)
                            if result.startswith("❌"):
                                st.error(result)
                            else:
                                st.session_state.generated_email = result
                                st.session_state.current_action = "medium"
                                st.rerun()
        with col_c:
            if st.button("📑 Detailed", use_container_width=True):
                if not length_input.strip():
                    st.warning("⚠️ Please enter an email!")
                else:
                    if not is_connected:
                        st.error("❌ API not connected. Please check your GROQ_API_KEY in Secrets.")
                    else:
                        with st.spinner(f"Expanding with {selected_model_name}..."):
                            prompt = f"Create a detailed, expanded version of this email. Add relevant details and explanations:\n\n{length_input}"
                            result = generate_with_groq(prompt)
                            if result.startswith("❌"):
                                st.error(result)
                            else:
                                st.session_state.generated_email = result
                                st.session_state.current_action = "expand"
                                st.rerun()
    
    with col2:
        st.markdown("### 📤 Adjusted Email")
        if st.session_state.generated_email and st.session_state.current_action in ["shorten", "medium", "expand"]:
            st.markdown("---")
            st.markdown(st.session_state.generated_email)
            st.markdown("---")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("📋 Copy", use_container_width=True):
                    try:
                        import pyperclip
                        pyperclip.copy(st.session_state.generated_email)
                        st.success("✅ Copied!")
                    except:
                        st.error("Copy not available")
            with col_b:
                st.download_button(label="📄 TXT", data=st.session_state.generated_email, file_name=f"length_adjusted_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", mime="text/plain", use_container_width=True)
            with col_c:
                try:
                    from src.utils.pdf_export import create_pdf
                    pdf_data = create_pdf(st.session_state.generated_email)
                    st.download_button(label="📑 PDF", data=pdf_data, file_name=f"length_adjusted_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf", use_container_width=True)
                except:
                    st.button("📑 PDF", disabled=True, use_container_width=True)
        else:
            st.info("👈 Adjust length to see it here")

# ========== TAB 5: More ==========
with t5:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📌 Subject Lines")
        subject_input = st.text_area("Email for subjects:", height=150, placeholder="Paste email...", key="tab5_subject")
        if st.button("📌 Generate Subject Lines", use_container_width=True):
            if not subject_input.strip():
                st.warning("⚠️ Please enter an email!")
            else:
                if not is_connected:
                    st.error("❌ API not connected. Please check your GROQ_API_KEY in Secrets.")
                else:
                    with st.spinner(f"Generating subjects with {selected_model_name}..."):
                        prompt = f"Generate 5 professional subject lines for this email:\n\n{subject_input}"
                        result = generate_with_groq(prompt)
                        if result.startswith("❌"):
                            st.error(result)
                        else:
                            st.session_state.generated_email = result
                            st.session_state.current_action = "subject"
                            st.rerun()
        
        st.markdown("---")
        st.markdown("### 💡 Improvement Tips")
        tips_input = st.text_area("Email for tips:", height=150, placeholder="Paste email...", key="tab5_tips")
        if st.button("💡 Get Improvement Tips", use_container_width=True):
            if not tips_input.strip():
                st.warning("⚠️ Please enter an email!")
            else:
                if not is_connected:
                    st.error("❌ API not connected. Please check your GROQ_API_KEY in Secrets.")
                else:
                    with st.spinner(f"Generating tips with {selected_model_name}..."):
                        prompt = f"Provide improvement suggestions for this email including grammar, readability, tone, and professional wording:\n\n{tips_input}"
                        result = generate_with_groq(prompt)
                        if result.startswith("❌"):
                            st.error(result)
                        else:
                            st.session_state.generated_email = result
                            st.session_state.current_action = "tips"
                            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🌐 Translate")
        translate_input = st.text_area("Email to translate:", height=100, placeholder="Paste email...", key="tab5_translate")
        lang = st.selectbox("Language:", ["Spanish", "French", "German", "Chinese", "Japanese", "Arabic", "Hindi", "Portuguese", "Russian", "Italian"])
        if st.button("🌐 Translate Email", use_container_width=True):
            if not translate_input.strip():
                st.warning("⚠️ Please enter an email!")
            else:
                if not is_connected:
                    st.error("❌ API not connected. Please check your GROQ_API_KEY in Secrets.")
                else:
                    with st.spinner(f"Translating with {selected_model_name}..."):
                        prompt = f"Translate this email to {lang}:\n\n{translate_input}"
                        result = generate_with_groq(prompt)
                        if result.startswith("❌"):
                            st.error(result)
                        else:
                            st.session_state.generated_email = result
                            st.session_state.current_action = "translate"
                            st.rerun()
    
    with col2:
        st.markdown("### 📤 Output")
        if st.session_state.generated_email and st.session_state.current_action in ["subject", "tips", "translate"]:
            st.markdown("---")
            st.markdown(st.session_state.generated_email)
            st.markdown("---")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("📋 Copy", use_container_width=True):
                    try:
                        import pyperclip
                        pyperclip.copy(st.session_state.generated_email)
                        st.success("✅ Copied!")
                    except:
                        st.error("Copy not available")
            with col_b:
                st.download_button(label="📄 TXT", data=st.session_state.generated_email, file_name=f"output_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", mime="text/plain", use_container_width=True)
            with col_c:
                try:
                    from src.utils.pdf_export import create_pdf
                    pdf_data = create_pdf(st.session_state.generated_email)
                    st.download_button(label="📑 PDF", data=pdf_data, file_name=f"output_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf", use_container_width=True)
                except:
                    st.button("📑 PDF", disabled=True, use_container_width=True)
        else:
            st.info("👈 Use features to see output here")

# ========== FOOTER ==========
st.divider()
st.caption(f"✉️ AI Email Assistant Pro | Powered by Groq API | Model: {selected_model_name}")

with st.expander("ℹ️ System Status"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Groq API", "✅ Connected" if is_connected else "❌ Disconnected")
    with c2:
        st.metric("Model", selected_model_name)
    with c3:
        st.metric("PDF Export", "✅ Available
