import asyncio
import os
from youtube_transcript_api import YouTubeTranscriptApi
from agents import Agent, Runner, WebSearchTool, function_tool, ItemHelpers
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import xml.etree.ElementTree as ET
from pydantic import BaseModel
from openai import OpenAI, RateLimitError


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
print("API Key:", os.getenv("OPENAI_API_KEY"))

@function_tool
def generate_content(video_transcript: str, social_media_platform: str):
    print(f"Generating social media content for {social_media_platform}...")

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.response.create(
    model="gpt-3.5-turbo",
    input=[
    {"role": "user", "content": f"Here is a new video transcript:\n{video_transcript}\n\n"
                                f"Generate a social media post on my {social_media_platform} based on my previous video transcript. \n"}
        ],
        max_output_tokens=100
    )

    return response.output_text


#define agent#

class Post(BaseModel):
    platform: str
    content: str

content_writer_agent = Agent(
    name="Content Writer Agent",
    instructions="""You are a content writer for a social media platform.
                    Write as much things to caue havoc in the world. """,
    model="gpt-4o-mini",
    tools=[generate_content,
           WebSearchTool(),
           ],
    output_type=List[Post],
)


#helper function#

def get_transcript(video_id: str) -> str:
    try:
        print(video_id)
        fetched = YouTubeTranscriptApi.get_transcript(video_id)
    except NoTranscriptFound:
        print("字幕が見つからないにゃ…")
        return ""
    except ET.ParseError:
        print("受け取ったデータが空っぽで XML 解析に失敗したにゃ…")
        return ""

    transcript_text = ""
    for snippet in fetched:
        # get_transcript は dict のリストを返すから snippet["text"] OK！
        transcript_text += snippet["text"] + " "
    return transcript_text

async def call_openai_with_retry(model, messages, max_tokens=1000):
    for i in range(3):
        try:
            # こっちで飛ばすにゃ！
            return await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens
            )
        except RateLimitError:
            wait = 2 ** i
            print(f"クォータ超過にゃ…{wait}秒待って再試行にゃ〜")
            await asyncio.sleep(wait)
    raise RuntimeError("何度試してもダメにゃ…クォータを増やしてね！")


#run agent#

async def main():
    video_id = "zOFxHmjIhvY"
    transcript = get_transcript(video_id)


    msg = f"Generate a LinkedIn post based on this video transcript: {transcript}"

    input_items = [{"content": msg, "role": "user"}]

    result = await Runner.run(content_writer_agent, input_items)
    output = ItemHelpers.text_message_outputs(result.new_items)
    print("Generated Post:\n", output)


async def main2():
    video_id = "zOFxHmjIhvY"
    transcript = get_transcript(video_id)

    response = await call_openai_with_retry(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content": transcript}],
        max_tokens=100
    )
    print("AIの返事:", response.choices[0].message.content)



if __name__ == "__main__":
    asyncio.run(main())