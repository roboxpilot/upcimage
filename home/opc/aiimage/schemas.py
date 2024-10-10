from typing import List, Dict, Any, Union
from pydantic import BaseModel, Field
from typing import Optional
class Message(BaseModel):
    role: str = Field(..., example="user")
    content: str = Field(..., example="Please activate Data_1_GB")

class PlanRequest(BaseModel):
    message: List[Message] = Field(
        default=[
            Message(role="system", content="Hi @username! I am AARYA (Automated AI Responder for Your Applications). What are you looking for today?"),
            Message(role="user", content="Hi, I need a list of available packs!"),
            Message(role="assistant", content="Sure, I can help you with that. What kind of packs are you looking for? We have data packs, voice packs, and combo packs available."),
            Message(role="user", content="I'm interested in data packs. Can you show me the options?"),
            Message(role="assistant", content="Certainly! Here are our available data packs:\n1. Data_200_MB: 200 MB for 1 day at $2\n2. Data_500_MB: 500 MB for 7 days at $5\n3. Data_1_GB: 1 GB for 30 days at $10\nWhich one would you like more information about?"),
            Message(role="user", content="The Data_1_GB pack sounds good. Can you tell me more about it?"),
            Message(role="assistant", content="Certainly! The Data_1_GB pack offers:\n- 1 GB of high-speed data\n- Valid for 30 days\n- Priced at $10\n- No daily usage limit\n- Suitable for moderate data users\nWould you like to activate this pack?"),
            Message(role="user", content="Yes, please activate the Data_1_GB pack for me.")
        ],
        example=[
            {"role": "system", "content": "Hi @username! I am AARYA (Automated AI Responder for Your Applications). What are you looking for today?"},
            {"role": "user", "content": "Hi, I need a list of available packs!"},
            {"role": "assistant", "content": "Sure, I can help you with that. What kind of packs are you looking for? We have data packs, voice packs, and combo packs available."},
            {"role": "user", "content": "I'm interested in data packs. Can you show me the options?"},
            {"role": "assistant", "content": "Certainly! Here are our available data packs:\n1. Data_200_MB: 200 MB for 1 day at $2\n2. Data_500_MB: 500 MB for 7 days at $5\n3. Data_1_GB: 1 GB for 30 days at $10\nWhich one would you like more information about?"},
            {"role": "user", "content": "The Data_1_GB pack sounds good. Can you tell me more about it?"},
            {"role": "assistant", "content": "Certainly! The Data_1_GB pack offers:\n- 1 GB of high-speed data\n- Valid for 30 days\n- Priced at $10\n- No daily usage limit\n- Suitable for moderate data users\nWould you like to activate this pack?"},
            {"role": "user", "content": "Yes, please activate the Data_1_GB pack for me."}
        ]
    )
    product_schema: Dict[str, Any] = Field(
        default={
            "price": 0,
            "validity": 0,
            "validity_time_period": "string",
            "daily_limit": "string",
            "voice_unit": "string",
            "voice_unit_value": "string",
            "data_unit_value": "string",
            "data_unit": "string"
        },
        example={
            "price": 10,
            "validity": 30,
            "validity_time_period": "days",
            "daily_limit": "N/A",
            "voice_unit": "N/A",
            "voice_unit_value": "N/A",
            "data_unit_value": "1",
            "data_unit": "GB"
        }
    )
    product_schema: Dict[str, Any] = Field(
        default={
            "price": 0,
            "validity": 0,
            "validity_time_period": "string",
            "daily_limit": "string",
            "voice_unit": "string",
            "voice_unit_value": "string",
            "data_unit_value": "string",
            "data_unit": "string"
        },
        example={
            "price": 20,
            "validity": 1,
            "validity_time_period": "month",
            "daily_limit": "N/A",
            "voice_unit": "minutes",
            "voice_unit_value": "200",
            "data_unit_value": "300",
            "data_unit": "MB"
        }
    )

from pydantic import BaseModel
from typing import Union

# class ProductMessage(BaseModel):
#     product_name: str
#     price: str
#     validity: str
#     validity_time_period: str
#     daily_limit: str
#     voice_unit: str
#     voice_unit_value: str
#     data_unit_value: str
#     data_unit: str

class ProductMessage(BaseModel):
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    product_family: Optional[str] = None
    product_group: Optional[str] = None
    Product_offer_price: Optional[str] = None
    pop_type: Optional[str] = None
    price_category: Optional[str] = None
    price_mode: Optional[str] = None
    product_specification_type: Optional[str] = None
class CurrentMessage(BaseModel):
    messageTime: Optional[str] = Field(None, exclude=True)
    messageId: Optional[str] = Field(None, exclude=True)
    source: str = Field(default="AI")
    status: str = Field(default="success")
    messageType: str = Field(default="text")
    payload:  Union[Dict[str, Any], str, ProductMessage]


    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            # Add any custom JSON encoders here if needed
        }
        exclude_none = True

class CurrentMessageResponse(BaseModel):
    messageTime: str
    messageId: str
    source: str
    status: str
    messageType: str
    payload: Dict[str, Any]

class PlanResponse(BaseModel):
    conversationId: Optional[str] = Field(None, example="conv-12345",exclude=True)
    currentMessage: Optional[CurrentMessage] = Field(None, example={
        "messageTime": "2024-08-02T10:53:07.954204Z",
        "messageId": "msg-789",
        "source": "AI",
        "status": "success",
        "messageType": "text",
        "payload": {"text": "Hello! How can I assist you today?"}
    })

    class Config:
        json_encoders = {
            # Add any custom JSON encoders here if needed
        }
        exclude_none = True
class PlanResponseBack(BaseModel):
    conversationId: Optional[str] = Field(None, example="conv-12345")
    currentMessage: Optional[CurrentMessageResponse] = Field(None, example={
        "messageTime": "2024-08-02T10:53:07.954204Z",
        "messageId": "msg-789",
        "source": "AI",
        "status": "success",
        "messageType": "text",
        "payload": {"text": "Hello! How can I assist you today?"}
    })