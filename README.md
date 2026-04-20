# podcast

把文章轉成 Podcast 音檔的 Claude Code plugin，支援雙人對談與說書人獨白兩種模式。

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
| `podcast:talk` | 把文章改寫成 `[曉臻]/[雲哲]` 對話腳本 |
| `podcast:tell` | 把文章改寫成 `[說書人]` 獨白腳本 |
| `podcast:audio` | 把腳本合成 mp3，支援雙人對談與說書人兩種格式 |

## Workflow

```
# 雙人對談
文章 → podcast:talk → 對話腳本.txt → podcast:audio → mp3

# 說書人獨白
文章 → podcast:tell → 說書腳本.txt → podcast:audio → mp3
```

## License

Apache License 2.0 — Copyright 2026 [cowbear6598](https://github.com/cowbear6598).

任何使用、修改、再發布請保留 `LICENSE` 與 `NOTICE` 檔案，並標註作者 cowbear6598。

## Acknowledgements

- [edge-tts](https://github.com/rany2/edge-tts) — Microsoft Edge TTS Python wrapper (GPL v3)
