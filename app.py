"""
AI Content Generator - Streamlit app.

A small, professional writing tool that uses Google Gemini to generate
blog posts and social media captions, with support for regenerating,
refining, and copying the result.
"""

import html

import streamlit as st

from gemini_client import GeminiConfigError, GeminiGenerationError, generate_content, is_configured
from prompts import build_prompt, build_refine_prompt

CONTENT_TYPES = ["Blog Post", "Social Media Caption"]
TONES = [
    "Professional",
    "Friendly",
    "Casual",
    "Informative",
    "Persuasive",
    "Creative",
    "Inspirational",
]

st.set_page_config(page_title="AI Content Generator", page_icon="✍️", layout="centered")

st.markdown(
    """
    <style>
    .main .block-container { max-width: 760px; padding-top: 2rem; }
    .app-title { font-size: 2.1rem; font-weight: 700; margin-bottom: 0; }
    .app-subtitle { color: #6b7280; margin-top: 0.25rem; margin-bottom: 1.5rem; }
    .stats-row { display: flex; gap: 1.5rem; margin-top: 0.5rem; margin-bottom: 0.5rem; }
    .stat-pill {
        background: #f1f5f9; border-radius: 8px; padding: 0.4rem 0.9rem;
        font-size: 0.9rem; color: #334155; font-weight: 500;
    }
    .copy-btn {
        background-color: #2563eb; color: white; border: none; border-radius: 6px;
        padding: 0.45rem 1rem; font-size: 0.9rem; cursor: pointer; margin-top: 0.5rem;
    }
    .copy-btn:hover { background-color: #1d4ed8; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
defaults = {
    "generated_content": "",
    "previous_content": "",
    "last_topic": "",
    "last_content_type": CONTENT_TYPES[0],
    "last_tone": TONES[0],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def set_content(new_text: str):
    st.session_state.previous_content = st.session_state.generated_content
    st.session_state.generated_content = new_text


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<p class="app-title">✍️ AI Content Generator</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="app-subtitle">Generate blog posts and social media captions with Google Gemini.</p>',
    unsafe_allow_html=True,
)

if not is_configured():
    st.warning(
        "⚠️ Gemini API key not configured. Create a `.env` file in this folder with:\n\n"
        "`GEMINI_API_KEY=your_api_key_here`"
    )

# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------
st.subheader("1. Enter your content details")

topic = st.text_area(
    "Topic",
    placeholder="e.g. Benefits of Artificial Intelligence in Education",
    height=90,
)

col1, col2 = st.columns(2)
with col1:
    content_type = st.selectbox("Content Type", CONTENT_TYPES)
with col2:
    tone = st.selectbox("Tone", TONES)

generate_clicked = st.button("🚀 Generate Content", type="primary", use_container_width=True)

if generate_clicked:
    if not topic.strip():
        st.error("Please enter a topic before generating content.")
    else:
        st.session_state.last_topic = topic.strip()
        st.session_state.last_content_type = content_type
        st.session_state.last_tone = tone
        try:
            with st.spinner("Generating content with Gemini..."):
                prompt = build_prompt(content_type, topic.strip(), tone)
                result = generate_content(prompt)
            set_content(result)
            st.success("Content generated successfully.")
        except GeminiConfigError:
            st.error(
                "The Gemini API key needs to be configured. Add GEMINI_API_KEY to your .env file."
            )
        except GeminiGenerationError:
            st.error("Unable to generate content right now. Please try again.")

# ---------------------------------------------------------------------------
# Generated content section
# ---------------------------------------------------------------------------
if st.session_state.generated_content:
    st.subheader("2. Generated content")
    st.markdown(st.session_state.generated_content)

    words = len(st.session_state.generated_content.split())
    characters = len(st.session_state.generated_content)
    st.markdown(
        f"""
        <div class="stats-row">
            <div class="stat-pill">Words: {words}</div>
            <div class="stat-pill">Characters: {characters}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    escaped_content = html.escape(st.session_state.generated_content).replace("`", "&#96;")
    st.components.v1.html(
        f"""
        <textarea id="copy-source" style="position:absolute; left:-9999px;">{escaped_content}</textarea>
        <button class="copy-btn" onclick="copyContent()">📋 Copy to Clipboard</button>
        <span id="copy-status" style="margin-left:10px; color:#16a34a; font-size:0.9rem;"></span>
        <script>
        function copyContent() {{
            const text = document.getElementById("copy-source").value;
            navigator.clipboard.writeText(text).then(function() {{
                document.getElementById("copy-status").innerText = "Copied to clipboard!";
            }}, function() {{
                document.getElementById("copy-status").innerText = "Could not copy automatically - please select and copy manually.";
            }});
        }}
        </script>
        """,
        height=50,
    )

    st.markdown("---")
    st.subheader("3. Regenerate or refine")

    regen_col, _ = st.columns([1, 2])
    with regen_col:
        regenerate_clicked = st.button("🔄 Regenerate", use_container_width=True)

    if regenerate_clicked:
        try:
            with st.spinner("Regenerating content with Gemini..."):
                prompt = build_prompt(
                    st.session_state.last_content_type,
                    st.session_state.last_topic,
                    st.session_state.last_tone,
                )
                result = generate_content(prompt)
            set_content(result)
            st.success("New version generated.")
            st.rerun()
        except GeminiConfigError:
            st.error(
                "The Gemini API key needs to be configured. Add GEMINI_API_KEY to your .env file."
            )
        except GeminiGenerationError:
            st.error("Unable to generate content right now. Please try again.")

    refine_instruction = st.text_input(
        "How would you like to refine it?",
        placeholder="e.g. Make it shorter / more professional / add more detail",
    )
    refine_clicked = st.button("✨ Refine", use_container_width=True)

    if refine_clicked:
        if not refine_instruction.strip():
            st.error("Please describe how you'd like to refine the content.")
        else:
            try:
                with st.spinner("Refining content with Gemini..."):
                    prompt = build_refine_prompt(
                        st.session_state.generated_content,
                        refine_instruction.strip(),
                        st.session_state.last_content_type,
                        st.session_state.last_tone,
                    )
                    result = generate_content(prompt)
                set_content(result)
                st.success("Content refined.")
                st.rerun()
            except GeminiConfigError:
                st.error(
                    "The Gemini API key needs to be configured. Add GEMINI_API_KEY to your .env file."
                )
            except GeminiGenerationError:
                st.error("Unable to generate content right now. Please try again.")
else:
    st.info("Fill in a topic and click **Generate Content** to get started.")
