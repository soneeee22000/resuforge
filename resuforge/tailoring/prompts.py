"""All LLM prompt templates for the tailoring engine.

Never inline prompts in logic code — they all live here.
Prompts use XML-style tags to delimit resume content from instructions
(Anthropic best practice).
"""

SYSTEM_TAILORING = """You are a professional resume tailoring assistant.

You may ONLY reference skills, experience, projects, and facts
that are present in the provided resume JSON. Do not invent,
imply, or suggest anything that is not explicitly in the resume.

Rules:
- Preserve the user's voice and writing style
- Make targeted, minimal edits — not wholesale rewrites
- Never change job titles, company names, dates, or education entries
- Every change must have a clear reason tied to the job description
- Use active voice and strong action verbs
"""

PROMPT_GAP_ANALYSIS = """Analyze the semantic gap between this job description and resume.

<job_description>
{jd_json}
</job_description>

<resume>
{resume_json}
</resume>

Identify:
1. Strengths: resume content that directly matches JD requirements
2. Gaps: required JD skills/experience not present in resume
3. Opportunities: resume content that could be reframed to better match JD
"""

PROMPT_SUMMARY_REWRITE = """Rewrite the resume summary to better align with this role.

<job_description>
{jd_json}
</job_description>

<current_summary>
{summary}
</current_summary>

<resume_context>
{resume_json}
</resume_context>

Rewrite the summary to open with role-relevant framing. Only reference
skills and experience that exist in the resume. Preserve the user's
writing style and voice.
"""

PROMPT_BULLET_REPHRASE = """Rephrase this resume bullet point to better match the job description.

<job_description>
{jd_json}
</job_description>

<bullet>
{bullet_text}
</bullet>

<context>
Company: {company}
Role: {title}
</context>

Rephrase to incorporate relevant JD keywords where accurate.
Do NOT change the factual content — only adjust language and emphasis.
"""

PROMPT_SKILLS_REORDER = """Reorder the skills in each category to surface JD-relevant skills first.

<job_description>
{jd_json}
</job_description>

<skills>
{skills_json}
</skills>

Reorder items within each category so that skills matching the JD
appear first. Do NOT add or remove any skills — only reorder.
"""
