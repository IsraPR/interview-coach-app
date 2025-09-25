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
async def read_profile_async(profile_id: str) -> dict:
    """
    Read a user profile from the database (async-safe).
    """
    profile = await JobProfile.objects.aget(id=profile_id)
    return {
        "profile_name": profile.profile_name,
        "job_description": profile.job_description,
        "company_name": profile.company_name,
        "company_background": profile.company_background,
        "responsibilities": list(profile.responsibilities),
        "required_skills": list(profile.required_skills),
    }


@tool
async def get_session_transcription(session_id: str) -> dict:
    """
    Read the full session transcription (async-safe).
    """
    session = await InterviewSession.objects.aget(id=session_id)
    return session.full_transcript
