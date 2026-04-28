# gpt-image-2

A Claude Code skill for generating, editing, and fusing images using OpenAI's GPT-Image-2 model via the [geekai.co](https://geekai.co) API.

## Quick Start

Install as a Claude Code skill:

```bash
# Clone into your skills directory
git clone https://github.com/whhxf/gpt-image-2.git ~/.claude/skills/gpt-image-2
```

### Set up your API key

Get an API key from [geekai.co](https://docs.geekai.co/cn/docs/quick_start), then set it as an environment variable:

```bash
export GEEKAI_API_KEY="sk-..."
```

Or save it to `~/.config/geekai/key.txt` (single line, no quotes).

### Generate your first image

Just tell Claude what you want:

```
画一只赛博朋克风格的东京夜景，霓虹灯光，雨夜街道
```

The skill automatically handles three modes:

| Mode | Input | Parameter |
|------|-------|-----------|
| **Text-to-image** | Text description only | `prompt` |
| **Image edit** | One reference image + text | `image` + `prompt` |
| **Image fusion** | Multiple reference images + text | `images` + `prompt` |

## CLI Usage

You can also use the helper script directly:

```bash
python scripts/generate.py \
  --key "$GEEKAI_API_KEY" \
  --prompt "A cat playing in the garden" \
  --size 1024x1024 \
  --quality medium \
  --output-dir ./generated
```

### Parameters

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--prompt` | string | *required* | Text description of the desired image |
| `--key` | string | *required* | Your geekai.co API key |
| `--image` | URL | — | Single reference image (edit mode) |
| `--images` | URLs | — | Multiple reference images (fusion mode) |
| `--size` | `1024x1024`, `1024x1536`, `1536x1024` | `1024x1024` | Image dimensions |
| `--quality` | `low`, `medium`, `high` | `medium` | Generation quality |
| `--output-format` | `png`, `jpeg`, `webp` | API default | Output format |
| `--background` | `auto`, `transparent`, `none` | API default | Background handling |
| `--async` | flag | sync mode | Use async polling for long generations |
| `--output-dir` | path | `./generated-images` | Where to save downloaded images |

### Price Reference

| quality | 1024×1024 | 1024×1536 | 1536×1024 |
|---------|-----------|-----------|-----------|
| low | ¥0.048 | ¥0.040 | ¥0.040 |
| medium | ¥0.398 | ¥0.310 | ¥0.310 |
| high | ¥1.586 | ¥1.240 | ¥1.240 |

Prices may be lower with discount channels — see [geekai pricing docs](https://docs.geekai.co/cn/docs/model_price).

## Prompt Tips

- Be specific about subject, style, lighting, and composition
- Include artistic style references (e.g., "watercolor illustration", "photorealistic")
- Mention mood, atmosphere, and color palette when relevant
- For image fusion: describe which elements from each source to preserve

## License

MIT
