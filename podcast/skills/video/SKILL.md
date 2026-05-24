---
name: video
description: 把 podcast mp3 與 episode_structure.json 做成完整 MP4。當使用者說「做成影片」「產生 mp4」「做 YouTube 版」「建立 HyperFrames 畫面」「把 podcast 做成完整影片」時觸發。
---

# 工作流程

把 `structure` skill 產生的 `episode_structure.json` 和 podcast mp3 轉成完整 MP4。預設使用 HyperFrames CLI，不需要全域安裝。

## 輸入

- `episode_structure.json`
- podcast mp3
- 可選：`caption_segments.json`
- 可選：封面圖、截圖、圖表、品牌色

若缺少 `episode_structure.json`，先使用 `structure` skill 產生。若缺少 mp3，先使用 `audio` skill 產生。若使用者要求字幕但缺少字幕資料，先使用 `caption` skill 產生。

## 產出

- HyperFrames 專案資料夾，預設 `<episode_slug>_video/`
- `assets/<audio>.mp3`
- `index.html`
- 最終 MP4，預設 `<episode_slug>.mp4`

## HyperFrames 執行方式

不要要求全域安裝。使用固定版本 `npx`：

```bash
npx --yes hyperframes@0.6.40 init "<project_dir>"
cd "<project_dir>"
npx --yes hyperframes@0.6.40 render -o "../<output>.mp4" --fps 24 --quality draft
```

正式輸出可把 `--quality draft` 改成 `--quality standard` 或 `--quality high`。

## Composition 規則

1. 根 composition 使用 `data-composition-id="main"`。
2. `data-duration` 必須等於音訊實際長度或 structure 的 duration。
3. `<audio>` 必須有穩定 `id`，否則 render 會靜音。
4. 每個 timed scene 必須有：
   - `id`
   - `class="clip"`
   - `data-start`
   - `data-duration`
   - `data-track-index`
5. 畫面採用 podcast companion 風格：章節卡、重點卡、quote、recap、waveform。
6. 若有 `caption_segments.json`，要燒進逐句字幕；字幕最多顯示兩行，避免遮住章節重點。
7. 不使用 `Date.now()`、`Math.random()` 或網路 fetch。

## 基本模板

第一版只使用下列模板：

- `intro`：標題、節目名稱、簡單 waveform
- `chapter`：章節切換
- `bullet_points`：三個以內重點
- `quote`：一句核心觀點
- `recap`：最後總結

## 字幕規則

- 讀取 `caption_segments.json` 的 `captions` 陣列。
- 每段字幕做成 timed `.clip`，`data-start` 與 `data-duration` 依 caption 計算。
- 字幕固定放在畫面下方安全區，使用半透明深色底或高對比文字。
- 單段字幕不超過兩行；過長時在產生 HTML 前拆段。
- 沒有字幕檔時仍可 render，但回報「本次影片未燒字幕」。

## 操作步驟

1. 讀取 `episode_structure.json`。
2. 確認 mp3 存在，並用 `ffprobe` 驗證 duration。
3. 若 structure 指向 `caption_segments.json`，確認字幕檔存在。
4. 用 `npx --yes hyperframes@0.6.40 init` 建立專案，或重用既有專案資料夾。
5. 複製 mp3 到 `assets/`。
6. 依 structure 產生章節 scenes，並依 captions 產生字幕 clips。
7. 執行檢查：

```bash
npm run check
```

若 `validate` 或 `inspect` 有 error，修正後再 render。`timeline_track_too_dense` 可在原型階段接受，正式版再拆 sub-compositions。

8. Render MP4：

```bash
npx --yes hyperframes@0.6.40 render -o "../episode.mp4" --fps 24 --quality draft
```

9. 用 `ffprobe` 驗證輸出含 video/audio stream：

```bash
ffprobe -v error -show_entries format=duration:stream=index,codec_type,codec_name,width,height -of json "episode.mp4"
```

## 失敗處理

- Render 後沒有聲音：檢查 `<audio>` 是否有 `id`，以及 `src` 是否指向 `assets/` 內存在的 mp3。
- 文字超出畫面：縮短 headline/bullets，或降低該元素字級。
- `npm run check` 找不到 `validate`：改用 `npx --yes hyperframes@0.6.40 lint && npx --yes hyperframes@0.6.40 inspect`。
- 中文字型警告：原型可先使用 `Arial, sans-serif`；正式版再加入 `@font-face`。
