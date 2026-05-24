---
name: structure
description: 把 podcast 腳本、分析摘要或 mp3 整理成影片結構 JSON。當使用者說「產生影片結構」「做 storyboard」「規劃 podcast 畫面」「整理成影片章節」「產生 visual plan」時觸發。
---

# 工作流程

把 podcast-first 的內容整理成 `episode_structure.json`，供 `video` skill 轉成 MP4。這個 skill 只規劃內容與畫面結構，不 render 影片。

## 輸入

可接受以下任一組輸入：

- podcast 腳本：`[曉臻]/[雲哲]` 或 `[說書人]` 格式
- podcast mp3：已由 `audio` skill 產生
- 字幕資料：`caption_segments.json`（若已由 `caption` skill 產生）
- 來源摘要：文章、YouTube 分析總結、Markdown notes

若有 mp3，先用 `ffprobe` 取得實際 duration。若沒有 mp3，用腳本段落估算時長，但要在輸出中標記 `timingSource: "estimated"`。

```bash
ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "episode.mp3"
```

## 輸出格式

預設輸出到當前目錄的 `episode_structure.json`。JSON 必須可被機器穩定讀取，不要包含註解。

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
        "bullets": []
      }
    ]
  }
}
```

## 欄位規則

- `title`：影片標題，避免過長，適合 YouTube 顯示
- `mode`：`talk`、`narration` 或 `unknown`
- `audio`：mp3 路徑；若尚未生成，填 `null`
- `duration`：秒數；有 mp3 時使用實際音訊長度
- `timingSource`：`audio` 或 `estimated`
- `visualRole`：固定使用 `companion`，表示畫面輔助 podcast，而不是主敘事
- `captions`：字幕 JSON 路徑；若沒有字幕，填 `null`
- `chapters`：依音訊長度調整；短集 4~6 個，中長集 6~12 個
- `template`：只能使用 `intro`、`chapter`、`bullet_points`、`quote`、`recap`
- `headline`：該段畫面主標，必須短而可讀
- `bullets`：最多 3 點，每點 20 字以內

## 規劃原則

1. **音訊是主時間軸**：畫面必須跟著 podcast 內容走。
2. **lunch-break 長度**：預設 12~15 分鐘；短內容 6~10 分鐘；長內容 15~20 分鐘；除非使用者明確指定，不超過 25 分鐘。
3. **不要逐句換畫面**：一般每 30~90 秒換一次視覺段落；長內容以 chapter 為主，每章可拆 2~4 個 scene。
4. **固定模板優先**：不要讓 LLM 自由發明複雜版型。
5. **少字大字**：畫面不是逐字稿，只放章節、重點、短句；字幕由 `caption` skill 管。
6. **可重跑**：JSON 欄位要穩定，讓 `video` skill 可重複 render。

## 操作步驟

1. 讀取腳本、摘要與 mp3 路徑。
2. 若有 mp3，用 `ffprobe` 取得實際長度。
3. 判斷模式：有 `[說書人]` 為 `narration`，有 `[曉臻]` 或 `[雲哲]` 為 `talk`。
4. 若有 `caption_segments.json`，用字幕時間輔助切章節。
5. 依長度切章節：6~10 分鐘約 4~6 章；12~15 分鐘約 6~8 章；15~25 分鐘約 8~12 章。
6. 為每章選模板並寫 `headline`、`summary`、`bullets`。
7. 確認章節 `start/end` 覆蓋完整 duration，且不重疊。
8. 輸出 `episode_structure.json`，並告知下一步可用 `video` skill 產 MP4。
