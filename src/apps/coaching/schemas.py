from ninja import ModelSchema, Schema
from .models import UserResume
from .models import JobProfile
from .models import InterviewSession
from .models import InterviewSessionSetup


class UserResumeSchema(ModelSchema):
    class Meta:
        model = UserResume
        fields = [
            "id",
            "current_role",
            "key_skills",
            "description",
            "created_at",
            "updated_at",
        ]


class UserResumeCreateSchema(Schema):
    current_role: str
    key_skills: list
    description: str


class UserResumeUpdateSchema(Schema):
    current_role: str = None
    key_skills: list = None
    description: str = None


# --- Output Schema ---
# We use ModelSchema to automatically generate a schema from our model.
# This is a powerful DRY (Don't Repeat Yourself) feature.


class JobProfileSchema(ModelSchema):
    class Meta:
        model = JobProfile
        fields = [
            "id",
            "profile_name",
            "target_role",
            "job_description",
            "company_name",
            "company_background",
            "responsibilities",
            "required_skills",
            "created_at",
            "updated_at",
        ]


# --- Input Schema for Creation ---
class JobProfileCreateSchema(Schema):
    profile_name: str
    target_role: str
    job_description: str = ""
    company_name: str = ""
    company_background: str = ""
    responsibilities: list = []
    required_skills: list = []


# --- Input Schema for Updates ---
# All fields are optional for updates.
class JobProfileUpdateSchema(Schema):
    profile_name: str = None
    target_role: str = None
    job_description: str = None
    company_name: str = None
    company_background: str = None
    responsibilities: list = None
    required_skills: list = None


# --- Output Schema Session ---
class InterviewSessionSchema(ModelSchema):
    class Meta:
        model = InterviewSession
        fields = [
            "id",
            "status",
            "prompt_name",
            "s2s_system_prompt",
            "inference_config",
            "session_feedback",
            "created_at",
        ]


# For creation, we don't need any input, as a session is just "started"
class InterviewSessionCreateSchema(Schema):
    practice_profile_id: int
    session_setup_id: int


class InterviewSessionUpdateSchema(Schema):
    status: str = None


# Session Setup Schemas
# Output Schema
class InterviewSessionSetupSchema(ModelSchema):
    class Meta:
        model = InterviewSessionSetup
        fields = [
            "id",
            "interviewer_name",
            "interviewer_attitude",
            "preferred_language",
            "model_voice",
            "created_at",
            "updated_at",
        ]


class InterviewSessionSetupCreateSchema(Schema):
    interviewer_name: str
    interviewer_attitude: str
    preferred_language: str


class InterviewSessionSetupUpdateSchema(Schema):
    interviewer_name: str = None
    interviewer_attitude: str = None
    preferred_language: str = None
