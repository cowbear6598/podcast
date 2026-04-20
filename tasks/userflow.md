# User Flow

## 把文章改寫成對談腳本（既有功能，skill 改名）

### 情境：使用者把文章改寫成雙人對談
- Given 使用者提供一篇文章、貼文或技術新聞
- When 使用者說「幫我變對話」「轉成 podcast 腳本」「改成兩人對談」
- Then Claude 觸發 `podcast:talk`（原 `podcast:content`），輸出 `[曉臻]/[雲哲]` 格式的 `.txt`

## 把文章改寫成說書人腳本（新功能）

### 情境：使用者把書或長文改寫成單人說書
- Given 使用者提供一本書的段落、長文章或想獨白呈現的內容
- When 使用者說「幫我變說書人」「改成獨白」「轉成有聲書旁白」
- Then Claude 觸發 `podcast:tell`，輸出 `[說書人]` 格式的 `.txt`，寫作風格偏有聲書旁白（自然、平實、不戲劇化）

## 把腳本合成 mp3

### 情境：合成雙人對談腳本
- Given 使用者有一份 `[曉臻]/[雲哲]` 格式的腳本
- When 使用者說「生成音檔」「跑 podcast」「合成語音」
- Then `podcast:audio` 呼叫 `podcast.py`，產出雙聲 mp3

### 情境：合成說書人腳本
- Given 使用者有一份 `[說書人]` 格式的腳本
- When 使用者說「生成音檔」「合成語音」
- Then `podcast:audio` 呼叫 `narration.py`，產出單聲 mp3，使用 `zh-TW-HsiaoChenNeural`

### 情境：腳本格式不符
- Given 使用者的腳本裡沒有任何 `[曉臻]`、`[雲哲]` 或 `[說書人]` 標記
- When 執行 `podcast:audio`
- Then 顯示錯誤「腳本需要 `[曉臻]/[雲哲]` 或 `[說書人]` 標記」，不產出 mp3

## 設定檢查

### 情境：使用者第一次使用，還沒裝環境
- Given 使用者還沒安裝 `edge-tts` 或 `ffmpeg`
- When 使用者執行 `podcast:setup`
- Then 告知缺哪些工具並給出安裝指令（既有行為，不變）
