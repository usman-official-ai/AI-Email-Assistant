import streamlit as st
import os
import time
import json
from datetime import datetime
from io import BytesIO
import requests
import pyperclip

# ========== SESSION STATE ==========
if 'email_input' not in st.session_state:
    st.session_state.email_input = ""
if 'generated_email' not in st.session_state:
    st.session_state.generated_email = ""
if 'current_action' not in st.session_state:
    st.session_state.current_action = ""
if 'selected_model_id' not in st.session_state:
    st.session_state.selected_model_id = "llama-3.1-8b-instant"
if 'groq_available' not in st.session_state:
    st.session_state.groq_available = False
if 'api_checked' not in st.session_state:
    st.session_state.api_checked = False
if 'email_history' not in st.session_state:
    st.session_state.email_history = []
if 'api_call_count' not in st.session_state:
    st.session_state.api_call_count = 0
if 'last_api_call' not in st.session_state:
    st.session_state.last_api_call = 0
if 'copy_success' not in st.session_state:
    st.session_state.copy_success = False

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
    """)
    st.stop()

st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="📧",
    layout="wide"
)

# ========== DARK THEME ==========
st.markdown("""
<style>
.stApp { background: #0a0a0f; }
.stSidebar { background: #111118; border-right: 1px solid #1a1a2e; }
h1, h2, h3, h4, h5, h6, .stTitle, .stHeader, .stSubheader { color: #ffffff !important; }
.stApp, .stMarkdown, .stText, .stCaption, .stInfo, .stSuccess, .stWarning, .stError,
.stTextInput > label, .stSelectbox > label, .stTextArea > label,
.stRadio > label, .stCheckbox > label { color: #ffffff !important; }
.stSidebar .stMarkdown, .stSidebar .stText, .stSidebar label { color: #ffffff !important; }
.stTextInput > div > div > input {
    background: #1a1a2e !important; color: #ffffff !important;
    border: 1px solid #2a2a44 !important; border-radius: 12px !important;
    padding: 14px 18px !important;
}
.stTextArea > div > div > textarea {
    background: #1a1a2e !important; color: #ffffff !important;
    border: 1px solid #2a2a44 !important; border-radius: 12px !important;
}
.stSelectbox > div > div > select {
    background: #1a1a2e !important; color: #ffffff !important;
    border: 1px solid #2a2a44 !important; border-radius: 12px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; padding: 12px 28px !important;
    font-weight: 600 !important; box-shadow: 0 4px 20px rgba(255, 75, 75, 0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 30px rgba(255, 75, 75, 0.35) !important;
}
.stDownloadButton > button {
    background: #1a1a2e !important; color: white !important;
    border: 1px solid #2a2a44 !important; border-radius: 10px !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #111118 !important; border-radius: 12px !important;
    padding: 4px !important; border: 1px solid #1a1a2e !important;
}
.stTabs [data-baseweb="tab"] { color: #8899aa !important; border-radius: 8px !important; padding: 10px 20px !important; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b) !important;
    color: #ffffff !important;
}
.stExpander { background: #111118 !important; border: 1px solid #1a1a2e !important; border-radius: 12px !important; }
.stMetric { background: #111118 !important; border-radius: 12px !important; padding: 14px !important; border: 1px solid #1a1a2e !important; }
.stMetric label { color: #8899aa !important; }
.stMetric .stMarkdown { color: #ffffff !important; }
hr { border-color: #1a1a2e !important; }
.stCaption { color: #555 !important; }
.stInfo { background: rgba(255,255,255,0.03) !important; border: 1px solid #1a1a2e !important; border-radius: 12px !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a44; border-radius: 4px; }
.output-box { background: #111118; border: 1px solid #1a1a2e; border-radius: 12px; padding: 20px; margin: 10px 0; }
.stAlert { background: rgba(255,255,255,0.03) !important; border: 1px solid #1a1a2e !important; }
</style>
""", unsafe_allow_html=True)

# ========== API SETUP ==========
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
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": "OK"}],
            "max_tokens": 5
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            st.session_state.groq_available = True
        else:
            st.session_state.groq_available = False
            
    except Exception as e:
        st.session_state.groq_available = False
    
    st.session_state.api_checked = True
    return st.session_state.groq_available

def call_groq_api(prompt, model="llama-3.1-8b-instant"):
    # ========== RATE LIMIT PROTECTION ==========
    current_time = time.time()
    if current_time - st.session_state.last_api_call < 3:
        st.warning("⏳ Please wait a few seconds between requests.")
        return None
    
    if st.session_state.api_call_count > 30:
        st.warning("⚠️ Too many API calls. Please refresh the app.")
        return None
    
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
        
        st.session_state.last_api_call = time.time()
        st.session_state.api_call_count += 1
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        elif response.status_code == 429:
            return "❌ Rate limit exceeded! Please wait 5-10 minutes."
        elif response.status_code == 401:
            return "❌ Invalid API Key! Please check your GROQ_API_KEY."
        else:
            return f"❌ API Error: {response.status_code}"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

def generate_with_groq(prompt):
    if not st.session_state.groq_available:
        return "❌ API not connected. Please check your GROQ_API_KEY."
    
    model_to_use = st.session_state.get('selected_model_id', 'llama-3.1-8b-instant')
    
    if not prompt or not prompt.strip():
        return "❌ Please provide a valid prompt."
    
    return call_groq_api(prompt, model_to_use)

is_connected = check_api_connection()

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("# 📧 AI Email Assistant")
    st.caption("Write, reply, correct, and polish your emails.")
    
    st.divider()
    
    st.markdown("### 🤖 Model")
    model_options = {
        "Llama 3.3 70B (Best)": "llama-3.3-70b-versatile",
        "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant",
        "Gemma 2 9B": "gemma2-9b-it"
    }
    
    selected_model_name = st.selectbox(
        "Choose AI Model:",
        list(model_options.keys()),
        key="model_select"
    )
    st.session_state.selected_model_id = model_options[selected_model_name]
    
    st.divider()
    
    # ========== TEMPLATES ==========
    st.markdown("### 📝 Templates")
    
    templates = {
        "📧 Job": """Subject: Application for Position

Dear Hiring Manager,

I am writing to apply for the position at your company. With my experience and skills, I believe I would be a valuable addition to your team.

Best regards,
[Your Name]""",
        "🏖️ Leave": """Subject: Leave Request

Dear Manager,

I am writing to request leave from [start date] to [end date]. Please approve my request.

Regards,
[Your Name]""",
        "📄 Proposal": """Subject: Business Proposal

Dear [Name],

I hope this email finds you well. I am writing to propose a collaboration between our companies.

Best regards,
[Your Name]""",
        "🙏 Thank You": """Subject: Thank You

Dear [Name],

I wanted to express my sincere gratitude for your support and guidance.

Thank you once again.

Best regards,
[Your Name]""",
        "👋 Follow-up": """Subject: Follow-up

Dear [Name],

I hope this email finds you well. I am writing to follow up on our previous conversation.

Looking forward to your response.

Best regards,
[Your Name]"""
    }
    
    for name, content in templates.items():
        if st.button(name, use_container_width=True):
            st.session_state.email_input = content
            st.rerun()
    
    st.divider()
    
    # ========== HISTORY ==========
    st.markdown("### 📜 Email History")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.email_history = []
        st.rerun()
    
    if st.session_state.email_history:
        st.caption(f"📊 {len(st.session_state.email_history)} entries")
        for entry in st.session_state.email_history[-5:]:
            st.caption(f"🕐 {entry['timestamp']} - {entry['action']}")
    
    st.divider()
    
    st.markdown("### 🔑 API Status")
    if is_connected:
        st.success("✅ Connected")
        st.caption(f"Calls: {st.session_state.api_call_count}")
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
    # ========== WRITE MODE ==========
    if mode == "Write a new email":
        st.markdown("### ✍️ What's the email about?")
        input_text = st.text_area(
            "Describe the topic, purpose, or bullet points for your email",
            height=150,
            placeholder="e.g. Ask my manager for 2 days of leave next week for a family event...",
            key="input_new",
            value=st.session_state.email_input if st.session_state.email_input else ""
        )

        col_tone, col_length = st.columns(2)
        with col_tone:
            tone = st.selectbox("Tone", ["Professional", "Friendly", "Formal", "Casual", "Persuasive", "Confident", "Apologetic"], index=0)
        with col_length:
            length = st.selectbox("Length", ["Short", "Medium", "Detailed"], index=1)

        if st.button("✨ Generate Email", type="primary", use_container_width=True):
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
                    result = generate_with_groq(prompt)
                    if result and not result.startswith("❌"):
                        st.session_state.generated_email = result
                        st.session_state.current_action = "write"
                        st.session_state.email_history.insert(0, {
                            "timestamp": datetime.now().strftime("%H:%M"),
                            "action": "Write Email",
                            "content": result[:100] + "..."
                        })
                        st.rerun()
                    elif result:
                        st.error(result)

    # ========== REPLY MODE ==========
    elif mode == "Reply to an email":
        st.markdown("### 📨 Paste the email you're replying to")
        input_text = st.text_area(
            "Original email",
            height=150,
            placeholder="Paste the email you received here...",
            key="input_reply",
            value=st.session_state.email_input if st.session_state.email_input else ""
        )

        reply_type = st.selectbox(
            "Reply type",
            ["General", "Accept Meeting", "Decline Politely", "Request More Info", "Thank You", "Follow-up"],
            index=0
        )

        col_tone, col_length = st.columns(2)
        with col_tone:
            tone = st.selectbox("Tone", ["Professional", "Friendly", "Formal", "Casual", "Persuasive", "Confident", "Apologetic"], index=0, key="reply_tone")
        with col_length:
            length = st.selectbox("Length", ["Short", "Medium", "Detailed"], index=1, key="reply_length")

        if st.button("↩️ Generate Reply", type="primary", use_container_width=True):
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
                    result = generate_with_groq(prompt)
                    if result and not result.startswith("❌"):
                        st.session_state.generated_email = result
                        st.session_state.current_action = "reply"
                        st.session_state.email_history.insert(0, {
                            "timestamp": datetime.now().strftime("%H:%M"),
                            "action": f"Reply ({reply_type})",
                            "content": result[:100] + "..."
                        })
                        st.rerun()
                    elif result:
                        st.error(result)

    # ========== IMPROVE MODE ==========
    else:
        st.markdown("### 🛠️ Paste the email you want to improve")
        input_text = st.text_area(
            "Your email draft",
            height=150,
            placeholder="Paste your draft email here...",
            key="input_edit",
            value=st.session_state.email_input if st.session_state.email_input else ""
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
                        result = generate_with_groq(prompt)
                        if result and not result.startswith("❌"):
                            st.session_state.generated_email = result
                            st.session_state.current_action = "grammar"
                            st.session_state.email_history.insert(0, {
                                "timestamp": datetime.now().strftime("%H:%M"),
                                "action": "Grammar Fix",
                                "content": result[:100] + "..."
                            })
                            st.rerun()
                        elif result:
                            st.error(result)
        
        with col2:
            if st.button("🎭 Change Tone", use_container_width=True):
                if not input_text.strip():
                    st.warning("Please paste an email first.")
                else:
                    with st.spinner("Changing tone..."):
                        prompt = f"Rewrite this email in a professional tone. Keep the core message but adjust the language:\n\n{input_text}"
                        result = generate_with_groq(prompt)
                        if result and not result.startswith("❌"):
                            st.session_state.generated_email = result
                            st.session_state.current_action = "tone"
                            st.session_state.email_history.insert(0, {
                                "timestamp": datetime.now().strftime("%H:%M"),
                                "action": "Tone Change",
                                "content": result[:100] + "..."
                            })
                            st.rerun()
                        elif result:
                            st.error(result)
        
        with col3:
            if st.button("📏 Adjust Length", use_container_width=True):
                if not input_text.strip():
                    st.warning("Please paste an email first.")
                else:
                    with st.spinner("Adjusting length..."):
                        prompt = f"Create a medium-length version of this email. Keep it balanced (about 60-70% of original):\n\n{input_text}"
                        result = generate_with_groq(prompt)
                        if result and not result.startswith("❌"):
                            st.session_state.generated_email = result
                            st.session_state.current_action = "medium"
                            st.session_state.email_history.insert(0, {
                                "timestamp": datetime.now().strftime("%H:%M"),
                                "action": "Medium Length",
                                "content": result[:100] + "..."
                            })
                            st.rerun()
                        elif result:
                            st.error(result)
        
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
                        result = generate_with_groq(prompt)
                        if result and not result.startswith("❌"):
                            st.session_state.generated_email = result
                            st.session_state.current_action = "suggest"
                            st.session_state.email_history.insert(0, {
                                "timestamp": datetime.now().strftime("%H:%M"),
                                "action": "Suggestions",
                                "content": result[:100] + "..."
                            })
                            st.rerun()
                        elif result:
                            st.error(result)
    
    # ========== ADDITIONAL FEATURES ==========
    st.divider()
    
    # ========== SUBJECT LINE GENERATOR ==========
    st.markdown("### 🏷️ Subject Line Generator")
    if st.button("Generate Subject Lines (3-5)", use_container_width=True):
        source_text = st.session_state.generated_email or input_text if 'input_text' in locals() else ""
        if not source_text.strip():
            st.warning("Generate or paste an email first.")
        else:
            with st.spinner("Generating subject lines..."):
                prompt = f"Generate 5 professional subject lines for this email. Return only the subject lines, one per line:\n\n{source_text}"
                result = generate_with_groq(prompt)
                if result and not result.startswith("❌"):
                    st.session_state.generated_email = result
                    st.session_state.current_action = "subject"
                    st.session_state.email_history.insert(0, {
                        "timestamp": datetime.now().strftime("%H:%M"),
                        "action": "Subject Lines",
                        "content": result[:100] + "..."
                    })
                    st.rerun()
                elif result:
                    st.error(result)
    
    # ========== TRANSLATION ==========
    st.markdown("### 🌐 Translate Email")
    col_trans1, col_trans2 = st.columns([2, 1])
    with col_trans1:
        translate_input = st.text_area(
            "Email to translate:",
            height=80,
            placeholder="Paste email to translate...",
            key="translate_input"
        )
    with col_trans2:
        lang = st.selectbox(
            "Language:",
            ["Spanish", "French", "German", "Chinese", "Japanese", "Arabic", "Hindi", "Portuguese", "Russian", "Italian"],
            key="lang_select"
        )
        if st.button("🌐 Translate", use_container_width=True):
            if not translate_input.strip():
                st.warning("Please paste an email to translate.")
            else:
                with st.spinner(f"Translating to {lang}..."):
                    prompt = f"Translate this email to {lang}. Maintain the professional tone and meaning:\n\n{translate_input}"
                    result = generate_with_groq(prompt)
                    if result and not result.startswith("❌"):
                        st.session_state.generated_email = result
                        st.session_state.current_action = "translate"
                        st.session_state.email_history.insert(0, {
                            "timestamp": datetime.now().strftime("%H:%M"),
                            "action": f"Translation ({lang})",
                            "content": result[:100] + "..."
                        })
                        st.rerun()
                    elif result:
                        st.error(result)
    
    # ========== SENTIMENT ANALYSIS ==========
    st.markdown("### 📊 Sentiment Analysis")
    sentiment_input = st.text_area(
        "Email to analyze:",
        height=80,
        placeholder="Paste email to analyze sentiment...",
        key="sentiment_input"
    )
    if st.button("📊 Analyze Sentiment", use_container_width=True):
        if not sentiment_input.strip():
            st.warning("Please paste an email to analyze.")
        else:
            with st.spinner("Analyzing sentiment..."):
                prompt = f"""Analyze the sentiment of this email and provide:
1. Overall sentiment (Positive/Negative/Neutral)
2. Emotional tone
3. Key emotional indicators
4. Suggested response approach

Email:
{sentiment_input}

Sentiment Analysis:"""
                result = generate_with_groq(prompt)
                if result and not result.startswith("❌"):
                    st.session_state.generated_email = result
                    st.session_state.current_action = "sentiment"
                    st.session_state.email_history.insert(0, {
                        "timestamp": datetime.now().strftime("%H:%M"),
                        "action": "Sentiment Analysis",
                        "content": result[:100] + "..."
                    })
                    st.rerun()
                elif result:
                    st.error(result)

with right:
    st.markdown("### 📤 Output")
    
    if st.session_state.generated_email:
        st.markdown('<div class="output-box">', unsafe_allow_html=True)
        st.markdown(st.session_state.generated_email)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns(3)
        
        # ========== COPY BUTTON ==========
        with col_a:
            if st.button("📋 Copy", use_container_width=True):
                try:
                    pyperclip.copy(st.session_state.generated_email)
                    st.success("✅ Copied to clipboard!")
                except Exception as e:
                    st.warning("⚠️ Copy not available. Please select and copy manually.")
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
            st.session_state.current_action = ""
            st.rerun()
    else:
        st.info("Your generated or improved email will appear here.")

# ========== FOOTER ==========
st.divider()
st.caption("⚠️ Always review AI-generated content before sending. This tool assists — it doesn't replace your judgment.")
