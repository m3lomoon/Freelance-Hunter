import os
import re
import tempfile

import yt_dlp

# 允許的影片平台白名單（防止 SSRF）
_ALLOWED_DOMAINS = {
    "youtube.com", "youtu.be", "www.youtube.com",
    "bilibili.com", "www.bilibili.com",
    "tiktok.com", "www.tiktok.com", "vm.tiktok.com",
    "instagram.com", "www.instagram.com",
    "twitter.com", "x.com", "www.twitter.com", "www.x.com",
    "facebook.com", "www.facebook.com", "fb.watch",
    "twitch.tv", "www.twitch.tv",
    "vimeo.com", "www.vimeo.com",
    "nicovideo.jp", "www.nicovideo.jp",
}


def validate_url(url: str) -> str:
    """驗證 URL 是否來自允許的平台，回傳清理後的 URL 或 raise ValueError"""
    url = url.strip()
    if len(url) > 2000:
        raise ValueError("URL 過長（最多 2000 字元）")
    if not url.startswith(("http://", "https://")):
        raise ValueError("連結必須以 http:// 或 https:// 開頭")

    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower().lstrip("www.")
        # 移除 port
        domain = domain.split(":")[0]

        full_domain = parsed.netloc.lower()
        if full_domain not in _ALLOWED_DOMAINS and domain not in _ALLOWED_DOMAINS:
            raise ValueError(
                f"不支援的平台：{full_domain}\n"
                "支援：YouTube、Bilibili、TikTok、Instagram、Twitter/X、Facebook、Twitch、Vimeo"
            )
    except ValueError:
        raise
    except Exception:
        raise ValueError("無效的連結格式")

    return url


def _sanitize_ig_session(session: str) -> str:
    """清理 Instagram session ID — 只保留字母數字底線，防止 CRLF Header Injection"""
    # 移除 % 等可能用於 CRLF 注入的字元（%0d%0a = \r\n）
    cleaned = re.sub(r'[^\w]', '', session.strip())
    if len(cleaned) > 200:
        cleaned = cleaned[:200]
    return cleaned


# ── 影片元數據 ──────────────────────────────────────────────────────────────

_IG_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}


def _build_ydl_opts(base: dict, ig_session: str = "") -> dict:
    if ig_session:
        safe_session = _sanitize_ig_session(ig_session)
        if safe_session:
            base["http_headers"] = {
                **_IG_HEADERS,
                "Cookie": f"sessionid={safe_session}; ds_user_id=0",
            }
    return base


def _is_instagram(url: str) -> bool:
    return "instagram.com" in url.lower()


def get_video_info(url: str, ig_session: str = "") -> dict:
    try:
        url = validate_url(url)
    except ValueError as e:
        return {"error": str(e)}

    base = {"quiet": True, "no_warnings": True, "skip_download": True, "sleep_interval": 1}
    if _is_instagram(url) and not ig_session:
        base["http_headers"] = _IG_HEADERS
    ydl_opts = _build_ydl_opts(base, ig_session)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        err = str(e)
        if "429" in err and _is_instagram(url):
            return {"error": "Instagram 限制存取（429）。請在左側欄輸入你的 Instagram Session ID，或稍後再試。"}
        return {"error": err}

    if not info:
        return {"error": "無法取得影片資訊"}

    return {
        "title": info.get("title", ""),
        "description": info.get("description", ""),
        "view_count": info.get("view_count") or 0,
        "like_count": info.get("like_count") or 0,
        "comment_count": info.get("comment_count") or 0,
        "duration": info.get("duration") or 0,
        "channel": info.get("channel") or info.get("uploader", ""),
        "channel_url": info.get("channel_url") or info.get("uploader_url", ""),
        "channel_follower_count": info.get("channel_follower_count") or 0,
        "upload_date": info.get("upload_date", ""),
        "thumbnail": info.get("thumbnail", ""),
        "webpage_url": info.get("webpage_url") or url,
        "platform": info.get("extractor_key", ""),
        "available_subtitles": list(info.get("subtitles", {}).keys()),
        "available_auto_captions": list(info.get("automatic_captions", {}).keys()),
    }


# ── 逐字稿 ─────────────────────────────────────────────────────────────────

def _extract_youtube_id(url: str) -> str:
    for pattern in [
        r"(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com/(?:embed|shorts)/([a-zA-Z0-9_-]{11})",
    ]:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return ""


def get_transcript(url: str, preferred_langs: list[str] | None = None, ig_session: str = "") -> tuple[list[dict], str]:
    """
    回傳 (entries, detected_lang)
    entries: [{"start": float, "duration": float, "text": str}]
    """
    if preferred_langs is None:
        preferred_langs = ["zh-Hant", "zh-TW", "zh-Hans", "zh", "en", "ja", "ko"]

    # YouTube → 優先用 youtube-transcript-api（快且準）
    video_id = _extract_youtube_id(url)
    if video_id:
        entries, lang = _transcript_via_api(video_id, preferred_langs)
        if entries:
            return entries, lang

    # 其他平台或備援 → yt-dlp 下載字幕
    return _transcript_via_ytdlp(url, preferred_langs, ig_session)


def _transcript_via_api(video_id: str, preferred_langs: list[str]) -> tuple[list[dict], str]:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
    except ImportError:
        return [], ""

    try:
        tlist = YouTubeTranscriptApi.list_transcripts(video_id)
    except TranscriptsDisabled:
        return [], ""
    except Exception:
        return [], ""

    def _fetch(transcript) -> list[dict]:
        data = transcript.fetch()
        return [{"start": e["start"], "duration": e.get("duration", 0), "text": e["text"]} for e in data]

    # 手動字幕優先
    for lang in preferred_langs:
        try:
            return _fetch(tlist.find_manually_created_transcript([lang])), lang
        except Exception:
            continue

    # 自動字幕
    for lang in preferred_langs:
        try:
            return _fetch(tlist.find_generated_transcript([lang])), f"{lang}（自動）"
        except Exception:
            continue

    # 任意可用字幕
    try:
        all_t = list(tlist._manually_created_transcripts.values()) + \
                list(tlist._generated_transcripts.values())
        if all_t:
            t = all_t[0]
            return _fetch(t), t.language_code
    except Exception:
        pass

    return [], ""


def _transcript_via_ytdlp(url: str, preferred_langs: list[str], ig_session: str = "") -> tuple[list[dict], str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = _build_ydl_opts({
            "quiet": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": preferred_langs[:6],
            "subtitlesformat": "vtt",
            "skip_download": True,
            "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
        }, ig_session)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info.get("id", "video")
        except Exception:
            return [], ""

        for lang in preferred_langs:
            path = os.path.join(tmpdir, f"{video_id}.{lang}.vtt")
            if os.path.exists(path):
                return _parse_vtt(path), lang

        for f in os.listdir(tmpdir):
            if f.endswith(".vtt"):
                parts = f.rsplit(".", 2)
                lang = parts[1] if len(parts) >= 3 else "unknown"
                return _parse_vtt(os.path.join(tmpdir, f)), lang

    return [], ""


def _parse_vtt(filepath: str) -> list[dict]:
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    entries = []
    ts_pat = re.compile(
        r"(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})"
    )

    for block in re.split(r"\n\n+", content):
        lines = block.strip().splitlines()
        ts_line = next((l for l in lines if ts_pat.match(l)), None)
        if not ts_line:
            continue

        m = ts_pat.match(ts_line)
        start = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1000
        end   = int(m.group(5)) * 3600 + int(m.group(6)) * 60 + int(m.group(7)) + int(m.group(8)) / 1000

        text_parts = []
        for l in lines:
            if ts_pat.match(l) or l.startswith("WEBVTT") or re.match(r"^\d+$", l) or l.startswith("NOTE"):
                continue
            clean = re.sub(r"<[^>]+>", "", l).strip()
            if clean:
                text_parts.append(clean)

        if text_parts:
            entries.append({"start": start, "duration": end - start, "text": " ".join(text_parts)})

    # 去掉完全重複的相鄰段落
    deduped = []
    for e in entries:
        if not deduped or e["text"] != deduped[-1]["text"]:
            deduped.append(e)
    return deduped


# ── Whisper 語音辨識（備援，無字幕時使用）──────────────────────────────────

_VALID_WHISPER_MODELS = {"tiny", "base", "small", "medium"}


def transcribe_with_whisper(audio_path: str, model_size: str = "base") -> tuple[list[dict], str]:
    if model_size not in _VALID_WHISPER_MODELS:
        raise ValueError(f"不支援的 Whisper 模型：{model_size}")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise RuntimeError("請先安裝 faster-whisper：pip install faster-whisper")

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, beam_size=5)

    entries = [
        {"start": seg.start, "duration": seg.end - seg.start, "text": seg.text.strip()}
        for seg in segments
    ]
    return entries, info.language


# ── 音頻下載 ────────────────────────────────────────────────────────────────

def download_audio(url: str, output_dir: str) -> str:
    """下載音頻為 MP3，回傳檔案路徑。需要 ffmpeg。"""
    ydl_opts = {
        "quiet": True,
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id", "audio")
    except Exception as e:
        raise RuntimeError(f"音頻下載失敗：{e}")

    for fname in os.listdir(output_dir):
        if fname.startswith(video_id):
            return os.path.join(output_dir, fname)

    raise RuntimeError("找不到下載的音頻檔案")
