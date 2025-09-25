from strands import Agent
from strands.models import BedrockModel
from .tools import read_profile, get_session_transcription

pro_model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    temperature=0.2,
    streaming=True,
    region_name="us-east-1",
)

basic_model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    temperature=0.4,
    region_name="us-east-1",
)


def get_question_generator_agent():
    SYSTEM_PROMPT = """
    You are an expert at creating a set of questions for an job interviewer. 
    The questions must be the most relevant based on the job profile the candidate is applying.
    You need to get the job profile using the read_profile tool and based on the profile information you will create around 5-8 question the interviewer may ask the candidate

    Your output response should a JSON compatible:

    [
        "1. Question one?",
        "2. Question two?",
        "3. Question three?"
    ]

    Make sure to add the square bracket at the end of the file
    """  # noqa
    agent = Agent(
        tools=[read_profile],
        model=basic_model,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent


def get_feedback_agent():
    SYSTEM_PROMPT = """
        You are coach tasked with evaluating user performance in an interview session. Use the get_session_transcription tool to retrieve the interview transcript and the read_profile tool to access the job profile. Analyze the user's performance based on relevance to the job, clarity, technical/professional competence, communication skills, and problem-solving. Provide feedback in this format:

        General Feedback: 2-3 sentences summarizing overall performance and alignment with the job profile.
        Strengths: 2-3 specific strengths with examples from the transcript.
        Areas of Improvement: 2-3 actionable improvements tied to the transcript or job profile.
        Final Rating: A 0-100 score with a brief justification.

        Maintain a professional, neutral, and concise tone. Base feedback solely on the transcript and job profile, noting any incomplete data. Avoid assumptions and ensure feedback is specific and tailored.
    """  # noqa
    agent = Agent(
        tools=[read_profile, get_session_transcription],
        model=pro_model,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent
