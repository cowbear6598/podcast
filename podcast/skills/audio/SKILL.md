---
name: audio
description: 把腳本轉成 mp3 與 TTS timing JSON。支援 `[曉臻]/[雲哲]` 雙人對談與 `[說書人]` 獨白。
---

# 工作流程

讀取腳本標記，自動選擇合成腳本：

- `[曉臻]/[雲哲]` → `scripts/podcast.py`
- `[說書人]` → `scripts/narration.py`

```bash
python3 <skill-dir>/scripts/podcast.py "對話腳本.txt" -o "episode.mp3"
python3 <skill-dir>/scripts/narration.py "獨白腳本.txt" -o "episode.mp3"
```

預設會同步輸出 `episode_timing.json`。可用 `--timing custom.json` 指定 timing 路徑。

## 輸入

- 必要：`.txt` 腳本
- 對談腳本只能包含 `[曉臻]`、`[雲哲]`
- 獨白腳本只能包含 `[說書人]`

## 輸出

- `episode.mp3`
- `episode_timing.json`

Timing JSON 是後續 `caption` skill 的必要輸入；若沒有生成，視為失敗，不進入字幕或影片步驟。

## 格式偵測

- 含 `[說書人]` 且不含 `[曉臻]/[雲哲]`：呼叫 `narration.py`
- 含 `[曉臻]` 或 `[雲哲]` 且不含 `[說書人]`：呼叫 `podcast.py`
- 兩類標記都出現：停手，V1 不支援混合腳本
- 沒有任何標記：停手，要求先用 `talk` 或 `tell` 產生腳本

## Timing 契約

正流程只使用 TTS segment timing，不使用 Whisper，也不使用字數估算 fallback。

Timing 來源：

1. Edge TTS 逐段合成。
2. ffmpeg 裁掉段落頭尾靜音。
3. ffprobe 量每段實際 duration。
4. 累加段落時間與 `PAUSE_SECONDS`。
5. 合併 mp3，同步寫出 timing JSON。

格式：

```json
{
  "audio": "episode.mp3",
  "duration": 360.4,
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

## 預設設定

| 模式 | 腳本 | 聲音 | 語速 | 段落停頓 |
|---|---|---|---|---|
| 對談 | `podcast.py` | 曉臻 `zh-TW-HsiaoChenNeural`；雲哲 `zh-TW-YunJheNeural` | `-10%` | `0.25s` |
| 獨白 | `narration.py` | 說書人 `zh-TW-HsiaoChenNeural` | `-10%` | `0.25s` |

## 操作步驟

1. 確認腳本存在。
2. 依格式偵測選擇合成腳本。
3. 執行合成並顯示每段前 30 字作為進度。
4. 確認 mp3 與 timing JSON 都已產生。
5. 回報輸出路徑、檔案大小與下一步。

## 常見問題

- 語速調整：改 `_core.py` 的 `RATE`，需使用 `-10%` 或 `+0%` 這類兩位數百分比。
- 段落停頓：改 `_core.py` 的 `PAUSE_SECONDS`，建議 `0.1` 到 `0.4`。
- 無音訊：通常是網路或 voice 名稱問題；腳本會依 fallback 聲音重試。
- 腳本誤用：`podcast.py` 與 `narration.py` 都會偵測錯誤格式並提示改用另一個腳本。
