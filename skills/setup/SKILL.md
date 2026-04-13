---
name: setup
description: 檢查 podcast 所需的工具是否已安裝（Python edge-tts 套件、ffmpeg），未安裝則提供安裝指引
---

# 工作流程

依序檢查以下工具，未安裝則顯示安裝指令：

| 工具 | 檢查方式 | 安裝指令 |
|------|---------|---------|
| ffmpeg | `which ffmpeg` | `brew install ffmpeg`（Mac）或 `sudo apt install ffmpeg`（Ubuntu）|
| Python 3.8+ | `python3 --version` | 系統內建或 `brew install python` |
| edge-tts | `python3 -c "import edge_tts"` | `pip install edge-tts`（建議在 venv 內安裝）|

# 補充

- `edge-tts` 走微軟 Edge 內部 API，免費、不需 API key
- 僅供個人/內部使用，不建議對外商用（會違反微軟 ToS）
- 公司內部分享為灰色地帶，實務上風險低
