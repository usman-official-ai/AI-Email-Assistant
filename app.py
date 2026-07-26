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
    page_title="AI Email Assistant",
    page_icon="📧",
    layout="wide",
)

# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------

if "output_text" not in st.session_state:
    st.session_state.output_text = ""
if "subject_lines" not in st.session_state:
    st.session_state.subject_lines = []
if "suggestions" not in st.session_state:
    st.session_state.suggestions = ""


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
            background-color:#2563eb;color:white;border:none;
            padding:8px 16px;border-radius:6px;cursor:pointer;
            font-size:14px;font-family:sans-serif;">
            📋 Copy to Clipboard
        </button>
        <script>
        const btn = document.getElementById("copy-btn-{key}");
        btn.addEventListener("click", () => {{
            navigator.clipboard.writeText(`{escaped}`);
            btn.innerText = "✅ Copied!";
            setTimeout(() => btn.innerText = "📋 Copy to Clipboard", 1500);
        }});
        </script>
        """,
        height=45,
    )


# ---------------------------------------------------------------------
# Sidebar — global settings
# ---------------------------------------------------------------------

PROVIDER_LABELS: dict[str, str] = {"gemini": "Google Gemini", "groq": "Groq"}


def _format_provider_label(p: str) -> str:
    return PROVIDER_LABELS.get(p, p)


with st.sidebar:
    st.title("📧 AI Email Assistant")
    st.caption("Powered by Google Gemini + Groq")

    st.divider()
    st.subheader("AI Provider")

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
    st.subheader("Settings")

    tone = st.selectbox("Tone", prompts.AVAILABLE_TONES, index=0)
    length = st.selectbox("Length", prompts.LENGTH_OPTIONS, index=1)

    st.divider()
    st.caption("Built with Streamlit + Gemini API + Groq API")

# ---------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------

st.title("AI Email Assistant")
st.caption("Write, reply, correct, and polish your emails in seconds.")

if provider is None:
    st.error(
        "No AI provider is configured yet. Add **GEMINI_API_KEY** and/or "
        "**GROQ_API_KEY** to your `.env` file (see `.env.example`), then restart the app."
    )
    st.stop()

mode = st.radio(
    "What do you want to do?",
    ["Write a new email", "Reply to an email", "Improve / edit an existing email"],
    horizontal=True,
)

left, right = st.columns(2)

# ---------------------------------------------------------------------
# LEFT COLUMN — Input
# ---------------------------------------------------------------------

with left:
    if mode == "Write a new email":
        st.subheader("✍️ What's the email about?")
        input_text = st.text_area(
            "Describe the topic, purpose, or bullet points for your email",
            height=280,
            placeholder="e.g. Ask my manager for 2 days of leave next week for a family event...",
            key="input_new",
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

    elif mode == "Reply to an email":
        st.subheader("📨 Paste the email you're replying to")
        input_text = st.text_area(
            "Original email",
            height=220,
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
                        # ========== FIX: Provider parameter pass karo ==========
                        result = email_utils.generate_reply(
                            input_text, reply_type, tone, length, provider=provider
                        )
                        set_output(result)
                        st.rerun()
                    except email_utils.EmailAssistantError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Unexpected error: {str(e)}")

    else:  # Improve / edit an existing email
        st.subheader("🛠️ Paste the email you want to improve")
        input_text = st.text_area(
            "Your email draft",
            height=280,
            placeholder="Paste your draft email here...",
            key="input_edit",
        )

        st.markdown("**Actions**")
        b1, b2, b3, b4 = st.columns(4)

        with b1:
            fix_grammar_clicked = st.button("✅ Fix Grammar", use_container_width=True)
        with b2:
            change_tone_clicked = st.button("🎭 Change Tone", use_container_width=True)
        with b3:
            adjust_length_clicked = st.button(
                "📏 Shorten / Expand", use_container_width=True
            )
        with b4:
            improve_clicked = st.button("💡 Improve Email", use_container_width=True)

        if fix_grammar_clicked:
            if not input_text.strip():
                st.warning("Please paste an email first.")
            else:
                with st.spinner("Fixing grammar and spelling..."):
                    try:
                        result = email_utils.fix_grammar(input_text, provider=provider)
                        set_output(result)
                        st.rerun()
                    except email_utils.EmailAssistantError as e:
                        st.error(str(e))

        if change_tone_clicked:
            if not input_text.strip():
                st.warning("Please paste an email first.")
            else:
                with st.spinner(f"Rewriting in a {tone.lower()} tone..."):
                    try:
                        result = email_utils.change_tone(
                            input_text, tone, provider=provider
                        )
                        set_output(result)
                        st.rerun()
                    except email_utils.EmailAssistantError as e:
                        st.error(str(e))

        if adjust_length_clicked:
            if not input_text.strip():
                st.warning("Please paste an email first.")
            else:
                with st.spinner(f"Adjusting to {length.lower()} length..."):
                    try:
                        result = email_utils.adjust_length(
                            input_text, length, provider=provider
                        )
                        set_output(result)
                        st.rerun()
                    except email_utils.EmailAssistantError as e:
                        st.error(str(e))

        if improve_clicked:
            if not input_text.strip():
                st.warning("Please paste an email first.")
            else:
                with st.spinner("Analyzing your email..."):
                    try:
                        st.session_state.suggestions = (
                            email_utils.get_improvement_suggestions(
                                input_text, provider=provider
                            )
                        )
                        st.rerun()
                    except email_utils.EmailAssistantError as e:
                        st.error(str(e))

        if st.session_state.suggestions:
            with st.expander("💡 Improvement Suggestions", expanded=True):
                st.text(st.session_state.suggestions)

    st.divider()
    st.subheader("🏷️ Subject Line Generator")
    if st.button("Generate Subject Lines", use_container_width=True):
        source_for_subject = st.session_state.output_text or input_text if 'input_text' in locals() else ""
        if not source_for_subject.strip():
            st.warning(
                "Generate or paste an email first so there's content to base subject lines on."
            )
        else:
            with st.spinner("Generating subject line ideas..."):
                try:
                    st.session_state.subject_lines = email_utils.generate_subject_lines(
                        source_for_subject, provider=provider
                    )
                    st.rerun()
                except email_utils.EmailAssistantError as e:
                    st.error(str(e))

    if st.session_state.subject_lines:
        for i, subj in enumerate(st.session_state.subject_lines, start=1):
            st.markdown(f"**{i}.** {subj}")

# ---------------------------------------------------------------------
# RIGHT COLUMN — Output
# ---------------------------------------------------------------------

with right:
    st.subheader("📤 Output")

    if st.session_state.output_text:
        st.text_area(
            "Generated email",
            value=st.session_state.output_text,
            height=280,
            key="output_display",
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            copy_button(st.session_state.output_text, key="output")

        with col2:
            st.download_button(
                label="⬇️ Download TXT",
                data=st.session_state.output_text,
                file_name="email.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with col3:
            try:
                pdf_bytes = export_to_pdf(st.session_state.output_text, title="Email")
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name="email.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Could not generate PDF: {e}")

        st.divider()
        st.markdown("**Refine this output further:**")
        r1, r2, r3 = st.columns(3)
        with r1:
            if st.button(
                "✅ Fix Grammar", key="refine_grammar", use_container_width=True
            ):
                with st.spinner("Fixing grammar..."):
                    try:
                        set_output(
                            email_utils.fix_grammar(
                                st.session_state.output_text, provider=provider
                            )
                        )
                        st.rerun()
                    except email_utils.EmailAssistantError as e:
                        st.error(str(e))
        with r2:
            if st.button("🎭 Change Tone", key="refine_tone", use_container_width=True):
                with st.spinner("Adjusting tone..."):
                    try:
                        set_output(
                            email_utils.change_tone(
                                st.session_state.output_text, tone, provider=provider
                            )
                        )
                        st.rerun()
                    except email_utils.EmailAssistantError as e:
                        st.error(str(e))
        with r3:
            if st.button(
                "📏 Adjust Length", key="refine_length", use_container_width=True
            ):
                with st.spinner("Adjusting length..."):
                    try:
                        set_output(
                            email_utils.adjust_length(
                                st.session_state.output_text, length, provider=provider
                            )
                        )
                        st.rerun()
                    except email_utils.EmailAssistantError as e:
                        st.error(str(e))
    else:
        st.info("Your generated or improved email will appear here.")

st.divider()
st.caption(
    "⚠️ Always review AI-generated content before sending. This tool assists — it doesn't replace your judgment."
)
