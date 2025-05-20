import asyncio
from config import YOUTUBE_AGENT_VIDEO_ID
from utils import extract_video_id, get_transcript
from agent_client import content_writer_agent, Post   # ← Post をインポート！
from agents import Runner

async def main():
    # 1. 動画ID の正規化＆トランスクリプト取得
    vid = extract_video_id(YOUTUBE_AGENT_VIDEO_ID)
    print(vid)
    transcript = get_transcript(vid)
    if not transcript:
        print("トランスクリプトが取得できませんでした…")
        return

    # 2. Agent 実行
    user_msg = f"Generate a Facebook post based on this transcript:\n{transcript}"
    items = [{"role": "user", "content": user_msg}]
    result = await Runner.run(content_writer_agent, items)
    print(dir(result))

    # 3. 直接 Post オブジェクトを取り出してループ
    posts: list[Post] = result.final_output_as(list[Post])
    for post in posts:
        print(f"--- {post.platform} ---")
        print(post.content)
        print()

if __name__ == "__main__":
    asyncio.run(main())