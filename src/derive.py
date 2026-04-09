from ollama import chat
from ollama import ChatResponse
import sys

derivation_prompt = """
You are an elite executive assistant. 
Your role is to describe a screenshot/image that is passed to you AND then return structure tags.

The structured tags would then be used to organize the screenshots and images so the screenshots are
structurally sound for the user to come and search and look through.
"""

if len(sys.argv)>1:
    image_path = sys.argv[1]
else:
    image_path = input("Add the path for the image")


response = chat(
    model = "llava:7b",
    messages = [
        {
            "role": "user",
            "content": derivation_prompt,
            "images": [image_path]
        }
    ],
)

print(response.message.content)


