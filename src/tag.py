# Main production script for tag and description extraction.
from typing import List, Optional
from pydantic import BaseModel
from ollama import chat


class TagAndDescription(BaseModel):
    description: str
    tag: str
    existing_tags: List[str]

default_starting_tags = [
    "code-snippets",
    "chat/messages",
    "web article",
    "dashboard/data viz",
    "fashion",
    "random"
]

derivation_prompt = """
You are an elite executive assistant.
Your role is to describe a screenshot/image that is passed to you AND then return relevant tag.
The tag will be used to organize and index screenshots so make sure to accurately do the tagging.
Return your output in a JSON format. Here's a sample output:

{
    "description": "some_description_of_the_screenshot",
    "tag": "tag1",
    "existing_tags": ["tag1", "tag2", "tag3"]
}
"""

def get_description_and_tag_for_image(
    path: str,
    prompt: str = derivation_prompt,
    starting_tags: Optional[List[str]] = None
) -> TagAndDescription:
    if starting_tags is None:
        starting_tags = default_starting_tags
    
    prompt_with_tags = (
        f"{prompt.strip()}\n\n"
        f"Please choose the most appropriate tag for this image, selecting from the following list if possible:\n"
        f"{starting_tags}.\n"
        "If none of these tags are appropriate, you may suggest a new one."
    )

    class TagAndDescriptionWithChoices(TagAndDescription):
        existing_tags: List[str] = starting_tags  # Pydantic will use this as a default value

    response = chat(
        model="llava:7b",
        messages=[
            {
                "role": "user",
                "content": prompt_with_tags,
                "images": [path],
            }
        ],
        format=TagAndDescriptionWithChoices.model_json_schema(),
    )

    td_object = TagAndDescriptionWithChoices.model_validate_json(response.message.content)
    return td_object

if __name__ == "__main__":
    result = get_description_and_tag_for_image("/Users/ten-jampa/Documents/llm-pipeline-portfolio/screenshot-tagger/test-images/me_with_newton.jpg")
    print(result.description)
    print(result.tag)
    print(result.existing_tags)