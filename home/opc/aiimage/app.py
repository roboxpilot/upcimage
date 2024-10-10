from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List
from conversation_adapter import *
import client_factory
from schemas import PlanRequest, PlanResponse, CurrentMessage, ProductMessage
from schemas import *
from config import Config
from exceptions import APICallError, JSONParseError, InvalidModelError
from missing_info_adapter import MissingInfoAdapter
from conversation_adapter import ConversationRequest, handle_conversation, handle_conversation_general, format_messages, \
    User
from plan_extractor import extract_plan ,form_final_message ,check_confirmation
from datetime import datetime
from prompts import PRODUCT_CONVERSATION_CLASSIFIER_PROMPT
from plan_extractor import make_api_call
from imageprocess import ImageProcessor
import json
import logging
import aiofiles
import base64

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()


def is_product_related(message: str) -> bool:
    """
    Check if the given message is related to product creation using LLM.
    """
    prompt = PRODUCT_CONVERSATION_CLASSIFIER_PROMPT.format(message=message)
    try:
        response = make_api_call(prompt)
        print(f"----------------------------classification",response)
        response_data = json.loads(response)
        return response_data['classification'] == 'product_related'
    except (APICallError, JSONParseError) as e:
        # Log the error and fall back to a default behavior
        print(f"Error in LLM classification: {str(e)}")
        # Fallback: assume it's product-related to err on the side of caution
        return True


# @app.post("/extract_plan", response_model=PlanResponse)
# async def extract_plan_endpoint(request: PlanRequest):
#     result = extract_plan(request.message, request.product_schema)
#     return PlanResponse(**result)
#

client = client_factory.client


@app.post("/handle_missing_info", response_model=PlanResponse)
async def handle_missing_info(request_data: Dict[str, Any]):
    print(f"Received request_data in missing info : {json.dumps(request_data)}")
    adapter = MissingInfoAdapter(client)
    try:
        response = adapter.process_request(request_data)
        return PlanResponse(
            conversationId="1234",
            currentMessage=CurrentMessage(
                messageTime=datetime.utcnow().isoformat() + "Z",
                messageId=request_data.get("currentMessage").get("messageId"),
                source="AI",
                status="success",
                messageType="text",
                payload={"text": response}
            )
        )
        return {"response": response}
    except HTTPException as e:
        logger.error(f"Error in handle_missing_info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
        

class SenderInfo(BaseModel):
    name: str = Field(..., example="USER123")
    phoneNumber: str = Field(..., example="1234567899")


class GreetingRequest(BaseModel):
    sender: SenderInfo = Field(..., example={
        "name": "USER123",
        "phoneNumber": "1234567899"
    })


@app.post("/greeting", response_model=PlanResponse)
async def greeting(request: GreetingRequest):
    print("Received request", json.dumps(request.dict()))
    user_name = request.sender.name
    resp = handle_greeting(user_name)
    return PlanResponse(
        currentMessage=CurrentMessage(
            source="AI",
            status="success",
            messageType="text",
            payload={"text": resp}
        )
    )


def process_payload(payload):
    for key, value in payload.items():
        if value == "0" or value == 0:
            payload[key] = "None"
    return payload

def check_fields(data):
    bool = all(value is not None and value != "" for key, value in data.items() if key != "product_description")
    print(f"the boolean in check field is {bool}")
    # return all(value is not None and value!= "" for value in data.values())
    return all(value is not None and value != "" for key, value in data.items() if key != "product_description")

@app.post("/conversation", response_model=PlanResponse)
async def conversation_endpoint(request: ConversationRequest):
    try:
#         print("Received request", request.dict())
        
        # Handle image messages
        if request.currentMessage.messageType == "image":
            print("processing image")
            image_processor = ImageProcessor(client)  # Assuming 'client' is defined elsewhere
            image_data = request.currentMessage.payload.image 
            
            
            extracted_content = image_processor.extract_image_content(image_data)
            print("************", extracted_content)
            
            # Replace the image payload with the extracted content
            request.currentMessage.payload.image = extracted_content
            request.currentMessage.messageType = "text"
            request.currentMessage.payload.text = extracted_content
        
        # Proceed with normal message handling
        all_messages = request.previousMessages + [request.currentMessage]
        formatted_messages1 = format_messages(all_messages)
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in formatted_messages1]
        messages = json.dumps(formatted_messages, indent=2)
        print('messagesssssssssssssssss--------------->>>>>>>>>>>>>>>>>>>>>',messages)
#         all_messages = request.previousMessages + [request.currentMessage]
#         formatted_messages1 = format_messages(all_messages)
#         formatted_messages = [{"role": msg.role, "content": msg.content} for msg in formatted_messages1]
#         messages = json.dumps(formatted_messages, indent=2)
 
        if is_product_related(messages):
            print('messagesssssssssssssssss',messages)
            extracted_plan = await handle_conversation(request)
            if check_fields(extracted_plan):
                if check_confirmation(messages):
                    final_message = "the product has been created successfully "
                    var = {
                        "text": final_message
                    }
                    return PlanResponse(
                        conversationId=request.conversationId,
                        currentMessage=CurrentMessage(
                            messageTime=datetime.utcnow().isoformat() + "Z",
                            messageId=request.currentMessage.messageId,
                            source="AI",
                            status="success",
                            messageType="product",
                            payload=ProductMessage(**extracted_plan)
                        )
                    )


                final_message = form_final_message(extracted_plan)
                resp = {"text": final_message}
                return PlanResponse(
                    conversationId=request.conversationId,
                    currentMessage=CurrentMessage(
                        messageTime=datetime.utcnow().isoformat() + "Z",
                        messageId=request.currentMessage.messageId,
                        source="AI",
                        status="success",
                        messageType="text",
                        payload=resp
                    )
                )

            for key,value in extracted_plan.items():
                if value == "0":
                    extracted_plan[key] = "None"
            print("the extracted information", json.dumps(extracted_plan, indent=2))

            return PlanResponse(
                conversationId=request.conversationId,
                currentMessage=CurrentMessage(
                    messageTime=datetime.utcnow().isoformat() + "Z",
                    messageId=request.currentMessage.messageId,
                    source="AI",
                    status="success",
                    messageType="product",
                    payload=ProductMessage(**extracted_plan)
                )
            )
        else:
            response = handle_conversation_general(messages)
            print("the the conversation response ", response)

            return PlanResponse(
                conversationId=request.conversationId,
                currentMessage=CurrentMessage(
                    messageTime=datetime.utcnow().isoformat() + "Z",
                    messageId=request.currentMessage.messageId,
                    source="AI",
                    status="success",
                    messageType="text",
                    payload={"text": response}
                )
            )
    except Exception as e:
        raise e
        # return PlanResponse(
        #     conversationId=request.conversationId,
        #     currentMessage=CurrentMessage(
        #         messageTime=datetime.utcnow().isoformat() + "Z",
        #         messageId=request.currentMessage.messageId,
        #         source="AI",
        #         status="failure",
        #         messageType="text",
        #         message=f"An error occurred: {str(e)}"
        #     )
        # )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
