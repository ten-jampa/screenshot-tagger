from ollama import chat
from ollama import ChatResponse
import sys


# sys.argv[0] is the script name itself
# sys.argv[1] is the first argument provided


if len(sys.argv) > 1:
	image_path = sys.argv[1]
	print(f"image_path at: {image_path}")
else:
	image_path = input("Which image do you want to process?")

response = chat(
	model = "llava:7b",
	messages = [
		{
			"role":"user",
			"content": "What is in this image? Be detailed and accurate as possible.",
			"images": [image_path],
		}
	],
)

print(response.message.content) 
