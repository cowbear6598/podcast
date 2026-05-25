---
name: structure
description: 把 podcast 腳本、摘要、字幕或 mp3 整理成 `episode_structure.json`，供影片生成使用。
---

# 工作流程

產生 podcast-first 的影片結構 JSON。這個 skill 只規劃章節與畫面節奏，不 render 影片。

## 輸入

可接受任一組：

- podcast 腳本：`[曉臻]/[雲哲]` 或 `[說書人]`
- podcast mp3：已由 `audio` skill 產生
- 字幕資料：`caption_segments.json`
- 來源摘要：文章、YouTube 分析總結、Markdown notes

有 mp3 時必須用 `ffprobe` 取得實際 duration；沒有 mp3 才能估算，並標記 `timingSource: "estimated"`。

```bash
ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "episode.mp3"
```

## 輸出

預設輸出 `episode_structure.json`。JSON 不得包含註解。

```json
{
  "episode": {
    "title": "一個 YouTube 頻道為什麼穩定成長",
    "mode": "narration",
    "audio": "episode.mp3",
    "duration": 360.0,
    "timingSource": "audio",
    "visualRole": "companion",
    "captions": "caption_segments.json",
    "chapters": [
      {
        "start": 0,
        "end": 42,
        "title": "開場",
        "summary": "先建立這集的核心問題。",
        "template": "intro",
        "headline": "成長不是靠單一爆款",
        "bullets": [],
        "ideaBeats": [
          {
            "start": 0,
            "end": 14,
            "idea": "先建立本集核心問題",
            "visual": "headline-reveal",
            "elements": ["核心問題", "為什麼重要"]
          }
        ]
      }
    ]
  }
}
```

## 結構契約

- `duration`：有 mp3 時使用實際秒數。
- `visualRole`：固定 `companion`，代表畫面輔助 podcast，不取代旁白。
- `chapters`：4~6 分鐘約 3~5 章；6~10 分鐘約 5~8 章。
- `template`：只能用 `intro`、`chapter`、`bullet_points`、`quote`、`recap`。
- `headline`：短而可讀，避免塞完整句。
- `bullets`：最多 3 點，每點 20 字內。
- `ideaBeats`：每章 2~5 個，是影片動態的最小敘事單位。

## Idea Beat 規則

- 一個 beat 是一個敘述內容，不是逐句字幕；可是一個小觀點、例子、轉折或結論。
- 每個 beat 通常 8~25 秒。
- 必填 `start`、`end`、`idea`、`visual`、`elements`。
- `idea` 不必逐字等於旁白，但要對應同一段敘述。
- `elements` 最多 4 個，用於 panel 內逐步 reveal 或 highlight。
- `visual` 可用：`headline-reveal`、`bullet-reveal`、`keyword-pop`、`contrast-split`、`flow-build`、`quote-focus`、`recap-stack`。
- beat 時間必須落在所屬 chapter 內；章節時間不可重疊。

## 格式偵測

- 含 `[說書人]` 且不含 `[曉臻]/[雲哲]`：`mode` 使用 `narration`。
- 含 `[曉臻]` 或 `[雲哲]` 且不含 `[說書人]`：`mode` 使用 `talk`。
- 兩類標記都出現：停手；V1 不支援混合腳本。
- 沒有腳本標記時，可依來源摘要產生結構，`mode` 使用 `unknown`。

## 規劃原則

- 音訊是主時間軸，畫面跟著 podcast 內容走。
- 預設 6~8 分鐘；長內容做 8~10 分鐘。除非使用者明確指定，不超過 10 分鐘。
- 長來源要高密度整理，不逐段翻譯。
- 成品畫面不得顯示 `0:00-1:20` 這類時間 range。
- 畫面少字大字；字幕由 `caption` skill 處理。

## 操作步驟

1. 讀取腳本、摘要、字幕與 mp3。
2. 取得或估算 duration。
3. 依格式偵測決定 `mode`；混合腳本要停手。
4. 用字幕時間輔助切章節。
5. 產生 chapters、headline、summary、bullets 與 ideaBeats。
6. 檢查章節覆蓋完整 duration、互不重疊，且 beat 落在章節內。
7. 輸出 `episode_structure.json`。
