from pydantic import BaseModel, Field

class TextModerationRequest(BaseModel):
    text: str = Field(
        ..., 
        min_length=1, 
        max_length=5000, 
        description="The text content to moderate.",
        strip_whitespace=True, 
        example="This is an example text for moderation."
    )

    class Config:
        str_strip_whitespace = True  