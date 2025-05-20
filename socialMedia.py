import asyncio
import os
from youtube_transcript_api import YouTubeTranscriptApi
from agents import Agent, Runner, WebSearchTool, function_tool, ItemHelpers
from openai import OpenAI
from dotenv import load_dotenv


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)