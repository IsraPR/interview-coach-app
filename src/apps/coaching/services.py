from typing import List
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth import get_user_model
from .models import JobProfile
from .models import InterviewSession
from .models import UserResume
from .models import InterviewSessionSetup
from .schemas import JobProfileCreateSchema, JobProfileUpdateSchema
from .schemas import UserResumeCreateSchema
from .schemas import InterviewSessionSetupCreateSchema

from core.settings import logger


User = get_user_model()


def create_job_profile(
    user: User, payload: JobProfileCreateSchema
) -> JobProfile:
    """
    Creates a new JobProfile for a given user.
    """
    # The user is passed in from the request, ensuring ownership.
    profile = JobProfile.objects.create(user=user, **payload.dict())
    return profile


def list_job_profiles(user: User) -> List[JobProfile]:
    """
    Lists all JobProfiles for a given user.
    """
    return JobProfile.objects.filter(user=user)


def get_job_profile_detail(user: User, profile_id: int) -> JobProfile:
    """
    Retrieves a single JobProfile, ensuring it belongs to the user.
    """
    # get_object_or_404 will raise a 404 if the profile doesn't exist OR
    # if it doesn't belong to the specified user. This is a secure pattern.
    return get_object_or_404(JobProfile, id=profile_id, user=user)


def update_job_profile(
    user: User, profile_id: int, payload: JobProfileUpdateSchema
) -> JobProfile:
    """
    Updates an existing JobProfile, ensuring it belongs to the user.
    """
    profile = get_object_or_404(JobProfile, id=profile_id, user=user)

    # We use payload.dict(exclude_unset=True) to only update the fields
    # that the client actually sent in the request.
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(profile, attr, value)

    profile.save()
    return profile


def delete_job_profile(user: User, profile_id: int):
    """
    Deletes a JobProfile, ensuring it belongs to the user.
    """
    profile = get_object_or_404(JobProfile, id=profile_id, user=user)
    profile.delete()  # This will perform a soft delete because of our BaseModel
    return


def create_interview_session(
    user: User, profile_id: int, session_data: dict
) -> InterviewSession:
    """
    Creates a new, pending interview session for one of the user's job profiles.
    """
    # First, ensure the parent JobProfile exists and belongs to the user.
    profile = get_job_profile_detail(user=user, profile_id=profile_id)

    # Create the new session linked to this profile.
    session = InterviewSession.objects.create(
        job_profile=profile, **session_data
    )
    return session


def list_interview_sessions(
    user: User, profile_id: int
) -> List[InterviewSession]:
    """
    Lists all interview sessions for a specific job profile owned by the user.
    """
    # Ensure the parent profile belongs to the user before listing its children.
    get_job_profile_detail(user=user, profile_id=profile_id)

    return InterviewSession.objects.filter(job_profile__id=profile_id)


def get_interview_session_detail(
    user: User, session_id: int
) -> InterviewSession:
    """
    Retrieves a single interview session, ensuring the parent profile belongs to the user.
    """
    session = get_object_or_404(InterviewSession, id=session_id)

    # Security check: Does this session's parent profile belong to the requesting user?
    if session.job_profile.user != user:
        raise Http404("No InterviewSession found matching the query")

    return session


def create_user_resume(
    user: User, payload: UserResumeCreateSchema
) -> UserResume:
    """
    Creates or updates the UserResume for a given user.
    Each user can have only one resume per current_role.
    """
    resume = UserResume.objects.create(
        user=user,
        current_role=payload.current_role,
        key_skills=payload.key_skills,
        description=payload.description,
    )
    return resume


def update_user_resume(
    user: User, payload: UserResumeCreateSchema
) -> UserResume:
    """
    Updates an existing UserResume, ensuring it belongs to the user.
    """
    resume = get_object_or_404(UserResume, user=user)

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(resume, attr, value)

    resume.save()
    return resume


def get_user_resume(user: User) -> UserResume:
    """
    Retrieves the UserResume for a given user.
    """
    return get_object_or_404(UserResume, user=user)


# Session setup schema


def create_interview_session_setup(
    payload: InterviewSessionSetupCreateSchema,
) -> InterviewSession:
    """
    Updates the setup details for a specific interview session.
    """
    setup, created = InterviewSessionSetup.objects.get_or_create(
        **payload.model_dump()
    )
    logger.info(
        f"Interview session setup {'created' if created else 'updated'}: {setup.id}"
    )

    return setup


def list_interview_session_setups() -> List[InterviewSessionSetup]:
    """
    Lists all interview session setups.
    """
    return InterviewSessionSetup.objects.all()


def get_session_setup_detail(setup_id: int) -> InterviewSessionSetup:
    """
    Retrieves a single interview session setup by its ID.
    """
    return get_object_or_404(InterviewSessionSetup, id=setup_id)
