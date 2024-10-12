import groq
import openai
import anthropic
import instructor
from config import Config, ModelType
from exceptions import InvalidModelError

def create_client():
    if Config.SELECTED_MODEL == ModelType.GROQ:
        return groq.Groq(api_key=Config.get_api_key())
    elif Config.SELECTED_MODEL == ModelType.OPENAI:
        return openai.OpenAI(api_key=Config.get_api_key())
    elif Config.SELECTED_MODEL == ModelType.CLAUDE:
        return anthropic.Anthropic(api_key=Config.get_api_key())
    else:
        raise InvalidModelError(Config.SELECTED_MODEL.value)

def create_image_client():
    # Always use OpenAI for image processing
    api_key = Config.get_api_key(ModelType.OPENAI)
    return instructor.patch(openai.OpenAI(api_key=api_key))

client = create_client()
image_client = create_image_client()