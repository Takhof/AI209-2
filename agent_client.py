from pydantic import BaseModel
from agents import Agent, Runner, WebSearchTool, function_tool, ItemHelpers
from utils import get_transcript, openai_chat_retry

class Post(BaseModel):
    platform: str
    content: str

@function_tool
def generate_content(video_transcript: str, social_media_platform: str) -> str:
    prompt = (
        "以下の動画トランスクリプトをもとに、"
        f"{social_media_platform} 用のキャッチーな投稿文を100字以内で作成してね。\n\n"
        f"{video_transcript}"
    )
    resp = openai_chat_retry(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":prompt}],
        max_tokens=150
    )
    return resp.choices[0].message.content 

content_writer_agent = Agent(
    name="ContentWriter",
    instructions="You are a creative social-media writer. Spread joy and insight!",
    model="gpt-4o-mini",
    tools=[generate_content, WebSearchTool()],
    output_type=list[Post],
)