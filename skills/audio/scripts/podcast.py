#!/usr/bin/env python3
"""
把 [曉臻] / [雲哲] 格式的對話腳本轉成雙人 Podcast mp3

用法：
    python podcast.py script.txt
    python podcast.py script.txt -o my_podcast.mp3
"""
import argparse
import asyncio
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import edge_tts

VOICES = {
    "曉臻": "zh-TW-HsiaoChenNeural",
    "雲哲": "zh-TW-YunJheNeural",
}
PAUSE_SECONDS = 0.25
RATE = "-10%"  # 語速：-20% 更慢 / +0% 正常 / +10% 更快（注意：只接受兩位數）


def parse_script(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"\[(曉臻|雲哲)\]\s*(.+?)(?=\n\s*\[(?:曉臻|雲哲)\]|\Z)", re.DOTALL)
    segments = []
    for m in pattern.finditer(text):
        speaker = m.group(1)
        line = re.sub(r"\s+", " ", m.group(2)).strip()
        if line:
            segments.append((speaker, line))
    if not segments:
        sys.exit("腳本裡找不到 [曉臻] 或 [雲哲] 的台詞，請檢查格式")
    return segments


async def synthesize(speaker: str, line: str, out_path: Path) -> None:
    voice = VOICES[speaker]
    raw = out_path.with_suffix(".raw.mp3")
    communicate = edge_tts.Communicate(line, voice, rate=RATE)
    await communicate.save(str(raw))
    # 裁掉頭尾靜音（< -40dB 超過 0.1 秒算靜音）
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(raw),
         "-af", "silenceremove=start_periods=1:start_silence=0.1:start_threshold=-40dB:"
                "stop_periods=-1:stop_silence=0.1:stop_threshold=-40dB",
         "-acodec", "libmp3lame", "-q:a", "4", str(out_path)],
        check=True, capture_output=True,
    )
    raw.unlink()


async def main_async(script_path: Path, output_path: Path) -> None:
    segments = parse_script(script_path)
    print(f"解析到 {len(segments)} 段台詞")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        parts: list[Path] = []

        pause_file = None
        if PAUSE_SECONDS > 0:
            pause_file = tmp / "pause.mp3"
            subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i",
                 f"anullsrc=r=24000:cl=mono", "-t", str(PAUSE_SECONDS),
                 "-q:a", "9", "-acodec", "libmp3lame", str(pause_file)],
                check=True, capture_output=True,
            )

        for i, (speaker, line) in enumerate(segments):
            seg_file = tmp / f"seg_{i:03d}.mp3"
            print(f"  [{i+1}/{len(segments)}] {speaker}: {line[:30]}{'...' if len(line) > 30 else ''}")
            await synthesize(speaker, line, seg_file)
            parts.append(seg_file)
            if pause_file and i < len(segments) - 1:
                parts.append(pause_file)

        concat_list = tmp / "list.txt"
        concat_list.write_text("\n".join(f"file '{p}'" for p in parts), encoding="utf-8")

        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", str(concat_list), "-c", "copy", str(output_path)],
            check=True, capture_output=True,
        )

    size_kb = output_path.stat().st_size // 1024
    print(f"\n完成：{output_path} ({size_kb} KB)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=Path, help="對話腳本檔案 (.txt)")
    ap.add_argument("-o", "--output", type=Path, default=Path("output.mp3"))
    args = ap.parse_args()

    if not args.script.exists():
        sys.exit(f"找不到檔案：{args.script}")

    asyncio.run(main_async(args.script, args.output))


if __name__ == "__main__":
    main()
