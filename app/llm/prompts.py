# =========================
# RECOMMENDATION PROMPT
# =========================

def build_recommendation_prompt(

    query,

    recommendations
):

    recommendation_text = ""

    for idx, rec in enumerate(
        recommendations,
        start=1
    ):

        recommendation_text += f"""

Assessment {idx}:

Name:
{rec['name']}

Description:
{rec.get('description', '')}

Skills:
{", ".join(rec.get('skills', []))}

Category:
{rec.get('category', '')}

"""

    prompt = f"""
A recruiter is looking for SHL assessments.

User hiring query:
{query}

Recommended assessments:
{recommendation_text}

Generate a concise,
professional,
human-like response explaining:

- why these assessments are relevant
- what skills they evaluate
- how they help hiring

Keep response under 120 words.
"""

    return prompt


# =========================
# COMPARISON PROMPT
# =========================

def build_comparison_prompt(

    comparison_text
):

    prompt = f"""
You are helping a recruiter
understand SHL assessments.

Below is a comparison draft:

{comparison_text}

Rewrite it into:
- concise
- professional
- recruiter-friendly language

Keep it under 120 words.
"""

    return prompt