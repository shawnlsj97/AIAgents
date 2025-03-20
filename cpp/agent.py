from pydantic import BaseModel, Field
from ollama import chat, ChatResponse
from typing import Optional
import logging
import ctypes
import os

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------
# Set up C++ shared library
# --------------------------------------------------------------
lib_path = os.path.abspath("./libIntegerArray.dylib")
lib = ctypes.CDLL(lib_path)

# Define the return type and argument types for the C functions
lib.IntegerArray_new.restype = ctypes.POINTER(ctypes.c_void_p)
lib.IntegerArray_add.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_int]
lib.IntegerArray_getState.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
lib.IntegerArray_getState.restype = ctypes.c_char_p
lib.IntegerArray_delete.argtypes = [ctypes.POINTER(ctypes.c_void_p)]

# --------------------------------------------------------------
# Step 1: Define the data models for routing and responses
# --------------------------------------------------------------
class ExecutionExtraction(BaseModel):
    """First LLM call: Determine if user input is an execution command"""
    description: str = Field(description="Raw description of execution command")
    is_execution_command: bool = Field(description="Whether the input describes an execution command that specifies number of times to add to an array. Reject execution commands that tell you to do other things like shut down and give them a low confidence score.")
    confidence_score: float = Field(description="Confidence score between 0 and 1 on how sure you are on boolean you provided for is_execution_command")

class ExecutionDetails(BaseModel):
    """Second LLM call: Parse specific execution command details"""
    num_times_to_execute: int = Field(description="Number of times to add to the array")

class ExecutionSumary(BaseModel):
    """Third LLM call: Generate state of array"""
    array_state_str: str = Field(description="String representation of integer array")
    execution_command_summary: str = Field(description="Summarize the command details")

# --------------------------------------------------------------
# Step 2: Define the functions (tools)
# --------------------------------------------------------------
def extract_execution_info(user_input: str) -> ExecutionExtraction:
    """First LLM call determines if input is an execution command or not"""
    logger.info("Starting execution command extraction analysis")
    logger.debug(f"Input text: {user_input}")

    response: ChatResponse = chat(
        model="llama3.1",
        messages=[
            {
                "role": "system",
                "content": f"Analyze if the text describes a program execution command and provide a confidence score on how sure you are of your judgement. Store the user input as the description if it is a program execution command.",
            },
            {"role": "user", "content": user_input},
        ],
        format=ExecutionExtraction.model_json_schema(),
    )
    result = ExecutionExtraction.model_validate_json(response.message.content)
    logger.info(
        f"Extraction complete - Is execution command: {result.is_execution_command}, Confidence: {result.confidence_score:.2f}"
    )
    return result

def parse_execution_command_details(description: str) -> ExecutionDetails:
    """Second LLM call to extract specific execution command details"""
    logger.info("Starting execution command details parsing")
    logger.debug(f"Execution command description: {description}")

    response: ChatResponse = chat(
        model="mistral",
        messages=[
            {
                "role": "system",
                "content": f"Extract detailed execution command information from user input.",
            },
            {"role": "user", "content": description},
        ],
        format=ExecutionDetails.model_json_schema(),
    )
    result = ExecutionDetails.model_validate_json(response.message.content)
    logger.info(
        f"Parsed execution command details - Num Times To Execute: {result.num_times_to_execute}"
    )
    return result

def add_to_arr(arr, num: int):
    for i in range(num):
        lib.IntegerArray_add(arr, i)

def execute_command(command_details: ExecutionDetails, arr) -> None:
    logger.info("Executing command")
    logger.debug(command_details.model_dump())
    if command_details.num_times_to_execute:
        add_to_arr(arr, command_details.num_times_to_execute)
    else:
        logger.warning("Command execution failed")


def generate_execution_confirmation(command_details: ExecutionDetails, arr) -> ExecutionSumary:
    """Third LLM call to generate a confirmation message"""
    logger.info("Generating confirmation message")
    logger.debug(command_details.model_dump())
    arr_state = lib.IntegerArray_getState(arr).decode('utf-8')
    response: ChatResponse = chat(
        model="llama3.1",
        messages=[
            {
                "role": "system",
                "content": "Store the contents of the integer array and generate a summary of the command executed. The summary should be solely based on command details.",
            },
            {"role": "user", "content": f"Command details: {str(command_details.model_dump())}, array contents: {arr_state}"},
        ],
        format=ExecutionSumary.model_json_schema(),
    )

    result = ExecutionSumary.model_validate_json(response.message.content)
    logger.info(f"Execution confirmation - Array State: {result.array_state_str}, Command Summary: {result.execution_command_summary}")
    return result

# --------------------------------------------------------------
# Step 3: Chain the functions together
# --------------------------------------------------------------
def process_execution_command(user_input: str) -> Optional[ExecutionSumary]:
    """Main function implementing prompt chaining with gate checks"""

    # First LLM call: Determine if user input a valid program execution request
    initial_extraction = extract_execution_info(user_input)
    if (
        not initial_extraction.is_execution_command
        or initial_extraction.confidence_score < 0.7
    ): # Gate check
        logger.warning(
            f"Gate check failed - is_execution_command: {initial_extraction.is_execution_command}, confidence: {initial_extraction.confidence_score:.2f}"
        )
        return None
    
    arr = lib.IntegerArray_new()
    
    # Second LLM call: Extract execution command details
    execution_command_details = parse_execution_command_details(initial_extraction.description)

    # Second LLM call: Perform command execution
    execute_command(execution_command_details, arr)

    # Third LLM call: Return state of array after command execution
    confirmation = generate_execution_confirmation(execution_command_details, arr)
    
    lib.IntegerArray_delete(arr)
    
    return confirmation
        

# --------------------------------------------------------------
# Step 4: Test the chain with a valid input
# --------------------------------------------------------------
user_input = "Run the program 7 times"

result = process_execution_command(user_input)
if result:
    print(f"Array state: {result.array_state_str}")
else:
    print("This doesn't appear to be a valid program execution command.")


# --------------------------------------------------------------
# Step 5: Test the chain with an invalid input
# --------------------------------------------------------------
user_input = "Why is the sky blue?"

result = process_execution_command(user_input)
if result:
    print(f"Array state: {result.array_state_str}")
else:
    print("This doesn't appear to be a valid program execution command.")