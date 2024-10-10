from fastapi import HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from schemas import Message, PlanResponse, ProductMessage
from plan_extractor import extract_plan, make_api_call
from prompts import Prompts


# class MessageContent(BaseModel):
#     text: str = Field(..., example="Please activate Data_1_GB")

class MessageContent(BaseModel):
    text: Optional[str] = Field(None, example="Please activate Data_1_GB")
    image: Optional[str] = Field(None, example="base64_encoded_image_data")


class MessageItem(BaseModel):
    messageTime: datetime = Field(..., example="2024-07-30T10:15:30Z")
    messageId: str = Field(..., example="msg-789")
    source: str = Field(..., example="ui")
    status: str = Field(..., example="success")
    messageType: str = Field(..., example="text")
    payload: MessageContent


class User(BaseModel):
    name: str = Field(..., example="USER123")
    phoneNumber: str = Field(..., example="1234567899")


class ConversationRequest(BaseModel):
    conversationId: str = Field(..., example="conv-12345")
    currentMessage: MessageItem
    sender: User
    previousMessages: List[MessageItem] = Field(
        default=[
            MessageItem(
                messageTime=datetime.strptime("2024-07-30T10:15:30Z", "%Y-%m-%dT%H:%M:%S%z"),
                messageId="msg-123",
                source="ui",
                status="success",
                messageType="text",
                payload=MessageContent(text="Hi, I need a list of available packs!")
            ),
            MessageItem(
                messageTime=datetime.strptime("2024-07-30T10:15:30Z", "%Y-%m-%dT%H:%M:%S%z"),
                messageId="msg-124",
                source="bpmn",
                status="success",
                messageType="text",
                payload=MessageContent(
                    text="Sure, I can help you with that. What kind of packs are you looking for? We have data packs, voice packs, and combo packs available.")
            ),
            MessageItem(
                messageTime=datetime.strptime("2024-07-30T10:15:30Z", "%Y-%m-%dT%H:%M:%S%z"),
                messageId="msg-125",
                source="ui",
                status="success",
                messageType="text",
                payload=MessageContent(text="I'm interested in data packs. Can you show me the options?")
            ),
            MessageItem(
                messageTime=datetime.strptime("2024-07-30T10:15:30Z", "%Y-%m-%dT%H:%M:%S%z"),
                messageId="msg-126",
                source="bpmn",
                status="success",
                messageType="text",
                payload=MessageContent(
                    text="Certainly! Here are our available data packs:\n1. Data_200_MB: 200 MB for 1 day at $2\n2. Data_500_MB: 500 MB for 7 days at $5\n3. Data_1_GB: 1 GB for 30 days at $10\nWhich one would you like more information about?")
            )
        ],
        example=[
            {
                "messageTime": "2024-07-30T10:15:30Z",
                "messageId": "msg-123",
                "source": "ui",
                "status": "success",
                "messageType": "text",
                "message": {
                    "text": "Hi, I need a list of available packs!"
                }
            },
            {
                "messageTime": "2024-07-30T10:15:31Z",
                "messageId": "msg-124",
                "source": "bpmn",
                "status": "success",
                "messageType": "text",
                "message": {
                    "text": "Sure, I can help you with that. What kind of packs are you looking for? We have data packs, voice packs, and combo packs available."
                }
            },
            {
                "messageTime": "2024-07-30T10:15:32Z",
                "messageId": "msg-125",
                "source": "ui",
                "status": "success",
                "messageType": "text",
                "message": {
                    "text": "I'm interested in data packs. Can you show me the options?"
                }
            },
            {
                "messageTime": "2024-07-30T10:15:33Z",
                "messageId": "msg-126",
                "source": "bpmn",
                "status": "success",
                "messageType": "text",
                "message": {
                    "text": "Certainly! Here are our available data packs:\n1. Data_200_MB: 200 MB for 1 day at $2\n2. Data_500_MB: 500 MB for 7 days at $5\n3. Data_1_GB: 1 GB for 30 days at $10\nWhich one would you like more information about?"
                }
            }
        ]
    )




def extract_product_schema(messages: List[MessageItem]) -> Dict[str, Any]:
    return {
        "product_name": "",
        "product_description": "",
        "product_family": "GSM",
        "product_group": "Prepaid",
        "Product_offer_price": "",
        "pop_type": "Normal",
        "price_category": "Base Price",
        "price_mode": "Non-Recurring",
        "product_specification_type": "ADDON"
    }


def format_messages(messages: List[MessageItem]) -> List[Message]:
    # formating msg
    return [
        Message(
            role="user" if msg.source == "ui" else "assistant",
            content=msg.payload.text
        )
        for msg in messages
    ]


def handle_greeting(username: str):
    # handling greeting
    try:
        prompt = Prompts.AI_GREETING_PROMPT.format(
            user_name=username
        )
        response = make_api_call(prompt)
        print(response)
        return response


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def handle_conversation(request: ConversationRequest) -> Dict[str, Any]:
    try:
        all_messages = request.previousMessages + [request.currentMessage]
        product_schema = extract_product_schema(all_messages)
        formatted_messages = format_messages(all_messages)
        extracted_plan = extract_plan(formatted_messages, product_schema)
        plan_response = ProductMessage(**extracted_plan)
        return plan_response.dict()
    except Exception as e:
        print("error ",e)

        raise HTTPException(status_code=500, detail=str(e))


def handle_conversation_general(message):
    prompt = Prompts.AI_RESPONSE_PROMPT.format(incoming_message=message)
    json_response = make_api_call(prompt)
    return json_response
