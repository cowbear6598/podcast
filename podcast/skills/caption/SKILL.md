---
name: caption
description: 用 audio skill 產生的 TTS timing JSON 轉出 podcast 字幕。當使用者說「產生字幕」「加字幕」「轉 SRT」「做 captions」「產生 transcript」「幫 podcast 對字幕」時觸發。
---

# 工作流程

把 `audio` skill 產生的 `episode_timing.json` 轉成字幕資料，供 `video` skill 燒進 MP4，也可另存 SRT 給 YouTube 使用。

## 輸入

- 必要：`episode_timing.json`
- 建議：`episode.mp3`，用於驗證 duration

正流程不使用 Whisper，也不使用字數估算 fallback。若缺少 `episode_timing.json`，停手並要求先重跑 `audio` skill 產生 timing。

## 輸出

- `transcript.json`：由 timing segments 整理出的完整文字與時間軸
- `subtitles.srt`：標準字幕檔
- `caption_segments.json`：給 HyperFrames/`video` skill 使用的精簡字幕段落

`caption_segments.json` 格式：

```json
{
  "captions": [
    {
      "start": 0.4,
      "end": 4.8,
      "text": "今天要說的是一個 YouTube 頻道成長的案例。"
    }
  ],
  "timingSource": "tts-segment"
}
```

## 字幕策略

- 第一版使用逐句或短段字幕，不做逐字 karaoke。
- 每段字幕建議 8 到 24 個中文字；太長要拆段。
- 單段顯示時間至少 1.2 秒，避免閃太快。
- 字幕文字要去掉 speaker tag，例如 `[說書人]`、`[曉臻]`、`[雲哲]`。
- 保留英文專有名詞原文。

## Timing 來源

只接受 `audio` skill 產生的 TTS segment timing：

```json
{
  "audio": "episode.mp3",
  "duration": 94.595,
  "timingSource": "tts-segment",
  "segments": [
    {
      "start": 0.0,
      "end": 3.21,
      "speaker": "說書人",
      "text": "今天要說的是一個很小的測試。"
    }
  ]
}
```

如果使用者提供的是外部音訊或真人錄音，那是另一個流程，不屬於 podcast 正流程。不要在此 skill 自動改用 Whisper。

## SRT 輸出規則

SRT timestamp 格式：

```text
1
00:00:00,400 --> 00:00:04,800
今天要說的是一個 YouTube 頻道成長的案例。
```

## 操作步驟

1. 確認 `episode_timing.json` 存在且 `timingSource` 是 `tts-segment`。
2. 可選：用 `ffprobe` 驗證 mp3 duration 與 timing duration 接近。
3. 將 timing segments 整理成 `transcript.json`。
4. 將 segments 轉成 `caption_segments.json`；過長文字要拆成較短字幕段。
5. 同步輸出 `subtitles.srt`。
6. 告知下一步可用 `structure` 和 `video` skill。
