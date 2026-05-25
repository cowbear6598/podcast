---
name: video
description: 把 podcast mp3、`episode_structure.json` 與字幕做成完整 MP4。
---

# 工作流程

使用 HyperFrames CLI 將 `episode_structure.json`、podcast mp3 與可選字幕轉成 MP4。不要要求全域安裝。

## 輸入

- 必要：`episode_structure.json`
- 必要：podcast mp3
- 可選：`caption_segments.json`
- 可選：封面圖、截圖、圖表、品牌色

缺 `episode_structure.json` 時先跑 `structure`。缺 mp3 時先跑 `audio`。要求字幕但缺字幕資料時先跑 `caption`。

## 輸出

- HyperFrames project：預設 `<episode_slug>_video/`
- `assets/<audio>.mp3`
- `index.html`
- 最終 MP4：預設 `<episode_slug>.mp4`

預設所有影片 project 檔案都留在 `<episode_slug>_video/`，最終 MP4 只輸出到上一層。不得在 episode 根目錄建立 `scripts/`、`node_modules/`、`package.json`、`package-lock.json` 等自製 render 專案檔，除非使用者明確指定根目錄就是 HyperFrames project。

## HyperFrames 指令

```bash
npx --yes hyperframes@0.6.40 init "<project_dir>"
cd "<project_dir>"
npx --yes hyperframes@0.6.40 render -o "../<output>.mp4" --fps 12 --quality draft
```

原型先用 `--fps 12 --quality draft`；正式輸出再用 `--fps 24 --quality standard/high`。

## 執行邊界

影片步驟只能組裝 HyperFrames project 並 render，不得自製影片引擎。

- 必須使用 `npx --yes hyperframes@0.6.40 init/render`。
- 禁止建立自製 frame-by-frame renderer。
- 禁止把 full video 拆成 `frames/frame-*.jpg` 或 `frames/frame-*.png` 作為主要流程。
- 禁止用 Puppeteer、Playwright、Canvas 或 ffmpeg 逐幀截圖後自行合成 MP4，除非使用者明確要求不用 HyperFrames。
- 同一版最多 render 1 次；失敗後先修明確錯誤再重跑。
- project 建立、HTML 產生與 `npm run check` 目標 3 分鐘內完成；超過 5 分鐘要停下回報。
- draft render 目標 8 分鐘內完成；超過 10 分鐘要中止並回報卡在哪一步。
- 重跑前刪除舊 `<episode_slug>_video/` 與舊 MP4，避免沿用舊 layout。

## Composition 契約

- root 使用 `data-composition-id="main"`。
- `data-duration` 等於音訊實際長度或 structure duration。
- `<audio>` 必須有穩定 `id`、`data-start`、`data-duration`。
- 每個 timed clip 必須有 `id`、`class="clip"`、`data-start`、`data-duration`、`data-track-index`。
- 不使用 `Date.now()`、`Math.random()` 或網路 fetch。
- 成品不得顯示 chapter 或 beat 的時間 range。

## Layout 契約

- 畫布固定 1920x1080。
- `.clip` 必須維持 `position: absolute`；所有 timed visual clips 要有明確位置與尺寸。
- headline、summary、visual panel、caption 必須有固定安全區，不可靠自然流排。
- visual elements 只能在 visual panel 內，不得覆蓋 headline、summary、chapter mark 或字幕。
- 不重複顯示完整 episode title；panel title 優先用短 chapter title。
- 文字容器要有 `overflow: hidden`、縮字或截短策略。
- 禁止巢狀 card、未限制寬高的大字、未設 track 的重疊 clip。

建議安全區：

| 元素 | 位置與尺寸 |
|---|---|
| chapter mark | 左上，寬度不超過 720px，高 48~64px |
| headline | 左側，寬 720~860px，高 260~360px，46~60px，最多 3 行 |
| summary | headline 下方，寬 700~820px，高 120~180px，24~30px，最多 3 行 |
| visual panel | 右側，寬 680~780px，高 520~620px |
| caption | 底部單行安全區，不遮住主視覺 |

## 動態敘事

影片以 `ideaBeats` 為動畫單位，不以字幕逐句切畫面。

- 每個 beat 對應一個敘述內容。
- beat 開始時 headline 或主 keyword 要有進場動畫。
- beat 內 elements 要逐步 reveal、highlight、pop、slide 或 stack。
- 不得把整個 beat 的所有文字放進同一個 scene 一次顯示。
- 同一 beat 的 visual elements 要沿 beat duration 或 caption anchors 分散，不能集中在開頭 2~4 秒。
- visual elements 必須在原本 visual panel 內做動畫；不得在 panel 外額外產生重複 chip、badge、tag 或 debug-like overlay。
- 若 panel 內已有某關鍵詞，不得在畫面其他位置複製同一關鍵詞來假裝動畫。
- GSAP timeline 必須使用每個 clip 的實際 `data-start`，不能只有一條從 0 秒開始的全域動畫。
- 每個 chapter 切換要有 transition 或 crossfade，不得硬切黑畫面。

建議 visual type：

- `headline-reveal`
- `bullet-reveal`
- `keyword-pop`
- `contrast-split`
- `flow-build`
- `quote-focus`
- `recap-stack`

## 字幕規則

- 讀取 `caption_segments.json.captions`。
- 每段字幕是 timed `.clip`，依 caption `start/end` 計算。
- 字幕固定單行，不插入 `<br>` 或換行。
- 過長時優先縮短文字、降低字級、加寬字幕框或 `text-overflow: ellipsis`。
- 字幕底板高度以單行為準，避免大黑底遮住畫面。
- 沒有字幕檔仍可 render，但要回報未燒字幕。

## 檢查清單

Render 前：

- 非字幕 timed clips 至少約為 `ideaBeats 數 * 5`。
- 每個 beat 至少有 headline、summary、visual panel、progress 或等效層。
- 每個 beat 中後段仍有可感知變化。
- `.clip` 沒被覆蓋成 `position: relative`。
- headline、summary、panel、visual elements 不共用同一個 timed clip 一次顯示。
- 不存在 panel 外的重複關鍵詞 chip / badge / tag。
- caption 內容不含 `<br>`，CSS 是單行 `white-space: nowrap`。

執行：

```bash
npm run check
```

`text_box_overflow`、元素重疊、黑畫面、音訊缺失都不能接受。`timeline_track_too_dense` 可在原型階段接受。

## 驗證

```bash
ffprobe -v error -show_entries format=duration:stream=index,codec_type,codec_name,width,height -of json "episode.mp4"
ffmpeg -ss 00:00:30 -i "episode.mp4" -frames:v 1 "frame-030.jpg"
ffmpeg -ss 00:02:00 -i "episode.mp4" -frames:v 1 "frame-120.jpg"
ffmpeg -ss 00:04:00 -i "episode.mp4" -frames:v 1 "frame-240.jpg"
ffmpeg -hide_banner -nostats -i "episode.mp4" -vf blackdetect=d=0.2:pic_th=0.98 -an -f null -
```

只從最終 MP4 抽樣 3 張 frame，不得輸出完整 frames 目錄。抽樣要確認：文字不溢出、不重疊、字幕單行、沒有黑畫面硬切、動畫跟著 beat 推進。

## 失敗處理

- 沒聲音：檢查 `<audio>` 的 `id`、`src`、`data-start`、`data-duration`。
- 文字溢出：先縮短文案，再降字級；不得放大容器到遮住其他元素。
- 畫面重疊：先檢查 `.clip` positioning，再查各 layer 安全區。
- 動畫只在開頭：檢查 element timing 是否分散到 beat 中後段。
- 切主題黑屏：加入 0.5~1.2 秒 transition overlay 或 crossfade。
- 超過時間預算：停止命令並回報，不能改走自製逐幀 pipeline。
- root-level `scripts/`、`node_modules/` 或 `package.json`：視為流程錯誤，刪除後重做 HyperFrames project。
