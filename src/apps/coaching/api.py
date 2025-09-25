from typing import List
from pydantic import BaseModel
from ninja import Router, Path
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

from apps.agents.services.agent_factory import get_question_generator_agent
from common.prompts.prompt_manager import PromptManager

from core.settings import logger

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


class QuestionSet(BaseModel):
    questions: list[str]


@profile_sessions_router.post(
    "",
    response={201: InterviewSessionSchema},
    summary="Start a new Interview Session",
)
def create_interview_session(
    request,
    payload: InterviewSessionCreateSchema,
    profile_id: int = Path(...),
):

    session_setup = services.get_session_setup_detail(
        setup_id=payload.session_setup_id
    )
    question_generator = get_question_generator_agent()
    job_profile = services.get_job_profile_detail(
        user=request.auth, profile_id=profile_id
    )
    set_questions = question_generator.structured_output(
        output_model=QuestionSet,
        prompt=f"Create the set of question for the profile {profile_id}",
    ).questions

    logger.info(
        f"Generated questions for profile {profile_id}: {set_questions}"
    )
    user_resume = services.get_user_resume(request.user)
    template_data = {
        "candidate_name": request.user.first_name,
        "candidate_background": user_resume.description,
        "set_of_question": set_questions,
        "company_name": job_profile.company_name,
        "company_background": job_profile.company_background,
        "target_role": job_profile.target_role,
        "recruiter_style": session_setup.interviewer_attitude,
    }
    prompt_manager = PromptManager()
    system_prompt = prompt_manager.get_prompt(
        session_setup.interview_type, data=template_data
    )

    session_data = {
        "session_setup": session_setup,
        "s2s_system_prompt": system_prompt,
        "inference_config": {
            "maxTokens": 1024,
            "temperature": 0.7,
            "topP": 1.0,
        },
    }
    return 201, services.create_interview_session(
        user=request.auth, profile_id=profile_id, session_data=session_data
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


@session_setup_router.get(
    "",
    response=List[InterviewSessionSetupSchema],
    summary="List all Session Setups",
)
def list_interview_session_setups(request):
    return services.list_interview_session_setups()


@session_setup_router.get(
    "/{setup_id}",
    response=InterviewSessionSetupSchema,
    summary="Retrieve a specific Session Setup",
)
def get_session_setup_detail(request, setup_id: int):
    return services.get_session_setup_detail(setup_id=setup_id)
