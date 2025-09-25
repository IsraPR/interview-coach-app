from typing import List
from ninja import Router
from .schemas import (
    JobProfileSchema,
    JobProfileCreateSchema,
    JobProfileUpdateSchema,
)
from .schemas import (
    UserResumeSchema,
    UserResumeCreateSchema,
    UserResumeUpdateSchema,
)
from .schemas import InterviewSessionSchema, InterviewSessionCreateSchema

from .schemas import (
    InterviewSessionSetupSchema,
    InterviewSessionSetupCreateSchema,
)

from . import services

# --- Router for User Resumes ---
resume_router = Router(tags=["User Resume"])


@resume_router.post(
    "",
    response={201: UserResumeSchema},
    summary="Create User Resume",
)
def create_user_resume(request, payload: UserResumeCreateSchema):
    return 201, services.create_user_resume(user=request.auth, payload=payload)


@resume_router.put(
    "",
    response={200: UserResumeSchema},
    summary="Update User Resume",
)
def update_user_resume(request, payload: UserResumeUpdateSchema):
    return services.update_user_resume(user=request.auth, payload=payload)


@resume_router.get(
    "",
    response={200: UserResumeSchema},
    summary="Retrieve User Resume",
)
def get_user_resume(request):
    return services.get_user_resume(user=request.auth)


# --- Router for Job Profiles ---
profiles_router = Router(tags=["Job Profiles"])


@profiles_router.post(
    "", response={201: JobProfileSchema}, summary="Create a new Job Profile"
)
def create_job_profile(request, payload: JobProfileCreateSchema):
    return 201, services.create_job_profile(user=request.auth, payload=payload)


@profiles_router.get(
    "", response=List[JobProfileSchema], summary="List all Job Profiles"
)
def list_job_profiles(request):
    return services.list_job_profiles(user=request.auth)


@profiles_router.get(
    "/{profile_id}",
    response=JobProfileSchema,
    summary="Retrieve a specific Job Profile",
)
def get_job_profile_detail(request, profile_id: int):
    return services.get_job_profile_detail(
        user=request.auth, profile_id=profile_id
    )


@profiles_router.put(
    "/{profile_id}", response=JobProfileSchema, summary="Update a Job Profile"
)
def update_job_profile(
    request, profile_id: int, payload: JobProfileUpdateSchema
):
    return services.update_job_profile(
        user=request.auth, profile_id=profile_id, payload=payload
    )


@profiles_router.delete(
    "/{profile_id}", response={204: None}, summary="Delete a Job Profile"
)
def delete_job_profile(request, profile_id: int):
    services.delete_job_profile(user=request.auth, profile_id=profile_id)
    return 204, None


# --- Router for sessions nested under profiles ---
profile_sessions_router = Router(tags=["Profile Interview Sessions"])


@profile_sessions_router.post(
    "",
    response={201: InterviewSessionSchema},
    summary="Start a new Interview Session",
)
def create_interview_session(
    request, profile_id: int, payload: InterviewSessionCreateSchema
):

    return 201, services.create_interview_session(
        user=request.auth, profile_id=profile_id
    )


@profile_sessions_router.get(
    "",
    response=List[InterviewSessionSchema],
    summary="List Sessions for a Profile",
)
def list_interview_sessions(request, profile_id: int):
    return services.list_interview_sessions(
        user=request.auth, profile_id=profile_id
    )


# --- Router for accessing sessions directly by their ID ---
sessions_router = Router(tags=["Interview Sessions"])


@sessions_router.get(
    "/{session_id}",
    response=InterviewSessionSchema,
    summary="Retrieve a specific Interview Session",
)
def get_interview_session_detail(request, session_id: int):
    return services.get_interview_session_detail(
        user=request.auth, session_id=session_id
    )


# --- Router for the session setup ---
session_setup_router = Router(tags=["Interview Session Setup"])


@session_setup_router.post(
    "",
    response={201: InterviewSessionSetupSchema},
    summary="Create a new Interview Session Setup",
)
def create_interview_session_setup(
    request, payload: InterviewSessionSetupCreateSchema
):
    return 201, services.create_interview_session_setup(payload=payload)
