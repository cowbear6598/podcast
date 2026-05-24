# podcast

把文章轉成 Podcast 音檔與 Podcast 影片的 Claude Code plugin，支援雙人對談、說書人獨白，以及用 HyperFrames 產出 YouTube 版 MP4。

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
| `podcast:audio` | 把腳本合成 mp3 與 TTS timing JSON，支援雙人對談與說書人兩種格式 |
| `podcast:caption` | 用 TTS timing JSON 產生 transcript、SRT 與字幕時間軸 |
| `podcast:structure` | 把腳本、摘要與 mp3 整理成影片結構 JSON |
| `podcast:video` | 把影片結構 JSON 與 mp3 做成完整 MP4 |

## Workflow

```
# 雙人對談
文章 → podcast:talk → 對話腳本.txt → podcast:audio → mp3

# 說書人獨白
文章 → podcast:tell → 說書腳本.txt → podcast:audio → mp3

# Podcast 影片
文章 → podcast:talk/tell → 腳本.txt → podcast:audio → mp3 + timing → podcast:caption → 字幕 → podcast:structure → episode_structure.json → podcast:video → mp4
```

## License

Apache License 2.0 — Copyright 2026 [cowbear6598](https://github.com/cowbear6598).

任何使用、修改、再發布請保留 `LICENSE` 與 `NOTICE` 檔案，並標註作者 cowbear6598。

## Acknowledgements

- [edge-tts](https://github.com/rany2/edge-tts) — Microsoft Edge TTS Python wrapper (GPL v3)
