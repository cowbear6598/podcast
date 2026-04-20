# Changelog

## [1.1.1] - 2026-04-20

### 新增
- `podcast:tell` skill — 把文章改寫成說書人獨白腳本
- `narration.py` — 合成說書人獨白 mp3 音檔

### 改進
- `content` skill 改名為 `talk`
- 抽出 `_core.py` 共用模組（TTS、重試、靜音、concat）
- `audio` skill 支援自動偵測腳本格式並分派對應 Python 腳本

## [1.1.0] - 2026-04-13
- Initial 1.1.0 release
