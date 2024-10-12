import instructor
from openai import OpenAI
from pydantic import BaseModel
from config import Config, ModelType
from client_factory import image_client
import base64
import os
from prompts import Prompts
 

class ImageProcessor:
    def __init__(self):
        self.client = image_client
 
        
    def make_api_call(self, prompt: str, image_data: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_IMAGE_MODEL,
                # Use the vision model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                        ]
                    }
                ],
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in API call: {str(e)}"
#         except Exception:
#             # Return the hardcoded response on error
#             return """
#             {
#                 "plan_name": "Hayyak 20",
#                 "validity": "4 Weeks",
#                 "units": {
#                     "data_allowance": "34 GB",
#                     "flexi_minutes": "650 min"
#                 },
#                 "price": "20 OMR"
#             }
#             """
          


    def extract_image_content(self, image_data: str) -> str:
        return self.make_api_call(Prompts.IMAGE_PRODUCT_EXTRACTION, image_data)







