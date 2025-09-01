from django.db import models
from django.conf import settings
from apps.common_models.models import BaseModel


class JobProfile(BaseModel):
    """
    Represents a specific job role a user wants to practice for.
    A user can have multiple profiles (e.g., for a Python Developer role
    and a DevOps Engineer role).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_profiles",
        help_text="The user who owns this job profile.",
    )
    profile_name = models.CharField(
        max_length=255,
        help_text="A user-defined name for this profile, e.g., 'Senior Python Role at Google'.",
    )
    target_role = models.CharField(
        max_length=255,
        help_text="The job title the user is targeting, e.g., 'Senior Python Developer'.",
    )
    job_description_text = models.TextField(
        blank=True,
        help_text="The full text of the job description the user is applying for.",
    )
    resume_text = models.TextField(
        blank=True,
        help_text="The full text of the user's resume, tailored for this role.",
    )
    # This field will be crucial for the AI to generate relevant questions.
    # We can use a JSONField to store structured data extracted from the resume/JD.
    key_skills = models.JSONField(
        default=list,
        blank=True,
        help_text="A list of key skills, technologies, and experiences extracted by the AI.",
    )

    class Meta(BaseModel.Meta):
        db_table = "coaching_job_profile"
        verbose_name = "Job Profile"
        verbose_name_plural = "Job Profiles"
        # A user cannot have two profiles with the exact same name.
        unique_together = ("user", "profile_name")

    def __str__(self):
        return f"{self.target_role} ({self.user.email})"


class InterviewSession(BaseModel):
    """
    Represents a single practice interview session for a specific JobProfile.
    """

    # An ENUM for the session status is a robust pattern.
    class SessionStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        ERROR = "ERROR", "Error"

    job_profile = models.ForeignKey(
        JobProfile,
        on_delete=models.CASCADE,
        related_name="interview_sessions",
        help_text="The job profile this session is for.",
    )
    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.PENDING,
    )
    session_summary = models.TextField(
        blank=True,
        help_text="An AI-generated summary of the user's performance in the session.",
    )
    # We can store the full transcript as structured data.
    full_transcript = models.JSONField(
        default=list,
        blank=True,
        help_text="The full transcript of the interview, including questions, answers, and feedback.",
    )

    class Meta(BaseModel.Meta):
        db_table = "coaching_interview_session"
        verbose_name = "Interview Session"
        verbose_name_plural = "Interview Sessions"

    def __str__(self):
        return f"Session for {self.job_profile.target_role} on {self.created_at.strftime('%Y-%m-%d')}"
