from django.db import models
from django.conf import settings
from apps.common_models.models import BaseModel
from uuid import uuid4


class UserResume(BaseModel):
    """
    Represents the current job profile of a user.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The user associated with this resume.",
    )

    current_role = models.CharField(
        max_length=255,
        help_text="The job role currently held by the user, e.g., 'Software Engineer'.",
    )

    key_skills = models.JSONField(
        default=list,
        blank=True,
        help_text="A list of key skills, technologies, and experiences.",
    )

    description = models.TextField(
        blank=True, help_text="The full description text of the user's resume."
    )

    class Meta(BaseModel.Meta):
        db_table = "user_resume"
        verbose_name = "User Resume"
        verbose_name_plural = "User Resumes"
        unique_together = ("user", "current_role")

    def __str__(self):
        return f"{self.user.email} - {self.current_role}"


class JobProfile(BaseModel):
    """
    Represents a specific job role a user wants to practice for.
    A user can have multiple profiles to practice (e.g., for a Python Developer role
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

    job_description = models.TextField(
        blank=True,
        help_text="The full text of the job description the user is applying for.",
    )
    company_name = models.CharField(
        max_length=50, help_text="The name of the company the user is applying"
    )
    company_background = models.TextField(
        blank=True, help_text="Brief description of the company background"
    )
    responsibilities = models.JSONField(
        default=list,
        blank=True,
        help_text="A list of key responsibilities for this job profile.",
    )
    required_skills = models.JSONField(
        default=list,
        blank=True,
        help_text="A list of skills required for this job profile.",
    )

    class Meta(BaseModel.Meta):
        db_table = "job_profile"
        verbose_name = "Job Profile"
        verbose_name_plural = "Job Profiles"
        # A user cannot have two profiles with the exact same name.
        unique_together = ("user", "profile_name")

    def __str__(self):
        return f"{self.target_role} ({self.user.email})"


class InterviewSessionSetup(BaseModel):
    """
    Represents a single practice interview session setup for a specific session.
    """

    class ModelVoices(models.TextChoices):
        MATTHEW = "matthew", "Matthew"
        TIFFANY = "tiffany", "Tiffany"
        AMY = "amy", "Amy"
        LUPE = "lupe", "Lupe"
        CARLOS = "carlos", "Carlos"
        AMBRE = "ambre", "Ambre"
        FLORIAN = "florian", "Florian"
        GRETA = "greta", "Greta"
        LENNART = "lennart", "Lennart"
        BEATRICE = "beatrice", "Beatrice"
        LORENZO = "lorenzo", "Lorenzo"

    class SessionLanguage(models.TextChoices):
        ENGLISH = "English", "English"
        SPANISH = "Spanish", "Spanish"

    class InterviewerAttitude(models.TextChoices):
        FRIENDLY = "Friendly", "Friendly"
        FORMAL = "Formal", "Formal"
        CHALLENGING = "Challenging", "Challenging"
        SUPPORTIVE = "Supportive", "Supportive"
        NEUTRAL = "Neutral", "Neutral"

    interviewer_name = models.CharField(
        max_length=50,
        default="Matthew",
        help_text="The name of the interviewer",
    )

    model_voice = models.CharField(
        max_length=20,
        choices=ModelVoices.choices,
        default=ModelVoices.MATTHEW,
        help_text="The voice for the speech to speech model",
    )
    preferred_language = models.CharField(
        max_length=50,
        choices=SessionLanguage.choices,
        default=SessionLanguage.ENGLISH,
        help_text="The preferred language for the speech to speech model",
    )

    interviewer_attitude = models.CharField(
        max_length=50,
        choices=InterviewerAttitude.choices,
        default=InterviewerAttitude.FRIENDLY,
        help_text="The attitude of the interviewer",
    )
    interview_type = models.CharField(
        max_length=50, default="initial_interview"
    )  # TODO: Add several types once conversation history and Websocket re-connection are supported

    class Meta(BaseModel.Meta):
        db_table = "interview_session_setup"
        verbose_name = "Interview Session Setup"
        verbose_name_plural = "Interview Session Setups"

    def __str__(self):
        return f"Session setup for {self.model_voice} in {self.preferred_language}"


class InterviewSession(BaseModel):
    """
    Represents a single practice interview session for a specific JobProfile.
    """

    class SessionStatus(models.TextChoices):
        CREATED = "CREATED", "Created"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        INCOMPLETE = "INCOMPLETE", "Incomplete"
        CANCELLED = "CANCELLED", "Cancelled"
        ERROR = "ERROR", "Error"

    job_profile = models.ForeignKey(
        JobProfile,
        on_delete=models.CASCADE,
        related_name="interview_sessions",
        help_text="The job profile this session is for.",
    )

    prompt_name = models.UUIDField(
        default=uuid4,
        help_text="The unique identifier for the prompt used in this session.",
    )

    session_setup = models.ForeignKey(
        InterviewSessionSetup,
        on_delete=models.CASCADE,
        help_text="The session setup selected by the user previously",
    )

    s2s_system_prompt = models.TextField(
        blank=True,
        help_text="The system prompt for the speech to speech model",
    )

    inference_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configuration parameters for the AI models used in this session.",
    )

    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.CREATED,
    )

    session_feedback = models.JSONField(
        blank=True,
        help_text="An AI-generated feedback of the user's performance in the session.",
    )

    # We can store the full transcript as structured data.
    full_transcript = models.JSONField(
        default=list,
        blank=True,
        help_text="The full transcript of the interview session, including both user and AI responses.",
    )

    session_cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0.0,
        help_text="The cost incurred for this session based on model usage.",
    )

    class Meta(BaseModel.Meta):
        db_table = "interview_session"
        verbose_name = "Interview Session"
        verbose_name_plural = "Interview Sessions"

    def __str__(self):
        return f"Session for {self.job_profile.target_role} on {self.created_at.strftime('%Y-%m-%d')}"
