from typing import List, Dict, Any
import json

import instructor

from config import Config, ModelType
from exceptions import APICallError, JSONParseError
from schemas import Message,ProductMessage
from prompts import Prompts
from client_factory import client
import random

def check_confirmation(messages):

    prompt = Prompts.CONFIRMATION_MESSAGE_CHECKER.format(message=json.dumps(messages, indent=2))
    print(f"the prompt for confirmation is {prompt}")
    response = make_api_call(prompt)
    print(f"-----------------------------Confirmation message: {response}")
    response  = response.lower()
    if response == 'true':
        return True
    elif response == 'false':
        return False


def form_final_message(extracted_plan):
    prompt = Prompts.FINAL_MESSAGE_TEMPLATE.format(schema=json.dumps(extracted_plan, indent=2))
    response = make_api_call(prompt)
    return response.strip()

def make_api_call_instruct(prompt: str) -> str:
    try:
        print(f"the prompt is {prompt}")
        if Config.SELECTED_MODEL == ModelType.GROQ:
            inst_client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)
            resp = inst_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant that extracts information and formats it as JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                response_model=ProductMessage,
            )
            print(f"the response is form instruct api is {resp.model_dump_json(indent=2)}")
            return resp.json()

    except Exception as e:
        raise APICallError(Config.SELECTED_MODEL.value, str(e))
def make_api_call(prompt: str) -> str:
    try:
        print(f"the prompt is {prompt}")
        if Config.SELECTED_MODEL == ModelType.GROQ:
            response = client.chat.completions.create(
                model=Config.get_model_name(),
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant that extracts information and formats it as JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400
            )
            print(f"the response is {response.choices[0].message.content}")
            return response.choices[0].message.content
        elif Config.SELECTED_MODEL == ModelType.OPENAI:
            response = client.chat.completions.create(
                model=Config.get_model_name(),
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant that extracts information and formats it as JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200
            )
            return response.choices[0].message.content
        elif Config.SELECTED_MODEL == ModelType.CLAUDE:
            response = client.completions.create(
                model=Config.get_model_name(),
                prompt=f"Human: {prompt}\n\nAssistant:",
                max_tokens_to_sample=200
            )
            return response.completion
    except Exception as e:
        raise APICallError(Config.SELECTED_MODEL.value, str(e))


def generate_extraction_prompt(product_schema: Dict[str, Any]) -> str:
    prompt = Prompts.GENERATE_EXTRACT_PROMPT.format(product_schema=json.dumps(product_schema, indent=2))
    response = make_api_call(prompt)
    return response.strip()


def extract_plan(messages: List[Message], product_schema: Dict[str, Any]) -> Dict[str, Any]:
    # extraction_instructions = generate_extraction_prompt(product_schema)
    formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

    # prompt = Prompts.EXTRACT_PLAN.format(
    #     extraction_instructions=extraction_instructions,
    #     messages=json.dumps(formatted_messages, indent=2)
    # )

    prompt = Prompts.PRODUCT_INFO_EXTRACTION.format(messages=json.dumps(formatted_messages, indent=2), product_schema=json.dumps(product_schema, indent=2))

    # json_response = make_api_call(prompt)
    # print(f"--------------------------------Response from API: product extraction  {json_response}")
    # try:
    #     adjectives = ["Super", "Ultra", "Mega", "Giga", "Hyper", "Turbo"]
    #     nouns = ["Pack", "Bundle", "Plan", "Deal", "Offer", "Package"]
    #     random_product_name = f"{random.choice(adjectives)} {random.choice(nouns)}"
    #     plan_data = json.loads(json_response)
    #     # plan_data = {k: str(v) for k, v in plan_data.items()}
    #     # plan_data["product_name"] = random_product_name
    #     return plan_data
    # except json.JSONDecodeError:
    #     print("Invalid JSON")
    #     raise JSONParseError()

    max_retries = 3
    retries = 0

    while retries < max_retries:
        json_response = make_api_call_instruct(prompt)
        print(f"--------------------------------Response from API: product extraction  {json_response}")
        try:
            plan_data = json.loads(json_response)
            break  # Exit loop if parsing is successful
        except json.JSONDecodeError:
            print("Invalid JSON, retrying...")
            retries += 1
            if retries >= max_retries:
                print("Maximum retries reached. Failed to parse valid JSON.")
                raise JSONParseError()
    return plan_data