import redis
import json
import base64
from openai import OpenAI
from app.config import REDIS_URL


redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


client = OpenAI()


def get_cached_moderation(key: str):
    """Retrieve cached moderation result from Redis."""
    return redis_client.get(f"moderation:{key}")


def set_cached_moderation(key: str, result: dict, ttl: int = 3600):
    """Cache the moderation result in Redis with a TTL (default 1 hour)."""
    redis_client.setex(f"moderation:{key}", ttl, json.dumps(result))


def analyze_text(text: str):
    """Analyze text using OpenAI Moderation API and cache the result."""
    cached_result = get_cached_moderation(text)
    if cached_result:
        return json.loads(cached_result)

    response = client.moderations.create(
        model="omni-moderation-latest",
        input={"type": "text", "text": text},
    )

    moderation_result = response.results[0]  


    set_cached_moderation(text, moderation_result)

    return moderation_result


def analyze_image(base64_image: str):
    """Analyze image using OpenAI Moderation API and cache the result."""
    cached_result = get_cached_moderation(base64_image)
    if cached_result:
        return json.loads(cached_result)

    response = client.moderations.create(
        model="omni-moderation-latest",
        input={
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
        },
    )

    moderation_result = response.results[0] 


    set_cached_moderation(base64_image, moderation_result)

    return moderation_result
