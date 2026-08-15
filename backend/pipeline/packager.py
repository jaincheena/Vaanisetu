"""
VaaniSetu — Output Packager
Generates .txt, bilingual .docx, .srt, .vtt, TTS .mp3, captioned .mp4, and manifest ZIP.
"""

import json
import logging
import os
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger("vaanisetu.packager")


# ---------------------------------------------------------------------------
# Plain text
# ---------------------------------------------------------------------------
def write_txt(segments: list[dict], lang_name: str, out_dir: Path) -> str:
    path = str(out_dir / f"translation_{lang_name}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# VaaniSetu Translation — {lang_name}\n")
        f.write(f"# Generated: {datetime.now().strftime('%d %b %Y %H:%M')}\n\n")
        for seg in segments:
            f.write(seg.get("translated", "") + "\n")
    return path


# ---------------------------------------------------------------------------
# Bilingual DOCX
# ---------------------------------------------------------------------------
def write_bilingual_docx(
    segments: list[dict],
    source_lang: str,
    target_lang: str,
    out_dir: Path,
    farmer_context: Optional[str] = None,
    mode: str = "translate",
) -> str:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    
    if mode == "reverse_bridge" or (farmer_context and farmer_context.strip()):
        title = doc.add_heading("BAIF Development Research Foundation — Farmer Query Advisory", level=1)
        title.runs[0].font.color.rgb = RGBColor(27, 67, 50)
        
        doc.add_paragraph(f"Operational Mode: Reverse Bridge (Field Recording Translation)")
        doc.add_paragraph(f"Languages: {source_lang} (Farmer Voice) ➔ {target_lang} (HQ Translation)")
        doc.add_paragraph(f"Generated on: {datetime.now().strftime('%d %b %Y, %H:%M')} (IST)")
        
        if farmer_context and farmer_context.strip():
            doc.add_heading("Field Recording & Farmer Context", level=2)
            ctx_p = doc.add_paragraph(farmer_context.strip())
            ctx_p.paragraph_format.left_indent = Inches(0.2)
            if ctx_p.runs:
                ctx_p.runs[0].font.italic = True
                
        doc.add_heading("Spoken Query & Translation", level=2)
    else:
        title = doc.add_heading(f"VaaniSetu — {source_lang} ↔ {target_lang}", level=1)
        title.runs[0].font.color.rgb = RGBColor(27, 67, 50)
        doc.add_paragraph(f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}")
        doc.add_paragraph("")

    table = doc.add_table(rows=1, cols=2)
    table.style = "Light Grid"
    hdr = table.rows[0].cells
    hdr[0].text = f"{source_lang} (Original)"
    hdr[1].text = f"{target_lang} (Translation)"
    for cell in hdr:
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(82, 183, 136)

    for seg in segments:
        row = table.add_row().cells
        row[0].text = seg.get("text", "")
        row[1].text = seg.get("translated", "")

    if mode == "reverse_bridge" or (farmer_context and farmer_context.strip()):
        doc.add_paragraph("")
        doc.add_heading("HQ Expert / Agronomist Advisory & Action Plan", level=2)
        p = doc.add_paragraph(
            "Diagnosis / Recommendation for Field Worker:\n\n"
            "_________________________________________________________________________________\n\n"
            "_________________________________________________________________________________\n\n"
            "Signature / Reviewed By: ___________________________   Date: ____________________"
        )

    path = str(out_dir / f"bilingual_{target_lang}.docx")
    doc.save(path)
    return path


# ---------------------------------------------------------------------------
# Translated CSV
# ---------------------------------------------------------------------------
def write_translated_csv(
    segments: list[dict],
    lang_name: str,
    out_dir: Path,
) -> str:
    import csv
    path = str(out_dir / f"translated_{lang_name}.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Original", f"Translation ({lang_name})"])
        for seg in segments:
            writer.writerow([seg.get("text", ""), seg.get("translated", "")])
    return path


# ---------------------------------------------------------------------------
# SRT subtitles
# ---------------------------------------------------------------------------
def _fmt_srt_time(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    total_ms = int(td.total_seconds() * 1000)
    h, rem = divmod(total_ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms  = divmod(rem, 1_000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _wrap_caption_line(text: str, max_chars: int = 42) -> str:
    """
    Wrap caption text so no line exceeds max_chars characters.
    Splits on word boundaries; preserves existing newlines.
    TV-safe: max 42 chars/line, max 2 lines.
    """
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if current and len(current) + 1 + len(word) > max_chars:
            lines.append(current)
            current = word
            if len(lines) == 2:
                # Cap at 2 lines — append remaining words to line 2
                remaining = " ".join(words[words.index(word):])
                lines[-1] = remaining[:max_chars * 2]  # hard truncate if extreme
                break
        else:
            current = (current + " " + word).strip() if current else word
    if current and len(lines) < 2:
        lines.append(current)
    return "\n".join(lines)


def write_srt(segments: list[dict], lang_name: str, out_dir: Path) -> str:
    path = str(out_dir / f"subtitles_{lang_name}.srt")
    with open(path, "w", encoding="utf-8") as f:
        idx = 1
        for seg in segments:
            text = seg.get("translated", "").strip()
            if not text:
                continue
            start_s = float(seg.get("start", 0))
            end_s   = float(seg.get("end",   0))
            # Enforce minimum cue duration of 0.5 s
            if end_s <= start_s:
                end_s = start_s + 0.5
            elif end_s - start_s < 0.5:
                end_s = start_s + 0.5
            start = _fmt_srt_time(start_s)
            end   = _fmt_srt_time(end_s)
            wrapped = _wrap_caption_line(text)
            f.write(f"{idx}\n{start} --> {end}\n{wrapped}\n\n")
            idx += 1
    return path


# ---------------------------------------------------------------------------
# WebVTT subtitles
# ---------------------------------------------------------------------------
def _fmt_vtt_time(seconds: float) -> str:
    return _fmt_srt_time(seconds).replace(",", ".")


def write_vtt(segments: list[dict], lang_name: str, out_dir: Path) -> str:
    path = str(out_dir / f"subtitles_{lang_name}.vtt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        idx = 1
        for seg in segments:
            text = seg.get("translated", "").strip()
            if not text:
                continue
            start_s = float(seg.get("start", 0))
            end_s   = float(seg.get("end",   0))
            if end_s <= start_s:
                end_s = start_s + 0.5
            elif end_s - start_s < 0.5:
                end_s = start_s + 0.5
            start = _fmt_vtt_time(start_s)
            end   = _fmt_vtt_time(end_s)
            wrapped = _wrap_caption_line(text)
            f.write(f"{idx}\n{start} --> {end}\n{wrapped}\n\n")
            idx += 1
    return path


# ---------------------------------------------------------------------------
# TTS MP3
# ---------------------------------------------------------------------------
def write_tts_mp3(
    segments: list[dict],
    lang_name: str,
    out_dir: Path,
    quality_mode: str = "full",
    voice_gender: str = "female",
    speaker_wav: Optional[str] = None,
) -> Optional[str]:
    from backend.pipeline.tts import generate_tts_for_segments
    mp3_path = str(out_dir / f"audio_{lang_name}.mp3")
    result = generate_tts_for_segments(
        segments, lang_name, mp3_path,
        quality_mode=quality_mode,
        voice_gender=voice_gender,
        speaker_wav=speaker_wav,
    )
    return result


# ---------------------------------------------------------------------------
# Dubbed MP4 (Video with Translated Audio)
# ---------------------------------------------------------------------------
def write_dubbed_mp4(
    original_video_path: Optional[str],
    audio_path: Optional[str],
    lang_name: str,
    out_dir: Path,
) -> Optional[str]:
    if not original_video_path or not os.path.exists(original_video_path):
        return None
    if not audio_path or not os.path.exists(audio_path):
        return None
    from backend.pipeline.audio_extractor import replace_video_audio
    out_path = str(out_dir / f"dubbed_{lang_name}.mp4")
    try:
        return replace_video_audio(original_video_path, audio_path, out_path)
    except Exception as e:
        logger.warning(f"Dubbed MP4 generation failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Captioned & Dubbed MP4
# ---------------------------------------------------------------------------
def write_captioned_mp4(
    original_video_path: Optional[str],
    srt_path: str,
    lang_name: str,
    out_dir: Path,
    audio_path: Optional[str] = None,
) -> Optional[str]:
    if not original_video_path or not os.path.exists(original_video_path):
        return None
    from backend.pipeline.audio_extractor import burn_subtitles
    out_path = str(out_dir / f"captioned_{lang_name}.mp4")
    try:
        return burn_subtitles(original_video_path, srt_path, out_path, audio_path=audio_path)
    except Exception as e:
        logger.warning(f"Captioned MP4 generation failed: {e}")
        return None


# ---------------------------------------------------------------------------
# IVR / Feature Phone Export
# ---------------------------------------------------------------------------
def write_ivr_wav(
    mp3_path: Optional[str],
    lang_name: str,
    out_dir: Path,
) -> Optional[str]:
    if not mp3_path or not os.path.exists(mp3_path):
        return None
    import subprocess
    wav_path = str(out_dir / f"ivr_audio_{lang_name}.wav")
    try:
        # Downsample to 8kHz mono for IVR / feature phone compatibility
        from backend.utils.ffmpeg import ffmpeg_executable

        cmd = [ffmpeg_executable(), "-y", "-i", mp3_path, "-ar", "8000", "-ac", "1", wav_path]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return wav_path
    except Exception as e:
        logger.warning(f"IVR WAV generation failed: {e}")
        return None


# ---------------------------------------------------------------------------
# WhatsApp Auto-Splitter
# ---------------------------------------------------------------------------
def write_whatsapp_chunks(
    mp4_path: Optional[str],
    lang_name: str,
    out_dir: Path,
) -> list[str]:
    if not mp4_path or not os.path.exists(mp4_path):
        return []
    
    # Check file size. If < 15MB, no splitting needed.
    size_mb = os.path.getsize(mp4_path) / (1024 * 1024)
    if size_mb <= 15:
        return []

    import subprocess
    chunk_pattern = str(out_dir / f"whatsapp_part%02d_{lang_name}.mp4")
    try:
        # Split into 60-second segments (safest cross-platform way without re-encoding)
        from backend.utils.ffmpeg import ffmpeg_executable

        cmd = [
            ffmpeg_executable(), "-y", "-i", mp4_path,
            "-c", "copy", "-f", "segment",
            "-segment_time", "60",
            "-reset_timestamps", "1",
            chunk_pattern
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Collect generated chunks
        chunks = []
        for f in os.listdir(out_dir):
            if f.startswith("whatsapp_part") and f.endswith(f"_{lang_name}.mp4"):
                chunks.append(str(out_dir / f))
        return chunks
    except Exception as e:
        logger.warning(f"WhatsApp splitter failed: {e}")
        return []


# ---------------------------------------------------------------------------
# ZIP + manifest
# ---------------------------------------------------------------------------
def create_zip(
    job_id: str,
    out_dir: Path,
    file_paths: list[str],
    job_meta: dict,
    zip_path: str,
) -> str:
    manifest = {
        "job_id":     job_id,
        "generated":  datetime.utcnow().isoformat(),
        "source_lang": job_meta.get("source_lang"),
        "target_langs": job_meta.get("target_langs", []),
        "files": [os.path.basename(p) for p in file_paths if p and os.path.exists(p)],
        "file_guide": {
            "translation_LANG.txt":       {"size": "tiny",   "use": "Plain text — SMS, app content, offline reading"},
            "bilingual_LANG.docx":        {"size": "small",  "use": "Printed handout for field officers & trainers"},
            "subtitles_LANG.srt":         {"size": "tiny",   "use": "Subtitles for VLC player, video editors"},
            "subtitles_LANG.vtt":         {"size": "tiny",   "use": "Subtitles for web/YouTube embed"},
            "audio_LANG.mp3":             {"size": "medium", "use": "AI-spoken audio — radio, WhatsApp audio broadcast"},
            "dubbed_LANG.mp4":            {"size": "LARGE",  "use": "Video with translated audio — gram panchayat screenings"},
            "captioned_LANG.mp4":         {"size": "LARGE",  "use": "Video with burned subtitles — social media, WhatsApp"},
            "ivr_LANG.wav":               {"size": "small",  "use": "8kHz telephone audio for IVR/feature phone calls"},
            "whatsapp_partXX_LANG.mp4":   {"size": "medium", "use": "Auto-split <15MB chunks for WhatsApp delivery"},
            "translated_LANG.csv":        {"size": "tiny",   "use": "Translated CSV data — field survey reporting"},
        }
    }
    manifest_path = str(out_dir / "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(manifest_path, "manifest.json")
        for fp in file_paths:
            if fp and os.path.exists(fp):
                zf.write(fp, os.path.basename(fp))

    logger.info(f"ZIP created: {zip_path}")
    return zip_path
