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
npx --yes hyperframes@0.6.40 render -o "../<output>.mp4" --fps 24 --quality draft
```

Render profile：

| profile | 用途 | 指令 |
|---|---|---|
| `preview` | layout smoke test，只能輸出短片段或內部檢查，不是正式交付 | `--fps 24 --quality draft` |
| `draft` | 預設完整輸出 | `--fps 24 --quality draft` |
| `final` | 正式交付 | `--fps 24 --quality standard` |

完整 MP4 必須維持 24fps，不得降到 12fps、6fps、4fps 或 1fps。正常情況應保留克制的轉場與低頻動畫；只有 24fps render 太慢或 `npm run check` 因動畫複雜度失敗時，才把靜態 PPT 式畫面當 fallback。仍不行就停止並回報瓶頸，不得用低 fps 影片當交付。

## 執行邊界

影片步驟只能組裝 HyperFrames project 並 render，不得自製影片引擎。

- 必須使用 `npx --yes hyperframes@0.6.40 init/render`。
- 禁止建立自製 frame-by-frame renderer。
- 禁止把 full video 拆成 `frames/frame-*.jpg` 或 `frames/frame-*.png` 作為主要流程。
- 禁止用 Puppeteer、Playwright、Canvas 或 ffmpeg 逐幀截圖後自行合成 MP4，除非使用者明確要求不用 HyperFrames。
- 同一版最多 render 1 次；失敗後先修明確錯誤再重跑。
- project 建立、HTML 產生與 `npm run check` 目標 3 分鐘內完成；超過 5 分鐘要停下回報。
- draft render 目標 8 分鐘內完成；超過 10 分鐘要中止並回報卡在哪一步。中止後只能降低畫面複雜度，不得降低 fps。
- 重跑前刪除舊 `<episode_slug>_video/` 與舊 MP4，避免沿用舊 layout。

## 效能預算

長 podcast 的瓶頸通常是 Chrome frame capture，不是 ffmpeg。Render 前必須先控制 composition 複雜度。

預估項目：

- `estimatedFrames = audioDurationSeconds * renderFps`
- `timedClipCount = document.querySelectorAll('.clip').length`
- `captionClipCount = document.querySelectorAll('.caption.clip').length`
- `maxCaptionClipsPerTrack = max(caption clips grouped by data-track-index)`

產生 `index.html` 後，必須在回報或 log 中列出：

```text
duration=<seconds>
profile=<preview|draft|final>
fps=<fps>
estimatedFrames=<duration*fps>
timedClipCount=<all .clip>
captionClipCount=<caption .clip>
nonCaptionClipCount=<timedClipCount-captionClipCount>
```

硬性預算：

| 項目 | 上限 |
|---|---|
| total timed clips | 180 |
| video caption clips | 120 |
| caption clips per track | 15 |
| non-caption clips | `topicSegments + chapterTransitions + introOutro` |
| animated visual clips | 60 |

超過預算時，不得直接 render。先依序處理：

1. 合併 video captions 到 3~5 秒一段。
2. 將字幕分散到多個 `data-track-index`，避免任一 caption track 超過 15 個 clips；必要時每段字幕用獨立 track。
3. 以大主題建立 `topicSegments`，把多個 idea beats 合併到同一個 topic 畫面。
4. 每個 topic 保留一個主要 visual clip，優先使用低頻內部動畫，不新增額外重複 clips。
5. 移除裝飾性 overlay、shadow、progress、頁碼、章節計數等非內容層。
6. 若 render 仍太慢，才 fallback 成靜態 PPT 式 topic slides，但 fps 仍必須是 24。

`timeline_track_too_dense` 對完整影片不是可接受狀態。若只是在短 prototype 出現可暫時記錄；完整 episode render 前必須降 clip 數或拆成更少主 clip 的 layout。

## Composition 契約

- root 使用 `data-composition-id="main"`。
- `data-duration` 等於音訊實際長度或 structure duration。
- `<audio>` 必須有穩定 `id`、`data-start`、`data-duration`。
- 每個 timed clip 必須有 `id`、`class="clip"`、`data-start`、`data-duration`、`data-track-index`。
- 不使用 `Date.now()`、`Math.random()` 或網路 fetch。
- 成品不得顯示 chapter、topic 或 beat 的時間 range。

## Layout 契約

- 畫布固定 1920x1080。
- `.clip` 必須維持 `position: absolute`；所有 timed visual clips 要有明確位置與尺寸。
- headline、summary、visual panel、caption 必須有固定安全區，不可靠自然流排。
- visual elements 只能在 visual panel 內，不得覆蓋 headline、summary、chapter mark 或字幕。
- 不重複顯示完整 episode title；panel title 優先用短 chapter title。
- 文字容器要有 `overflow: hidden`、縮字或截短策略。
- 禁止巢狀 card、未限制寬高的大字、未設 track 的重疊 clip。
- 成品不得顯示 `01/7`、`1 of 7`、chapter counter、beat counter、progress bar 這類內部進度 UI。
- 禁止昂貴 CSS：`filter`、`backdrop-filter`、大面積 blur、動畫 gradient、大型 box-shadow、多層半透明 overlay。
- 若要用漸層，只能作為單層靜態背景；不得讓多個大型透明層疊在主畫布上。

建議安全區：

| 元素 | 位置與尺寸 |
|---|---|
| chapter mark | 左上，寬度不超過 720px，高 48~64px |
| headline | 左側，寬 720~860px，高 260~360px，46~60px，最多 3 行 |
| summary | headline 下方，寬 700~820px，高 120~180px，24~30px，最多 3 行 |
| visual panel | 右側，寬 680~780px，高 520~620px |
| caption | 底部單行安全區，不遮住主視覺 |

## 動態敘事

影片以大主題的 `topicSegments` 為畫面單位，不以字幕逐句切畫面，也不應讓一段話跳多次標籤。

- 每個 topic segment 對應一個大主題或標籤；一個標籤可以承載多個敘述點。
- topic segment 應維持足夠長的解說時間，通常 30~90 秒；短於 20 秒時要合併到相鄰 topic。
- 同一個大主題內不得因為每句話或每段字幕就切換標籤；除非 podcast 明確轉到下一個大主題，否則維持同一張主視覺。
- 每個 topic 預設只有一個主要 timed visual clip；該 clip 內可包含 headline、summary、diagram、keyword，不包含可見頁碼或進度條。
- topic 開始時應有一次簡短進場或 crossfade；topic 內可有 2~3 個低頻 reveal/highlight/slide 步驟，且不能造成標籤頻繁跳動。
- 只有 24fps render 太慢、layout 因動畫不穩、或使用者明確要求極簡時，才取消內部動畫改成靜態顯示完整 topic slide。
- 不得把每個 idea beat 都做成新的標籤畫面；idea beats 只作為同一 topic 下的敘述內容來源。
- 同一 topic 的 visual elements 若要變化，應沿 topic duration 做低頻 highlight，不能集中在開頭 2~4 秒。
- visual elements 必須在原本 visual panel 內做動畫；不得在 panel 外額外產生重複 chip、badge、tag 或 debug-like overlay。
- 若 panel 內已有某關鍵詞，不得在畫面其他位置複製同一關鍵詞來假裝動畫。
- 不得為了做動畫把同一關鍵詞複製成另一個 timed clip；應對原本元素加 class 或 data-step。
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
- SRT 或字幕資料可保留細粒度；video burned-in captions 必須先合併成 3~5 秒一段，避免 clip 過多。
- 每段 video 字幕是 timed `.clip`，依合併後 caption `start/end` 計算。
- 不得把所有字幕都放在同一個 `data-track-index`；同一 caption track 超過 15 個 clips 時要分散到更多 tracks。
- 相鄰字幕若 start/end 完全相同，將前一段 `data-duration` 縮短 0.01~0.03 秒，避免浮點誤差造成 `overlapping_clips_same_track`。
- 字幕固定單行，不插入 `<br>` 或換行。
- 過長時優先縮短文字、降低字級、加寬字幕框或 `text-overflow: ellipsis`。
- 字幕底板高度以單行為準，避免大黑底遮住畫面。
- 沒有字幕檔仍可 render，但要回報未燒字幕。

## 檢查清單

Render 前：

- full render 必須是 24fps。
- `timedClipCount <= 180`，`captionClipCount <= 120`。
- `maxCaptionClipsPerTrack <= 15`，且 lint 不得出現 `timeline_track_too_dense`。
- 非字幕 timed clips 不超過 `topicSegments + chapterTransitions + introOutro`。
- animated visual clips 不超過 60；超過時改靜態 topic slide。
- 每個 topic 至少有 headline、summary、visual panel 或等效層。
- 每個 topic 能承載一段完整講解，不得一段話切換多個標籤。
- `.clip` 沒被覆蓋成 `position: relative`。
- headline、summary、panel、visual elements 可共用同一個 topic clip；預設要有低頻內部動畫，render 壓力高時才 fallback 成一次顯示。
- 不存在 panel 外的重複關鍵詞 chip / badge / tag。
- 不存在可見的 `01/7`、chapter counter、beat counter 或 progress bar。
- caption 內容不含 `<br>`，CSS 是單行 `white-space: nowrap`。
- CSS 不含 `filter`、`backdrop-filter`、大面積 blur 或動畫 gradient。

執行：

```bash
npm run check
```

`text_box_overflow`、元素重疊、黑畫面、音訊缺失都不能接受。完整影片不得接受 `timeline_track_too_dense`。

## 驗證

```bash
ffprobe -v error -show_entries format=duration:stream=index,codec_type,codec_name,width,height -of json "episode.mp4"
ffmpeg -ss 00:00:30 -i "episode.mp4" -frames:v 1 "frame-030.jpg"
ffmpeg -ss 00:02:00 -i "episode.mp4" -frames:v 1 "frame-120.jpg"
ffmpeg -ss 00:04:00 -i "episode.mp4" -frames:v 1 "frame-240.jpg"
ffmpeg -hide_banner -nostats -i "episode.mp4" -vf blackdetect=d=0.2:pic_th=0.98 -an -f null -
```

只從最終 MP4 抽樣 3 張 frame，不得輸出完整 frames 目錄。抽樣要確認：文字不溢出、不重疊、字幕單行、沒有黑畫面硬切、畫面節奏跟著 topic 推進。

## 失敗處理

- 沒聲音：檢查 `<audio>` 的 `id`、`src`、`data-start`、`data-duration`。
- 文字溢出：先縮短文案，再降字級；不得放大容器到遮住其他元素。
- 畫面重疊：先檢查 `.clip` positioning，再查各 layer 安全區。
- 標籤變化太快：把多個 idea beats 合併成同一個 topic segment，讓一個標籤承載完整大主題講解。
- 動畫只在開頭：檢查 element timing 是否分散到 topic 中後段；若 render 壓力高，才移除動畫改靜態 slide。
- 切主題黑屏：加入 0.5~1.2 秒 transition overlay 或 crossfade。
- 出現 `01/7` 或 progress bar：刪除這類內部進度 UI；它不是觀眾需要看的內容。
- 超過時間預算：停止命令，先降 DOM/clip/caption 複雜度，再移除動畫 fallback 成靜態 PPT；不得降低 fps，也不能改走自製逐幀 pipeline。
- root-level `scripts/`、`node_modules/` 或 `package.json`：視為流程錯誤，刪除後重做 HyperFrames project。
