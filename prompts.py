"""
Prompt templates for the AI Content Generator.

Each function builds a structured prompt that tells Gemini exactly what
role to play, what to write about, and how the output should be shaped.
Keeping the templates here (instead of inline in app.py) makes it easy
to tweak the wording without touching the UI or API code.
"""


def build_blog_prompt(topic: str, tone: str) -> str:
    """Structured prompt for a blog post."""
    return f"""You are an expert content writer and blogger with years of experience
writing engaging, well-researched articles for online audiences.

Write a complete blog post about:
"{topic}"

Tone of writing: {tone}

Requirements:
- Create a catchy, relevant title at the top
- Write a strong introduction that hooks the reader
- Organize the body using clear headings or subheadings
- Provide useful, accurate, and relevant information about the topic
- Maintain the "{tone}" tone consistently throughout the piece
- Avoid unnecessary repetition or filler sentences
- End with a clear, satisfying conclusion that summarizes the key points
- Target length: roughly 350-550 words
- Audience: general readers interested in the topic, no specialist jargon
- Format the output using Markdown (e.g. "# Title", "## Heading")

Write only the blog post itself. Do not include any notes, explanations,
or commentary about the writing process.
"""


def build_social_prompt(topic: str, tone: str) -> str:
    """Structured prompt for a social media caption."""
    return f"""You are a skilled social media copywriter who writes short,
scroll-stopping captions for platforms like Instagram and LinkedIn.

Write an engaging social media caption about:
"{topic}"

Tone of writing: {tone}

Requirements:
- Keep it concise (roughly 2-5 short sentences or lines)
- Make it attention-grabbing from the very first line
- Maintain the "{tone}" tone throughout
- Make it feel natural for a social media post, not a formal article
- Include 3-6 relevant hashtags at the end
- Do not overuse hashtags or stuff keywords
- Audience: general social media followers interested in the topic

Write only the caption itself. Do not include any notes, explanations,
or commentary about the writing process.
"""


def build_refine_prompt(existing_content: str, instruction: str, content_type: str, tone: str) -> str:
    """Structured prompt for refining already-generated content."""
    return f"""You are an expert editor refining a piece of {content_type.lower()} content.

Here is the current content:
---
{existing_content}
---

The author wants the following change applied:
"{instruction}"

Requirements:
- Apply the requested change faithfully
- Preserve the original topic and overall meaning
- Keep the tone of writing as "{tone}" unless the instruction says otherwise
- Return the full revised content, not just the changed portion
- Do not add notes, explanations, or commentary about what you changed

Write only the revised content.
"""


def build_prompt(content_type: str, topic: str, tone: str) -> str:
    """Dispatch to the correct prompt builder based on content type."""
    if content_type == "Blog Post":
        return build_blog_prompt(topic, tone)
    elif content_type == "Social Media Caption":
        return build_social_prompt(topic, tone)
    raise ValueError(f"Unsupported content type: {content_type}")
