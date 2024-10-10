from dotenv import load_dotenv
import os
from enum import Enum

# Load environment variables from .env file
load_dotenv()

class ModelType(Enum):
    GROQ = "groq"
    OPENAI = "openai"
    CLAUDE = "claude"

class Config:
    # FastAPI settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Selected model
    SELECTED_MODEL: ModelType = ModelType(os.getenv("SELECTED_MODEL", ModelType.OPENAI.value))

    # API keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY")

    # Model-specific settings
    GROQ_MODEL: str = "llama3-70b-8192"
    OPENAI_MODEL: str = "gpt-4o-mini"
    CLAUDE_MODEL: str = "claude-2"

    @classmethod
    def get_api_key(cls) -> str:
        if cls.SELECTED_MODEL == ModelType.GROQ:
            return cls.GROQ_API_KEY
        elif cls.SELECTED_MODEL == ModelType.OPENAI:
            return cls.OPENAI_API_KEY
        elif cls.SELECTED_MODEL == ModelType.CLAUDE:
            return cls.CLAUDE_API_KEY
        else:
            raise ValueError(f"Invalid model selected: {cls.SELECTED_MODEL}")

    @classmethod
    def get_model_name(cls) -> str:
        if cls.SELECTED_MODEL == ModelType.GROQ:
            return cls.GROQ_MODEL
        elif cls.SELECTED_MODEL == ModelType.OPENAI:
            return cls.OPENAI_MODEL
        elif cls.SELECTED_MODEL == ModelType.CLAUDE:
            return cls.CLAUDE_MODEL
        else:
            raise ValueError(f"Invalid model selected: {cls.SELECTED_MODEL}")

# Verify environment variables are loaded correctly
if __name__ == "__main__":
    print(f"API_HOST: {Config.API_HOST}")
    print(f"API_PORT: {Config.API_PORT}")
    print(f"SELECTED_MODEL: {Config.SELECTED_MODEL}")
    print(f"GROQ_API_KEY: {Config.GROQ_API_KEY}")
    print(f"OPENAI_API_KEY: {Config.OPENAI_API_KEY}")
    print(f"CLAUDE_API_KEY: {Config.CLAUDE_API_KEY}")