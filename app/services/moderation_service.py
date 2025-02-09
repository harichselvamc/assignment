from openai import OpenAI

client = OpenAI()

def analyze_text(text: str):
    response = client.moderations.create(
        model="omni-moderation-latest",
        input=text
    )
    return response.results[0]  
