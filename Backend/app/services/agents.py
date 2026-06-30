import json
from google import genai
from google.genai import types
from app.core.config import settings


client = genai.Client(api_key=settings.GEMINI_API_KEY)


def run_mavs_pipeline(resume_content: str, jd_content: str) -> dict:
    """
    Executes MAVS pipeline and returns frontend-compatible JSON.
    """

    prompt = f"""
You are MAVS (Multi-Agent Validation Suite).

You have two inputs:

======================
RESUME
======================
{resume_content}

======================
JOB DESCRIPTION
======================
{jd_content}

Perform the following tasks.

1. Analyze the resume.
Extract:
- Candidate name
- Skills
- Experience
- Education

2. Analyze the Job Description.
Extract:
- Role
- Required Skills
- Required Experience

3. Compare resume with JD.

Generate:

- Match Score (0-100)
- Risk Score (Low / Medium / High)
- Status (Verified / Review Required / Rejected)
- Recommendation
- Candidate Match (Example: "87%")

4. Generate EXACTLY 3 deep technical interview questions.

Return ONLY VALID JSON.

Expected JSON format:

{{
  "resume_analysis": {{
      "name": "",
      "skills": [],
      "experience": "",
      "education": ""
  }},
  "jd_analysis": {{
      "role": "",
      "required_skills": [],
      "experience": ""
  }},
  "match_score": 0,
  "risk_score": "",
  "status": "",
  "recommendation": "",
  "candidate_match": "",
  "interview_questions": [
      "",
      "",
      ""
  ]
}}

Return ONLY JSON.
No markdown.
No explanation.
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )

        result = json.loads(response.text)

        return result

    except Exception as e:

        return {
            "resume_analysis": {
                "name": "Unknown",
                "skills": [],
                "experience": "",
                "education": ""
            },
            "jd_analysis": {
                "role": "",
                "required_skills": [],
                "experience": ""
            },
            "match_score": 0,
            "risk_score": "High",
            "status": "Pipeline Failed",
            "recommendation": str(e),
            "candidate_match": "0%",
            "interview_questions": []
        }