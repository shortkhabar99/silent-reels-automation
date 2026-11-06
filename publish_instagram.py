
import os
import json
import time
import glob
import hashlib
import requests
from urllib.parse import urlparse, unquote

CLOUDINARY_URL = os.environ["CLOUDINARY_URL"]
INSTAGRAM_ID = os.environ["INSTAGRAM_ACCOUNT_ID"]
ACCESS_TOKEN = os.environ["PAGE_ACCESS_TOKEN"]

GRAPH_URL = "https://graph.instagram.com/v25.0"

STATE_FILE = "publish_state.json"
REEL_FOLDER = "reels"


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"published": []}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def upload_to_cloudinary(video_path):
    parsed = urlparse(CLOUDINARY_URL)

    cloud_name = parsed.hostname
    api_key = unquote(parsed.username or "")
    api_secret = unquote(parsed.password or "")

    if not all([cloud_name, api_key, api_secret]):
        raise ValueError("CLOUDINARY_URL format is incorrect")

    timestamp = int(time.time())
    signature_text = f"timestamp={timestamp}{api_secret}"
    signature = hashlib.sha1(
        signature_text.encode("utf-8")
    ).hexdigest()

    upload_url = (
        f"https://api.cloudinary.com/v1_1/"
        f"{cloud_name}/video/upload"
    )

    with open(video_path, "rb") as video:
        response = requests.post(
            upload_url,
            data={
                "api_key": api_key,
                "timestamp": timestamp,
                "signature": signature
            },
            files={
                "file": (
                    os.path.basename(video_path),
                    video,
                    "video/mp4"
                )
            },
            timeout=300
        )

    response.raise_for_status()
    result = response.json()

    video_url = result.get("secure_url")
    if not video_url:
        raise RuntimeError("Cloudinary did not return a video URL")

    print("Video uploaded to Cloudinary")
    return video_url


def publish_reel(video_url, caption):
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

    print("Instagram media container created:", container_id)

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
        status_code = status.json().get("status_code")

        print("Video processing:", status_code)

        if status_code == "FINISHED":
            break

        if status_code == "ERROR":
            raise RuntimeError("Instagram video processing failed")

        if status_code == "EXPIRED":
            raise RuntimeError("Instagram media container expired")

        time.sleep(10)
    else:
        raise TimeoutError("Instagram processing timed out")

    result = requests.post(
        f"{GRAPH_URL}/{INSTAGRAM_ID}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": ACCESS_TOKEN
        },
        timeout=60
    )

    result.raise_for_status()
    print("SUCCESS! Instagram Reel published:", result.json())


def main():
    os.makedirs(REEL_FOLDER, exist_ok=True)

    state = load_state()
    published = state.get("published", [])

    reel_files = sorted(
        glob.glob(os.path.join(REEL_FOLDER, "*.mp4"))
    )

    if not reel_files:
        print("No MP4 reels found in reels folder.")
        return

    next_reel = next(
        (f for f in reel_files if f not in published),
        None
    )

    if next_reel is None:
        print("All available Reels have been published.")
        return

    print("Selected Reel:", next_reel)

    video_url = upload_to_cloudinary(next_reel)

    caption = (
        "ताजा खबर र अपडेटका लागि Khabar.short फलो गर्नुहोस्।\n\n"
        "#KhabarShort #NepalNews #BreakingNews #NewsUpdate"
    )

    publish_reel(video_url, caption)

    published.append(next_reel)
    state["published"] = published
    save_state(state)

    print("Completed. Next Reel will be selected in the next run.")


if __name__ == "__main__":
    main()
