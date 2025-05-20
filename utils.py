import re
import asyncio
from openai import OpenAI, RateLimitError
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from xml.etree import ElementTree as ET
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_video_id(url_or_id: str) -> str:
    """YouTube URL か ID から純粋な video_id を取り出す"""
    match = re.search(r"(?:v=|youtu\.be/)([\w-]+)", url_or_id)
    return match.group(1) if match else url_or_id

def get_transcript(video_id: str) -> str:
    """YouTube トランスクリプトを取得してひとつの文字列にまとめる"""
    try:
        segments = YouTubeTranscriptApi.get_transcript(video_id)
    except NoTranscriptFound:
        return ""
    except ET.ParseError:
        return ""
    return " ".join(seg["text"] for seg in segments)

async def openai_chat_retry(
    model: str,
    messages: list[dict],
    max_tokens: int = 1000,
    retries: int = 3
):
    """エラー時に指数バックオフでリトライする OpenAI チャット呼び出し"""
    for attempt in range(retries):
        try:
            return await client.chat.completions.acreate(
                model=model,
                messages=messages,
                max_tokens=max_tokens
            )
        except RateLimitError:
            wait = 2 ** attempt
            print(f"[Retry] RateLimit ({wait}s)...")
            await asyncio.sleep(wait)
    raise RuntimeError("OpenAI リクエストに失敗しました。")