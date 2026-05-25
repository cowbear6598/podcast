---
name: caption
description: 用 `audio` skill 產生的 TTS timing JSON 轉出 transcript、SRT 與影片字幕 JSON。
---

# 工作流程

把 `episode_timing.json` 轉成字幕資料，供 `video` skill 燒進 MP4，也可輸出 SRT 給 YouTube。

## 輸入

- 必要：`episode_timing.json`
- 可選：`episode.mp3`，用於驗證 duration

正流程只接受 `timingSource: "tts-segment"`。若缺少 timing JSON，停手並要求先重跑 `audio` skill。

## 輸出

- `transcript.json`
- `subtitles.srt`
- `caption_segments.json`

`caption_segments.json` 格式：

```json
{
  "timingSource": "tts-segment",
  "captions": [
    {
      "start": 0.4,
      "end": 4.8,
      "text": "今天要說的是一個 YouTube 頻道成長的案例。"
    }
  ]
}
```

## 字幕規則

- 第一版使用逐句或短段字幕，不做逐字 karaoke。
- 每段建議 8~24 個中文字；太長要拆段。
- 單段顯示至少 1.2 秒。
- 去掉 speaker tag，例如 `[說書人]`、`[曉臻]`、`[雲哲]`。
- 保留英文專有名詞原文。
- 不自動改用 Whisper；外部音訊或真人錄音是另一條流程。

## SRT 格式

```text
1
00:00:00,400 --> 00:00:04,800
今天要說的是一個 YouTube 頻道成長的案例。
```

## 操作步驟

1. 讀取 `episode_timing.json` 並確認 `timingSource`。
2. 可選：用 `ffprobe` 驗證 mp3 duration。
3. 輸出 `transcript.json`。
4. 拆分過長字幕並輸出 `caption_segments.json`。
5. 同步輸出 `subtitles.srt`。
6. 告知下一步可用 `structure` 和 `video` skill。
