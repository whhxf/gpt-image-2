---
name: gpt-image-2
description: Generate, edit, and fuse images using OpenAI's GPT-Image-2 model via geekai.co API. Use this skill whenever the user wants to create images from text descriptions, edit or modify existing images with AI, combine multiple reference images into a new composition, or generate visual assets. Trigger when the user mentions generating images, drawing pictures, creating visuals, editing photos, image fusion, or any request that involves producing or modifying images.
---

## Quick start

This skill generates images using the GPT-Image-2 model. It handles all three modes automatically:
- **Text-to-image**: describe what you want in words
- **Image edit**: provide a reference image + describe the change
- **Image fusion**: provide multiple reference images + describe how to combine them

## Prerequisites

You need a geekai.co API key. Check for it in this order:
1. Environment variable `GEEKAI_API_KEY`
2. Local config file `~/.config/geekai/key.txt` (single line with the key)
3. If neither exists, tell the user: "I need your geekai.co API key to generate images. Set it as the environment variable `GEEKAI_API_KEY` or put it in `~/.config/geekai/key.txt`. You can get one at [the docs](https://docs.geekai.co/cn/docs/quick_start)." and stop.

## Workflow

### 1. Determine the mode

Look at what the user provided:
- **Text only** → text-to-image mode
- **One image URL or file path** → image edit mode (use the `image` parameter)
- **Two or more image URLs or file paths** → image fusion mode (use the `images` parameter)

If the user didn't specify size or quality, use the defaults: `1024x1024`, `medium`.

### 2. For local file paths: upload or convert to URL first

If the user references a local image file (not a URL), you need to make it accessible to the API. Use the `web-access` skill to upload the image to a temporary hosting service (e.g., imgbb.com free upload or similar), then use the returned URL. Alternatively, if the user has a way to host the image, use that URL.

### 3. Build the API request

Use the helper script at `scripts/generate.py` from this skill's directory:

```bash
python /path/to/skill/scripts/generate.py \
  --key "$GEEKAI_API_KEY" \
  --prompt "your prompt here" \
  [--image "url"] \
  [--images "url1" "url2"] \
  [--size 1024x1024] \
  [--quality low|medium|high] \
  [--output-format png|jpeg|webp] \
  [--background auto|transparent|none] \
  [--output-dir /path/to/save]
```

The script handles:
- Calling the API (sync mode by default)
- Downloading the generated image(s) to the output directory
- Printing the result as JSON: `{ "success": true, "images": [{"path": "...", "url": "..."}], "revised_prompt": "..." }`
- On error: `{ "success": false, "error": "..." }`

If the user wants async mode (for long-running generations), pass `--async` and the script will poll for results.

### 4. Show the result

After a successful generation:
- Display the saved image using the Read tool (it accepts image files)
- Show the revised prompt if the API returned one
- Report any relevant details (cost estimate if you can calculate it)

### 5. Handle errors

If the API returns an error:
- **Authentication error (401)**: the API key is invalid or missing — tell the user to check their key
- **Rate limit (429)**: tell the user the rate limit was hit and to wait before retrying
- **Content policy violation**: explain what was flagged
- **Timeout or network error**: suggest retrying once

## API reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | `gpt-image-2` | Model ID (fixed) |
| `prompt` | string | required | Text description of the desired image |
| `image` | string | — | Single reference image URL (for image edit) |
| `images` | array | — | Multiple reference image URLs (for image fusion) |
| `size` | string | `1024x1024` | One of: `1024x1024`, `1024x1536`, `1536x1024` |
| `quality` | string | `medium` | One of: `low`, `medium`, `high` |
| `output_format` | string | — | One of: `png`, `jpeg`, `webp` |
| `response_format` | string | — | `url` (default) or `b64_json` |
| `background` | string | — | `auto`, `transparent`, or `none` |
| `async` | bool | false | Use async mode for long-running generations |

**Endpoint**: `POST https://geekai.co/api/v1/images/generations`
**Auth**: `Authorization: Bearer <API_KEY>`
**Content-Type**: `application/json`

### Price reference

| quality | 1024x1024 | 1024x1536 | 1536x1024 |
|---------|-----------|-----------|-----------|
| low | ¥0.048 | ¥0.040 | ¥0.040 |
| medium | ¥0.398 | ¥0.310 | ¥0.310 |
| high | ¥1.586 | ¥1.240 | ¥1.240 |

When the user asks about cost, you can estimate it from this table. Actual prices may vary based on the discount channel — check the [geekai docs](https://docs.geekai.co/cn/docs/model_price) for current rates.

## Tips for good prompts

- Be specific about subject, style, lighting, and composition
- Include artistic style references (e.g., "watercolor illustration", "photorealistic", "pixel art")
- Mention mood, atmosphere, and color palette when relevant
- For image fusion: describe which elements from each source should be preserved and how they should combine
