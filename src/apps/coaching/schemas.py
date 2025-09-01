from ninja import ModelSchema, Schema
from .models import JobProfile
from .models import InterviewSession


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
            "job_description_text",
            "resume_text",
            "created_at",
            "updated_at",
        ]


# --- Input Schema for Creation ---
class JobProfileCreateSchema(Schema):
    profile_name: str
    target_role: str
    job_description_text: str = ""
    resume_text: str = ""


# --- Input Schema for Updates ---
# All fields are optional for updates.
class JobProfileUpdateSchema(Schema):
    profile_name: str = None
    target_role: str = None
    job_description_text: str = None
    resume_text: str = None


class InterviewSessionSchema(ModelSchema):
    class Meta:
        model = InterviewSession
        fields = [
            "id",
            "status",
            "session_summary",
            "created_at",
        ]


# For creation, we don't need any input, as a session is just "started"
class InterviewSessionCreateSchema(Schema):
    pass  # No fields needed to start a session
