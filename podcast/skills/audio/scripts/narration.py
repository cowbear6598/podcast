#!/usr/bin/env python3
"""
把 [說書人] 格式的獨白腳本轉成單聲 mp3

用法：
    python narration.py script.txt
    python narration.py script.txt -o my_narration.mp3
"""
import argparse
import asyncio
import json
import re
import sys
import tempfile
from pathlib import Path

from _core import (
    PAUSE_SECONDS,
    _synth_with_retry,
    concat_mp3,
    default_timing_path,
    make_pause_file,
    probe_duration,
)

VOICES = {
    # 說書人候選聲音：主聲音失敗時依序 fallback
    "說書人": ["zh-TW-HsiaoChenNeural", "zh-CN-XiaoxiaoNeural", "zh-HK-HiuGaaiNeural"],
}


def parse_script(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")

    # 誤用保護：偵測雙人對談格式
    if re.search(r"\[曉臻\]", text) or re.search(r"\[雲哲\]", text):
        sys.exit(
            "此腳本為雙人對談格式，請改用 podcast.py：\n"
            f"    python podcast.py {path}"
        )

    pattern = re.compile(r"\[說書人\]\s*(.+?)(?=\n\s*\[說書人\]|\Z)", re.DOTALL)
    segments = []
    for m in pattern.finditer(text):
        line = re.sub(r"\s+", " ", m.group(1)).strip()
        if line:
            segments.append(line)

    if not segments:
        sys.exit("腳本裡找不到 [說書人] 的段落，請檢查格式")

    return segments


async def synth_all(voice: str, lines: list[str], tmp: Path) -> list[Path] | None:
    """用同一個聲音把所有段落合成完；任一段失敗就回傳 None（all-or-nothing）。"""
    results: list[Path] = []
    for idx, line in enumerate(lines):
        seg_file = tmp / f"seg_{idx:03d}_{voice}.mp3"
        if not await _synth_with_retry(voice, line, seg_file):
            return None
        results.append(seg_file)
    return results


def build_timing(
    script_path: Path,
    output_path: Path,
    segments: list[str],
    seg_files: list[Path],
    audio_duration: float,
) -> dict:
    timeline = []
    cursor = 0.0
    for idx, (line, seg_file) in enumerate(zip(segments, seg_files)):
        duration = probe_duration(seg_file)
        start = cursor
        end = start + duration
        timeline.append(
            {
                "index": idx,
                "start": round(start, 3),
                "end": round(end, 3),
                "speaker": "說書人",
                "text": line,
            }
        )
        cursor = end
        if idx < len(seg_files) - 1:
            cursor += PAUSE_SECONDS

    return {
        "script": str(script_path),
        "audio": str(output_path),
        "duration": round(audio_duration, 3),
        "timingSource": "tts-segment",
        "pauseSeconds": PAUSE_SECONDS,
        "segments": timeline,
    }


async def main_async(script_path: Path, output_path: Path, timing_path: Path) -> None:
    segments = parse_script(script_path)
    print(f"解析到 {len(segments)} 段說書人台詞")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        candidates = VOICES["說書人"]
        seg_files: list[Path] | None = None

        for v_idx, voice in enumerate(candidates):
            print(f"▶ 說書人 用 {voice} 生成 {len(segments)} 段")
            result = await synth_all(voice, segments, tmp)
            if result is not None:
                if v_idx > 0:
                    print(f"  ✓ fallback 成功（跳過主聲音 {candidates[0]}）")
                seg_files = result
                break
            if v_idx < len(candidates) - 1:
                print(f"  ⚠ {voice} 有段落失敗，整批改用下一個聲音 {candidates[v_idx + 1]} 重做")
            else:
                raise RuntimeError(f"說書人所有聲音都失敗：{candidates}")

        pause_file = make_pause_file(tmp, PAUSE_SECONDS) if PAUSE_SECONDS > 0 else None

        parts: list[Path] = []
        for i, seg in enumerate(seg_files):
            parts.append(seg)
            if pause_file and i < len(seg_files) - 1:
                parts.append(pause_file)

        concat_mp3(parts, output_path)
        audio_duration = probe_duration(output_path)
        timing = build_timing(script_path, output_path, segments, seg_files, audio_duration)
        timing_path.write_text(
            json.dumps(timing, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    size_kb = output_path.stat().st_size // 1024
    print(f"\n完成：{output_path} ({size_kb} KB)")
    print(f"Timing：{timing_path}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="把 [說書人] 格式的獨白腳本轉成 mp3"
    )
    ap.add_argument("script", type=Path, help="說書人腳本檔案 (.txt)")
    ap.add_argument("-o", "--output", type=Path, default=Path("output.mp3"))
    ap.add_argument("--timing", type=Path, help="Timing JSON 輸出路徑，預設由 mp3 檔名推導")
    args = ap.parse_args()

    if not args.script.exists():
        sys.exit(f"找不到檔案：{args.script}")

    timing_path = args.timing or default_timing_path(args.output)
    asyncio.run(main_async(args.script, args.output, timing_path))


if __name__ == "__main__":
    main()
