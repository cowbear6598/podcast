"""
共用底層模組：TTS 合成、ffmpeg 裁靜音、重試機制、靜音檔產生、mp3 concat。

供 podcast.py 與 narration.py（及其他需要 TTS 的腳本）共同引用。
"""
import asyncio
import subprocess
import tempfile
from pathlib import Path

import edge_tts

# ---------------------------------------------------------------------------
# 常數
# ---------------------------------------------------------------------------

RATE = "-10%"            # 語速：-20% 更慢 / +0% 正常 / +10% 更快（只接受兩位數）
RETRY_ATTEMPTS = 3       # 同一聲音的重試次數
RETRY_DELAY = 1.5        # 每次重試前等待秒數
PAUSE_SECONDS = 0.25     # 段落間預設靜音長度（秒）

SILENCE_REMOVE_FILTER = (
    "silenceremove=start_periods=1:start_silence=0.1:start_threshold=-40dB:"
    "stop_periods=-1:stop_silence=0.1:stop_threshold=-40dB"
)

# ---------------------------------------------------------------------------
# 核心函式
# ---------------------------------------------------------------------------


async def _tts_once(voice: str, line: str, out_path: Path) -> None:
    """用 edge-tts 合成單句，並用 ffmpeg 裁掉頭尾靜音。"""
    raw = out_path.with_suffix(".raw.mp3")
    communicate = edge_tts.Communicate(line, voice, rate=RATE)
    await communicate.save(str(raw))
    # 裁掉頭尾靜音（< -40dB 超過 0.1 秒算靜音）
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(raw),
         "-af", SILENCE_REMOVE_FILTER,
         "-acodec", "libmp3lame", "-q:a", "4", str(out_path)],
        check=True, capture_output=True,
    )
    raw.unlink()


async def _synth_with_retry(voice: str, line: str, out_path: Path) -> bool:
    """用指定 voice 合成，含重試。成功回傳 True，全部失敗回傳 False。"""
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            await _tts_once(voice, line, out_path)
            return True
        except edge_tts.exceptions.NoAudioReceived:
            if attempt < RETRY_ATTEMPTS:
                print(f"      ↳ NoAudioReceived，{RETRY_DELAY}s 後重試 ({attempt}/{RETRY_ATTEMPTS}) voice={voice}")
                await asyncio.sleep(RETRY_DELAY)
    return False


def make_pause_file(tmp_dir: Path, seconds: float = PAUSE_SECONDS) -> Path:
    """在 tmp_dir 中產生一個指定長度的靜音 mp3，回傳檔案路徑。"""
    pause_file = tmp_dir / f"pause_{seconds}s.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i",
         "anullsrc=r=24000:cl=mono", "-t", str(seconds),
         "-q:a", "9", "-acodec", "libmp3lame", str(pause_file)],
        check=True, capture_output=True,
    )
    return pause_file


def concat_mp3(parts: list[Path], output_path: Path) -> None:
    """用 ffmpeg concat demuxer 將多個 mp3 拼接成一個輸出檔案。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        concat_list = Path(tmpdir) / "list.txt"
        concat_list.write_text(
            "\n".join(f"file '{p}'" for p in parts), encoding="utf-8"
        )
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", str(concat_list), "-c", "copy", str(output_path)],
            check=True, capture_output=True,
        )
