# Backend 計畫書

> 註：本 plugin 是 CLI 工具（Claude Code skills + Python 腳本），無前端。所有改動都歸於 backend。

## 測試案例（先列名稱，內容寫在文末）

1. talk skill 改寫對談腳本 — 輸出 `[曉臻]/[雲哲]` 格式
2. tell skill 改寫說書人腳本 — 輸出 `[說書人]` 格式、有聲書旁白風格
3. podcast.py 合成對談 mp3 — 雙聲、無回歸
4. narration.py 合成說書人 mp3 — 單聲、HsiaoChen、有頭尾裁靜音
5. audio skill 自動分派 — 腳本內容決定呼叫哪個 Python 腳本
6. 腳本格式錯誤 — 沒有任何角色標記時給清楚訊息
7. 混合腳本格式 — 同時出現對談與說書人標記時給清楚錯誤（V1 不支援）

---

### Phase 1（可並行）

A. `content` skill 改名為 `talk`
  - [ ] 將目錄 `podcast/skills/content` 重命名為 `podcast/skills/talk`
  - [ ] 編輯 `podcast/skills/talk/SKILL.md` frontmatter：
    - `name: content` → `name: talk`
    - `description` 調整為：「把文章改寫成雙人對談 Podcast 腳本。當使用者提供文章、貼文、技術新聞並說『幫我變對話』『轉成 podcast 腳本』『改成兩人對談』時觸發。」（內容幾乎不動，但保留原觸發關鍵字）
  - [ ] SKILL.md 內文（工作流程、角色設定、改寫規則、操作步驟）維持不變
  - [ ] 確認沒有其他檔案 hard-code `podcast:content` 這個字串（grep 全專案）

B. 新增 `tell` skill
  - [ ] 建立目錄 `podcast/skills/tell`
  - [ ] 建立 `podcast/skills/tell/SKILL.md`，frontmatter：
    - `name: tell`
    - `description`：「把文章或書段改寫成說書人獨白腳本。當使用者說『改成說書人』『轉成有聲書』『變獨白』『旁白稿』時觸發。」
  - [ ] SKILL.md 主要章節：
    - **工作流程**：把使用者提供的內容改寫成單人獨白腳本，輸出給 `audio` skill 生成 mp3 的 `.txt`
    - **輸出格式**：固定 `[說書人]` 標記，一段一行，段落間空行
    - **寫作風格**：有聲書旁白 — 自然平實、像人在娓娓道來；不要戲劇化腔調（避免「話說」「且聽下回」「列位看官」）；不要把自己當第二個說話者與聽眾對話
    - **改寫規則**：沿用 talk skill 的 8 條（去 emoji、去 URL/mention、長句拆短、減少逗號、數字口語化、英文專有名詞保留、加自然語氣、開頭結尾招呼）
    - **結構建議**：開頭一句引入主題（「今天要說的是...」或「接下來這段...」），中段依邏輯講述重點，結尾一句收束
    - **長度建議**：10~25 段落，對應 5~8 分鐘
    - **操作步驟**：讀取原文 → 抽出主題脈絡 → 撰寫獨白腳本 → 預設輸出 `script_<日期>.txt`（可由使用者指定） → 告知下一步可執行 `audio` skill

C. 抽出共用模組 `_core.py`
  - [ ] 建立 `podcast/skills/audio/scripts/_core.py`
  - [ ] 從 `podcast.py` 搬出下列函式到 `_core.py`：
    - `_tts_once(voice, line, out_path)`：edge-tts 合成 + ffmpeg 裁頭尾靜音
    - `_synth_with_retry(voice, line, out_path)`：含重試的合成
    - `make_pause_file(tmp_dir, seconds)`：產生指定長度的靜音 mp3
    - `concat_mp3(parts, output_path)`：用 ffmpeg concat demuxer 拼接多個 mp3
  - [ ] 搬出共用常數：`RATE = "-10%"`、`RETRY_ATTEMPTS = 3`、`RETRY_DELAY = 1.5`、`PAUSE_SECONDS = 0.25`、`SILENCE_REMOVE_FILTER`（裁靜音 filter 字串）
  - [ ] 保持所有現有行為不變，只是搬家

### Phase 2（可並行）

A. 重構 `podcast.py`
  - [ ] 從 `_core.py` import 共用 helper 與常數
  - [ ] `VOICES` dict 留在 `podcast.py`（只關對談角色），內容不變：
    - 曉臻 → `zh-TW-HsiaoChenNeural` + fallback
    - 雲哲 → `zh-TW-YunJheNeural` + fallback
  - [ ] `parse_script` regex 維持只吃 `[曉臻|雲哲]`
  - [ ] 若腳本含 `[說書人]` 標記 → 印出提示「此腳本為說書人格式，請改用 narration.py」後退出
  - [ ] `main_async` 按角色分組、fallback 機制、pause 拼接邏輯維持不變，但 helper 改 call `_core` 的函式
  - [ ] CLI 介面不變：`python podcast.py script.txt -o out.mp3`

B. 新增 `narration.py`
  - [ ] 建立 `podcast/skills/audio/scripts/narration.py`
  - [ ] 從 `_core.py` import 共用 helper 與常數
  - [ ] `VOICES` dict：
    - 說書人 → `["zh-TW-HsiaoChenNeural", "zh-CN-XiaoxiaoNeural", "zh-HK-HiuGaaiNeural"]`
  - [ ] `parse_script(path)`：regex 只吃 `[說書人]`，回傳 `list[str]`（段落文字列表，無需 speaker 資訊）
  - [ ] 若腳本含 `[曉臻]` 或 `[雲哲]` → 印出提示「此腳本為對談格式，請改用 podcast.py」後退出
  - [ ] `main_async` 流程：
    - 解析段落
    - 嘗試 VOICES["說書人"] 的主聲音合成所有段落；任一段失敗 → 換下一個 fallback 聲音整批重做（沿用 podcast.py 的 all-or-nothing fallback 策略，確保整檔聲音一致）
    - 段落間插入 `PAUSE_SECONDS` 靜音
    - concat 輸出 mp3
  - [ ] CLI 介面：`python narration.py script.txt -o out.mp3`

### Phase 3

A. 更新 `audio` skill 文檔
  - [ ] 編輯 `podcast/skills/audio/SKILL.md`
  - [ ] description 調整：新增「生成說書人 mp3」「跑有聲書」等觸發詞
  - [ ] 新增「格式偵測」章節，規則：
    - 讀腳本檔
    - 若含 `[說書人]` 且無 `[曉臻]/[雲哲]` → 呼叫 `narration.py`
    - 若含 `[曉臻]` 或 `[雲哲]` 且無 `[說書人]` → 呼叫 `podcast.py`
    - 若兩類標記都出現 → 停手，告知使用者 V1 不支援混合腳本
    - 若都沒出現 → 告知使用者腳本需要 `[曉臻]/[雲哲]` 或 `[說書人]` 標記
  - [ ] 「預設設定」表格拆成兩列：
    - 對談（podcast.py）：曉臻+雲哲、RATE=-10%、PAUSE=0.25s
    - 說書人（narration.py）：HsiaoChen、RATE=-10%、PAUSE=0.25s
  - [ ] 操作步驟改為：確認腳本格式 → 選對腳本 → 顯示進度 → 完成回報 → 可選 Slack 發送

### Phase 4（可並行）

A. 更新 plugin metadata
  - [ ] 編輯 `podcast/.claude-plugin/plugin.json`
  - [ ] description 改為：「把文章改寫成雙人 Podcast 或說書人獨白音檔」
  - [ ] version 不動（由後續 release 流程決定）

B. 更新 README
  - [ ] 編輯 `README.md`
  - [ ] 首段描述調整為涵蓋對談＋說書人
  - [ ] Skills 表格：
    - `podcast:content` 改為 `podcast:talk`
    - 新增一列 `podcast:tell` — 把文章改寫成 `[說書人]` 獨白腳本
    - `podcast:audio` 說明更新為「支援雙人對談與說書人兩種格式」
  - [ ] Workflow 章節新增第二條流程：`文章 → podcast:tell → 說書腳本.txt → podcast:audio → mp3`

### Phase 5 — 測試

手動驗證以下案例（此 plugin 無自動化測試框架，所有測試靠實跑 + 聽）：

1. **talk 改寫不退化**
   - 用一則既有對談腳本重跑 `podcast:talk`，確認輸出格式 `[曉臻]/[雲哲]` 正確

2. **tell 改寫風格正確**
   - 餵一段約 500~800 字的技術文章給 `podcast:tell`
   - 檢查：全部用 `[說書人]` 標記、段落切得合理、沒有戲劇化腔調、沒有 emoji/URL/markdown

3. **podcast.py 合成無回歸**
   - 跑一份既有對談腳本，驗證雙聲 mp3 成功輸出、時長合理

4. **narration.py 合成成功**
   - 跑 case 2 產出的說書人腳本
   - 驗證：單聲 HsiaoChen、段落間停頓正常、無爆音/異常延遲

5. **audio skill 自動分派**
   - 把對談腳本交給 `podcast:audio` → 確認走 `podcast.py`
   - 把說書人腳本交給 `podcast:audio` → 確認走 `narration.py`

6. **腳本格式錯誤**
   - 餵一份純文字（無任何標記）給 audio → 應回報「需要標記」
   - 餵混合腳本（同時含 `[曉臻]` 與 `[說書人]`）→ 應回報「V1 不支援混合」

7. **單一 Python 腳本誤用保護**
   - `python podcast.py` 吃說書人腳本 → 應退出並指引改用 `narration.py`
   - `python narration.py` 吃對談腳本 → 應退出並指引改用 `podcast.py`
