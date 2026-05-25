---
name: setup
description: 檢查 podcast 所需工具是否已安裝：ffmpeg、Python 3.8+、edge-tts。
---

# 工作流程

檢查本機環境，缺少工具時提供安裝指令。

| 工具 | 檢查方式 | 安裝指令 |
|---|---|---|
| ffmpeg | `which ffmpeg` | macOS: `brew install ffmpeg`；Ubuntu: `sudo apt install ffmpeg` |
| Python 3.8+ | `python3 --version` | macOS: `brew install python`；Ubuntu: `sudo apt install python3` |
| edge-tts | `python3 -c "import edge_tts"` | `pip install edge-tts`，建議在 venv 內安裝 |

`edge-tts` 不需要 API key。
