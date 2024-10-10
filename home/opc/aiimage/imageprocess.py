import instructor
from openai import OpenAI
from pydantic import BaseModel
import base64
import os
from prompts import Prompts
from dotenv import load_dotenv

load_dotenv()

class ImageProcessor:
    def __init__(self, api_key):
        self.client = instructor.patch(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))

    def make_api_call(self, prompt: str, image_data: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Use the vision model
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

    def extract_image_content(self, image_data: str) -> str:
        return self.make_api_call(Prompts.IMAGE_PRODUCT_EXTRACTION, image_data)







# from openai import OpenAI

# class ImageProcessor:
#     def __init__(self, api_key):
#         self.client = OpenAI(api_key="sk-None-yjdh1eHVAQf8eC7Iaq6CT3BlbkFJrBJZE1y99Fr3Pvwjld8R")

#     def encode_image(self, image_data: str) -> str:
#         # Assuming image_data is already base64 encoded
#         return image_data

#     def make_api_call(self, prompt: str, image_data: str) -> str:
#         try:
#             response = self.client.chat.completions.create(
#                 model="gpt-4o-mini",  # Specify the model directly
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": [
#                             {"type": "text", "text": prompt},
#                             {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
#                         ]
#                     }
#                 ],
#                 max_tokens=300
#             )
#             return response.choices[0].message.content
#         except Exception as e:
#             return f"Error in API call: {str(e)}"

#     def extract_image_content(self, image_data: str) -> str:
#         prompt = '''Analyze the handwritten content from the provided image and extract the relevant proper query format. 
# 1. Please only provide what is present in the image. Do not include any extra information.
# 2. Ensure that there are no mistakes in the extracted content.
# 3. Do not add extra quotes or formatting.
# Format the output as a clean NLP query based on the content in the image.'''
        
#         encoded_image = self.encode_image(image_data)
#         return self.make_api_call(prompt, encoded_image)


