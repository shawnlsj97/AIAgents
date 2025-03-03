import logging
from typing import Optional
from datetime import datetime
from ollama import chat, ChatResponse
from pydantic import BaseModel, Field

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# --------------------------------------------------------------
# Step 1: Define the data models for each stage
# --------------------------------------------------------------
class EventExtraction(BaseModel):
    """First LLM call: Extract basic event information"""

    description: str = Field(description="Raw description of the event")
    is_calendar_event: bool = Field(
        description="Whether the input describes a calendar event"
    )
    confidence_score: float = Field(description="Confidence score between 0 and 1")


class EventDetails(BaseModel):
    """Second LLM call: Parse specific event details"""

    name: str = Field(description="Name of the event")
    date: str = Field(
        description="Date and time of the event, use ISO 8601 to format this value. "
    )
    duration_minutes: int = Field(description="Duration in minutes")
    participants: list[str] = Field(description="List of participants")


class EventConfirmation(BaseModel):
    """Third LLM call: Generate confirmation message"""

    confirmation_message: str = Field(
        description="Natural language confirmation message"
    )
    calendar_link: Optional[str] = Field(
        description="Generated calendar link if applicable"
    )

# --------------------------------------------------------------
# Step 2: Define the functions (tools)
# --------------------------------------------------------------
def extract_event_info(user_input: str) -> EventExtraction:
    """First LLM call determines if input is a calendar event or not"""
    logger.info("Starting event extraction analysis")
    logger.debug(f"Input text: {user_input}")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y %H:%M:%S')}."

    response: ChatResponse = chat(
        model="llama3.1",
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Analyze if the text describes a calendar event. Store the user input as the description if it is a valid calendar event.",
            },
            {"role": "user", "content": user_input},
        ],
        format=EventExtraction.model_json_schema(),
    )
    result = EventExtraction.model_validate_json(response.message.content)
    logger.info(
        f"Extraction complete - Is calendar event: {result.is_calendar_event}, Confidence: {result.confidence_score:.2f}"
    )
    return result

def parse_event_details(description: str) -> EventDetails:
    """Second LLM call to extract specific event details"""
    logger.info("Starting event details parsing")
    logger.debug(f"Event description: {description}")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y %H:%M:%S')}."

    response: ChatResponse = chat(
        model="llama3.1",
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Extract detailed event information from user input. When dates reference 'next Tuesday' or similar relative dates, use this current date as reference. Include the time of the event.",
            },
            {"role": "user", "content": description},
        ],
        format=EventDetails.model_json_schema(),
    )
    result = EventDetails.model_validate_json(response.message.content)
    logger.info(
        f"Parsed event details - Name: {result.name}, Date: {result.date}, Duration: {result.duration_minutes}min"
    )
    logger.info(f"Participants: {', '.join(result.participants)}")
    return result

def generate_confirmation(event_details: EventDetails) -> EventConfirmation:
    """Third LLM call to generate a confirmation message"""
    logger.info("Generating confirmation message")
    logger.info(event_details.model_dump())
    response: ChatResponse = chat(
        model="llama3.1",
        messages=[
            {
                "role": "system",
                "content": "Generate a confirmation message for the event and sign off with your name: Shawn",
            },
            {"role": "user", "content": str(event_details.model_dump())},
        ],
        format=EventConfirmation.model_json_schema(),
    )

    result = EventConfirmation.model_validate_json(response.message.content)
    logger.info("Confirmation message generated successfully")
    return result

# --------------------------------------------------------------
# Step 3: Chain the functions together
# --------------------------------------------------------------
def process_calendar_request(user_input: str) -> Optional[EventConfirmation]:
    """Main function implementing prompt chain with gate checks"""

    # First LLM call: Determine if user input a valid calendar event
    initial_extraction = extract_event_info(user_input)
    if (
        not initial_extraction.is_calendar_event 
        or initial_extraction.confidence_score < 0.7
    ): # Gate check
        logger.warning(
            f"Gate check failed - is_calendar_event: {initial_extraction.is_calendar_event}, confidence: {initial_extraction.confidence_score:.2f}"
        )
        return None

    # Second LLM call: Extract event details
    event_details = parse_event_details(initial_extraction.description)

    # Third LLM call: Generate confirmation
    confirmation = generate_confirmation(event_details)
    return confirmation

# --------------------------------------------------------------
# Step 4: Test the chain with a valid input
# --------------------------------------------------------------
user_input = "Let's schedule a 1h team meeting next Tuesday at 2pm with Alice and Bob to discuss the project roadmap."

result = process_calendar_request(user_input)
if result:
    print(f"Confirmation: {result.confirmation_message}")
    if result.calendar_link:
        print(f"Calendar Link: {result.calendar_link}")
else:
    print("This doesn't appear to be a calendar event request.")

# --------------------------------------------------------------
# Step 5: Test the chain with an invalid input
# --------------------------------------------------------------
user_input = "Can you send an email to Alice and Bob to discuss the project roadmap?"

result = process_calendar_request(user_input)
if result:
    print(f"Confirmation: {result.confirmation_message}")
    if result.calendar_link:
        print(f"Calendar Link: {result.calendar_link}")
else:
    print("This doesn't appear to be a calendar event request.")