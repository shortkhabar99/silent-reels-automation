import os
import sys
import requests

CLOUDINARY_URL = os.environ["CLOUDINARY_URL"]
INSTAGRAM_ID = os.environ["INSTAGRAM_ACCOUNT_ID"]
ACCESS_TOKEN = os.environ["PAGE_ACCESS_TOKEN"]

GRAPH_URL = "https://graph.instagram.com"

def publish_reel(video_url, caption):
    # Create media container
    response = requests.post(
        f"{GRAPH_URL}/{INSTAGRAM_ID}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": "true",
            "access_token": ACCESS_TOKEN
        },
        timeout=60
    )
    response.raise_for_status()

    container_id = response.json()["id"]

    # Check container status
    for attempt in range(30):
        status = requests.get(
            f"{GRAPH_URL}/{container_id}",
            params={
                "fields": "status_code",
                "access_token": ACCESS_TOKEN
            },
            timeout=30
        )
        status.raise_for_status()

        if status.json().get("status_code") == "FINISHED":
            break

        if status.json().get("status_code") == "ERROR":
            raise RuntimeError("Instagram video processing failed")

        import time
        time.sleep(10)
    else:
        raise TimeoutError("Instagram processing timed out")

    # Publish
    result = requests.post(
        f"{GRAPH_URL}/{INSTAGRAM_ID}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": ACCESS_TOKEN
        },
        timeout=60
    )
    result.raise_for_status()

    print("Instagram Reel published:", result.json())


if __name__ == "__main__":
    print("Instagram publishing module ready.")
