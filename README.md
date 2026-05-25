# podcast

Claude Code plugin for turning articles or YouTube notes into podcast audio and companion MP4 videos.

Supports:

- Two-person talk scripts: `[曉臻]` / `[雲哲]`
- Single narrator scripts: `[說書人]`
- MP3 generation with TTS segment timing
- Captions, visual structure JSON, and HyperFrames MP4 rendering

## Install

```bash
/plugin marketplace add cowbear6598/podcast
/plugin install podcast
```

## Skills

| Skill | Purpose |
|---|---|
| `podcast:setup` | Check ffmpeg, Python, and edge-tts |
| `podcast:talk` | Convert source content into a two-person podcast script |
| `podcast:tell` | Convert source content into a single-narrator script |
| `podcast:audio` | Generate mp3 and TTS timing JSON |
| `podcast:caption` | Generate transcript, SRT, and caption segments |
| `podcast:structure` | Generate `episode_structure.json` |
| `podcast:video` | Render a HyperFrames MP4 |

## Workflow

```text
# Two-person podcast
source -> podcast:talk -> script.txt -> podcast:audio -> episode.mp3 + episode_timing.json

# Single-narrator podcast
source -> podcast:tell -> script.txt -> podcast:audio -> episode.mp3 + episode_timing.json

# Full companion video
source -> podcast:talk or podcast:tell -> podcast:audio -> podcast:caption -> podcast:structure -> podcast:video -> episode.mp4
```

## Commands

Claude Code triggers skills from natural language. These examples show the intended commands and expected outputs.

### Setup

```text
檢查 podcast 環境
```

Runs `podcast:setup` and checks `ffmpeg`, Python, and `edge-tts`.

### Create A Script

```text
把這篇文章改成雙人 podcast 腳本
```

Runs `podcast:talk` and outputs a `[曉臻]/[雲哲]` script.

```text
把這份內容改成說書人獨白
```

Runs `podcast:tell` and outputs a `[說書人]` script.

### Generate Audio

```text
把 script.txt 合成 podcast mp3
```

Runs `podcast:audio` and outputs:

- `episode.mp3`
- `episode_timing.json`

### Generate Captions

```text
用 episode_timing.json 產生字幕
```

Runs `podcast:caption` and outputs:

- `transcript.json`
- `subtitles.srt`
- `caption_segments.json`

### Generate Video Structure

```text
幫這集 podcast 產生影片結構
```

Runs `podcast:structure` and outputs `episode_structure.json`.

### Render MP4

```text
把 episode_structure.json 和 episode.mp3 做成完整 mp4
```

Runs `podcast:video` and outputs:

- `<episode_slug>_video/`
- `<episode_slug>.mp4`

### Full Automated Flow

```text
把這份 YouTube 分析做成說書人 podcast，產出字幕、影片結構和完整 mp4
```

Expected flow:

```text
podcast:tell -> podcast:audio -> podcast:caption -> podcast:structure -> podcast:video
```

## License

Apache License 2.0 — Copyright 2026 [cowbear6598](https://github.com/cowbear6598).

Keep `LICENSE` and `NOTICE` when using, modifying, or redistributing this project.

## Acknowledgements

- [edge-tts](https://github.com/rany2/edge-tts) — Microsoft Edge TTS Python wrapper (GPL v3)
