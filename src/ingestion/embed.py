from typing import List
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    text = text.replace("\n", " ")
    response = await client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding
