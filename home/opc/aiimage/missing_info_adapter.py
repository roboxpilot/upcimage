import json
import json
from typing import Dict, Any
from fastapi import HTTPException
from config import Config, ModelType
from exceptions import APICallError, JSONParseError
from prompts import Prompts
from conversation_adapter import ConversationRequest
from schemas import CurrentMessage

class MissingInfoAdapter:
    def __init__(self, client):
        self.client = client

    def generate_missing_info_prompt(self, conversation: ConversationRequest, missing_field: str) -> str:
        conversation_history = json.dumps([
            {"role": "user" if msg.get("source") == "user" else "assistant", "content": msg.get("payload").get("text")}
            for msg in conversation.get("previousMessages")
        ], indent=2)
        return Prompts.MISSING_INFO_PROMPT.format(
            missing_field=missing_field,
            conversation_history=conversation_history
        )

    def make_api_call(self, prompt: str) -> str:
        try:
            if Config.SELECTED_MODEL == ModelType.GROQ:
                response = self.client.chat.completions.create(
                    model=Config.get_model_name(),
                    messages=[
                        {"role": "system", "content": "You are AARYA, a helpful AI sales assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150
                )
                return response.choices[0].message.content
            elif Config.SELECTED_MODEL == ModelType.OPENAI:
                response = self.client.chat.completions.create(
                    model=Config.get_model_name(),
                    messages=[
                        {"role": "system", "content": "You are AARYA, a helpful AI sales assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150
                )
                return response.choices[0].message.content
            elif Config.SELECTED_MODEL == ModelType.CLAUDE:
                response = self.client.completions.create(
                    model=Config.get_model_name(),
                    prompt=f"Human: {prompt}\n\nAssistant:",
                    max_tokens_to_sample=150
                )
                return response.completion
        except Exception as e:
            raise APICallError(Config.SELECTED_MODEL.value, str(e))

    def process_request(self, request: ConversationRequest) -> str:
        try:
            print('99999999999999999999999',request)
            missing_field = request.get("currentMessage").get("status")
            print(f"Missing field info recived from BL: {missing_field}")
            prompt = self.generate_missing_info_prompt(request, missing_field)
            response = self.make_api_call(prompt)

            return response.strip()
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Missing key in request data: {str(e)}")
        except json.JSONDecodeError:
            raise JSONParseError()