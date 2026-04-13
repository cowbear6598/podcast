# podcast

把文章轉成雙人對談 Podcast 音檔的 Claude Code plugin。

## Install

```bash
# 1. Add marketplace
/plugin marketplace add cowbear6598/podcast

# 2. Install plugin
/plugin install podcast
```

## Skills

| Skill | 用途 |
|-------|------|
| `podcast:setup` | 檢查 ffmpeg / edge-tts 安裝環境 |
| `podcast:content` | 把文章改寫成 `[曉臻]/[雲哲]` 對話腳本 |
| `podcast:audio` | 把對話腳本合成成雙人 mp3 |

## Workflow

```
文章 → podcast:content → 對話腳本.txt → podcast:audio → mp3
```

## License

Apache License 2.0 — Copyright 2026 [cowbear6598](https://github.com/cowbear6598).

任何使用、修改、再發布請保留 `LICENSE` 與 `NOTICE` 檔案，並標註作者 cowbear6598。

## Acknowledgements

- [edge-tts](https://github.com/rany2/edge-tts) — Microsoft Edge TTS Python wrapper (GPL v3)
