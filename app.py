"""
app.py
--------
AI Email Assistant — Streamlit frontend.
Lets users write, reply, correct, and polish emails using Google Gemini + Groq.
"""

import streamlit as st
import streamlit.components.v1 as components

import email_utils
import prompts
from pdf_export import export_to_pdf

# ---------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="AI Email Assistant Pro",
    page_icon="📧",
    layout="wide",
)

# ========== CUSTOM CSS - PROFESSIONAL DARK THEME ==========
st.markdown("""
<style>
/* MAIN BACKGROUND */
.stApp { background: #0e1117; }
.stSidebar { background: #1a1a2e; }

/* ALL TEXT WHITE */
.stApp, .stApp viewport, .stApp .main,
.stMarkdown, .stText, .stCaption, .stInfo, .stSuccess, .stWarning, .stError,
.stTextInput > label, .stSelectbox > label, .stTextArea > label,
.stRadio > label, .stCheckbox > label, .stNumberInput > label,
.stSlider > label, .stDateInput > label, .stTimeInput > label,
.stMultiSelect > label, .stFileUploader > label,
h1, h2, h3, h4, h5, h6, .stTitle, .stHeader, .stSubheader {
    color: #ffffff !important;
}

/* SIDEBAR TEXT */
.stSidebar .stMarkdown, .stSidebar .stText, 
.stSidebar label, .stSidebar h1, .stSidebar h2, .stSidebar h3, 
.stSidebar h4, .stSidebar .stCaption, .stSidebar p,
.stSidebar .stTextInput > label, .stSidebar .stSelectbox > label,
.stSidebar .stRadio > label, .stSidebar .stCheckbox > label {
    color: #ffffff !important;
}

/* INPUT FIELDS */
.stTextInput > div > div > input {
    background: #2d2d44 !important;
    color: #ffffff !important;
    border: 1px solid #444 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
}
.stTextInput > div > div > input::placeholder {
    color: #888 !important;
}
.stTextArea > div > div > textarea {
    background: #2d2d44 !important;
    color: #ffffff !important;
    border: 1px solid #444 !important;
    border-radius: 10px !important;
}
.stTextArea > div > div > textarea::placeholder {
    color: #888 !important;
}
.stSelectbox > div > div > select {
    background: #2d2d44 !important;
    color: #ffffff !important;
    border: 1px solid #444 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
}
.stSelectbox > div > div > select option {
    background: #2d2d44 !important;
    color: #ffffff !important;
}
.stRadio > div > label {
    color: #ffffff !important;
}
.stRadio > div > label > div > p {
    color: #ffffff !important;
}
.stCheckbox > label {
    color: #ffffff !important;
}

/* BUTTONS - PRIMARY */
.stButton > button {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255, 75, 75, 0.4) !important;
}

/* DOWNLOAD BUTTONS */
.stDownloadButton > button {
    background: linear-gradient(135deg, #2d6a4f, #40916c) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 15px rgba(45, 106, 79, 0.4) !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: #1a1a2e !important;
    border-radius: 12px !important;
    padding: 6px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #8899aa !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
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
.stTabs [aria-selected="true"] button {
    color: #ffffff !important;
}

/* EXPANDER */
.stExpander {
    background: #1a1a2e !important;
    border: 1px solid #333 !important;
    border-radius: 12px !important;
}
.stExpander .streamlit-expanderHeader {
    color: #ffffff !important;
    font-weight: 500 !important;
}
.stExpander .streamlit-expanderContent {
    color: #e0e0e0 !important;
}

/* METRIC */
.stMetric {
    background: #1a1a2e !important;
    border-radius: 12px !important;
    padding: 16px !important;
    border: 1px solid #333 !important;
}
.stMetric label {
    color: #ffffff !important;
    font-weight: 500 !important;
}
.stMetric .stMarkdown {
    color: #ff4b4b !important;
    font-size: 24px !important;
    font-weight: 700 !important;
}

/* DIVIDER */
hr {
    border-color: #333 !important;
    margin: 20px 0 !important;
}
.stCaption {
    color: #888 !important;
}

/* INFO/WARNING/SUCCESS/ERROR */
.stInfo {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid #444 !important;
    border-radius: 10px !important;
    padding: 16px !important;
}
.stInfo .stMarkdown {
    color: #aaaaaa !important;
}
.stSuccess {
    background: rgba(0, 200, 0, 0.1) !important;
    border: 1px solid #00cc00 !important;
    border-radius: 10px !important;
    padding: 16px !important;
}
.stSuccess .stMarkdown {
    color: #00cc00 !important;
}
.stError {
    background: rgba(255, 0, 0, 0.1) !important;
    border: 1px solid #ff4444 !important;
    border-radius: 10px !important;
    padding: 16px !important;
}
.stError .stMarkdown {
    color: #ff4444 !important;
}
.stWarning {
    background: rgba(255, 200, 0, 0.1) !important;
    border: 1px solid #ffcc00 !important;
    border-radius: 10px !important;
    padding: 16px !important;
}
.stWarning .stMarkdown {
    color: #ffcc00 !important;
}

/* SCROLLBAR */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #1a1a2e;
}
::-webkit-scrollbar-thumb {
    background: #444;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #666;
}

/* API STATUS */
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

/* OUTPUT BOX */
.output-box {
    background: #1a1a2e;
    border: 1px solid #333;
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------

if "output_text" not in st.session_state:
    st.session_state.output_text = ""
if "subject_lines" not in st.session_state:
    st.session_state.subject_lines = []
if "suggestions" not in st.session_state:
    st.session_state.suggestions = ""
if "email_content" not in st.session_state:
    st.session_state.email_content = ""

def set_output(text: str):
    st.session_state.output_text = text

# ---------------------------------------------------------------------
# Helper: JS-based copy button
# ---------------------------------------------------------------------

def copy_button(text: str, key: str):
    escaped = text.replace("\\", "\\\\").replace("`", "\\`").replace("</", "<\\/")
    components.html(
        f"""
        <button id="copy-btn-{key}" style="
            background: linear-gradient(135deg, #2563eb, #3b82f6);
            color:white;border:none;
            padding:10px 20px;border-radius:10px;cursor:pointer;
            font-size:14px;font-family:sans-serif;font-weight:600;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
            transition: all 0.3s ease;
            width:100%;
        ">
            📋 Copy to Clipboard
        </button>
        <script>
        const btn = document.getElementById("copy-btn-{key}");
        btn.addEventListener("click", () => {{
            navigator.clipboard.writeText(`{escaped}`);
            btn.innerText = "✅ Copied!";
            btn.style.background = "linear-gradient(135deg, #16a34a, #22c55e)";
            setTimeout(() => {{
                btn.innerText = "📋 Copy to Clipboard";
                btn.style.background = "linear-gradient(135deg, #2563eb, #3b82f6)";
            }}, 2000);
        }});
        </script>
        """,
        height=50,
    )

# ---------------------------------------------------------------------
# Sidebar — global settings
# ---------------------------------------------------------------------

PROVIDER_LABELS: dict[str, str] = {"gemini": "Google Gemini", "groq": "Groq"}

def _format_provider_label(p: str) -> str:
    return PROVIDER_LABELS.get(p, p)

with st.sidebar:
    st.markdown("# 📧 AI Email Assistant")
    st.caption("Powered by Google Gemini + Groq")

    st.divider()
    st.markdown("### 🤖 AI Provider")

    if not email_utils.AVAILABLE_PROVIDERS:
        st.error(
            "⚠️ No API keys found. Add GEMINI_API_KEY and/or GROQ_API_KEY to your .env file."
        )
        provider = None
    else:
        provider_options: list[str] = list(email_utils.AVAILABLE_PROVIDERS)
        default_index: int = (
            provider_options.index(email_utils.DEFAULT_PROVIDER)
            if email_utils.DEFAULT_PROVIDER in provider_options
            else 0
        )
        provider = st.selectbox(
            "Model provider",
            provider_options,
            index=default_index,
            format_func=_format_provider_label,
        )
        model_in_use = (
            email_utils.GEMINI_MODEL if provider == "gemini" else email_utils.GROQ_MODEL
        )
        st.success(f"✅ Connected — {PROVIDER_LABELS[provider]} ({model_in_use})")

        missing = [
            p for p in ["gemini", "groq"] if p not in email_utils.AVAILABLE_PROVIDERS
        ]
        if missing:
            missing_labels = ", ".join(PROVIDER_LABELS[p] for p in missing)
            st.caption(f"ℹ️ {missing_labels} not configured (missing API key).")

    st.divider()
    st.markdown("### ⚙️ Settings")

    tone = st.selectbox("Tone", prompts.AVAILABLE_TONES, index=0)
    length = st.selectbox("Length", prompts.LENGTH_OPTIONS, index=1)

    st.divider()
    
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
            st.rerun()
    
    st.divider()
    st.caption("Built with Streamlit + Gemini + Groq")

# ---------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------

st.markdown("# ✉️ AI Email Assistant Pro")
st.markdown("Write, reply, correct, and polish your emails in seconds.")

if provider is None:
    st.error(
        "No AI provider is configured yet. Add **GEMINI_API_KEY** and/or "
        "**GROQ_API_KEY** to your `.env` file (see `.env.example`), then restart the app."
    )
    st.stop()

# ========== TABS ==========
tab1, tab2, tab3 = st.tabs(["📝 Write & Reply", "🛠️ Improve Email", "📌 Subject Lines"])

# ========== TAB 1: Write & Reply ==========
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Input Email")
        
        mode = st.radio(
            "Choose mode:",
            ["Write a new email", "Reply to an email"],
            horizontal=True,
        )
        
        if mode == "Write a new email":
            st.markdown("#### ✍️ What's the email about?")
            input_text = st.text_area(
                "Describe the topic, purpose, or bullet points for your email",
                height=200,
                placeholder="e.g. Ask my manager for 2 days of leave next week for a family event...",
                key="input_new",
                value=st.session_state.email_content if st.session_state.email_content else ""
            )

            if st.button("✨ Generate Email", type="primary", use_container_width=True):
                if not input_text.strip():
                    st.warning("Please describe what the email should be about.")
                else:
                    with st.spinner("Drafting your email..."):
                        try:
                            result = email_utils.write_new_email(
                                input_text, tone, length, provider=provider
                            )
                            set_output(result)
                            st.rerun()
                        except email_utils.EmailAssistantError as e:
                            st.error(str(e))

        else:  # Reply to an email
            st.markdown("#### 📨 Paste the email you're replying to")
            input_text = st.text_area(
                "Original email",
                height=200,
                placeholder="Paste the email you received here...",
                key="input_reply",
            )

            reply_type = st.selectbox("Reply type", prompts.REPLY_TYPES)

            if st.button("↩️ Generate Reply", type="primary", use_container_width=True):
                if not input_text.strip():
                    st.warning("Please paste the original email first.")
                else:
                    with st.spinner("Writing your reply..."):
                        try:
                            result = email_utils.generate_reply(
                                input_text, reply_type, tone, length, provider=provider
                            )
                            set_output(result)
                            st.rerun()
                        except email_utils.EmailAssistantError as e:
                            st.error(str(e))
    
    with col2:
        st.markdown("### 📤 Output")
        
        if st.session_state.output_text:
            st.markdown('<div class="output-box">', unsafe_allow_html=True)
            st.text_area(
                "Generated email",
                value=st.session_state.output_text,
                height=300,
                key="output_display",
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                copy_button(st.session_state.output_text, key="output")

            with col_b:
                st.download_button(
                    label="📄 Download TXT",
                    data=st.session_state.output_text,
                    file_name="email.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            with col_c:
                try:
                    pdf_bytes = export_to_pdf(st.session_state.output_text, title="Email")
                    st.download_button(
                        label="📑 Download PDF",
                        data=pdf_bytes,
                        file_name="email.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Could not generate PDF: {e}")
            
            st.divider()
            st.markdown("#### 🔄 Refine this output:")
            r1, r2, r3 = st.columns(3)
            with r1:
                if st.button("✅ Fix Grammar", key="refine_grammar", use_container_width=True):
                    with st.spinner("Fixing grammar..."):
                        try:
                            result = email_utils.fix_grammar(
                                st.session_state.output_text, provider=provider
                            )
                            set_output(result)
                            st.rerun()
                        except email_utils.EmailAssistantError as e:
                            st.error(str(e))
            with r2:
                if st.button("🎭 Change Tone", key="refine_tone", use_container_width=True):
                    with st.spinner("Adjusting tone..."):
                        try:
                            result = email_utils.change_tone(
                                st.session_state.output_text, tone, provider=provider
                            )
                            set_output(result)
                            st.rerun()
                        except email_utils.EmailAssistantError as e:
                            st.error(str(e))
            with r3:
                if st.button("📏 Adjust Length", key="refine_length", use_container_width=True):
                    with st.spinner("Adjusting length..."):
                        try:
                            result = email_utils.adjust_length(
                                st.session_state.output_text, length, provider=provider
                            )
                            set_output(result)
                            st.rerun()
                        except email_utils.EmailAssistantError as e:
                            st.error(str(e))
        else:
            st.info("👈 Your generated email will appear here.")

# ========== TAB 2: Improve Email ==========
with tab2:
    st.markdown("### 🛠️ Improve an Existing Email")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📋 Paste your email draft")
        improve_input = st.text_area(
            "Your email draft",
            height=280,
            placeholder="Paste your draft email here...",
            key="input_edit",
        )

        st.markdown("#### 🎯 Actions")
        b1, b2, b3, b4 = st.columns(4)

        with b1:
            fix_grammar_clicked = st.button("✅ Fix Grammar", use_container_width=True)
        with b2:
            change_tone_clicked = st.button("🎭 Change Tone", use_container_width=True)
        with b3:
            adjust_length_clicked = st.button("📏 Adjust Length", use_container_width=True)
        with b4:
            improve_clicked = st.button("💡 Get Suggestions", use_container_width=True)

        if fix_grammar_clicked:
            if not improve_input.strip():
                st.warning("Please paste an email first.")
            else:
                with st.spinner("Fixing grammar and spelling..."):
                    try:
                        result = email_utils.fix_grammar(improve_input, provider=provider)
                        set_output(result)
                        st.rerun()
                    except email_utils.EmailAssistantError as e:
                        st.error(str(e))

        if change_tone_clicked:
            if not improve_input.strip():
                st.warning("Please paste an email first.")
            else:
                with st.spinner(f"Rewriting in a {tone.lower()} tone..."):
                    try:
                        result = email_utils.change_tone(
                            improve_input, tone, provider=provider
                        )
                        set_output(result)
                        st.rerun()
                    except email_utils.EmailAssistantError as e:
                        st.error(str(e))

        if adjust_length_clicked:
            if not improve_input.strip():
                st.warning("Please paste an email first.")
            else:
                with st.spinner(f"Adjusting to {length.lower()} length..."):
                    try:
                        result = email_utils.adjust_length(
                            improve_input, length, provider=provider
                        )
                        set_output(result)
                        st.rerun()
                    except email_utils.EmailAssistantError as e:
                        st.error(str(e))

        if improve_clicked:
            if not improve_input.strip():
                st.warning("Please paste an email first.")
            else:
                with st.spinner("Analyzing your email..."):
                    try:
                        st.session_state.suggestions = (
                            email_utils.get_improvement_suggestions(
                                improve_input, provider=provider
                            )
                        )
                    except email_utils.EmailAssistantError as e:
                        st.error(str(e))

        if st.session_state.suggestions:
            with st.expander("💡 Improvement Suggestions", expanded=True):
                st.markdown(st.session_state.suggestions)
    
    with col2:
        st.markdown("### 📤 Output")
        
        if st.session_state.output_text:
            st.markdown('<div class="output-box">', unsafe_allow_html=True)
            st.text_area(
                "Improved email",
                value=st.session_state.output_text,
                height=280,
                key="output_display_improve",
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                copy_button(st.session_state.output_text, key="output_improve")

            with col_b:
                st.download_button(
                    label="📄 Download TXT",
                    data=st.session_state.output_text,
                    file_name="improved_email.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            with col_c:
                try:
                    pdf_bytes = export_to_pdf(st.session_state.output_text, title="Improved Email")
                    st.download_button(
                        label="📑 Download PDF",
                        data=pdf_bytes,
                        file_name="improved_email.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Could not generate PDF: {e}")
        else:
            st.info("👈 Your improved email will appear here.")

# ========== TAB 3: Subject Lines ==========
with tab3:
    st.markdown("### 📌 Subject Line Generator")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📋 Email content for subject lines")
        
        subject_input = st.text_area(
            "Paste your email content here",
            height=250,
            placeholder="Paste the email content to generate subject lines from...",
            key="subject_input",
        )
        
        if st.button("📌 Generate Subject Lines", type="primary", use_container_width=True):
            if not subject_input.strip():
                st.warning("Please paste an email first.")
            else:
                with st.spinner("Generating subject line ideas..."):
                    try:
                        st.session_state.subject_lines = email_utils.generate_subject_lines(
                            subject_input, provider=provider
                        )
                    except email_utils.EmailAssistantError as e:
                        st.error(str(e))
    
    with col2:
        st.markdown("### 📤 Generated Subject Lines")
        
        if st.session_state.subject_lines:
            st.markdown('<div class="output-box">', unsafe_allow_html=True)
            for i, subj in enumerate(st.session_state.subject_lines, start=1):
                st.markdown(f"**{i}.** {subj}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Copy all subject lines
            all_subjects = "\n".join(st.session_state.subject_lines)
            copy_button(all_subjects, key="subjects")
        else:
            st.info("👈 Generate subject lines to see them here.")

# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.divider()
st.caption(
    "⚠️ Always review AI-generated content before sending. This tool assists — it doesn't replace your judgment."
)

with st.expander("ℹ️ System Status"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Provider", PROVIDER_LABELS.get(provider, "None"))
    with c2:
        st.metric("Tone", tone)
    with c3:
        st.metric("Length", length)
