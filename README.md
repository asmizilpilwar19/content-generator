# AI Content Generator

**Internship Task 3** — An AI-powered content generation tool built with
**Google Gemini** and **Streamlit**.

## Project Objective

Generate high-quality written content (blog posts and social media
captions) based on a user-provided topic, content type, and tone, using
the Gemini API as the generation engine.

## Features

- Topic input with content type (Blog Post / Social Media Caption) and
  tone (7 options) selectors
- Input validation — won't generate without a topic
- Structured, role-based prompt templates for each content type
- **Regenerate** — get a new version with the same topic/type/tone
- **Refine** — tweak the existing result with a plain-English instruction
  (e.g. "make it shorter")
- **Copy to Clipboard** button with a success message
- Live **word count** and **character count**
- Clean, single-page Streamlit UI
- Graceful error handling for missing API keys, empty topics, and API
  failures

## Tech Stack

- Python 3.13
- [Streamlit](https://streamlit.io/) — UI
- [google-genai](https://pypi.org/project/google-genai/) — official
  Google Gemini Python SDK
- python-dotenv — loads the API key from `.env`

## Architecture

```
content-generator/
│
├── app.py              # Streamlit UI, session state, buttons, display
├── prompts.py           # Prompt templates (blog, social, refine)
├── gemini_client.py      # Gemini API configuration + error handling
├── requirements.txt
├── .env                  # Real API key (not committed)
├── .env.example          # Placeholder for the key
├── .gitignore
├── README.md
└── samples/               # Sample generated outputs
    ├── blog_ai_education.txt
    ├── social_sustainable_living.txt
    └── blog_productivity.txt
```

- **app.py** owns everything UI-related: rendering the form, handling
  button clicks, keeping `st.session_state` in sync, and showing the
  generated text, stats, and messages.
- **prompts.py** turns `(topic, tone)` into a full instruction string for
  Gemini. Keeping this separate from `app.py` means the prompt wording
  can be tuned without touching any UI code.
- **gemini_client.py** is the only file that talks to the Gemini API. It
  loads the key from `.env`, sends the prompt, and translates SDK
  exceptions into two simple error types (`GeminiConfigError`,
  `GeminiGenerationError`) that `app.py` turns into friendly messages.

## Gemini API Setup

1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Add your key to `.env`:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

The key is loaded with `python-dotenv` in `gemini_client.py` and is
never hard-coded anywhere in the source.

> **Note on the model:** the app uses `gemini-flash-lite-latest`. During
> development, `gemini-2.5-flash` and even `gemini-3.8-flash` returned
> "no longer available" or quota errors on a free-tier key, while
> `gemini-flash-lite-latest` worked reliably and has its own quota pool.
> If Google retires this alias too, update `MODEL_NAME` in
> `gemini_client.py` to whatever `client.models.list()` shows as current.

## Prompt Engineering Approach

Each prompt follows the same structure: **role → task → topic → tone →
explicit requirements → audience/format constraints**. For example, the
blog prompt (see `prompts.py`) tells Gemini it is "an expert content
writer," gives the topic and tone, and lists concrete requirements
(title, introduction, headings, conclusion, no repetition, target word
count, Markdown formatting). This is deliberately more specific than a
one-line prompt like `"Write a blog about {topic}"` — the structure is
what makes the output consistently usable without extra editing.

- **Blog Post prompt** — asks for a title, introduction, headed
  sections, useful information, and a conclusion, in the selected tone.
- **Social Media Caption prompt** — asks for a short, engaging caption
  with 3–6 relevant hashtags, written for a social feed rather than an
  article.
- **Refine prompt** — passes the *existing* generated content plus the
  user's plain-English instruction (e.g. "make it more professional")
  and asks Gemini to return the full revised text.

## Supported Content Types

1. Blog Post
2. Social Media Caption

## Supported Tones

Professional, Friendly, Casual, Informative, Persuasive, Creative,
Inspirational.

## How Regeneration Works

The **Regenerate** button re-runs the *same* prompt (same topic, content
type, and tone, stored in `st.session_state`) through Gemini. Since
Gemini's output isn't deterministic, this produces a different version
each time without the user re-entering anything.

## How Refinement Works

The **Refine** button sends the *currently displayed* content together
with the user's instruction (e.g. "make it shorter") to Gemini via the
refine prompt template, and replaces the displayed content with the
revised version. The topic/type/tone are preserved.

## Word & Character Count

Calculated directly from the generated content string:

- **Words** = `len(content.split())`
- **Characters** = `len(content)`

Both update automatically after every Generate, Regenerate, or Refine,
since they're computed live from `st.session_state.generated_content`
on each rerun.

## Error Handling

| Scenario | Behavior |
|---|---|
| Empty topic | "Please enter a topic before generating content." |
| Missing API key | Warning banner + friendly error, key itself never shown |
| API failure | "Unable to generate content right now. Please try again." |
| Empty Gemini response | Treated as a generation error (same friendly message) |
| Regenerate before any content exists | Regenerate/Refine controls are only rendered after a first successful generation |
| Refine before any content exists | Same as above |
| Refine with no instruction text | "Please describe how you'd like to refine the content." |

## Security

- The real key lives only in `.env`, which is listed in `.gitignore`
  along with `__pycache__/`, `*.pyc`, and `venv/`.
- `.env.example` contains only a placeholder.
- The key is never printed, logged, or displayed in the UI — error
  messages only ever say the key is "missing" or "needs to be
  configured."

## Testing

Tested manually during development:

- ✅ Blog Post and Social Media Caption, across all 7 tones
- ✅ Multiple topics: "Artificial Intelligence in Education",
  "Sustainable Living", "Productivity for Students", plus a very short
  topic ("AI") and a long multi-sentence topic
- ✅ Empty topic → shows the validation error, no API call made
- ✅ Generate → Regenerate → produces a different version of the same
  topic/type/tone
- ✅ Generate → Refine ("make it shorter") → produces a shorter revised
  version
- ✅ Copy to Clipboard → button copies the text and shows "Copied to
  clipboard!"
- ✅ Word/character counts verified against the actual generated text
  and confirmed they update after regenerate/refine
- ✅ Missing API key (`.env` temporarily removed) → `is_configured()`
  returns `False` and `generate_content()` raises `GeminiConfigError`,
  which the UI turns into the "needs to be configured" message
- ✅ API failure — reproduced for real: the first model tried
  (`gemini-2.5-flash`) returned a live 404 from Google, and a later one
  (`gemini-3.8-flash`) returned a live 429 quota-exceeded error; both
  were caught by `gemini_client.py` and surfaced as the friendly
  "Unable to generate content right now" message rather than a crash
- ✅ `python -m py_compile` on all three modules — no syntax errors
- ✅ App launches with `streamlit run app.py` and responds `HTTP 200`

## Sample Outputs

Three real, Gemini-generated samples are in [`samples/`](samples/):

1. [`blog_ai_education.txt`](samples/blog_ai_education.txt) — Blog Post,
   topic "Artificial Intelligence in Education", tone Informative
2. [`social_sustainable_living.txt`](samples/social_sustainable_living.txt)
   — Social Media Caption, topic "Sustainable Living", tone Inspirational
3. [`blog_productivity.txt`](samples/blog_productivity.txt) — Blog Post,
   topic "Productivity for Students", tone Friendly

## How to Run

```bash
# 1. Create and activate a virtual environment (optional but recommended)
python -m venv venv
# source venv/Scripts/activate   # Windows Git Bash
 venv\Scripts\activate.bat    # Windows cmd

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key (skip if .env already has your real key —
#    do NOT re-copy .env.example over it, that overwrites it with the placeholder)
cp .env.example .env
# then edit .env and paste your real key

# 4. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.
