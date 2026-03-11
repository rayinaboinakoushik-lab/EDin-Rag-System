import requests

API_KEY = "AIzaSyCxMe6U4W5ovKLclyQgjm-iB9Gx3ZolIV0"

def fetch_video_metadata(channel_id, max_results=16):
    """
    Fetch metadata for the latest videos from a YouTube channel.
    Returns a list of dicts with keys: video_id, title, published_at
    """
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?key={API_KEY}&channelId={channel_id}&part=snippet&order=date&maxResults={max_results}"
    )
    response = requests.get(url)
    data = response.json()

    videos_list = []
    for item in data.get("items", []):
        video_id = item["id"].get("videoId")
        if not video_id:
            continue  # skip non-video items like playlists
        title = item["snippet"]["title"]
        published_at = item["snippet"]["publishedAt"]

        videos_list.append({
            "video_id": video_id,
            "title": title,
            "published_at": published_at
        })

    return videos_list


if __name__ == "__main__":
    # Optional test when running this file directly
    CHANNEL_ID = "UCmeSC2WkskoLgOV5aVGlRrg"
    videos = fetch_video_metadata(CHANNEL_ID,max_results=16)
    print(len(videos))
    for v in videos:
        print(v)
