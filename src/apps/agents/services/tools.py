from strands import tool
from apps.coaching.models import JobProfile, InterviewSession


@tool
def read_profile(profile_id: str) -> dict:
    """
    Read a user profile from the database
    """
    # Use Django ORM for safe read
    profile = JobProfile.objects.get(id=profile_id)
    return {
        "profile_name": profile.profile_name,
        "job_description": profile.job_description,
        "company_name": profile.company_name,
        "company_background": profile.company_background,
        "responsibilities": [res for res in profile.responsibilities],
        "required_skills": [skill for skill in profile.required_skills],
    }


@tool
def get_session_transcription(session_id: str) -> dict:
    """
    Reads the full session transcription
    """
    # Use Django ORM for safe read
    session = InterviewSession.objects.get(id=session_id)
    return session.full_transcript
