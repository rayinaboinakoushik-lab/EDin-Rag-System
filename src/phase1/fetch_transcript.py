import time
import random
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi

def fetch_transcript_chunks(video_id, languages=("te", "en"), retries=3):
    """
    INSTANCE VERSION: Creates the tool first, then uses it.
    Matches your library's 'list' and 'fetch' methods perfectly.
    """
    cookie_path = "youtube_cookies.txt"
    
    # 1. Create the 'instance' of the API and give it the cookies here
    # This is likely where your version expects the configuration
    try:
        if Path(cookie_path).exists():
            api = YouTubeTranscriptApi(cookies=cookie_path)
        else:
            api = YouTubeTranscriptApi()
    except TypeError:
        # Fallback if your version doesn't take cookies in the constructor
        api = YouTubeTranscriptApi()

    for attempt in range(retries):
        try:
            # 2. Use the 'list' method ON THE INSTANCE (api), not the Class
            # We don't pass cookies here because we gave them to 'api' above
            transcript_list = api.list(video_id)
            
            transcript = transcript_list.find_transcript(list(languages))
            data = transcript.fetch()

            return [
                {
                    "text": p['text'] if isinstance(p, dict) else p.text,
                    "start": p['start'] if isinstance(p, dict) else p.start,
                    "duration": p['duration'] if isinstance(p, dict) else p.duration
                }
                for p in data
            ]

        except Exception as e:
            msg = str(e).lower()
            if "blocked" in msg or "too many requests" in msg:
                wait = random.uniform(60, 90)
                print(f"🛑 Rate limited. Attempt {attempt+1}. Waiting {int(wait)}s...")
                time.sleep(wait)
                continue
            raise e

    raise Exception(f"Failed {video_id} after {retries} retries.")