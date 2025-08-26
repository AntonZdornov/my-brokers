from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel
# langchain

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class SetName(BaseModel):
    title: str
    description: str


def get_set_name(
    prompt="One chillstep set name for focus/coding/relaxing. and description and hashtags",
):
    resp = client.responses.create(
        model="gpt-4o-2024-08-06",
        input=[
            {
                "role": "system",
                "content": "You name music sets min 4 words, Return **only** valid JSON, without any markdown formatting json with keys: title, description, hashtags only separated by commas.",
            },
            {"role": "user", "content": prompt},
        ],
        # text_format=SetName,
        # response_format=SetName,
        # json_schema=SetName,
        temperature=0.7,
    )
    return json.loads(resp.output_text)
