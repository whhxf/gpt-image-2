#!/usr/bin/env python3
"""Call GPT-Image-2 API via geekai.co and download generated images."""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


API_URL = "https://geekai.co/api/v1/images/generations"
POLL_INTERVAL = 5
MAX_POLLS = 60


def call_api(key: str, payload: dict, async_mode: bool = False) -> dict:
    """Make the API request. Returns the parsed JSON response."""
    data = json.dumps({**payload, "model": "gpt-image-2", "async": async_mode,
                        "response_format": "url"}).encode()
    req = urllib.request.Request(
        API_URL, data=data, method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else str(e)
        return {"error": f"HTTP {e.code}: {body}"}
    except urllib.error.URLError as e:
        return {"error": f"Network error: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def poll_task(key: str, task_id: str) -> dict:
    """Poll async task status until completion or timeout."""
    url = f"https://geekai.co/api/v1/tasks/{task_id}"
    for _ in range(MAX_POLLS):
        req = urllib.request.Request(
            url, method="GET",
            headers={"Authorization": f"Bearer {key}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            status = result.get("status", "")
            if status == "completed":
                return result
            if status in ("failed", "error"):
                return {"error": f"Task failed: {result}"}
        except Exception as e:
            return {"error": f"Poll error: {e}"}
        time.sleep(POLL_INTERVAL)
    return {"error": "Polling timed out"}


def download_image(url_str: str, output_dir: str) -> str:
    """Download an image from URL to output_dir. Returns the saved file path."""
    os.makedirs(output_dir, exist_ok=True)
    # Derive filename from URL or use timestamp
    basename = os.path.basename(urllib.parse.urlparse(url_str).path) or f"image_{int(time.time())}.png"
    # Ensure valid extension
    if not basename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        basename += ".png"
    filepath = os.path.join(output_dir, basename)
    # Avoid overwriting
    base, ext = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(filepath):
        filepath = f"{base}_{counter}{ext}"
        counter += 1

    req = urllib.request.Request(url_str, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
        return filepath
    except Exception as e:
        raise RuntimeError(f"Failed to download {url_str}: {e}")


def main():
    p = argparse.ArgumentParser(description="Generate images with GPT-Image-2")
    p.add_argument("--key", required=True, help="geekai.co API key")
    p.add_argument("--prompt", required=True, help="Image description")
    p.add_argument("--image", help="Single reference image URL (edit mode)")
    p.add_argument("--images", nargs="*", help="Multiple reference image URLs (fusion mode)")
    p.add_argument("--size", default="1024x1024",
                   choices=["1024x1024", "1024x1536", "1536x1024"])
    p.add_argument("--quality", default="medium", choices=["low", "medium", "high"])
    p.add_argument("--output-format", choices=["png", "jpeg", "webp"])
    p.add_argument("--background", choices=["auto", "transparent", "none"])
    p.add_argument("--async", dest="async_mode", action="store_true",
                   help="Use async mode for long generations")
    p.add_argument("--output-dir", default="./generated-images",
                   help="Directory to save images")
    args = p.parse_args()

    # Build request payload
    payload = {
        "prompt": args.prompt,
        "size": args.size,
        "quality": args.quality,
    }
    if args.image:
        payload["image"] = args.image
    if args.images:
        payload["images"] = args.images
    if args.output_format:
        payload["output_format"] = args.output_format
    if args.background:
        payload["background"] = args.background

    # Call API
    print(json.dumps({"status": "calling_api"}), flush=True)
    result = call_api(args.key, payload, async_mode=args.async_mode)

    if "error" in result:
        print(json.dumps({"success": False, "error": result["error"]}), flush=True)
        sys.exit(1)

    # Handle async mode
    if args.async_mode:
        task_id = result.get("id") or result.get("task_id")
        if not task_id:
            print(json.dumps({"success": False, "error": f"No task ID in async response: {result}"}), flush=True)
            sys.exit(1)
        print(json.dumps({"status": "polling", "task_id": task_id}), flush=True)
        result = poll_task(args.key, task_id)
        if "error" in result:
            print(json.dumps({"success": False, "error": result["error"]}), flush=True)
            sys.exit(1)

    # Extract image URLs
    images = []
    # Response format: {"data": [{"url": "...", "revised_prompt": "..."}]}
    for item in result.get("data", []):
        url = item.get("url")
        if not url:
            continue
        try:
            filepath = download_image(url, args.output_dir)
            images.append({"path": filepath, "url": url,
                           "revised_prompt": item.get("revised_prompt", "")})
        except RuntimeError as e:
            print(json.dumps({"success": False, "error": str(e)}), flush=True)
            sys.exit(1)

    if not images:
        print(json.dumps({"success": False, "error": "No image URLs in API response"}), flush=True)
        sys.exit(1)

    print(json.dumps({"success": True, "images": images}, indent=2), flush=True)


if __name__ == "__main__":
    main()
