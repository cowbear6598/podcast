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
import sys
import tempfile
from pathlib import Path

from _core import (
    PAUSE_SECONDS,
    RATE,
    RETRY_ATTEMPTS,
    RETRY_DELAY,
    _synth_with_retry,
    concat_mp3,
    make_pause_file,
)

VOICES = {
    # 每個角色用 list：主聲音失敗時依序 fallback
    "曉臻": ["zh-TW-HsiaoChenNeural", "zh-CN-XiaoxiaoNeural", "zh-HK-HiuGaaiNeural"],
    "雲哲": ["zh-TW-YunJheNeural", "zh-CN-YunxiNeural", "zh-HK-WanLungNeural"],
}


def parse_script(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    if "[說書人]" in text:
        print(
            "此腳本為說書人獨白格式，請改用 narration.py：\n"
            "    python narration.py ..."
        )
        sys.exit(1)
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


def _voice_candidates(speaker: str) -> list[str]:
    voices = VOICES[speaker]
    return [voices] if isinstance(voices, str) else list(voices)


async def synth_speaker_all(
    speaker: str, voice: str, speaker_segments: list[tuple[int, str]], tmp: Path
) -> dict[int, Path] | None:
    """用同一個聲音把該角色的所有段落合成完；任一段失敗就回傳 None 讓外層 fallback。"""
    results: dict[int, Path] = {}
    for idx, line in speaker_segments:
        seg_file = tmp / f"seg_{idx:03d}_{voice}.mp3"
        if not await _synth_with_retry(voice, line, seg_file):
            return None
        results[idx] = seg_file
    return results


async def main_async(script_path: Path, output_path: Path) -> None:
    segments = parse_script(script_path)
    print(f"解析到 {len(segments)} 段台詞")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 按角色分組段落
        by_speaker: dict[str, list[tuple[int, str]]] = {}
        for i, (speaker, line) in enumerate(segments):
            by_speaker.setdefault(speaker, []).append((i, line))

        # 每個角色依序嘗試候選聲音，某聲音任一段失敗就整個角色換下一個聲音重做
        seg_files: dict[int, Path] = {}
        for speaker, speaker_segs in by_speaker.items():
            candidates = _voice_candidates(speaker)
            for v_idx, voice in enumerate(candidates):
                print(f"▶ {speaker} 用 {voice} 生成 {len(speaker_segs)} 段")
                result = await synth_speaker_all(speaker, voice, speaker_segs, tmp)
                if result is not None:
                    if v_idx > 0:
                        print(f"  ✓ fallback 成功（跳過主聲音 {candidates[0]}）")
                    seg_files.update(result)
                    break
                if v_idx < len(candidates) - 1:
                    print(f"  ⚠ {voice} 有段落失敗，整個 {speaker} 改用下一個聲音 {candidates[v_idx + 1]} 重做")
                else:
                    raise RuntimeError(f"{speaker} 所有聲音都失敗：{candidates}")

        pause_file = None
        if PAUSE_SECONDS > 0:
            pause_file = make_pause_file(tmp, PAUSE_SECONDS)

        parts: list[Path] = []
        for i in range(len(segments)):
            parts.append(seg_files[i])
            if pause_file and i < len(segments) - 1:
                parts.append(pause_file)

        concat_mp3(parts, output_path)

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
